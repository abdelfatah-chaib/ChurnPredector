import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.nav_bar import nav_bar, render_home_page, render_notification_page, render_profile_page, initialize_user_data_globally, get_user_by_email
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3

# Configuration de la page
st.set_page_config(
    page_title="Churn Predictor",
    page_icon="images/wazeLogo.png",
    layout="wide"
)

# CORRECTION: Chemins des bases de données
USERS_DB_PATH = 'database/users.db'
HISTORY_DB_PATH = 'database/history.db'

def get_users_conn():
    """Connexion à la base users"""
    return sqlite3.connect(USERS_DB_PATH, check_same_thread=False)

def get_history_conn():
    """Connexion à la base history"""
    return sqlite3.connect(HISTORY_DB_PATH, check_same_thread=False)

def get_prediction_stats_fixed(user_email=None):
    """Statistiques des prédictions depuis history.db"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        if user_email:
            cur.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                    SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                    AVG(confidence_score) as avg_conf,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_pred
                FROM prediction_history 
                WHERE user_email = ?
            ''', (user_email,))
        else:
            cur.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                    SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                    AVG(confidence_score) as avg_conf,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_pred
                FROM prediction_history
            ''')
        
        stats = cur.fetchone()
        conn.close()
        
        return {
            'total_predictions': stats[0] or 0,
            'churned_count': stats[1] or 0,
            'retained_count': stats[2] or 0,
            'avg_confidence': stats[3] or 0,
            'unique_datasets': stats[4] or 0,
            'last_prediction': stats[5]
        }
    except Exception as e:
        st.error(f"Erreur get_prediction_stats: {e}")
        return {
            'total_predictions': 0,
            'churned_count': 0,
            'retained_count': 0,
            'avg_confidence': 0,
            'unique_datasets': 0,
            'last_prediction': None
        }

def get_monthly_predictions_fixed(user_email):
    """Données mensuelles depuis history.db"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                strftime('%Y-%m', prediction_date) as month,
                SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                COUNT(*) as total
            FROM prediction_history 
            WHERE user_email = ?
            GROUP BY strftime('%Y-%m', prediction_date)
            ORDER BY month DESC
            LIMIT 6
        ''', (user_email,))
        
        monthly_data_raw = cur.fetchall()
        conn.close()
        
        monthly_data = []
        for data in monthly_data_raw:
            monthly_data.append({
                'month': data[0],
                'churned': data[1],
                'retained': data[2],
                'total': data[3]
            })
        
        return monthly_data
    except Exception as e:
        st.error(f"Erreur get_monthly_predictions: {e}")
        return []

def get_user_predictions_fixed(user_email, limit=10):
    """Prédictions utilisateur depuis history.db"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT prediction_date, dataset_name, prediction_result, 
                   confidence_score, model_used, id
            FROM prediction_history 
            WHERE user_email = ?
            ORDER BY prediction_date DESC
            LIMIT ?
        ''', (user_email, limit))
        
        predictions = cur.fetchall()
        conn.close()
        
        recent_predictions = []
        for pred in predictions:
            recent_predictions.append({
                'prediction_date': pred[0],
                'dataset_name': pred[1],
                'prediction_result': pred[2],
                'confidence_score': pred[3],
                'model_used': pred[4],
                'id': pred[5]
            })
        
        return recent_predictions
    except Exception as e:
        st.error(f"Erreur get_user_predictions: {e}")
        return []

def get_confidence_distribution(user_email):
    """Distribution des scores de confiance par tranches"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                CASE 
                    WHEN confidence_score < 0.5 THEN 'Faible (< 50%)'
                    WHEN confidence_score < 0.7 THEN 'Moyen (50-70%)'
                    WHEN confidence_score < 0.9 THEN 'Élevé (70-90%)'
                    ELSE 'Très élevé (> 90%)'
                END as confidence_range,
                COUNT(*) as count,
                prediction_result
            FROM prediction_history 
            WHERE user_email = ?
            GROUP BY confidence_range, prediction_result
            ORDER BY confidence_score
        ''', (user_email,))
        
        results = cur.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        st.error(f"Erreur get_confidence_distribution: {e}")
        return []

def get_dataset_performance(user_email):
    """Performance par dataset"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                dataset_name,
                COUNT(*) as total,
                SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                AVG(confidence_score) as avg_confidence,
                MIN(prediction_date) as first_pred,
                MAX(prediction_date) as last_pred
            FROM prediction_history 
            WHERE user_email = ?
            GROUP BY dataset_name
            ORDER BY total DESC
        ''', (user_email,))
        
        results = cur.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        st.error(f"Erreur get_dataset_performance: {e}")
        return []

def get_daily_activity(user_email, days=30):
    """Activité quotidienne sur les X derniers jours"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                DATE(prediction_date) as date,
                COUNT(*) as predictions_count,
                AVG(confidence_score) as avg_confidence
            FROM prediction_history 
            WHERE user_email = ? 
            AND prediction_date >= date('now', '-{} days')
            GROUP BY DATE(prediction_date)
            ORDER BY date
        '''.format(days), (user_email,))
        
        results = cur.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        st.error(f"Erreur get_daily_activity: {e}")
        return []

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

def get_dashboard_data(user_email):
    """Récupérer toutes les données nécessaires pour le dashboard"""
    try:
        # Vérifier que l'utilisateur existe
        user_data = get_user_by_email(user_email)
        if not user_data:
            # Créer un utilisateur demo si n'existe pas
            st.warning(f"Utilisateur {user_email} non trouvé, utilisation des données demo")
            
        # Statistiques utilisateur
        user_stats = get_prediction_stats_fixed(user_email)
        
        # Prédictions mensuelles
        monthly_data = get_monthly_predictions_fixed(user_email)
        
        # Dernières prédictions
        recent_predictions = get_user_predictions_fixed(user_email, limit=10)
        
        # Statistiques globales
        global_stats = get_prediction_stats_fixed()
        
        # Nouvelles données
        confidence_dist = get_confidence_distribution(user_email)
        dataset_perf = get_dataset_performance(user_email)
        daily_activity = get_daily_activity(user_email)
        
        return {
            'user_stats': user_stats,
            'monthly_data': monthly_data,
            'recent_predictions': recent_predictions,
            'global_stats': global_stats,
            'confidence_distribution': confidence_dist,
            'dataset_performance': dataset_perf,
            'daily_activity': daily_activity
        }
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return None

# Navigation
nav_bar()

# Vérifier quelle page afficher
pages = st.query_params.get_all("page")
current_page = pages[0] if pages else "home"

if current_page == "home":
    render_home_page()
    st.stop()
elif current_page == "notification":
    render_notification_page()
    st.stop()
elif current_page == "profile":
    render_profile_page()
    st.stop()
elif current_page == "prediction":
    from pages.prediction import render_prediction_page 
    render_prediction_page()
    st.stop()
elif current_page != "dashboard":
    current_page = "dashboard"

# ========== CONTENU DU DASHBOARD ==========

# Apply background
add_bg_from_local("images/background_img.jpg")

# Récupérer l'email utilisateur depuis session_state
if 'user_email' not in st.session_state or 'user_name' not in st.session_state:
    st.error("Aucun utilisateur connecté – veuillez vous reconnecter.")
    st.stop()

current_user_email = st.session_state['user_email']
current_user_name  = st.session_state['user_name']

# Récupérer les données
dashboard_data = get_dashboard_data(current_user_email)

if dashboard_data is None:
    st.error("Impossible de charger les données du dashboard")
    st.stop()

# Main title avec nom utilisateur dynamique
st.title(f"Tableau de bord de Churn - {current_user_name}")

# Métriques principales
user_stats = dashboard_data['user_stats']
global_stats = dashboard_data['global_stats']

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pred = user_stats['total_predictions']
    change = f"+{min(5, total_pred)}" if total_pred > 0 else "0"
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
    
    # Récupérer TOUTES les prédictions de la base de données
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        # Requête pour obtenir le compte total de toutes les prédictions
        cur.execute('''
            SELECT 
                SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as total_retained,
                SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as total_churned,
                COUNT(*) as total_predictions
            FROM prediction_history
        ''')
        
        result = cur.fetchone()
        conn.close()
        
        if result and result[2] > 0:  # Si il y a des prédictions
            total_retained = result[0] or 0
            total_churned = result[1] or 0
            total_all_predictions = result[2]
            
            # Graphique en camembert pour TOUTES les prédictions
            labels = ['Retained', 'Churned']
            values = [total_retained, total_churned]
            colors = ['#00CC96', '#EF553B']
            
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3,
                                            marker_colors=colors)])
            fig_pie.update_layout(
                height=300, 
                margin=dict(l=10, r=10, t=10, b=10),
                title=dict(text=f"Total: {total_all_predictions:,} prédictions", x=0.5, font_size=14)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Statistiques textuelles pour toutes les prédictions
            retained_percentage = (total_retained / total_all_predictions) * 100
            churned_percentage = (total_churned / total_all_predictions) * 100
            
            st.success(f"🟢 **Clients retenus (Global)** - {total_retained:,} ({retained_percentage:.1f}%)")
            st.error(f"🔴 **Clients perdus (Global)** - {total_churned:,} ({churned_percentage:.1f}%)")
            
            # Afficher aussi les stats de l'utilisateur courant en comparaison
            if user_stats['total_predictions'] > 0:
                st.info(f"📊 **Vos prédictions**: {user_stats['retained_count']} retenus, {user_stats['churned_count']} perdus sur {user_stats['total_predictions']} total")
            else:
                st.info("📊 **Vos prédictions**: Aucune prédiction personnelle")
                
        else:
            st.info("Aucune prédiction disponible dans la base de données")
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données globales: {e}")
        # Fallback vers les données utilisateur si erreur
        if user_stats['total_predictions'] > 0:
            labels = ['Retained', 'Churned']
            values = [user_stats['retained_count'], user_stats['churned_count']]
            colors = ['#00CC96', '#EF553B']
            
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3,
                                            marker_colors=colors)])
            fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                                title=dict(text="Vos prédictions uniquement", x=0.5, font_size=14))
            st.plotly_chart(fig_pie, use_container_width=True)
            
            total_user_pred = user_stats['total_predictions']
            st.success(f"🟢 **Clients retenus** - {user_stats['retained_count']} ({(user_stats['retained_count']/total_user_pred)*100:.1f}%)")
            st.error(f"🔴 **Clients perdus** - {user_stats['churned_count']} ({(user_stats['churned_count']/total_user_pred)*100:.1f}%)")
        else:
            st.info("Aucune prédiction disponible pour l'analyse")

# Row 2: Nouvelles analyses - Distribution de confiance + Performance par dataset
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Distribution des scores de confiance")
    confidence_dist = dashboard_data['confidence_distribution']
    
    if confidence_dist:
        # Préparer les données pour le graphique
        df_conf = pd.DataFrame(confidence_dist, columns=['Range', 'Count', 'Result'])
        
        # Créer un graphique en barres groupées
        fig_conf = px.bar(df_conf, x='Range', y='Count', color='Result',
                         color_discrete_map={'churned': '#EF553B', 'retained': '#00CC96'},
                         title="Répartition par niveau de confiance")
        fig_conf.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_conf, use_container_width=True)
    else:
        st.info("Aucune donnée de confiance disponible")

with col2:
    st.subheader("📋 Performance par Dataset")
    dataset_perf = dashboard_data['dataset_performance']
    
    if dataset_perf:
        # Créer un tableau de performance
        perf_data = []
        for perf in dataset_perf:
            churn_rate = (perf[2] / perf[1]) * 100 if perf[1] > 0 else 0
            perf_data.append({
                'Dataset': perf[0],
                'Total': perf[1],
                'Taux Churn': f"{churn_rate:.1f}%",
                'Confiance Moy.': f"{(perf[4] or 0)*100:.1f}%"
            })
        
        df_perf = pd.DataFrame(perf_data)
        st.dataframe(df_perf, use_container_width=True)
        
        # Graphique en barres pour les totaux
        datasets = [perf[0] for perf in dataset_perf]
        totals = [perf[1] for perf in dataset_perf]
        
        fig_datasets = go.Figure([go.Bar(x=datasets, y=totals, 
                                        marker_color='lightblue')])
        fig_datasets.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10),
                                  yaxis_title="Nombre de prédictions")
        st.plotly_chart(fig_datasets, use_container_width=True)
    else:
        st.info("Aucune donnée de performance disponible")

# Row 3: Activité quotidienne
st.markdown("---")
st.subheader("📅 Activité quotidienne (30 derniers jours)")

daily_activity = dashboard_data['daily_activity']

if daily_activity:
    # Créer le graphique d'activité
    dates = [datetime.strptime(activity[0], '%Y-%m-%d').date() for activity in daily_activity]
    counts = [activity[1] for activity in daily_activity]
    confidences = [(activity[2] or 0) * 100 for activity in daily_activity]
    
    fig_activity = go.Figure()
    fig_activity.add_trace(go.Scatter(x=dates, y=counts, mode='lines+markers',
                                     name='Nombre de prédictions', 
                                     line=dict(color='blue')))
    
    # Ajouter une ligne de tendance
    if len(dates) > 1:
        z = np.polyfit(range(len(counts)), counts, 1)
        p = np.poly1d(z)
        fig_activity.add_trace(go.Scatter(x=dates, y=p(range(len(counts))),
                                         mode='lines', name='Tendance',
                                         line=dict(color='red', dash='dash')))
    
    fig_activity.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10),
                              xaxis_title="Date", yaxis_title="Nombre de prédictions")
    st.plotly_chart(fig_activity, use_container_width=True)
    
    # Statistiques d'activité
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        total_days_active = len(daily_activity)
        st.metric("Jours actifs", total_days_active, "sur 30 jours")
    
    with col_act2:
        avg_daily_preds = sum(counts) / len(counts) if counts else 0
        st.metric("Moyenne/jour", f"{avg_daily_preds:.1f}", "prédictions")
    
    with col_act3:
        max_daily_preds = max(counts) if counts else 0
        st.metric("Maximum/jour", max_daily_preds, "prédictions")
else:
    st.info("Aucune activité récente détectée")

# Row 4: Historique détaillé des prédictions
st.markdown("---")
st.subheader(f"📂 Historique des prédictions de {current_user_name}")

recent_predictions = dashboard_data['recent_predictions']

if recent_predictions:
    # Convertir en DataFrame pour l'affichage
    df_display = pd.DataFrame({
        'Date': [datetime.fromisoformat(pred['prediction_date']).strftime('%d/%m/%Y %H:%M') 
                for pred in recent_predictions],
        'Dataset': [pred['dataset_name'] for pred in recent_predictions],
        'Résultat': [f"{'🔴 Churned' if pred['prediction_result'] == 'churned' else '🟢 Retained'}" 
                    for pred in recent_predictions],
        'Confiance': [f"{(pred['confidence_score'] or 0)*100:.1f}%" 
                     for pred in recent_predictions],
        'Modèle': ['Régression Logistique' for _ in recent_predictions]  # Modèle fixe
    })
    
    st.dataframe(df_display, use_container_width=True)
    
    # Style CSS pour le bouton de téléchargement
    st.markdown("""
        <style>
        .download-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .stDownloadButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            box-shadow: 0 8px 15px rgba(102, 126, 234, 0.3) !important;
            transition: all 0.3s ease !important;
            text-transform: none !important;
            letter-spacing: 0.5px !important;
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 20px rgba(102, 126, 234, 0.4) !important;
        }
        .stDownloadButton > button:active {
            transform: translateY(0px) !important;
            box-shadow: 0 5px 10px rgba(102, 126, 234, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Bouton de téléchargement stylé
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📄 Télécharger l'historique complet",
            data=csv,
            file_name=f"historique_predictions_{current_user_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_history_styled"
        )
else:
    st.info(f"Aucune prédiction dans l'historique de {current_user_name}")

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

# Section informative sur le modèle utilisé
st.markdown("---")
st.info("**Modèle utilisé**: Régression Logistique - Modèle de classification binaire optimisé pour la prédiction de churn avec une performance équilibrée entre précision et rappel.")

# Style CSS pour les boutons d'action
st.markdown("""
    <style>
    /* Bouton Actualiser - Bleu */
    .stButton:has(button[key="refresh_btn"]) > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 6px 12px rgba(79, 172, 254, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 50px !important;
    }
    .stButton:has(button[key="refresh_btn"]) > button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 16px rgba(79, 172, 254, 0.4) !important;
    }
    
    /* Bouton Exporter - Vert */
    .stButton:has(button[key="export_btn"]) > button {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 6px 12px rgba(67, 233, 123, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 50px !important;
    }
    .stButton:has(button[key="export_btn"]) > button:hover {
        background: linear-gradient(135deg, #38f9d7 0%, #43e97b 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 16px rgba(67, 233, 123, 0.4) !important;
    }
    
    /* Bouton Analyser Churns - Rouge/Orange */
    .stButton:has(button[key="analyze_btn"]) > button {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 6px 12px rgba(250, 112, 154, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        height: 50px !important;
    }
    .stButton:has(button[key="analyze_btn"]) > button:hover {
        background: linear-gradient(135deg, #fee140 0%, #fa709a 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 16px rgba(250, 112, 154, 0.4) !important;
    }
    
    /* Style pour le bouton de téléchargement JSON */
    .stDownloadButton:has(button[key="download_json"]) > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 8px 20px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        margin-top: 10px !important;
    }
    .stDownloadButton:has(button[key="download_json"]) > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Animation pour tous les boutons */
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Boutons d'action
st.markdown("---")
col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("🔄 Actualiser les Données", use_container_width=True, key="refresh_btn"):
        st.cache_data.clear()
        st.success("Données actualisées avec succès!")
        st.rerun()

with col_action2:
    if st.button("📤 Exporter le Rapport Complet", use_container_width=True, key="export_btn"):
        # Générer un rapport complet
        report_data = {
            'utilisateur': {
                'nom': current_user_name,
                'email': current_user_email,
                'date_rapport': datetime.now().isoformat()
            },
            'statistiques_utilisateur': user_stats,
            'donnees_mensuelles': monthly_data,
            'predictions_recentes': recent_predictions[:20]
        }
        
        import json
        report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            "📊 Télécharger Rapport JSON",
            report_json,
            file_name=f"rapport_complet_{current_user_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key="download_json"
        )
        st.info("Rapport généré avec succès!")

with col_action3:
    if user_stats['churned_count'] > 0:
        if st.button("🚨 Analyser les Churns", use_container_width=True, key="analyze_btn"):
            st.warning(f"Analyse des {user_stats['churned_count']} cas de churn détectés pour {current_user_name}!")
            
            # Afficher les cas de churn récents
            churn_cases = [pred for pred in recent_predictions if pred['prediction_result'] == 'churned']
            if churn_cases:
                st.subheader("🔍 Cas de Churn Récents")
                churn_df = pd.DataFrame({
                    'Date': [datetime.fromisoformat(case['prediction_date']).strftime('%d/%m/%Y') 
                            for case in churn_cases[:5]],
                    'Dataset': [case['dataset_name'] for case in churn_cases[:5]],
                    'Confiance': [f"{(case['confidence_score'] or 0)*100:.1f}%" 
                                 for case in churn_cases[:5]],
                    'Modèle': [case['model_used'] for case in churn_cases[:5]]
                })
                st.dataframe(churn_df, use_container_width=True)
                
                # Recommandations personnalisées
                st.subheader("💡 Recommandations")
                st.info(f"**{current_user_name}**, voici des actions recommandées pour réduire le churn:")
                st.write("• Analyser les patterns communs dans vos cas de churn")
                st.write("• Améliorer l'engagement client sur les segments à risque")
                st.write("• Mettre en place des campagnes de rétention ciblées")
            else:
                st.info("Aucun cas de churn récent à analyser")
    else:
        st.info(f"🎉 Félicitations {current_user_name}! Aucun cas de churn détecté récemment!")
# Footer avec dernière mise à jour et informations utilisateur
st.markdown("---")
col_footer1, col_footer2 = st.columns(2)

with col_footer1:
    last_update = user_stats.get('last_prediction')
    if last_update:
        try:
            last_date = datetime.fromisoformat(last_update).strftime('%d/%m/%Y à %H:%M')
            st.caption(f"📅 Dernière prédiction de {current_user_name}: {last_date}")
        except:
            st.caption(f"📅 Dernière prédiction de {current_user_name}: Date non disponible")
    else:
        st.caption(f"📅 {current_user_name}: Aucune prédiction effectuée")

with col_footer2:
    st.caption(f"👤 Connecté en tant que: {current_user_name} ({current_user_email})")

