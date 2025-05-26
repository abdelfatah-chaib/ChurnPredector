import streamlit as st
from PIL import Image
import base64
from database.db import authenticate, create_user, get_user
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pages.nav_bar import nav_bar, render_home_page, render_notification_page, render_profile_page

# Configuration de la page
st.set_page_config(
    page_title="Churn Predictor - Accueil",
    page_icon="images/wazeLogo.png",
    layout="wide"
)

# Initialiser la session si nécessaire
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Changé de True à False

# Vérifier si l'utilisateur est déjà connecté et rediriger vers le dashboard
if st.session_state.get('logged_in', False):
    st.switch_page("pages/dashboard.py")

# ========== BACKGROUND ==========
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

add_bg_from_local("images/world6.png")

# ========== CSS (NAVBAR + PANEL) ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playball&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 40px;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        margin-bottom: 30px;
    }
    .nav-left, .nav-right { display: flex; gap: 20px; }

    .nav-button {
        background-color: white;
        color: black;
        border: 2px solid #FFFFFF;
        padding: 14px 32px;
        border-radius: 10px;
        font-size: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .nav-button:hover {
        background-color: #3EDAD8;
        color: white;
        transform: scale(1.05);
    }
    .nav-signup {
        background-color: #3EDAD8;
        color: white;
        border: none;
    }
    .nav-signup:hover {
        background-color: #2FC5C3;
        transform: scale(1.05);
    }
    /* Page d'accueil */
    .main-title {
      font-family: 'Playball', cursive;
      font-size: 80px; color: #05c8f7;
      text-align: center; margin-top: 0px;
    }
    .subtitle {
      font-family: 'Poppins', sans-serif; font-weight: 600;
      font-size:20px; color: #404040;
       margin: 0px auto;text-align: center;
      width: 50%; line-height: 1.6;
    }

    /* --------- PANEL LOGIN / SIGNUP --------- */
    .panel {
      width: 450px; height: 630px;
      margin: 50px auto;
      background: rgba(62,218,216,0.3);
      backdrop-filter: blur(5px);
      border-radius: 20px;
      position: relative;
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
      padding: 10px 40px;
      font-family: 'Poppins', sans-serif;
    }
    .panel h1 {
      font-family: 'Playball', cursive;
      font-size: 48px;
      color: #3DA6DF;
      text-align: center;
      margin-bottom: 60px;
    }

    .panel label {
      display: block;
      font-weight: 600;
      margin-bottom: 8px;
      color: #fff;
    }
    .panel input {
      width: 100%; padding: 14px 18px;
      border: none; border-radius: 12px;
      font-size: 16px; margin-bottom: 30px;
    }
    .password-wrapper {
      position: relative;
    }
    .password-wrapper img {
      position: absolute; right: 20px; top: 50%;
      transform: translateY(-50%);
      width: 24px; cursor: pointer;
    }
    .panel .btn-main {
      display: block; width: 100%; padding: 18px;
      background: #3EDAD8; color: white; border: none;
      border-radius: 12px; font-size: 20px;
      font-weight: 600; cursor: pointer;
      transition: background .3s ease;
    }
    .panel .btn-main:hover { background: #2FC5C3; }
    
    /* Styles globaux pour tous les formulaires Streamlit */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        height: 48px !important;
        box-sizing: border-box !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3EDAD8 !important;
        box-shadow: 0 0 0 2px rgba(62,218,216,0.2) !important;
    }
    
    .stTextInput > label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stFormSubmitButton > button {
        width: 100% !important;
        background: #3EDAD8 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        height: 56px !important;
        font-family: 'Poppins', sans-serif !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #2FC5C3 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(62,218,216,0.3) !important;
    }
    
    /* Masquer les éléments Streamlit par défaut */
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    /* Messages d'erreur et de succès */
    .stAlert {
        margin: 15px 0 !important;
        border-radius: 8px !important;
    }

    </style>
    <!-- SCRIPT pour toggler le password -->
    <script>
    function togglePwd(el){
      const pwd = el.closest('.password-wrapper').querySelector('input');
      if(pwd.type==='password'){
        pwd.type='text';
        el.src='https://img.icons8.com/ios-filled/50/ffffff/closed-eye.png';
      } else {
        pwd.type='password';
        el.src='https://img.icons8.com/ios-filled/50/ffffff/visible.png';
      }
    }
    </script>
""", unsafe_allow_html=True)


# ========== NAVBAR ==========
st.markdown("""
<div class="navbar">
    <div class="nav-left">
        <form method="get"><button name="page" value="home"    class="nav-button">ACCUEIL</button></form>
        <form method="get"><button name="page" value="service" class="nav-button">SERVICES</button></form>
        <form method="get"><button name="page" value="contact" class="nav-button">CONTACT</button></form>
    </div>
    <div class="nav-right">
        <form method="get"><button name="page" value="login"  class="nav-button">S'IDENTIFIER</button></form>
        <form method="get"><button name="page" value="signup" class="nav-button nav-signup">S'INSCRIRE</button></form>
    </div>
</div>
""", unsafe_allow_html=True)


# ========== LOGIQUE DE PAGE ==========
pages = st.query_params.get_all("page")
page = pages[0] if pages else "home"

# ========== CONTENU PAR PAGE ==========
if page == "home":
    st.markdown('''
    <div class="main-title">
        <span style="color:#3DA6DF;">Churn</span> <span style="color:#43D9D7;">Predictor</span>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("""
    <div class="subtitle">
    Cette application permet aux entreprises d'analyser leurs données clients pour prédire les désabonnements grâce à l'intelligence artificielle.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 60px;
        margin: 80px 0;
    }
    .stat-card {
        background: rgba(62, 218, 216, 0.3);
        backdrop-filter: blur(5px);
        padding: 30px 50px;
        border-radius: 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 48px;
        color: #3DA6DF;
        font-weight: 700;
        font-family: 'Poppins';
    }
    .stat-label {
        color: white;
        font-size: 18px;
        margin-top: 10px;
    }
    </style>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number" id="userCount">0</div>
            <div class="stat-label">Utilisateurs actifs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="predictionCount">0</div>
            <div class="stat-label">Prédictions réalisées</div>
        </div>
    </div>

    <script>
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.textContent = Math.floor(progress * (end - start) + start).toLocaleString();
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }
    
    // Valeurs réelles à remplacer
    const userCount = 1542;
    const predictionCount = 89245;
    
    // Démarrage de l'animation après un court délai
    setTimeout(() => {
        animateValue(document.getElementById("userCount"), 0, userCount, 2000);
        animateValue(document.getElementById("predictionCount"), 0, predictionCount, 2500);
    }, 500);
    </script>
    """, unsafe_allow_html=True)


elif page == "service":
    # -------- CSS pour les cartes de service --------
 st.markdown("""
    <style>
    .service-card {
        background: rgba(62, 218, 216, 0.25) !important;
        backdrop-filter: blur(4px);
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        transition: transform .3s ease, box-shadow .3s ease;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .service-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(62, 218, 216, 0.3);
    }
    .service-icon {
        font-size: 42px;
        margin-bottom: 12px;
        color: #3DA6DF;
    }
    .service-title {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #111;
    }
    .service-desc {
        font-size: 15px;
        line-height: 1.7;
        color: #333;
    }
    .tech-badge {
        display: inline-block;
        background: rgba(255,255,255,0.3);
        padding: 4px 12px;
        border-radius: 12px;
        margin: 4px 4px 0 0;
        font-size: 11px;
    }
    .service-explain {
        font-size: 14px;
        color: #444;
        margin: 8px 0 24px 0;
        background: rgba(255,255,255,0.15);
        padding: 12px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

 st.markdown(
        '''
        <div class="main-title">
            <span style="color:#3DA6DF;">Nos Solutions Waze</span> <span style="color:#43D9D7;">Churn</span>
        </div>
        ''', 
        unsafe_allow_html=True
    )
 col1, col2 = st.columns(2)
 with col1:
        st.markdown("""
        <div class="service-card">
            <div class="service-icon">🔮</div>
            <div class="service-title">Prédiction du Churn</div>
            <div class="service-desc">
                Utilise XGBoost pour calculer la probabilité de churn.<br>
                Les explications sont fournies par SHAP pour plus de transparence.<br>
                Dashboard dynamique pour explorer les résultats.
                <div style="margin-top:12px;">
                    <span class="tech-badge">Machine Learning</span>
                    <span class="tech-badge">SHAP</span>
                    <span class="tech-badge">Streamlit</span>
                </div>
            </div>
            <div class="service-explain">
                🔮 Calcule la probabilité de churn avec un modèle ML (XGBoost).  
                Les résultats sont expliqués avec SHAP et affichés dans un tableau de bord dynamique.
            </div>
        </div>
        """, unsafe_allow_html=True)

 with col2:
     st.markdown("""
        <div class="service-card">
            <div class="service-icon">📬</div>
            <div class="service-title">Système d’Alertes et Emails Automatisés</div>
            <div class="service-desc">
                Détection automatique des causes de churn (problème technique, inactivité...) 
                et envoi d’emails personnalisés à l’utilisateur pour l'inciter à revenir.
                <div style="margin-top:12px;">
                    <span class="tech-badge">Flask API</span>
                    <span class="tech-badge">Gmail / SendGrid</span>
                    <span class="tech-badge">Trigger Rules</span>
                </div>
            </div>
            <div class="service-explain">
                📬 Détecte les signaux de churn et envoie des emails ciblés pour récupérer les clients.  
                Utilise des APIs comme Flask et des services d’emailing pour alerter rapidement.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------- 2ème rangée : 3 cartes au centre ---------
 col3, col4, col5 = st.columns(3)
 with col3:
     st.markdown("""
        <div class="service-card">
            <div class="service-icon">🤖</div>
            <div class="service-title">Chatbot IA d’Analyse du Churn</div>
            <div class="service-desc">
                Un assistant virtuel intelligent qui répond aux questions sur les raisons du churn, 
                explique les prédictions et propose des recommandations de rétention client.
                <div style="margin-top:12px;">
                    <span class="tech-badge">GPT-4 API</span>
                    <span class="tech-badge">NLP</span>
                    <span class="tech-badge">Interprétabilité</span>
                </div>
            </div>
            <div class="service-explain">
                💬 Ce chatbot intelligent analyse les causes de churn et propose des solutions pour le prévenir.  
                Il utilise GPT-4 et le NLP pour fournir des explications claires et interactives.
            </div>
        </div>
        """, unsafe_allow_html=True)

 with col4:
     st.markdown("""
        <div class="service-card">
            <div class="service-icon">🗺</div>
            <div class="service-title">Carte Interactive des Zones à Risque</div>
            <div class="service-desc">
                Visualise les régions où le churn est le plus élevé grâce à la géolocalisation, 
                pour orienter les campagnes locales ou publicitaires.
                <div style="margin-top:12px;">
                    <span class="tech-badge">Plotly Mapbox</span>
                    <span class="tech-badge">Choropleth</span>
                    <span class="tech-badge">GeoJSON</span>
                </div>
            </div>
            <div class="service-explain">
                🗺 Montre où le churn est plus fréquent pour aider à cibler les efforts publicitaires localement.  
                Utilise Plotly et la géolocalisation pour une carte dynamique.
            </div>
        </div>
        """, unsafe_allow_html=True)

 with col5:
     st.markdown("""
        <div class="service-card">
            <div class="service-icon">🧠</div>
            <div class="service-title">Segmentation Intelligente des Utilisateurs</div>
            <div class="service-desc">
                Regroupe les utilisateurs selon leurs comportements (fréquence de conduite, fidélité, incidents), 
                pour adapter les campagnes marketing.
                <div style="margin-top:12px;">
                    <span class="tech-badge">KMeans</span>
                    <span class="tech-badge">PCA</span>
                    <span class="tech-badge">Dashboards</span>
                </div>
            </div>
            <div class="service-explain">
                🧠 Regroupe les clients en segments (ex: actifs, inactifs, fidèles) pour une stratégie marketing personnalisée.
                Algorithmes comme KMeans et PCA pour des groupes précis.
            </div>
        </div>
        """, unsafe_allow_html=True)

if page == "contact":
   st.markdown("""
    <style>
    .panel {
        width: 450px;
        height: 830px;
        margin: 50px auto;
        background: rgba(62,218,216,0.3);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        padding: 10px 40px;
        font-family: 'Poppins', sans-serif;
       
    }
    .panel h1 {
        font-size: 32px;
        margin-bottom: 30px;
        font-weight: 700;
        color: #3DA6DF;
        text-align: center;
    }
    .panel label {
        display: block;
        margin-bottom: 6px;
        font-size: 14px;
        font-weight: 500;
        color: black;
    }
    .panel input, .panel textarea {
        width: 100%;
        padding: 12px;
        margin-bottom: 20px;
        border: none;
        border-radius: 10px;
        font-size: 14px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    .btn-main {
        background: #3DA6DF;
        color: white;
        padding: 14px;
        border: none;
        width: 100%;
        border-radius: 10px;
        font-size: 16px;
        cursor: pointer;
        transition: 0.3s ease;
    }
    .btn-main:hover {
        background: #3490dc;
    }
    </style>
    """, unsafe_allow_html=True)

   st.markdown("""
    <div class="panel">
      <h1><span style="color:#3DA6DF;">Get</span> <span style="color:#43D9D7;">in Touch</span></h1>
      <label for="first">Nom :</label>
      <input type="text" id="first" placeholder="Nom" required>
      <label for="last">Prénom :</label>
      <input type="text" id="last" placeholder="Prénom" required>
      <label for="email">Email</label>
      <input type="email" id="email" placeholder="Votre email" required>
      <label for="phone">Numéro de téléphone</label>
      <input type="tel" id="phone" placeholder="Votre numéro">
      <label for="msg">Message</label>
      <textarea id="msg" rows="4" placeholder="What do you have in mind?"></textarea>
      <button class="btn-main">Envoyer</button>
    </div>
    """, unsafe_allow_html=True)

# ============ LOGIN ============
elif page == "login":
    # Centrer le formulaire avec du CSS personnalisé
    st.markdown("""
    <style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }
    .login-form {
        width: 350px;
        background: rgba(62,218,216,0.3);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        margin-left: 110px;
        padding-left: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .login-title {
        font-family: 'Playball', cursive;
        font-size: 48px;
        color: #3DA6DF;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* Styles pour les inputs Streamlit */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        height: 50px !important;
    }
    
    .stTextInput > label {
        color: black !important;
        font-weight: 600 !important;
        font-size: 24px !important;
        margin-bottom: 8px !important;
    }
    
    .stFormSubmitButton > button {
        width: 100% !important;
        background: #3EDAD8 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        height: 60px !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #2FC5C3 !important;
        transform: scale(1.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-form">
            <h1 class="login-title"><span style="color:#3DA6DF;">Se</span> <span style="color:#43D9D7;">connecter</span></h1>'
         """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email", placeholder="Entrez votre email")
            password = st.text_input("Mot de passe", type="password", key="login_password", placeholder="Entrez votre mot de passe")
            login_submitted = st.form_submit_button("Connexion")
            
            if login_submitted:
                if email and password:
                    if authenticate(email, password):
                        user = get_user(email)
                        if user:
                            st.success(f"Bienvenue {user['first_name']} {user['last_name']} 🎉")
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = user
                            st.session_state['user_email'] = user['email']
                            st.session_state['user_name'] = f"{user['first_name']} {user['last_name']}"
                            # Forcer le rechargement de la page pour déclencher la redirection
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la récupération des données utilisateur.")
                    else:
                        st.error("❌ Email ou mot de passe incorrect.")
                else:
                    st.error("❌ Veuillez remplir tous les champs.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ SIGNUP ============
elif page == "signup":
    # CSS pour le signup similaire au login
    st.markdown("""
    <style>
    .signup-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }
    .signup-form {
        width: 450px;
        background: rgba(62,218,216,0.3);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        padding: 20px;
        margin-left: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .signup-form {
        width: 450px;
        background: rgba(62,218,216,0.3);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        margin-left: 120px;
        padding: 0px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .signup-title {
        font-family: 'Playball', cursive;
        font-size: 48px;
        color: #3DA6DF;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Styles pour les inputs Streamlit */
    .stTextInput > div > div > input {
        background-color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        height: 50px !important;
    }
    
    .stTextInput > label {
        color: black !important;
        font-weight: 600 !important;
        font-size: 24px !important;
        margin-bottom: 8px !important;
    }
    
    .stFormSubmitButton > button {
        width: 100% !important;
        background: #3EDAD8 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        height: 60px !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #2FC5C3 !important;
        transform: scale(1.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="signup-form">
            <h1 class="signup-title"><span style="color:#3DA6DF;">Créer</span> <span style="color:#43D9D7;">compte</span></h1>
            """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            prenom = st.text_input("Prénom", key="signup_prenom", placeholder="Entrez votre prénom")
            nom = st.text_input("Nom", key="signup_nom", placeholder="Entrez votre nom")
            email = st.text_input("Email", key="signup_email", placeholder="Entrez votre email")
            password = st.text_input("Mot de passe", type="password", key="signup_password", placeholder="Entrez votre mot de passe")
            signup_submitted = st.form_submit_button("Créer le compte")
            
            if signup_submitted:
                if all([prenom, nom, email, password]):
                    if get_user(email):
                        st.error("Un compte existe déjà avec cet email")
                    else:
                        create_user(prenom, nom, email, password)
                        st.success("Compte créé avec succès !")
                        st.info("Vous pouvez maintenant vous connecter.")
                else:
                    st.error("Veuillez remplir tous les champs.")
        
        st.markdown('</div>', unsafe_allow_html=True)