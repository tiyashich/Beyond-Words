import streamlit as st

def initialize_session():
    defaults = {
        "saved_full_view": None,
        "saved_hand_crop": None,
        "saved_prediction": None,
        "countdown_start": None,
        "active_countdown": False,
        "run_camera": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value