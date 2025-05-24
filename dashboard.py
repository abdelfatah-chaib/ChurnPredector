# dashboard.py
import streamlit as st
from PIL import Image
import base64

# ========== CONFIG ==========
st.set_page_config(page_title="Churn Predictor - Dashboard", layout="wide")

# ========== BACKGROUND FUNCTION ==========
def add_bg_from_local(image_path):
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
        .block-container {{ padding-top: 1rem; }}
        </style>
        """,
        unsafe_allow_html=True
    )

# apply background
add_bg_from_local("images/world6.jpg")

# ========== GLOBAL CSS (Navbar + Buttons + Cards) ==========
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playball&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 40px;
        background: rgba(255,255,255,0.85);
        border-radius: 12px;
        margin-bottom: 30px;
        font-family: 'Poppins', sans-serif;
    }
    .nav-left, .nav-right { display: flex; gap: 20px; }
    .nav-button {
        background-color: white;
        color: black;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    .nav-button:hover { background-color: #3EDAD8; color: white; }
    .nav-button.active { background-color: #3EDAD8; color: white; }
    .btn-icon {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        position: relative;
    }
    .badge {
        position: absolute;
        top: -4px;
        right: -4px;
        background: #E63946;
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 12px;
    }
    .card {
        background: rgba(255,255,255,0.9);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ========== NAVBAR ==========
selected = "Dashboard"
st.markdown(
    f"""
    <div class="navbar">
      <div class="nav-left">
        <button class="nav-button">Accueil</button>
        <button class="nav-button">Prédiction</button>
        <button class="nav-button active">Dashboard</button>
        <button class="nav-button">Chatbot</button>
      </div>
      <div class="nav-right">
        <button class="btn-icon">💬</button>
        <button class="btn-icon">🔔<span class="badge">1</span></button>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-weight:600;">RACHID AIT AISSA</span>
          <span>👤</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ========== SIDEBAR ==========
st.sidebar.markdown("<h3 style='font-family:Poppins; color:#333;'>Dashboard</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)
sections = ["Dashboard", "Prédiction", "Note", "Planification", "Paramètres", "My Account", "Déconnexion", "Help"]
choice = st.sidebar.radio("", sections)

# ========== MAIN CONTENT CARDS ==========
# Causes principales du churn
st.markdown("<div class='card'><h4>Causes principales du churn</h4>", unsafe_allow_html=True)
causes = [
    ("Problèmes de paiement","40%"),
    ("Faible utilisation de la plateforme","70%"),
    ("Manque de support client","10%"),
]
for text, pct in causes:
    st.markdown(f"<p style='margin:4px 0;'><strong>{text}</strong> <span style='float:right;color:#E63946;'>{pct}</span></p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Tendance churn par mois
st.markdown("<div class='card' style='padding-bottom:8px;'><h4>Tendance de churn par mois</h4>", unsafe_allow_html=True)
import pandas as pd
import numpy as np
# Dummy data
df = pd.DataFrame({
    'Mois': ['Jan','Fév','Mar','Avr','Mai'],
    'Valeur': [10,25,20,35,30]
})
chart = st.line_chart(df.set_index('Mois'))
st.markdown("</div>", unsafe_allow_html=True)

# KPIs synthétiques
st.markdown("<div class='card'><h4>KPIs synthétiques</h4>", unsafe_allow_html=True)
st.bar_chart(pd.DataFrame({'KPI': ['A','B','C','D'], 'Valeur':[30,5,45,15]}).set_index('KPI'))
st.markdown("</div>", unsafe_allow_html=True)

# Toutes les prédictions
st.markdown("<div class='card'><h4>Toutes les prédictions <button style='float:right;border:none;background:#3EDAD8;color:white;padding:4px 8px;border-radius:4px;'>PDF</button></h4>", unsafe_allow_html=True)
preds = pd.DataFrame({
    'Prédiction': ['waze_dataset.csv','waze_dataset.csv'],
    'Date': ['Janvier 2025','Janvier 2025'],
    'Résultat': ['Done','Done']
})
st.table(preds)
st.markdown("</div>", unsafe_allow_html=True)