# =====================================================================
# 📊 PIPELINE CONSTANTS & BENGALI CHARACTER TRACKING MAP
# =====================================================================
IMG_RESOLUTION = 299
FALLBACK_CONFIDENCE_THRESHOLD = 0.3

# Minimum acceptable mean grayscale luminance (0-255 scale) for a captured
# frame to be considered usable. Below this, the frame is rejected before
# YOLO detection or the recognition model ever run.
LUMINANCE_THRESHOLD = 65

MODEL_PATH = "weights/bdsl49_xception_triplet.keras"
CENTROIDS_PATH = "weights/class_centroids.npy"
CLASS_NAMES_PATH = "weights/class_names.json"
CLASS_THRESHOLDS_PATH = "weights/class_thresholds.json"

BENGALI_CHARS = [
    'অ', 'আ', 'ই', 'উ', 'এ', 'ও', 'ক', 'খ', 'গ', 'ঘ',
    'চ', 'ছ', 'জ', 'ঝ', 'ট', 'ঠ', 'ড', 'ঢ', 'ত', 'থ',
    'দ', 'ধ', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য়', 'র', 'ল',
    'ন', 'স', 'হ', 'ড়', 'ৎ', 'ঃ', 'ং', '১', '২', '৩',
    '৪', '৫', '৬', '৭', '৮', '৯', 'ৃ', 'space', 'ঞ'
]