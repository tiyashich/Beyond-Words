import numpy as np

from utils.image_utils import preprocess_cropped_image
from utils.constants import (
    BENGALI_CHARS,
    FALLBACK_CONFIDENCE_THRESHOLD,
)
from models.gradcam import generate_gradcam

def predict_crop(crop_bgr, feature_extractor, backbone_grad_model, centroids, class_names, class_thresholds):
    batch = preprocess_cropped_image(crop_bgr)
    embedding = feature_extractor(batch, training=False).numpy()[0]

    similarities = np.dot(centroids, embedding)
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])
    best_class_name = class_names[best_idx]
    target_centroid = centroids[best_idx]

    # Clean class lookup
    try:
        folder_idx = int(best_class_name)
        bengali_char = BENGALI_CHARS[folder_idx]
    except (ValueError, IndexError):
        bengali_char = best_class_name

    # Top 3 Translated Elements
    top3_idx = np.argsort(similarities)[::-1][:3]
    top3_translated = []
    for i in top3_idx:
        try:
            f_idx = int(class_names[i])
            char = BENGALI_CHARS[f_idx]
        except (ValueError, IndexError):
            char = class_names[i]
        top3_translated.append((char, float(similarities[i])))

    # Resolve actual classification thresholds
    class_info = class_thresholds.get(best_class_name)
    threshold = class_info["threshold"] if class_info else FALLBACK_CONFIDENCE_THRESHOLD

    # --- FIXED: Passed backbone_grad_model to satisfy 4-arg signature requirement ---
    if best_score >= threshold:
        explanation_heatmap = generate_gradcam(crop_bgr, feature_extractor, backbone_grad_model, target_centroid)
    else:
        explanation_heatmap = None

    return bengali_char, best_class_name, best_score, threshold, top3_translated, explanation_heatmap