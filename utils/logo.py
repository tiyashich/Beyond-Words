import os
import base64

def get_base64_image(image_path):
    # Safe path variations avoiding destructive global .capitalize() side-effects
    paths_to_try = [
        image_path,
        image_path.lower(),
        # Capitalizes only the file name base rather than breaking folder structures
        os.path.join(os.path.dirname(image_path), os.path.basename(image_path).capitalize()) if os.path.dirname(image_path) else image_path.capitalize()
    ]
    
    for p in paths_to_try:
        if p and os.path.exists(p):
            with open(p, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    return None