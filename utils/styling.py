
import streamlit as st

BACKGROUND = "#0D0D0D"
SURFACE = "#191714"
BEIGE = "#E8DFD1"
RED = "#B22222"
TAUPE = "#8B7D72"
BORDER = "#39332D"


def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0D0D0D;
        color: #E8DFD1;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #E8DFD1 !important;
    }

    p, label, span {
        color: #E8DFD1;
    }

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none;
    }

    [data-testid="stHeader"] {
        background: #0D0D0D;
    }

    [data-testid="stMetric"] {
        background: #191714;
        border: 1px solid #39332D;
        border-radius: 10px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #A99B8B;
    }

    [data-testid="stMetricValue"] {
        color: #E8DFD1;
        font-family: 'Playfair Display', serif;
    }

    [data-testid="stMetricDelta"] {
        color: #B22222;
    }

    div[data-testid="stPlotlyChart"] {
        background: #191714;
        border: 1px solid #39332D;
        border-radius: 10px;
        padding: 8px;
    }

    div.stButton > button {
        background: #B22222;
        color: #FFFFFF;
        border: 1px solid #B22222;
        border-radius: 6px;
    }

    div.stButton > button:hover {
        background: #8F1919;
        border-color: #8F1919;
        color: #FFFFFF;
    }

    .eyebrow {
        color: #B22222;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 3px;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        color: #E8DFD1;
        font-size: 38px;
        line-height: 1.2;
        font-weight: 600;
    }

    .hero-subtitle {
        color: #A99B8B;
        font-size: 14px;
        line-height: 1.7;
    }

    .section-heading {
        font-family: 'Playfair Display', serif;
        font-size: 25px;
        font-weight: 600;
        color: #E8DFD1;
        margin-bottom: 12px;
    }

    .insight-panel {
        background: #191714;
        border: 1px solid #39332D;
        border-left: 4px solid #B22222;
        padding: 24px;
        border-radius: 8px;
        margin-top: 18px;
    }

    .insight-label {
        color: #B22222;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
    }

    .insight-text {
        color: #E8DFD1;
        font-size: 14px;
        margin-top: 8px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #39332D;
        border-radius: 9px;
    }

    [data-testid="stDataFrame"] th {
        font-weight: 700 !important;
    }

    hr {
        border-color: #39332D !important;
    }

    </style>
    """, unsafe_allow_html=True)
