import cv2
import numpy as np
import tensorflow as tf

from utils.image_utils import preprocess_cropped_image

def generate_gradcam(crop_bgr, feature_extractor, backbone_grad_model, target_centroid):
    gap_layer = feature_extractor.get_layer("gradcam_gap")
    dense_layer = feature_extractor.get_layer("gradcam_dense")
    bn_layer = feature_extractor.get_layer("gradcam_batch_norm")
    lambda_layer = feature_extractor.get_layer("metric_embedding")

    batch_img = preprocess_cropped_image(crop_bgr)

    with tf.GradientTape() as tape:
        last_conv_output, backbone_features = backbone_grad_model(batch_img, training=False)
        tape.watch(last_conv_output)
        x = gap_layer(backbone_features)
        x = dense_layer(x)
        x = bn_layer(x, training=False)
        embedding = lambda_layer(x)
        similarity_score = tf.reduce_sum(embedding[0] * target_centroid)

    grads = tape.gradient(similarity_score, last_conv_output)[0]
    last_conv_output = last_conv_output[0]

    weights = tf.reduce_mean(grads, axis=(0, 1))
    cam = tf.reduce_sum(weights * last_conv_output, axis=-1).numpy()
    cam = np.maximum(cam, 0)

    if np.max(cam) != 0:
        cam = cam / np.max(cam)

    cam_resized = cv2.resize(cam, (crop_bgr.shape[1], crop_bgr.shape[0]))
    heatmap = np.uint8(255 * cam_resized)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    gradcam_output = cv2.addWeighted(crop_bgr, 0.6, heatmap_colored, 0.4, 0)
    return cv2.cvtColor(gradcam_output, cv2.COLOR_BGR2RGB)