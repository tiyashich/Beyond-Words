import cv2
import numpy as np
import tensorflow as tf
from keras.applications.xception import preprocess_input
from utils.constants import IMG_RESOLUTION

def apply_clahe_tf(images):
    def _clahe_numpy(img_batch):
        img_batch_uint8 = np.clip(img_batch, 0, 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        processed = np.empty((img_batch_uint8.shape[0], img_batch_uint8.shape[1], img_batch_uint8.shape[2], 1), dtype=np.float32)
        
        for i in range(img_batch_uint8.shape[0]):
            single_img = img_batch_uint8[i, :, :, 0]
            processed[i, :, :, 0] = clahe.apply(single_img)
        return processed
    return tf.numpy_function(_clahe_numpy, [images], tf.float32)

def preprocess_cropped_image(crop_bgr):
    # Sharpness Optimization: Blur reduction via Unsharp Digital Masking
    gaussian_blur = cv2.GaussianBlur(crop_bgr, (5, 5), 0)
    sharpened_bgr = cv2.addWeighted(crop_bgr, 1.5, gaussian_blur, -0.5, 0)
    
    crop_rgb = cv2.cvtColor(sharpened_bgr, cv2.COLOR_BGR2RGB)
    img_tensor = tf.convert_to_tensor(crop_rgb, dtype=tf.float32)
    img_resized = tf.image.resize(img_tensor, [IMG_RESOLUTION, IMG_RESOLUTION])
    img_batch = tf.expand_dims(img_resized, axis=0)
    
    gray = tf.image.rgb_to_grayscale(img_batch)
    gray = apply_clahe_tf(gray)
    gray.set_shape((1, IMG_RESOLUTION, IMG_RESOLUTION, 1))
    
    three_channel = tf.image.grayscale_to_rgb(gray)
    processed = preprocess_input(three_channel)
    return processed