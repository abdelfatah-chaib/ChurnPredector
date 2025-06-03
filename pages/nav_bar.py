import streamlit as st
import sqlite3
import base64
from datetime import datetime
import pandas as pd
import sqlite3
from datetime import datetime
import streamlit as st

# CORRECTION: Chemins des bases de données
USERS_DB_PATH = 'database/users.db'
HISTORY_DB_PATH = 'database/history.db'

def get_users_conn():
    """Connexion à la base users"""
    return sqlite3.connect(USERS_DB_PATH, check_same_thread=False)

def get_history_conn():
    """Connexion à la base history"""
    return sqlite3.connect(HISTORY_DB_PATH, check_same_thread=False)

def get_user_by_email(email):
    """Récupérer un utilisateur par email depuis users.db"""
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, email FROM users WHERE email = ?", (email,))
        result = cur.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Erreur get_user_by_email: {e}")
        return None

def get_prediction_stats(user_email=None):
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
        print(f"Erreur get_prediction_stats: {e}")
        return {
            'total_predictions': 0,
            'churned_count': 0,
            'retained_count': 0,
            'avg_confidence': 0,
            'unique_datasets': 0,
            'last_prediction': None
        }

def get_monthly_predictions(user_email):
    """Données mensuelles depuis history.db"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        user = get_user_by_email(user_email)
        if not user:
            return []
        
        user_id = user[0]
        
        cur.execute('''
            SELECT 
                strftime('%Y-%m', prediction_date) as month,
                SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                COUNT(*) as total
            FROM predictions 
            WHERE user_id = ?
            GROUP BY strftime('%Y-%m', prediction_date)
            ORDER BY month DESC
            LIMIT 12
        ''', (user_id,))
        
        monthly_data = cur.fetchall()
        conn.close()
        
        result = []
        for data in monthly_data:
            result.append({
                'month': data[0],
                'churned': data[1],
                'retained': data[2],
                'total': data[3]
            })
        
        return result
        
    except Exception as e:
        print(f"Erreur get_monthly_predictions: {e}")
        return []

def add_prediction(user_id, user_email, dataset_name, prediction_result, confidence_score, model_used):
    """Ajoute une nouvelle prédiction à la base de données"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO predictions 
            (user_id, user_email, dataset_name, prediction_result, confidence_score, model_used, prediction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_email, dataset_name, prediction_result, confidence_score, model_used, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur add_prediction: {e}")
        return False

def initialize_user_data_globally():
    """
    Initialise une seule fois les données de l'utilisateur dans st.session_state.
    
    1. Si st.session_state['user_email'] est déjà renseigné (≠ ""), on ne touche rien.
       → On considère que l'utilisateur est déjà connecté (même si en base le user pourrait ne pas exister).
    2. Sinon (st.session_state['user_email'] est vide), on tente de prendre le PREMIER
       utilisateur de la table `users`. Si aucun utilisateur réel n'existe, on passe en mode "demo".
    """

    # 1) Si un email existe déjà en session (qu'importe s'il existe réellement en DB), on le conserve
    if st.session_state.get('user_email'):
        # L'utilisateur (ou son email) est déjà en session : on ne modifie rien d'autre.
        return

    # 2) Si on arrive ici, c'est qu'il n'y a aucun 'user_email' défini.
    #    On tente donc une reconnexion automatique sur le premier utilisateur en base.
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, email FROM users LIMIT 1")
        first_user = cur.fetchone()
        conn.close()

        if first_user:
            # On place ce premier utilisateur en session, une seule fois
            user_id, first_name, last_name, email = first_user
            st.session_state['logged_in']  = True
            st.session_state['user_email'] = email
            st.session_state['user_name']  = f"{first_name} {last_name}"
            st.session_state['user_id']    = user_id
            st.session_state['user_data']  = {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
            return
        else:
            # Pas d'utilisateurs réels en base → on définit le demo user (une seule fois)
            st.session_state['logged_in']  = True
            st.session_state['user_email'] = "demo@example.com"
            st.session_state['user_name']  = "Demo User"
            st.session_state['user_id']    = 0
            st.session_state['user_data']  = {
                'id': 0,
                'first_name': "Demo",
                'last_name': "User",
                'email': "demo@example.com"
            }
            return

    except Exception:
        # En cas d'erreur DB, on bascule également en mode demo
        st.session_state['logged_in']  = True
        st.session_state['user_email'] = "demo@example.com"
        st.session_state['user_name']  = "Demo User"
        st.session_state['user_id']    = 0
        st.session_state['user_data']  = {
            'id': 0,
            'first_name': "Demo",
            'last_name': "User",
            'email': "demo@example.com"
        }
        return


def nav_bar():
    """
    Barre de navigation avec gestion des pages et utilisateur dynamique
    """
    initialize_user_data_globally()

    user_name = st.session_state['user_name']
    user_email  = st.session_state['user_email']
    # Récupération de la page courante
    pages = st.query_params.get_all("page")
    current_page = pages[0] if pages else "home"
    
    # Fonction pour déterminer la classe CSS active
    def get_active_class(page_name):
        return "nav-button active" if current_page == page_name else "nav-button"
        
    # Gestion des clics sur les icônes
    if st.session_state.get('show_notification', False):
        st.success("🎉 Bienvenue sur notre plateforme ! Nous sommes ravis de vous accueillir.")
        st.session_state.show_notification = False
    
    st.markdown(f'''
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playball&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 40px;
            background: rgba(255,255,255,0.85);
            border-radius: 12px;
            margin-bottom: 30px;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .nav-left, .nav-right {{ 
            display: flex; 
            gap: 20px; 
            align-items: center;
        }}
        .nav-button {{
            background-color: white;
            color: black;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(0,0,0,0.1);
        }}
        .nav-button:hover {{ 
            background-color: #3EDAD8; 
            color: white; 
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(62, 218, 216, 0.3);
        }}
        .nav-button.active {{ 
            background-color: #3EDAD8; 
            color: white; 
            box-shadow: 0 4px 15px rgba(62, 218, 216, 0.4);
        }}
        .btn-icon {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            position: relative;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.3s;
        }}
        .btn-icon:hover {{
            background: rgba(62, 218, 216, 0.2);
            transform: translateY(-1px);
        }}
        .badge {{
            position: absolute;
            top: -4px;
            right: -4px;
            background: #E63946;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 12px;
            font-weight: bold;
        }}
        .user-section {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255,255,255,0.7);
            border-radius: 20px;
            border: 1px solid rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s;
            font-family: 'Poppins', sans-serif;
        }}
        .user-section:hover {{
            background: rgba(62, 218, 216, 0.2);
            transform: translateY(-1px);
        }}
        </style>
        <div class="navbar">
          <div class="nav-left">
            <form method="get" style="display: inline;">
                <button name="page" value="home" class="{get_active_class('home')}">
                    <i class="bi bi-house"></i> Accueil
                </button>
            </form>
            <form method="get" style="display: inline;">
                <button name="page" value="dashboard" class="{get_active_class('dashboard')}">
                    <i class="bi bi-graph-up"></i> Tableau de bord
                </button>
            </form>
            <form method="get" style="display: inline;">
                <button name="page" value="prediction" class="{get_active_class('prediction')}">
                    <i class="bi bi-cpu"></i> Prédiction
                </button>
            </form>
          </div>
          <div class="nav-right">
            <form method="get" style="display: inline;">
                <button name="page" value="notification" class="btn-icon" title="Notifications" type="submit">
                    <i class="bi bi-bell"></i>
                    <span class="badge">1</span>
                </button>
            </form>
            <form method="get" style="display: inline;">
                <button name="page" value="profile" class="user-section" title="Profil utilisateur" type="submit" style="border: none; background: transparent;">
                  <span style="font-weight:600;">{user_name}</span>
                  <i class="bi bi-person-circle" style="font-size: 20px; color: #3DA6DF;"></i>
                </button>
            </form>
          </div>
        </div>
        ''', unsafe_allow_html=True)

def render_notification_page():
    """Affiche la page de notifications"""
    user_name = st.session_state.get("user_name", "Utilisateur")
    
    st.markdown(f'''
        <div style="
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
            border-radius: 20px;
            margin: 40px 0;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(5px);
        ">
            <h1 style="
                font-family: 'Poppins', sans-serif;
                font-size: 36px;
                color: #E63946;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            ">
                🔔 Notifications pour {user_name}
            </h1>
            <div style="
                background: rgba(255,255,255,0.9);
                padding: 25px;
                border-radius: 15px;
                margin: 20px auto;
                max-width: 600px;
                text-align: left;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                    <div style="
                        background: #E63946;
                        color: white;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 18px;
                    ">🎉</div>
                    <div>
                        <h3 style="margin: 0; color: #2c3e50; font-size: 18px;">Bienvenue {user_name} !</h3>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">Il y a 2 minutes</p>
                    </div>
                </div>
                <p style="color: #555; line-height: 1.6; margin: 0;">
                    Nous sommes ravis de vous accueillir sur notre plateforme d'analyse prédictive. 
                    Explorez nos fonctionnalités pour optimiser la rétention de vos clients !
                </p>
            </div>
            <div style="
                background: rgba(255,255,255,0.7);
                padding: 20px;
                border-radius: 15px;
                margin: 20px auto;
                max-width: 600px;
                text-align: left;
                border: 2px dashed #ddd;
            ">
                <p style="color: #999; text-align: center; margin: 0; font-style: italic;">
                    Aucune autre notification pour le moment
                </p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def handle_logout():
    """Gère la déconnexion de l'utilisateur"""
    # Nettoyer toutes les données de session
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Rediriger vers home.py
    st.switch_page("home.py")

def render_profile_page():
    """Affiche la page de profil utilisateur avec données de la base"""
    user_email = st.session_state.get('user_email', 'demo@example.com')
    
    # Utiliser les données déjà en session_state si disponibles
    if st.session_state.get('user_data'):
        user_data = st.session_state['user_data']
        user_id = user_data.get('id', 'N/A')
        first_name = user_data.get('first_name', 'Demo')
        last_name = user_data.get('last_name', 'User')
        email = user_data.get('email', user_email)
    else:
        # Sinon récupérer depuis la DB
        user_tuple = get_user_by_email(user_email) if user_email else None
        
        if user_tuple:
            user_id, first_name, last_name, email = user_tuple
        else:
            # Données par défaut si pas de connexion DB
            user_id = "N/A"
            first_name = "Demo"
            last_name = "User"
            email = user_email
    
    full_name = f"{first_name} {last_name}"
    
    # Récupérer les statistiques de l'utilisateur
    user_stats = get_prediction_stats(user_email)
    
    st.markdown(f'''
        <div style="
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(61, 166, 223, 0.1) 0%, rgba(67, 217, 215, 0.1) 100%);
            border-radius: 20px;
            margin: 40px 0;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(5px);
        ">
            <div style="text-align: center; margin-bottom: 40px;">
                <div style="
                    width: 120px;
                    height: 120px;
                    background: linear-gradient(135deg, #3DA6DF, #43D9D7);
                    border-radius: 50%;
                    margin: 0 auto 20px auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 48px;
                    color: white;
                    box-shadow: 0 8px 25px rgba(61, 166, 223, 0.3);
                ">
                    <i class="bi bi-person-circle"></i>
                </div>
                <h1 style="
                    font-family: 'Poppins', sans-serif;
                    font-size: 36px;
                    color: #3DA6DF;
                    margin: 0 0 10px 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                ">
                    {full_name}
                </h1>
                <p style="color: #666; font-size: 18px; margin: 0;">Profil Utilisateur</p>
            </div>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                max-width: 800px;
                margin: 0 auto;
            ">
                <div style="
                    background: rgba(255,255,255,0.9);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                ">
                    <h3 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 20px; display: flex; align-items: center; gap: 10px;">
                        <i class="bi bi-person-badge" style="color: #3DA6DF;"></i>
                        Informations Personnelles
                    </h3>
                    <div style="space-y: 15px;">
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">ID Utilisateur</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">{user_id}</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Prénom</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">{first_name}</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Nom</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">{last_name}</p>
                        </div>
                        <div>
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Email</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">{email}</p>
                        </div>
                    </div>
                </div>
                <div style="
                    background: rgba(255,255,255,0.9);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                ">
                    <h3 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 20px; display: flex; align-items: center; gap: 10px;">
                        <i class="bi bi-graph-up" style="color: #43D9D7;"></i>
                        Statistiques d'Utilisation
                    </h3>
                    <div style="space-y: 15px;">
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Prédictions Effectuées</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #e8f5e8; border-radius: 8px; font-weight: 600;">{user_stats['total_predictions']}</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Clients Retenus</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #e3f2fd; border-radius: 8px; font-weight: 600;">{user_stats['retained_count']}</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Clients Perdus</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #ffebee; border-radius: 8px; font-weight: 600;">{user_stats['churned_count']}</p>
                        </div>
                        <div>
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Précision Moyenne</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f3e5f5; border-radius: 8px; font-weight: 600;">{(user_stats['avg_confidence'] or 0) * 100:.1f}%</p>
                        </div>
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 40px;">
                <p style="color: #666; font-style: italic; font-size: 16px;">
                    Membre depuis janvier 2025
                </p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Bouton de déconnexion
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "🚪 Se déconnecter", 
            key="logout_button",
            help="Retourner à la page de connexion",
            use_container_width=True
        ):
            handle_logout()


def render_home_page():
    """
    Affiche le contenu de la page d'accueil avec message de bienvenue
    """
    user_name = st.session_state.get("user_name", "cher utilisateur")
    add_bg_from_local("images/background_img.jpg")
        
    st.markdown(f'''
        <div style="
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, rgba(61, 166, 223, 0.1) 0%, rgba(67, 217, 215, 0.1) 100%);
            border-radius: 20px;
            margin: 40px 0;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(5px);
        ">
            <h1 style="
                font-family: 'Playball', cursive;
                font-size: 48px;
                color: #3DA6DF;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            ">
                Bienvenue chèr {user_name} !
            </h1>
            <p style="
                font-size: 20px;
                color: #2c3e50;
                line-height: 1.8;
                max-width: 800px;
                margin: 0 auto 30px auto;
                font-family: 'Poppins', sans-serif;
            ">
                Découvrez notre plateforme d'analyse prédictive des désabonnements clients. 
                Grâce à l'intelligence artificielle et au machine learning, anticipez les comportements 
                de vos utilisateurs et optimisez votre stratégie de rétention.
            </p>
            <div style="
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 40px;
                flex-wrap: wrap;
            ">
                <div style="
                    background: rgba(255,255,255,0.8);
                    padding: 25px;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255,255,255,0.3);
                    min-width: 200px;
                    transition: transform 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <i class="bi bi-graph-up" style="font-size: 36px; color: #3DA6DF; margin-bottom: 15px;"></i>
                    <h3 style="color: #2c3e50; margin: 10px 0 8px 0; font-size: 18px; font-weight: 600;">Analytics Avancés</h3>
                    <p style="color: #555; font-size: 14px; margin: 0; line-height: 1.4;">Tableaux de bord interactifs et métriques en temps réel</p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.8);
                    padding: 25px;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255,255,255,0.3);
                    min-width: 200px;
                    transition: transform 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <i class="bi bi-cpu" style="font-size: 36px; color: #43D9D7; margin-bottom: 15px;"></i>
                    <h3 style="color: #2c3e50; margin: 10px 0 8px 0; font-size: 18px; font-weight: 600;">IA Prédictive</h3>
                    <p style="color: #555; font-size: 14px; margin: 0; line-height: 1.4;">Modèles de machine learning pour anticiper le churn</p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.8);
                    padding: 25px;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255,255,255,0.3);
                    min-width: 200px;
                    transition: transform 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <i class="bi bi-shield-check" style="font-size: 36px; color: #2ecc71; margin-bottom: 15px;"></i>
                    <h3 style="color: #2c3e50; margin: 10px 0 8px 0; font-size: 18px; font-weight: 600;">Fiabilité</h3>
                    <p style="color: #555; font-size: 14px; margin: 0; line-height: 1.4;">Précision de 75% et validation croisée rigoureuse</p>
                </div>
            </div>
            <div style="margin-top: 50px;">
                <p style="
                    font-size: 16px;
                    color: #7f8c8d;
                    font-style: italic;
                    font-family: 'Poppins', sans-serif;
                ">
                    Commencez dès maintenant en explorant le tableau de bord ou en testant nos prédictions
                </p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
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
        pass

def refresh_user_data():
    """Force la mise à jour des données utilisateur depuis la DB"""
    email = st.session_state.get('user_email')
    if email and email != "demo@example.com":
        try:
            user_data = get_user_by_email(email)
            if user_data:
                st.session_state.user_name = f"{user_data['first_name']} {user_data['last_name']}"
                st.session_state.user_data = user_data
        except Exception as e:
            print(f"Erreur lors du rafraîchissement: {e}")





