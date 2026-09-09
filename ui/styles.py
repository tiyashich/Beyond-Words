"""
Compact Full-Screen Layout with Centered Camera Viewfinder

Design tokens
-------------
Primary Dark Blue    : #304674  (structure, text, primary surfaces)
Soft Blues           : #98BAD5, #B2CBDE, #C6D3E3, #D8E1E8  (borders, tints, fills)
Base Light Background: #FFFFFF
Signature Accent     : #D98E2E  (marigold) — used sparingly for the single active
                        call-to-action and the top-ranked prediction, a nod to the
                        marigold/kantha palette common in Bengali textile and alpona
                        art. Everything else stays disciplined navy-on-white so the
                        one warm accent reads as a deliberate signal, not decoration.

Type
----
Display / Latin body : Inter        (clean, high-legibility UI face)
Bengali glyphs        : Hind Siliguri (purpose-built for Bengali script legibility
                        at large display sizes — used only for predicted signs)
"""

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@600;700&family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

/* ============================================================
   FOUNDATIONS
   ============================================================ */

* {
    scrollbar-width: thin;
    scrollbar-color: #B2CBDE transparent;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #B2CBDE;
    border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover { background: #98BAD5; }

::selection {
    background: #98BAD5;
    color: #304674;
}

/* Visible keyboard focus everywhere, not just mouse hover */
a:focus-visible,
button:focus-visible,
[tabindex]:focus-visible,
input:focus-visible,
[data-baseweb="select"]:focus-within {
    outline: 2px solid #D98E2E !important;
    outline-offset: 2px !important;
    border-radius: 6px;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}

/* Lock viewport & prevent awkward vertical page scrolling */
html, body, [data-testid="stAppViewContainer"] {
    max-height: 100vh !important;
    overflow-y: auto !important;
}

[data-testid="stAppViewContainer"], .stApp {
    background:
        radial-gradient(circle at 100% 0%, rgba(152, 186, 213, 0.35) 0%, transparent 45%),
        linear-gradient(135deg, #FFFFFF 0%, #D8E1E8 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Inter', -apple-system, sans-serif;
    color: #304674 !important;
}

/* Compact padding for Streamlit root container */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 0rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Hide Streamlit Overhead Navigation Bar */
[data-testid="stHeader"] {
    display: none !important;
}

/* ============================================================
   HEADER
   ============================================================ */

h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #304674 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 0.15rem !important;
    margin-top: -0.5rem !important;
}

.subtitle-text {
    font-size: 1.0rem !important;
    font-weight: 600;
    font-style: italic !important;
    color: #304674;
    opacity: 0.85;
    display: block;
    position: relative;
    padding-bottom: 0.7rem !important;
    margin-bottom: 0.6rem !important;
}

/* Signature stitched-line motif under the header, a quiet nod to kantha
   running-stitch embroidery — the one decorative flourish on the page */
.subtitle-text::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: 0;
    width: 140px;
    height: 3px;
    background-image: repeating-linear-gradient(
        90deg,
        #D98E2E 0px, #D98E2E 6px,
        transparent 6px, transparent 11px
    );
    border-radius: 2px;
}

/* ============================================================
   CONTROL MATRIX PANEL
   ============================================================ */

[data-testid="stVerticalBlock"] > div:has(div.control-matrix-marker) {
    background: #FFFFFF !important;
    border: 1px solid #B2CBDE !important;
    border-radius: 14px !important;
    padding: 8px 14px !important;
    box-shadow: 0 4px 18px -4px rgba(48, 70, 116, 0.12) !important;
    transition: box-shadow 0.2s ease-in-out !important;
}

.section-label {
    font-size: 0.82rem !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #304674;
    margin-bottom: 1px !important;
}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 9px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    padding: 6px 12px !important;
    transition: transform 0.14s ease-out, box-shadow 0.14s ease-out, filter 0.14s ease-out !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D98E2E 0%, #C87D1E 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #C87D1E !important;
    box-shadow: 0 3px 12px -2px rgba(217, 142, 46, 0.5) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px -3px rgba(217, 142, 46, 0.6) !important;
    filter: brightness(1.04);
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0px);
    filter: brightness(0.97);
}

.stButton > button[kind="primary"]:disabled {
    background: #C6D3E3 !important;
    border-color: #B2CBDE !important;
    box-shadow: none !important;
    color: #98BAD5 !important;
}

/* Secondary buttons (e.g. "Capture Hand Gesture") — solid black fill
   with white text for maximum contrast against the light page. */
.stButton > button[kind="secondary"] {
    background: #1A1A1A !important;
    color: #FFFFFF !important;
    border: 1px solid #000000 !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #000000 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px -3px rgba(0, 0, 0, 0.5) !important;
}

.stButton > button[kind="secondary"]:active {
    transform: translateY(0px);
    filter: brightness(0.95);
}

/* Explicit disabled state so it doesn't fall back to Streamlit's
   default washed-out gray-on-gray look */
.stButton > button[kind="secondary"]:disabled {
    background: #D8E1E8 !important;
    border: 1px solid #B2CBDE !important;
    color: #7C93B3 !important;
    box-shadow: none !important;
}

/* Form Dropdowns & Sliders */
div[data-baseweb="select"] * {
    font-size: 0.95rem !important;
}

div[data-baseweb="slider"] div {
    background-color: #304674 !important;
}

div[data-baseweb="slider"] [role="slider"] {
    box-shadow: 0 0 0 4px rgba(217, 142, 46, 0.18) !important;
}

/* ============================================================
   PANEL CONTAINERS
   ============================================================ */

.panel {
    background: #FFFFFF;
    border: 1px solid #B2CBDE;
    border-radius: 16px;
    padding: 14px 18px !important;
    box-shadow: 0 8px 24px -8px rgba(48, 70, 116, 0.14);
    transition: box-shadow 0.2s ease-in-out;
}

.panel-title {
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase;
    color: #304674 !important;
    margin-bottom: 10px !important;
    padding-bottom: 6px !important;
    border-bottom: 2px solid #D8E1E8;
    position: relative;
}

/* Accent tick under the panel title, echoing the header stitch motif in miniature */
.panel-title::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 34px;
    height: 2px;
    background: #D98E2E;
    border-radius: 2px;
}

/* ============================================================
   CAMERA VIEWFINDER
   ============================================================ */

/*
 * Live Camera Feed Centering
 * ---------------------------------------------------------------
 * The countdown banner and camera feed live inside an actual
 * st.container(key="viewfinder_stage") in app.py, which Streamlit
 * gives the class "st-key-viewfinder_stage". Scoping to that real
 * container (rather than a raw HTML div that Streamlit never
 * actually nests content inside) is what makes this reliably
 * center and fill the frame regardless of Streamlit version.
 */
.st-key-viewfinder_stage {
    position: relative !important;
    width: 100% !important;
}

.st-key-viewfinder_stage [data-testid="stImage"],
.st-key-viewfinder_stage [data-testid="stImage"] > div,
.st-key-viewfinder_stage [data-testid="stImage"] > picture {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.st-key-viewfinder_stage [data-testid="stImage"] img,
.st-key-viewfinder_stage [data-testid="stImage"] picture img {
    display: block !important;
    width: 100% !important;
    height: 420px !important;
    object-fit: cover !important;
    object-position: center !important;
    border-radius: 12px;
    margin: 0 auto !important;
    box-shadow: 0 6px 20px -6px rgba(48, 70, 116, 0.35);
}

/* Fallback/Placeholder Viewfinder Frame */
.viewfinder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100% !important;
    height: 420px !important;
    background: linear-gradient(160deg, #304674 0%, #22344F 100%);
    color: #C6D3E3;
    border-radius: 12px;
    font-size: 1.05rem !important;
    font-weight: 700;
    letter-spacing: 0.03em;
    border: 1px solid #98BAD5;
    margin: 0 auto !important;
}

.floating-countdown-overlay {
    position: absolute;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(48, 70, 116, 0.92);
    backdrop-filter: blur(8px);
    color: #FFFFFF;
    border: 1px solid #98BAD5;
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: 800;
    font-size: 1.0rem !important;
    box-shadow: 0 4px 15px rgba(48, 70, 116, 0.25);
    z-index: 99;
    animation: pulse-glow 1.4s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 4px 15px rgba(48, 70, 116, 0.25); }
    50% { box-shadow: 0 4px 22px rgba(217, 142, 46, 0.45); }
}

/* ============================================================
   PREDICTION CARD
   ============================================================ */

.predicted-sign {
    background: linear-gradient(150deg, #304674 0%, #263A60 100%);
    border: 1px solid #98BAD5;
    border-radius: 14px;
    padding: 12px !important;
    text-align: center;
    margin-bottom: 8px !important;
    box-shadow: 0 6px 18px -6px rgba(48, 70, 116, 0.4);
}

.predicted-sign__label {
    font-size: 0.8rem !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #B2CBDE;
    margin: 0 !important;
}

.predicted-sign__glyph {
    font-family: 'Hind Siliguri', sans-serif !important;
    font-size: 2.9rem !important;
    font-weight: 700;
    color: #FFFFFF !important;
    margin: 0 !important;
    line-height: 1.05;
    text-shadow: 0 2px 10px rgba(217, 142, 46, 0.35);
}

/* ============================================================
   SIMILARITY & THRESHOLD STAT CARDS
   ============================================================ */

.stat-row {
    display: flex;
    gap: 8px;
    margin-bottom: 8px !important;
}

.stat-card {
    flex: 1;
    background: #D8E1E8;
    border: 1px solid #B2CBDE;
    border-left: 3px solid #304674;
    border-radius: 9px;
    padding: 6px 10px !important;
    text-align: center;
    transition: transform 0.15s ease-out;
}

.stat-card:hover {
    transform: translateY(-1px);
}

.stat-card__label {
    font-size: 0.75rem !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #304674;
    margin: 0;
    opacity: 0.85;
}

.stat-card__value {
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #304674 !important;
    margin: 0 !important;
}

/* ============================================================
   ALTERNATIVE PREDICTIONS LIST
   ============================================================ */

.alternatives-title {
    font-size: 0.75rem !important;
    font-weight: 800;
    color: #304674;
    margin: 6px 0 4px 0 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.alt-list {
    display: flex;
    flex-direction: column;
    gap: 5px !important;
}

.alt-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border: 1px solid #C6D3E3;
    padding: 5px 12px !important;
    border-radius: 9px;
    transition: transform 0.15s ease-out, border-color 0.15s ease-out;
}

.alt-bar:hover {
    transform: translateX(2px);
    border-color: #98BAD5;
}

.alt-bar--top {
    border-color: #D98E2E;
    background: linear-gradient(90deg, #FBF0DE 0%, #D8E1E8 100%);
}

.alt-bar__glyph {
    font-family: 'Hind Siliguri', sans-serif;
    font-size: 1.15rem !important;
    font-weight: 700;
    color: #304674;
}

.alt-bar__value {
    font-size: 0.9rem !important;
    font-weight: 700;
    color: #304674;
}
</style>
"""