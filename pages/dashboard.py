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
from datetime import datetime, timedelta
import sqlite3

# Import des fonctions de la base de données history
from database.db import (
    get_user_predictions, get_prediction_stats, get_monthly_predictions,
    get_all_predictions, add_prediction
)

# Configuration de la page
st.set_page_config(
    page_title="Churn Predictor - Accueil",
    page_icon="images/wazeLogo.png",
    layout="wide"
)

# Initialiser la session si nécessaire
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Utilisateur"
if 'user_email' not in st.session_state:
    st.session_state.user_email = "demo@example.com"

# Vérifier si l'utilisateur est connecté
if not st.session_state.get('logged_in', False):
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()

nav_bar()

# Vérifier quelle page afficher
pages = st.query_params.get_all("page")
current_page = pages[0] if pages else "home"

# Si on est sur la page home, afficher le contenu home et arrêter
if current_page == "home":
    render_home_page()
    st.stop()
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
            .block-container {{ margin-top: -40px; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

# Fonctions pour récupérer les données réelles
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def get_dashboard_data(user_email):
    """Récupérer toutes les données nécessaires pour le dashboard"""
    try:
        # Statistiques utilisateur
        user_stats = get_prediction_stats(user_email)
        
        # Prédictions mensuelles
        monthly_data = get_monthly_predictions(user_email)
        
        # Dernières prédictions
        recent_predictions = get_user_predictions(user_email)[:10]  # 10 dernières
        
        # Statistiques globales (pour comparaison)
        global_stats = get_prediction_stats()
        
        return {
            'user_stats': user_stats,
            'monthly_data': monthly_data,
            'recent_predictions': recent_predictions,
            'global_stats': global_stats
        }
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return None

# apply background
add_bg_from_local("images/background_img.jpg")

# Récupérer les données
current_user_email = st.session_state.user_email
dashboard_data = get_dashboard_data(current_user_email)

if dashboard_data is None:
    st.error("Impossible de charger les données du dashboard")
    st.stop()

# Main title
st.title("Tableau de bord de la fidélisation client")

# Métriques principales basées sur les données réelles
user_stats = dashboard_data['user_stats']
global_stats = dashboard_data['global_stats']

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pred = user_stats['total_predictions']
    global_total = global_stats['total_predictions']
    change = f"+{total_pred - max(0, total_pred-5)}" if total_pred > 5 else f"+{total_pred}"
    st.metric("Mes Prédictions", f"{total_pred:,}", change)

with col2:
    if total_pred > 0:
        churn_rate = (user_stats['churned_count'] / total_pred) * 100
        st.metric("Mon Taux de Churn", f"{churn_rate:.1f}%", f"{user_stats['churned_count']} churned")
    else:
        st.metric("Mon Taux de Churn", "0%", "Aucune prédiction")

with col3:
    confidence = user_stats['avg_confidence'] or 0
    st.metric("Précision Moyenne", f"{confidence*100:.1f}%", f"{user_stats['unique_datasets']} datasets")

with col4:
    retained_count = user_stats['retained_count']
    st.metric("Clients Retenus", f"{retained_count:,}", f"{retained_count}/{total_pred}")

# Row 1: Analyse des tendances + Historique récent
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Tendance de mes prédictions par mois")
    monthly_data = dashboard_data['monthly_data']
    
    if monthly_data:
        # Préparer les données pour le graphique
        months = [data['month'] for data in monthly_data[:6]]  # 6 derniers mois
        churned_values = [data['churned'] for data in monthly_data[:6]]
        retained_values = [data['retained'] for data in monthly_data[:6]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=churned_values, mode='lines+markers', 
                                name='Churned', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=months, y=retained_values, mode='lines+markers', 
                                name='Retained', line=dict(color='green')))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                         xaxis_title="Mois", yaxis_title="Nombre de prédictions")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée mensuelle disponible")

with col2:
    st.subheader("📊 Répartition des résultats")
    if total_pred > 0:
        # Graphique en camembert
        labels = ['Retained', 'Churned']
        values = [user_stats['retained_count'], user_stats['churned_count']]
        colors = ['#00CC96', '#EF553B']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3,
                                        marker_colors=colors)])
        fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Statistiques textuelles
        st.info(f"🟢 **Clients retenus** - {user_stats['retained_count']} ({(user_stats['retained_count']/total_pred)*100:.1f}%)")
        st.error(f"🔴 **Clients perdus** - {user_stats['churned_count']} ({(user_stats['churned_count']/total_pred)*100:.1f}%)")
    else:
        st.info("Aucune prédiction disponible pour l'analyse")

# Row 2: Historique détaillé des prédictions
st.markdown("---")
st.subheader("📂 Historique de mes prédictions")

recent_predictions = dashboard_data['recent_predictions']

if recent_predictions:
    # Convertir en DataFrame pour l'affichage
    df_predictions = pd.DataFrame(recent_predictions)
    
    # Formater les données pour l'affichage
    df_display = pd.DataFrame({
        'Date': [datetime.fromisoformat(pred['prediction_date']).strftime('%d/%m/%Y %H:%M') 
                for pred in recent_predictions],
        'Dataset': [pred['dataset_name'] for pred in recent_predictions],
        'Résultat': [f"{'🔴 Churned' if pred['prediction_result'] == 'churned' else '🟢 Retained'}" 
                    for pred in recent_predictions],
        'Confiance': [f"{(pred['confidence_score'] or 0)*100:.1f}%" 
                     for pred in recent_predictions],
        'Modèle': [pred['model_used'] for pred in recent_predictions]
    })
    
    st.dataframe(df_display, use_container_width=True)
    
    # Bouton de téléchargement
    csv = df_display.to_csv(index=False)
    st.download_button(
        label="📄 Télécharger l'historique (CSV)",
        data=csv,
        file_name=f"historique_predictions_{current_user_email}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("Aucune prédiction dans votre historique")

# Section de simulation d'une nouvelle prédiction
st.markdown("---")
st.subheader("🎯 Simuler une nouvelle prédiction")

col_sim1, col_sim2, col_sim3 = st.columns(3)

with col_sim1:
    sim_dataset = st.selectbox("Choisir un dataset", 
                              ["waze_dataset.csv", "customer_data.csv", "user_behavior.csv"])

with col_sim2:
    sim_model = st.selectbox("Modèle à utiliser", 
                            ["RandomForest", "XGBoost", "LogisticRegression"])

with col_sim3:
    if st.button(" Lancer la prédiction", use_container_width=True):
        # Simulation d'une prédiction
        import random
        
        result = random.choice(['churned', 'retained'])
        confidence = random.uniform(0.7, 0.95)
        
        # Ajouter à la base de données
        try:
            # Récupérer l'ID utilisateur (simulation)
            user_id = 1  # À adapter selon votre logique d'authentification
            
            add_prediction(user_id, current_user_email, sim_dataset, result, confidence, sim_model)
            
            # Afficher le résultat
            if result == 'churned':
                st.error(f"🔴 Prédiction: Client à risque de churn (Confiance: {confidence*100:.1f}%)")
            else:
                st.success(f"🟢 Prédiction: Client fidèle (Confiance: {confidence*100:.1f}%)")
            
            # Invalider le cache pour actualiser les données
            st.cache_data.clear()
            
            # Bouton pour actualiser la page
            st.rerun()
            
        except Exception as e:
            st.error(f"Erreur lors de l'enregistrement: {e}")

# Comparaison avec les statistiques globales
st.markdown("---")
st.subheader("📊 Comparaison avec la moyenne globale")

col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)

with col_comp1:
    global_total = global_stats['total_predictions']
    st.metric("Total Global", f"{global_total:,}", 
             f"Vous: {user_stats['total_predictions']}")

with col_comp2:
    if global_total > 0:
        global_churn_rate = (global_stats['churned_count'] / global_total) * 100
        user_churn_rate = (user_stats['churned_count'] / max(1, user_stats['total_predictions'])) * 100
        diff = user_churn_rate - global_churn_rate
        st.metric("Taux Churn Global", f"{global_churn_rate:.1f}%", 
                 f"{diff:+.1f}% vs vous")
    else:
        st.metric("Taux Churn Global", "0%", "Aucune donnée")

with col_comp3:
    global_confidence = (global_stats['avg_confidence'] or 0) * 100
    user_confidence = (user_stats['avg_confidence'] or 0) * 100
    diff_conf = user_confidence - global_confidence
    st.metric("Précision Globale", f"{global_confidence:.1f}%", 
             f"{diff_conf:+.1f}% vs vous")

with col_comp4:
    st.metric("Datasets Uniques", f"{global_stats['unique_datasets']}", 
             f"Vous: {user_stats['unique_datasets']}")

# Boutons d'action
st.markdown("---")
col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("🔄 Actualiser les Données", use_container_width=True):
        st.cache_data.clear()
        st.success("Données actualisées avec succès!")
        st.rerun()

with col_action2:
    if st.button("📤 Exporter le Rapport Complet", use_container_width=True):
        # Générer un rapport complet
        report_data = {
            'Statistiques Utilisateur': user_stats,
            'Données Mensuelles': monthly_data,
            'Prédictions Récentes': recent_predictions[:20]
        }
        
        report_json = pd.json_normalize(report_data).to_json()
        st.download_button(
            "📊 Télécharger Rapport JSON",
            report_json,
            file_name=f"rapport_complet_{current_user_email}_{datetime.now().strftime('%Y%m%d')}.json"
        )
        st.info("Rapport généré avec succès!")

with col_action3:
    if user_stats['churned_count'] > 0:
        if st.button("🚨 Analyser les Churns", use_container_width=True):
            st.warning(f"Analyse des {user_stats['churned_count']} cas de churn détectés!")
            
            # Afficher les cas de churn récents
            churn_cases = [pred for pred in recent_predictions if pred['prediction_result'] == 'churned']
            if churn_cases:
                st.subheader("🔍 Cas de Churn Récents")
                churn_df = pd.DataFrame({
                    'Date': [datetime.fromisoformat(case['prediction_date']).strftime('%d/%m/%Y') 
                            for case in churn_cases[:5]],
                    'Dataset': [case['dataset_name'] for case in churn_cases[:5]],
                    'Confiance': [f"{(case['confidence_score'] or 0)*100:.1f}%" 
                                 for case in churn_cases[:5]]
                })
                st.dataframe(churn_df, use_container_width=True)
    else:
        st.info("🎉 Aucun cas de churn détecté récemment!")

# Footer avec dernière mise à jour
st.markdown("---")
last_update = user_stats.get('last_prediction')
if last_update:
    try:
        last_date = datetime.fromisoformat(last_update).strftime('%d/%m/%Y à %H:%M')
        st.caption(f"📅 Dernière prédiction: {last_date}")
    except:
        st.caption("📅 Dernière prédiction: Date non disponible")
else:
    st.caption("📅 Aucune prédiction effectuée")