import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.nav_bar import nav_bar, render_home_page
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pages.nav_bar import nav_bar, render_home_page, render_notification_page, render_profile_page

# Configuration de la page
st.set_page_config(
    page_title="Churn Predictor - Accueil",
    page_icon="images/wazeLogo.png",
    layout="wide"
)

# Initialiser la session si nécessaire
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # ou False selon votre logique de connexion
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Utilisateur"
if 'user_email' not in st.session_state:
    st.session_state.user_email = "demo@example.com"

# Vérifier si l'utilisateur est connecté
if not st.session_state.get('logged_in', False):
    st.error("Vous devez être connecté pour accéder à cette page.")
    # Ici vous pourriez rediriger vers une page de login
    st.stop()

nav_bar()
# Vérifier quelle page afficher
pages = st.query_params.get_all("page")
current_page = pages[0] if pages else "home"

# Si on est sur la page home, afficher le contenu home et arrêter
if current_page == "home":
    render_home_page()
    st.stop()  # Important: arrêter l'exécution ici
elif current_page == "notification":
    render_notification_page()
    st.stop()
elif current_page == "profile":
    render_profile_page()
    st.stop()

# Si on n'est pas sur dashboard, ne pas afficher le contenu du dashboard
if current_page != "dashboard":
    st.stop()


# ========== CONTENU DU DASHBOARD SEULEMENT SI current_page == "dashboard" ==========

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
            .block-container {{ margin-top: -40px; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Si l'image n'existe pas, continuer sans background
        pass

# apply background
add_bg_from_local("images/background_img.jpg")

# Main title
st.title("Tableau de bord de la fidélisation client")

# Row 1: Causes principales du churn + Tendance de churn par mois
col1, col2 = st.columns(2)

with col1:
    st.subheader("Causes principales du churn")
    st.info("🔵 *Problèmes de paiement* - 40%")
    st.info("🔵 *Faible utilisation de la plateforme* - 70%")
    st.info("🔵 *Manque de support client* - 10%")
    st.markdown("1 Month Ago, 1 Region, 1 Company")

with col2:
    st.subheader("📈 Tendance de churn par mois")
    mois = ["Janvier", "Février", "Mars", "Avril", "Mai"]
    val1 = [12, 20, 18, 35, 42]
    val2 = [20, 28, 15, 38, 25]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mois, y=val1, mode='lines+markers', name='Modèle 1'))
    fig.add_trace(go.Scatter(x=mois, y=val2, mode='lines+markers', name='Modèle 2'))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# Row 2: KPIs synthétiques + toutes les prédictions
col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 KPIs synthétiques")
    kpi_labels = ["KPI1", "KPI2", "KPI3", "KPI4"]
    values = [35, 5, 45, 20]

    fig_kpi = go.Figure(data=[
        go.Bar(name='KPIs', x=kpi_labels, y=values, marker_color='indigo')
    ])
    fig_kpi.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_kpi, use_container_width=True)

with col4:
    st.subheader("📂 Toutes les prédictions")
    data = {
        "Prédiction": ["waze_dataset.csv", "waze_dataset.csv"],
        "Date": ["janvier 2025", "janvier 2025"],
        "Résultat": ["✅ Done", "✅ Done"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.download_button("📄 Télécharger PDF", "PDF content", file_name="rapport.pdf")

# Métriques principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Utilisateurs Actifs", "12,543", "↗️ +5.2%")

with col2:
    st.metric("Taux de Churn", "8.7%", "↘️ -1.3%")

with col3:
    st.metric("Prédictions Réalisées", "1,234", "↗️ +12%")

with col4:
    st.metric("Précision Modèle", "87.4%", "↗️ +0.8%")

# Graphiques
st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Évolution du Churn")
    
    # Données simulées
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    churn_data = pd.DataFrame({
        'Date': dates,
        'Taux de Churn': np.random.uniform(6, 12, 30),
        'Prédictions': np.random.uniform(50, 150, 30)
    })
    
    st.line_chart(churn_data.set_index('Date')['Taux de Churn'])

with col_right:
    st.subheader("🎯 Segmentation Utilisateurs")
    
    # Données de segmentation
    segments = pd.DataFrame({
        'Segment': ['Actifs', 'À Risque', 'Churners', 'Nouveaux'],
        'Nombre': [6500, 2100, 800, 1500],
        'Pourcentage': [59.1, 19.1, 7.3, 13.6]
    })
    
    st.bar_chart(segments.set_index('Segment')['Nombre'])

# Tableau des utilisateurs à risque
st.markdown("---")
st.subheader("⚠️ Utilisateurs à Risque Élevé")

risk_users = pd.DataFrame({
    'ID Utilisateur': [f'USER_{i:04d}' for i in range(1001, 1021)],
    'Nom': [f'Utilisateur {i}' for i in range(1, 21)],
    'Score de Risque': np.random.uniform(0.7, 0.95, 20),
    'Dernière Activité': pd.date_range('2024-05-01', periods=20, freq='D'),
    'Actions Recommandées': ['Email de rétention', 'Offre spéciale', 'Contact direct'] * 6 + ['Email de rétention', 'Offre spéciale'] # 20 éléments
})

risk_users['Score de Risque'] = risk_users['Score de Risque'].round(3)
st.dataframe(risk_users, use_container_width=True)

# Boutons d'action
st.markdown("---")
col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("🔄 Actualiser les Données", use_container_width=True):
        st.success("Données actualisées avec succès!")

with col_action2:
    if st.button("📤 Exporter le Rapport", use_container_width=True):
        st.info("Rapport exporté vers Downloads/rapport_churn.pdf")

with col_action3:
    if st.button("🚨 Lancer Campagne de Rétention", use_container_width=True):
        st.warning("Campagne de rétention lancée pour 20 utilisateurs à risque!")