import streamlit as st

# nav_bar.py: Navigation bar with dynamic user and Bootstrap icons

def nav_bar():
    user = st.session_state.get('user_name', 'Utilisateur')
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
    }}
    .nav-left, .nav-right {{ display: flex; gap: 20px; }}
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
    }}
    .nav-button:hover, .nav-button.active {{ background-color: #3EDAD8; color: white; }}
    .btn-icon {{
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        position: relative;
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
    }}
    </style>
    <div class="navbar">
      <div class="nav-left">
        <button class="nav-button" onclick="window.location.href='home.py'">Accueil</button>
        <button class="nav-button" onclick="window.location.href='pages/dashboard.py'">Dashboard</button>
        <button class="nav-button" onclick="window.location.href='pages/prediction.py'">Prédiction</button>
      </div>
      <div class="nav-right">
        <button class="btn-icon" title="Messages"><i class="bi bi-chat-dots"></i></button>
        <button class="btn-icon" title="Notifications"><i class="bi bi-bell"></i><span class="badge">1</span></button>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-weight:600;">{user}</span>
          <i class="bi bi-person-circle"></i>
        </div>
      </div>
    </div>
    ''', unsafe_allow_html=True)
