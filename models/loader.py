import json
import numpy as np
import streamlit as st
import tensorflow as tf

from keras import layers, models
from ultralytics import YOLO

from utils.constants import (
    IMG_RESOLUTION,
    MODEL_PATH,
    CENTROIDS_PATH,
    CLASS_NAMES_PATH,
    CLASS_THRESHOLDS_PATH,
)


@st.cache_resource
def load_yolo_detector():
    return YOLO("weights/best.pt")


@st.cache_resource
def load_recognition_pipeline():
    base_engine = tf.keras.applications.Xception(
        weights=None,
        include_top=False,
        input_shape=(IMG_RESOLUTION, IMG_RESOLUTION, 3),
    )

    image_input = layers.Input(
        shape=(IMG_RESOLUTION, IMG_RESOLUTION, 3),
        name="image_input",
    )

    x = base_engine(image_input)
    
    # ADDED NAMES HERE:
    x = layers.GlobalAveragePooling2D(name="gradcam_gap")(x)
    x = layers.Dense(512, activation=None, name="gradcam_dense")(x)
    x = layers.BatchNormalization(name="gradcam_batch_norm")(x)
    embedding_output = layers.Lambda(
        lambda v: tf.nn.l2_normalize(v, axis=1),
        output_shape=(512,),
        name="metric_embedding",
    )(x)

    feature_extractor = models.Model(
        inputs=image_input,
        outputs=embedding_output,
    )

    feature_extractor.load_weights(
        MODEL_PATH,
        skip_mismatch=True,
    )

    # --- FIX: Construct the missing backbone_grad_model for Grad-CAM ---
    # Taps into Xception's final convolutional layer activation
    last_conv_layer = base_engine.get_layer("block14_sepconv2_act")
    backbone_grad_model = models.Model(
        inputs=base_engine.input,
        outputs=[last_conv_layer.output, base_engine.output]
    )

    centroids = np.load(CENTROIDS_PATH)

    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    with open(CLASS_THRESHOLDS_PATH) as f:
        class_thresholds = json.load(f)

    return (
        feature_extractor,
        backbone_grad_model,  # Now returning the 5th element
        centroids,
        class_names,
        class_thresholds,
    )