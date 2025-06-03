import streamlit as st
from pages.nav_bar import nav_bar

def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)























def afficher_resultats():
    st.markdown("<h3 style='color:#2C6B55; font-weight: bold;'>Résultats de la prédiction</h3>", unsafe_allow_html=True)

    total_clients = 500
    churn_clients = 120
    churn_rate = (churn_clients / total_clients) * 100

    st.markdown(f"""
    <div style="border: 2px solid #2C6B55; border-radius: 30px; padding: 10px 20px; font-size: 16px; margin-bottom: 20px;">
        Sur <span style="background-color:#D9F0E6; border-radius:15px; padding:0 8px; color:#2C6B55; font-weight:700;">{total_clients}</span> clients,
        <span style="background-color:#F9D6D5; border-radius:15px; padding:0 8px; color:#C03D3A; font-weight:700;">{churn_clients}</span> sont susceptibles de se désabonner.
        Taux de churn estimé : <span style="background-color:#D9F0E6; border-radius:15px; padding:0 8px; color:#2C6B55; font-weight:700;">{churn_rate:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Tableau HTML complet — garde ton code tableau intact !
    html_table = """
    <style>
    .statut-quitte {
      background-color: #ffcccc;
      color: red;
      font-weight: bold;
    }
    .statut-reste {
      background-color: #ccffcc;
      color: green;
      font-weight: bold;
    }
    .info-icon {
      color: #ff9900;
      font-size: 18px;
    }
    .table-container {
      max-height: 260px;
      overflow-y: auto;
      border: 2px solid #2C6B55;
      border-radius: 15px;
      padding: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 650px;
    }
    th, td {
      border: 2px solid #2C6B55;
      padding: 10px;
      text-align: center;
    }
    th {
      background-color: #e6f0eb;
    }
    </style>

    <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>ID client</th>
          <th>Probabilité de churn</th>
          <th>Statut</th>
          <th>Raison principale</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>1</td><td>0.87</td><td class="statut-quitte">❌ Quitte</td><td>Faible engagement <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>2</td><td>0.32</td><td class="statut-reste">✅ Reste</td><td>Utilisation régulière <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>3</td><td>0.76</td><td class="statut-quitte">❌ Quitte</td><td>Problème de paiement <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>4</td><td>0.21</td><td class="statut-reste">✅ Reste</td><td>Satisfait de l’offre actuelle <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>5</td><td>0.50</td><td class="statut-quitte">❌ Quitte</td><td>Prix trop élevé <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>6</td><td>0.15</td><td class="statut-reste">✅ Reste</td><td>Bon support client <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>7</td><td>0.65</td><td class="statut-quitte">❌ Quitte</td><td>Fonctionnalités manquantes <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>8</td><td>0.30</td><td class="statut-reste">✅ Reste</td><td>Satisfaction produit <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>9</td><td>0.80</td><td class="statut-quitte">❌ Quitte</td><td>Difficultés techniques <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>10</td><td>0.10</td><td class="statut-reste">✅ Reste</td><td>Utilisation fréquente <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>11</td><td>0.55</td><td class="statut-quitte">❌ Quitte</td><td>Concurrence agressive <span class="info-icon">ℹ️</span></td></tr>
        <tr><td>12</td><td>0.20</td><td class="statut-reste">✅ Reste</td><td>Bonne expérience utilisateur <span class="info-icon">ℹ️</span></td></tr>
      </tbody>
    </table>
    </div>
    """

    st.markdown(html_table, unsafe_allow_html=True)




def afficher_boutons_action():
    st.markdown("""
    <style>
    .action-container {
        display: flex;
        justify-content: space-evenly;
        border: 2px solid #2C6B55;
        border-radius: 20px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .custom-btn {
        padding: 12px 25px;
        background-color: white;
        color: #000;
        font-weight: bold;
        border-radius: 20px;
        border: 3px solid #2C6B55;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 L'envoi de la notification"):
            st.session_state["show_notification"] = True
            st.session_state["show_email"] = False
    with col2:
        if st.button("✉️ Envoyer les emails personnalisés"):
            st.session_state["show_email"] = True
            st.session_state["show_notification"] = False
  



   

    # Pied de page
    st.markdown("""
    <div style="margin-top: 15px; font-family: 'Brush Script MT', cursive; font-size: 22px; color: #2C6B55; border-top: 1px dotted #2C6B55; padding-top: 10px; max-width: 900px;">
        ChurnPredictor
    </div>
    """, unsafe_allow_html=True)























def afficher_notification():
    st.markdown("<h3 id='notification'>💡 Notifications à envoyer</h3>", unsafe_allow_html=True)
    data = [
        {"id": "001", "message": "Merci pour votre fidélité !"},
        {"id": "002", "message": "N'oubliez pas de renouveler !"},
        {"id": "003", "message": "Offre spéciale en cours !"}
    ]
    for row in data:
        col1, col2, col3 = st.columns([1, 5, 1])
        col1.write(f"**{row['id']}**")
        col2.write(row["message"])
        if col3.button("Envoyer", key=f"notif_{row['id']}"):
            st.success(f"✅ Notification envoyée au client {row['id']}")

def afficher_emails():
    st.markdown("""
    <style>
    h3#email {
        color: #0077cc;
        font-size: 26px;
        margin-bottom: 25px;
    }

    .email-box {
        background-color: #f4faff;
        border-left: 5px solid #0077cc;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 14px;
        color: #333;
        height: 100px;
        overflow-y: auto;
    }

    .email-col-title {
        color: #0077cc;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
    }

    div.email-button-container button {
        background-color: #27ae60 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 18px;
        margin-top: 10px;
        border: none;
    }

    div.email-button-container button:hover {
        background-color: #1e874b !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 id='email'>✉️ Envoyer les emails personnalisés</h3>", unsafe_allow_html=True)

    data = [
        {"id": "001", "raison": "Faible engagement", "email": "Bonjour, baisse d’activité détectée. Essayez notre nouvelle version gratuite 7 jours !"},
        {"id": "002", "raison": "Problème de paiement", "email": "Votre abonnement a expiré. Payez 4 mois, recevez 1 gratuit !"},
        {"id": "003", "raison": "Inactivité prolongée", "email": "Nous vous manquons ! Reconnectez-vous et recevez 20 % de réduction."}
    ]

    for row in data:
        col1, col2, col3, col4 = st.columns([1, 2, 5, 1.5])
        with col1:
            st.markdown(f"<div class='email-col-title'>ID</div><div>{row['id']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='email-col-title'>Raison</div><div>{row['raison']}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='email-col-title'>Email suggéré</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='email-box'>{row['email']}</div>", unsafe_allow_html=True)
        with col4:
            st.markdown("<div class='email-col-title'>Action</div>", unsafe_allow_html=True)
            # conteneur personnalisé uniquement pour ces boutons
            with st.container():
                st.markdown('<div class="email-button-container">', unsafe_allow_html=True)
                if st.button("Envoyer", key=f"send_{row['id']}"):
                    st.success(f"📨 Email envoyé au client {row['id']}")
                st.markdown('</div>', unsafe_allow_html=True)




  


def page_prediction():
    navbar()
    load_css()

    st.markdown("<h2 style='font-family: Brush Script MT, cursive; color:#2C6B55;'>Prédiction</h2>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Uploader un fichier CSV", type=["csv"])

    if "nb_var" not in st.session_state:
        st.session_state.nb_var = 3
    if "show_result" not in st.session_state:
        st.session_state.show_result = False
    if "show_notification" not in st.session_state:
        st.session_state.show_notification = False
    if "show_email" not in st.session_state:
        st.session_state.show_email = False

    nb_var = st.number_input("Nombre de variables (entre 3 et 12)", min_value=3, max_value=12, value=st.session_state.nb_var, step=1)
    if nb_var != st.session_state.nb_var:
        st.session_state.nb_var = nb_var

    vars_values = []
    
    for i in range(1, st.session_state.nb_var + 1):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<div class='variable-label'>valeur {i}</div>", unsafe_allow_html=True)
        with col2:
            val = st.text_input(f"valeur_{i}", key=f"valeur_{i}")
            vars_values.append(val)

    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("❌ Annuler"):
            # Reset des champs
            for i in range(1, st.session_state.nb_var + 1):
                st.session_state[f"valeur_{i}"] = ""
            st.session_state.show_result = False
            st.session_state.show_email = False
            st.session_state.show_notification = False

    with col_right:
        if st.button("🔮 Prédire"):
            st.session_state.show_result = True
            st.session_state.show_email = False
            st.session_state.show_notification = False

    # Affichage conditionné globalement
    if st.session_state.show_result:
        afficher_resultats()
        afficher_boutons_action()

        if st.session_state.show_notification:
            afficher_notification()
        elif st.session_state.show_email:
            afficher_emails()


if __name__ == "__main__":
    page_prediction()
      