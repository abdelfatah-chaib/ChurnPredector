import streamlit as st
from PIL import Image
import base64

# ========== CONFIG ==========
st.set_page_config(page_title="Churn Predictor", layout="wide")

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

add_bg_from_local("images\world.jpg")

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
    /* Page d’accueil */
    .main-title {
      font-family: 'Playball', cursive;
      font-size: 80px; color: #05c8f7;
      text-align: center; margin-top: 10px;
    }
    .subtitle {
      font-family: 'Poppins', sans-serif; font-weight: 600;
      font-size:20px; color: #333;
       margin: 0px auto;text-align: center;
      width: 50%; line-height: 1.6;
    }

    /* --------- PANEL LOGIN / SIGNUP --------- */
    .panel {
      width: 450px; height: 550px;
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
        <form method="get"><button name="page" value="home"    class="nav-button">Accueil</button></form>
        <form method="get"><button name="page" value="service" class="nav-button">Service</button></form>
        <form method="get"><button name="page" value="pricing" class="nav-button">Pricing</button></form>
        <form method="get"><button name="page" value="contact" class="nav-button">Contact</button></form>
    </div>
    <div class="nav-right">
        <form method="get"><button name="page" value="login"  class="nav-button">Log in</button></form>
        <form method="get"><button name="page" value="signup" class="nav-button nav-signup">Sign up</button></form>
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
    Cette application permet aux entreprises d’analyser leurs données clients pour prédire les désabonnements grâce à l’intelligence artificielle.
    </div>
    """, unsafe_allow_html=True)

elif page == "service":
    st.subheader("🛠 Nos Services")
    st.write("Analyse prédictive, segmentation client, tableaux de bord dynamiques...")

elif page == "pricing":
    st.subheader("💸 Tarification")
    st.write("Choisissez le plan qui correspond à vos besoins.")

elif page == "contact":
    st.subheader("📞 Contactez-nous")
    st.write("Remplissez notre formulaire ou envoyez-nous un mail.")

elif page == "login":
    # -------- LOGIN PANEL --------
    st.markdown("""
    <div class="panel">
      <h1><span style="color:#3DA6DF;">Churn</span> <span style="color:#43D9D7;">Predictor</span></h1>
      <label for="email">Email</label>
      <input type="email" id="email" placeholder="username@email.com">

      <label for="pwd">Password</label>
      <div class="password-wrapper">
        <input type="password" id="pwd" placeholder="Enter Your Password">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/visible.png"
             onclick="togglePwd(this)" alt="toggle">
      </div>

      <button class="btn-main">Sign In</button>
    </div>
    """, unsafe_allow_html=True)

elif page == "signup":
    # -------- SIGNUP PANEL --------
    st.markdown("""
    <div class="panel">
      <h1>Churn Predictor</h1>
      <label for="user">Username</label>
      <input type="text" id="user" placeholder="Your username">

      <label for="email2">Email</label>
      <input type="email" id="email2" placeholder="username@email.com">

      <label for="pwd2">Password</label>
      <div class="password-wrapper">
        <input type="password" id="pwd2" placeholder="Create a Password">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/visible.png"
             onclick="togglePwd(this)" alt="toggle">
      </div>

      <button class="btn-main">Sign Up</button>
    </div>
    """, unsafe_allow_html=True)