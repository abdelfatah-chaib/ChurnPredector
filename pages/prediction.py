import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.nav_bar import nav_bar, render_home_page
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Prediction - Churn Predictor",
    page_icon="images/wazeLogo.png",
    layout="wide"
)

# Afficher la barre de navigation
nav_bar()

# Vérifier quelle page afficher
pages = st.query_params.get_all("page")
current_page = pages[0] if pages else "home"

# Si on est sur la page home, afficher le contenu home et arrêter
if current_page == "home":
    render_home_page()
    st.stop()  # Important: arrêter l'exécution ici

# ========== BACKGROUND FUNCTION ==========
def add_bg_from_local(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
            }}
            /* réduction padding top */
            .block-container {{ margin-top: -45px; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Si l'image n'existe pas, continuer sans background
        pass

# apply background
add_bg_from_local("images/background_img.jpg")
