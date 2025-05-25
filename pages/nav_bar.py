import streamlit as st
from PIL import Image
import base64
from database.db import authenticate, create_user, get_user
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def nav_bar():
    """
    Barre de navigation avec gestion des pages et utilisateur dynamique
    """
    user = st.session_state.get('user_name', 'Utilisateur')
    user_name = get_user(st.session_state.get('user_id')) if 'user_id' in st.session_state else None
    
    # Récupération de la page courante
    pages = st.query_params.get_all("page")
    current_page = pages[0] if pages else "home"
    
    # Fonction pour déterminer la classe CSS active
    def get_active_class(page_name):
        return "nav-button active" if current_page == page_name else "nav-button"
    
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
            <button class="btn-icon" title="Messages">
                <i class="bi bi-chat-dots"></i>
            </button>
            <button class="btn-icon" title="Notifications">
                <i class="bi bi-bell"></i>
                <span class="badge">1</span>
            </button>
            <div class="user-section" title="Profil utilisateur">
              <span style="font-weight:600;">{user_name}</span>
              <i class="bi bi-person-circle" style="font-size: 20px; color: #3DA6DF;"></i>
            </div>
          </div>
        </div>
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
                Bienvenue {user_name} !
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
                    <p style="color: #555; font-size: 14px; margin: 0; line-height: 1.4;">Précision de 68% et validation croisée rigoureuse</p>
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
            .block-container {{ margin-top: -45px; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Si l'image n'existe pas, continuer sans background
        pass

# apply background
