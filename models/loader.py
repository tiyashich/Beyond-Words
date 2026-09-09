import json
import numpy as np
import streamlit as st
import tensorflow as tf

# Force TensorFlow to run entirely on CPU and hide GPU devices
tf.config.set_visible_devices([], 'GPU')
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)

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
    # Force PyTorch model underlying YOLO to map directly to CPU memory
    model = YOLO("weights/best.pt")
    model.to("cpu")
    return model


@st.cache_resource
def load_recognition_pipeline():
    # Enforce CPU execution context during Keras model instantiation
    with tf.device('/CPU:0'):
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

        # Construct the backbone_grad_model for Grad-CAM
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
        backbone_grad_model,
        centroids,
        class_names,
        class_thresholds,
    )