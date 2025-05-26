import streamlit as st
import sqlite3
import base64
from database.db import get_user,get_users_conn
DB_PATH = 'database/users.db'

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_user_by_email(email):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, first_name, last_name, email FROM users WHERE email = ?', (email,))
        user = cur.fetchone()
        conn.close()
        return user
    except:
        return None

def nav_bar():
    """
    Barre de navigation avec gestion des pages et utilisateur dynamique
    """
    email = st.session_state.get("user_email")
    user = get_user(email)
    st.session_state['user'] = user
    st.session_state['user_name'] = f"{user['first_name']} {user['last_name']}"
    user = st.session_state.get("user_name")
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
                  <span style="font-weight:600;">{user}</span>
                  <i class="bi bi-person-circle" style="font-size: 20px; color: #3DA6DF;"></i>
                </button>
            </form>
          </div>
        </div>
        ''', unsafe_allow_html=True)

def render_notification_page():
    """
    Affiche la page de notifications
    """
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
                🔔 Notifications
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
                        <h3 style="margin: 0; color: #2c3e50; font-size: 18px;">Bienvenue sur notre plateforme !</h3>
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
    """
    Gère la déconnexion de l'utilisateur
    """
    # Nettoyer toutes les données de session
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Rediriger vers home.py
    st.switch_page("home.py")

def render_profile_page():
    """
    Affiche la page de profil utilisateur avec données de la base
    """
    user_email = st.session_state.get('user_email', '')
    user_data = get_user_by_email(user_email) if user_email else None
    
    if user_data:
        user_id, first_name, last_name, email = user_data
        full_name = f"{first_name} {last_name}"
    else:
        # Données par défaut si pas de connexion DB
        user_id = "N/A"
        first_name = st.session_state.get('user_name', 'Utilisateur')
        last_name = "Demo"
        email = st.session_state.get('user_email', 'demo@example.com')
        full_name = f"{first_name} {last_name}"
    
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
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #e8f5e8; border-radius: 8px; font-weight: 600;">127</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Dernière Connexion</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #e3f2fd; border-radius: 8px;">Aujourd'hui</p>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Statut du Compte</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #fff3cd; border-radius: 8px; font-weight: 600;">
                                <span style="color: #28a745;">●</span> Actif
                            </p>
                        </div>
                        <div>
                            <label style="color: #666; font-size: 14px; font-weight: 600; display: block; margin-bottom: 5px;">Type de Compte</label>
                            <p style="color: #333; font-size: 16px; margin: 0; padding: 10px; background: #f3e5f5; border-radius: 8px; font-weight: 600;">Premium</p>
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
    
    # Style CSS pour le bouton de déconnexion
    st.markdown('''
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            border: none;
            color: white;
            font-weight: 600;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #c0392b, #a93226);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
        }
        </style>
    ''', unsafe_allow_html=True)

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
                Bienvenue chèr utilisateur !
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