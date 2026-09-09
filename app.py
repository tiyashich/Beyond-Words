import os
import sys

# -------------------------------------------------------------------
# 1. ENVIRONMENT VARIABLES (MUST BE BEFORE ANY THIRD-PARTY IMPORTS)
# -------------------------------------------------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["USE_CUDA"] = "0"
os.environ["FORCE_CPU"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Force PyTorch to disable CUDA initialization checks entirely
try:
    import torch
    torch.cuda.is_available = lambda: False
except ImportError:
    pass

import cv2
import time
import numpy as np
import streamlit as st
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.predictor import predict_crop
from ui.session import initialize_session
from utils.constants import (
    IMG_RESOLUTION,
    FALLBACK_CONFIDENCE_THRESHOLD,
    LUMINANCE_THRESHOLD,
    MODEL_PATH,
    CENTROIDS_PATH,
    CLASS_NAMES_PATH,
    CLASS_THRESHOLDS_PATH,
    BENGALI_CHARS,
)
from utils.logo import get_base64_image
from utils.image_utils import apply_clahe_tf, preprocess_cropped_image
from models.gradcam import generate_gradcam
from ui.styles import custom_css

# -------------------------------------------------------------------
# 2. PAGE SETUP & STRUCTURAL CSS INJECTION
# -------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Beyond Words | BDSL49")
st.html(custom_css)

# Signature Branding Setup
logo_base64 = get_base64_image("assets/Signature_tc.png")
if logo_base64:
    st.html(
        f"""
        <div style="position: fixed; bottom: 24px; right: 24px; width: 110px; z-index: 999999; pointer-events: none;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100%; height: auto; opacity: 0.75;">
        </div>
        """
    )

# Load AI Engine models safely
from models.loader import load_yolo_detector, load_recognition_pipeline
try:
    detector = load_yolo_detector()
    feature_extractor, backbone_grad_model, centroids, class_names, class_thresholds = load_recognition_pipeline()
    system_online = True
except Exception as e:
    st.error(f"System Offline - Pipeline Initialization Failure: {e}")
    system_online = False

initialize_session()

# -------------------------------------------------------------------
# 3. BRAND HEADERS
# -------------------------------------------------------------------
st.title("Beyond Words: A Sign Language Recognition System")
st.html('<span class="subtitle-text" style="font-style: italic !important;">Decoding Signs, Empowering Lives</span>')

# -------------------------------------------------------------------
# 4. CONTROL MATRIX PANEL
# -------------------------------------------------------------------
with st.container(border=True):
    st.html('<div class="control-matrix-marker"></div>')
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.2, 1.0, 0.8], gap="medium") 
    with col_ctrl1:
        st.html("""
        <div class="section-label">
            <span>📹</span> Video Source
        </div>
        """)
        camera_choice = st.selectbox(
            label="Video Device Source",
            options=[
                "Integrated Device Camera (Built-in Webcam)",
                "Iriun Virtual Webcam / External USB Camera"
            ],
            label_visibility="collapsed"
        )
    with col_ctrl2:
        st.html("""
        <div class="section-label">
            <span>🔍</span> Optical / Digital Zoom
        </div>
        """)
        zoom_factor = st.slider(
            label="Camera Zoom Scaler",
            min_value=1.0,
            max_value=3.0,
            value=1.0,
            step=0.1,
            format="%.1fx",
            label_visibility="collapsed",
            key="zoom_scaler_slider"
        )
    with col_ctrl3:
        st.html("""<div style="margin-top: 25px;"></div>""")
        if st.session_state.get("run_camera", False):
            if st.button("🛑 Stop Stream", use_container_width=True, key="stop_cam_btn", type="secondary"):
                st.session_state.run_camera = False
                st.rerun()
        else:
            if st.button("🚀 Start Live Stream", use_container_width=True, key="launch_cam_btn", type="primary"):
                st.session_state.run_camera = True
                st.session_state.saved_prediction = None
                st.rerun()

if "gesture_history" not in st.session_state:
    st.session_state.gesture_history = []

def apply_digital_zoom(frame_bgr, zoom):
    """Crops and rescales frame centered on video coordinates based on zoom factor."""
    if zoom <= 1.0:
        return frame_bgr
    h, w, _ = frame_bgr.shape
    new_h, new_w = int(h / zoom), int(w / zoom)
    y1 = (h - new_h) // 2
    x1 = (w - new_w) // 2
    cropped_center = frame_bgr[y1 : y1 + new_h, x1 : x1 + new_w]
    return cv2.resize(cropped_center, (w, h), interpolation=cv2.INTER_LINEAR)

# -------------------------------------------------------------------
# 5. MAIN LIVE VIEWPORT WORKSPACE
# -------------------------------------------------------------------
col1, col2 = st.columns([1.35, 0.65], gap="large")
with col1:
    with st.container(key="viewfinder_panel"):
        st.markdown('<div class="panel"><h3 class="panel-title">LIVE VIEWFINDER</h3>', unsafe_allow_html=True)
        st.html('<div class="viewfinder-wrapper">')
        
        countdown_banner = st.empty()
        
        if not st.session_state.get("run_camera", False) and st.session_state.get("saved_prediction") is None:
            st.markdown('<div class="viewfinder">CAMERA FEED OFFLINE</div>', unsafe_allow_html=True)
            camera_file = None
        else:
            camera_file = st.camera_input("Capture Hand Gesture", label_visibility="collapsed", disabled=not system_online)

        st.html('</div>')
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        if st.session_state.get("saved_prediction") is None:
            shutter_btn = st.button(
                "📸 CAPTURE HAND GESTURE", 
                type="primary", 
                disabled=not (system_online and camera_file is not None), 
                use_container_width=True,
                key="shutter_action_trigger"
            )
        else:
            shutter_btn = False
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# 6. DIAGNOSTICS & COUNTDOWN PROCESSOR
# -------------------------------------------------------------------
if shutter_btn and camera_file is not None:
    # 3-Second Countdown Simulation Overlay
    for seconds_left in range(3, 0, -1):
        countdown_banner.markdown(
            f'<div class="floating-countdown-overlay">⏱️ Capturing in {seconds_left}s</div>', 
            unsafe_allow_html=True
        )
        time.sleep(1.0)
    
    countdown_banner.markdown(
        '<div class="floating-countdown-overlay">Running Diagnostics Pipeline...</div>', 
        unsafe_allow_html=True
    )

    # Process photo from browser buffer safely
    file_bytes = np.asarray(bytearray(camera_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if frame is not None:
        frame = apply_digital_zoom(frame, zoom_factor)
        full_frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.session_state.saved_full_view = full_frame_rgb
        
        mean_luminance = float(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean())
        if mean_luminance < LUMINANCE_THRESHOLD:
            st.session_state.saved_prediction = {
                "low_light": True,
                "luminance": mean_luminance,
            }
        else:
            # Force CPU execution inside YOLO detector to avoid CUDA driver checks
            yolo_results = detector(frame, conf=0.40, device="cpu", verbose=False)[0]
            if len(yolo_results.boxes) == 0:
                st.session_state.saved_prediction = {
                    "no_hand": True,
                }
            else:
                best_box = yolo_results.boxes[0].xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = best_box
                h_orig, w_orig = frame.shape[:2]
                crop_bgr = frame[max(0, y1):min(h_orig, y2), max(0, x1):min(w_orig, x2)]
                
                bengali_char, best_class_name, score, threshold, top3, explanation_map = predict_crop(
                    crop_bgr, feature_extractor, backbone_grad_model, centroids, class_names, class_thresholds
                )
                top3_formatted = [(char, f"{sim * 100:.1f}%") for char, sim in top3]
                
                st.session_state.saved_prediction = {
                    "char": bengali_char, 
                    "class_id": best_class_name,
                    "score": score, 
                    "threshold": threshold, 
                    "top3": top3_formatted
                }
                st.session_state.saved_hand_crop = explanation_map

    countdown_banner.empty()
    st.rerun()

# -------------------------------------------------------------------
# 7. DIAGNOSTICS DISPLAY PANEL
# -------------------------------------------------------------------
with col2:
    with st.container(key="diagnostics_panel"):
        st.markdown('<div class="panel diagnostics-panel"><h3 class="panel-title">AI DIAGNOSTICS & RESULTS</h3>', unsafe_allow_html=True)     
        metrics_slot = st.empty()
        
        col_img1, col_img2 = st.columns(2, gap="small")
        with col_img1:
            full_output_view = st.empty()
        with col_img2:
            crop_output_view = st.empty()

        alternatives_slot = st.empty()
        reset_slot = st.empty()
        
        if st.session_state.get("saved_prediction") is not None:
            res = st.session_state.saved_prediction
            
            if st.session_state.get("saved_full_view") is not None:
                full_output_view.image(st.session_state.saved_full_view, caption="Captured Frame", use_container_width=True)
            if st.session_state.get("saved_hand_crop") is not None:
                crop_output_view.image(st.session_state.saved_hand_crop, caption="Grad-CAM Focus", use_container_width=True)

            with metrics_slot:
                if res.get("low_light"):
                    st.html("""
                    <div class="predicted-sign">
                        <p class="predicted-sign__label">Brightness is too low to capture an image</p>
                        <h2 class="predicted-sign__glyph">—</h2>
                    </div>
                    """)
                elif res.get("no_hand"):
                    st.html("""
                    <div class="predicted-sign">
                        <p class="predicted-sign__label">No hand detected in the picture</p>
                        <h2 class="predicted-sign__glyph">—</h2>
                    </div>
                    """)
                elif res['score'] < res['threshold']:
                    st.html(f"""
                    <div class="predicted-sign">
                        <p class="predicted-sign__label">Sign could not be detected, please try again.</p>
                        <h2 class="predicted-sign__glyph">—</h2>
                    </div>

                    <div class="stat-row">
                        <div class="stat-card">
                            <p class="stat-card__label">Similarity</p>
                            <h4 class="stat-card__value">{res['score']*100:.1f}%</h4>
                        </div>
                        <div class="stat-card">
                            <p class="stat-card__label">Min Threshold</p>
                            <h4 class="stat-card__value">{res['threshold']*100:.1f}%</h4>
                        </div>
                    </div>
                    """)
                else:
                    st.html(f"""
                    <div class="predicted-sign">
                        <p class="predicted-sign__label">Predicted Sign</p>
                        <h2 class="predicted-sign__glyph">{res['char']}</h2>
                    </div>

                    <div class="stat-row">
                        <div class="stat-card">
                            <p class="stat-card__label">Similarity</p>
                            <h4 class="stat-card__value">{res['score']*100:.1f}%</h4>
                        </div>
                        <div class="stat-card">
                            <p class="stat-card__label">Min Threshold</p>
                            <h4 class="stat-card__value">{res['threshold']*100:.1f}%</h4>
                        </div>
                    </div>
                    """)

            with alternatives_slot:
                if res.get("low_light"):
                    st.html("""
                    <p class="alternatives-title">RECOMMENDATIONS</p>
                    <div class="alt-list">
                        <div class="alt-bar" style="justify-content: center; gap: 10px;">
                            <span class="alt-bar__glyph" style="font-size: 1.2rem;">💡</span>
                            <span class="alt-bar__value">Increase key lighting or adjust camera exposure.</span>
                        </div>
                    </div>
                    """)
                elif res.get("no_hand"):
                    st.html("""
                    <p class="alternatives-title">RECOMMENDATIONS</p>
                    <div class="alt-list">
                        <div class="alt-bar" style="justify-content: center; gap: 10px;">
                            <span class="alt-bar__glyph" style="font-size: 1.2rem;">🖐️</span>
                            <span class="alt-bar__value">Center your hand inside the camera frame.</span>
                        </div>
                    </div>
                    """)
                else:
                    alt_html = '<p class="alternatives-title">TOP ALTERNATIVE MATCHES</p><div class="alt-list">'
                    for idx, (alt_char, alt_score) in enumerate(res['top3']):
                        bar_class = "alt-bar alt-bar--top" if idx == 0 and res['score'] >= res['threshold'] else "alt-bar"
                        alt_html += f"""
                        <div class="{bar_class}">
                            <span class="alt-bar__glyph">{alt_char}</span>
                            <span class="alt-bar__value">{alt_score}</span>
                        </div>
                        """
                    alt_html += '</div>'
                    st.html(alt_html)
            
            with reset_slot:
                st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Test Another Sign", use_container_width=True, key="AnotherSignBtn", type="secondary"):
                    st.session_state.saved_full_view = None
                    st.session_state.saved_hand_crop = None
                    st.session_state.saved_prediction = None
                    st.session_state.run_camera = True
                    st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)