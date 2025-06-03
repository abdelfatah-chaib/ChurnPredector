import streamlit as st
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.nav_bar import nav_bar, render_home_page, render_notification_page, render_profile_page, refresh_user_data
from database.db import add_prediction, get_user
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

USERS_DB_PATH = 'database/users.db'
HISTORY_DB_PATH = 'database/history.db'

def get_users_conn():
    """Connexion à la base users"""
    return sqlite3.connect(USERS_DB_PATH, check_same_thread=False)

# Déterminer la page actuelle 
pages = st.query_params.get_all("page")
current_page = pages[0] if pages else "home"  

# ========== FONCTION DE PRÉDICTION ==========
def render_prediction_page():
    """Fonction pour rendre la page de prédiction"""
    
    # Initialisation du session state
    if "show_result" not in st.session_state:
        st.session_state["show_result"] = False
    if "df_result" not in st.session_state:
        st.session_state["df_result"] = None
    if "dataset_name" not in st.session_state:
        st.session_state["dataset_name"] = ""
    
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
    
    # Appliquer le background
    add_bg_from_local("images/background_img.jpg")

    # ========== FONCTIONS DE PRÉDICTION ==========

    def predict_churn_proba(df):
        """Fonction simulée de prédiction - remplacez par votre vraie fonction"""
        results = []
        for idx, row in df.iterrows():
            # Générer une probabilité aléatoire pour la démo
            proba = np.random.random()
            prediction = "Client Va Quitter ⚠️" if proba > 0.6 else "Client Retenu ✅"
            
            results.append({
                'ID': row.get('ID', idx),
                'proba': proba,
                'prediction': prediction
            })
        
        return pd.DataFrame(results)

    def save_to_sqlite(df_result, dataset_name):
        """Sauvegarder les résultats de prédiction dans la base de données history"""
        try:
            # Récupérer les informations de l'utilisateur connecté
            user_email = st.session_state.get('user_email')
            if not user_email:
                st.error("Erreur: Utilisateur non identifié")
                return False
            
            # Récupérer les infos complètes de l'utilisateur
            user_info = get_user(user_email)
            if not user_info:
                st.error("Erreur: Impossible de récupérer les informations utilisateur")
                return False
            
            user_id = user_info['id']
            
            # Calculer les statistiques de la prédiction
            total_predictions = len(df_result)
            churned_count = (df_result["prediction"] == "Client Va Quitter ⚠️").sum()
            retained_count = total_predictions - churned_count
            churn_rate = (churned_count / total_predictions * 100) if total_predictions > 0 else 0
            
            # Calculer le score de confiance moyen
            avg_confidence = df_result['proba'].mean() if 'proba' in df_result.columns else 0.0
            
            # Formater le résultat pour la base de données
            prediction_result = f"Total: {total_predictions}, Churn: {churned_count} ({churn_rate:.1f}%), Retained: {retained_count}"
            
            # Enregistrer dans la base de données
            success = add_prediction(
                user_id=user_id,
                user_email=user_email,
                dataset_name=dataset_name,
                prediction_result=prediction_result,
                confidence_score=avg_confidence,
                model_used="churn_prediction_model_v1"
            )
            
            if success:
                st.success(f"✅ Prédiction enregistrée avec succès pour {total_predictions} clients")
                return True
            else:
                st.error("❌ Erreur lors de l'enregistrement en base de données")
                return False
                
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")
            print(f"Erreur sauvegarde: {e}")
            return False

    def generer_messages(df):
        def message(row):
            if "Quitter" in row["prediction"]:
                return "💔 Nous sommes là pour vous aider. Dites-nous ce qui ne vous a pas plu."
            else:
                return "🙏 Merci pour votre fidélité ! Nous sommes heureux de vous compter parmi nos utilisateurs."
        df["message"] = df.apply(message, axis=1)
        return df

    def afficher_resultats(df_result):
        st.markdown("<h3 style='color:#2C6B55; font-weight: bold;'>📊 Résultats de la prédiction</h3>", unsafe_allow_html=True)

        # Créer un DataFrame pour l'affichage avec des colonnes plus lisibles
        df_display = df_result.copy()
        df_display['Probabilité'] = df_display['proba'].apply(lambda x: f"{x*100:.2f}%")
        df_display['Statut'] = df_display['prediction'].apply(lambda x: "❌ Va Quitter" if "Quitter" in x else "✅ Reste Fidèle")
        df_display['Message'] = df_display['message']
        
        # Sélectionner les colonnes à afficher
        columns_to_show = ['ID', 'Probabilité', 'Statut', 'Message']
        df_display = df_display[columns_to_show]
        
        # Affichage avec style
        st.dataframe(
            df_display,
            use_container_width=True,
            height=300
        )

    def afficher_kpis(df_result):
        total = len(df_result)
        churned = (df_result["prediction"] == "Client Va Quitter ⚠️").sum()
        retained = total - churned
        churn_rate = churned / total * 100 if total > 0 else 0

        # Utiliser les colonnes natives de Streamlit pour les KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total Clients",
                value=total,
            )
        
        with col2:
            st.metric(
                label="❌ Clients à Risque",
                value=churned,
                delta=f"{churn_rate:.1f}% du total"
            )
        
        with col3:
            st.metric(
                label="✅ Clients Fidèles",
                value=retained,
                delta=f"{100-churn_rate:.1f}% du total"
            )
        
        with col4:
            st.metric(
                label="📉 Taux de Churn",
                value=f"{churn_rate:.1f}%",
                delta="Risque" if churn_rate > 50 else "Acceptable",
                delta_color="inverse"
            )

    def afficher_distribution_et_variables(df_result):
        col1, col2 = st.columns([1.1, 1])

        with col1:
            st.subheader("📊 Distribution des prédictions")
            pred_counts = df_result["prediction"].value_counts()

            fig = go.Figure(go.Bar(
                y=["Client Va Quitter ⚠️", "Client Retenu ✅"],
                x=[
                    pred_counts.get("Client Va Quitter ⚠️", 0),
                    pred_counts.get("Client Retenu ✅", 0)
                ],
                orientation='h',
                text=[
                    pred_counts.get("Client Va Quitter ⚠️", 0),
                    pred_counts.get("Client Retenu ✅", 0)
                ],
                textposition='inside',
                insidetextanchor='end',
                textfont=dict(size=15, color='white'),
                marker=dict(
                    color=["#FF6B6B", "#4ECDC4"]
                )
            ))

            fig.update_layout(
                title="Distribution des probabilités de churn",
                title_font=dict(size=14, color="#2C6B55"),
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(title="Nombre de clients", showgrid=True, gridcolor='lightgray'),
                yaxis=dict(title="", tickfont=dict(size=12)),
                height=300,
                margin=dict(t=50, l=10, r=10, b=50),
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🔍 Variables importantes")
            
            # Affichage simplifié des variables importantes
            variables_importance = {
                "total_sessions": 40,
                "device": 15,
                "duration_minutes_drives": 20,
                "driven_km_drives": 10,
                "Autres": 15
            }
            
            # Créer un graphique en barres pour les variables
            fig_vars = go.Figure(go.Bar(
                x=list(variables_importance.keys()),
                y=list(variables_importance.values()),
                marker_color=['#2C6B55', '#4CAF50', '#8BC34A', '#CDDC39', '#FFC107'],
                text=[f"{v}%" for v in variables_importance.values()],
                textposition='outside'
            ))
            
            fig_vars.update_layout(
                title="Importance des variables (%)",
                title_font=dict(size=14, color="#2C6B55"),
                xaxis=dict(title="Variables", tickangle=45),
                yaxis=dict(title="Importance (%)", range=[0, 50]),
                height=300,
                margin=dict(t=50, l=50, r=50, b=100),
                showlegend=False
            )
            
            st.plotly_chart(fig_vars, use_container_width=True)

    def afficher_actions(df_filtered):
        """Affichage des actions avec compteur mis à jour"""
        st.markdown("### ✉️ Actions personnalisées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Envoyer les notifications", type="primary", use_container_width=True):
                st.success(f"✅ Notifications envoyées à {len(df_filtered)} clients.")
                
        with col2:
            if st.button("📧 Envoyer les e-mails", type="secondary", use_container_width=True):
                st.success(f"✅ E-mails envoyés à {len(df_filtered)} clients.")

    # ========== CONTENU DE LA PAGE PRÉDICTION ==========
    st.title("Prédiction de Churn")

    # Upload du fichier avec clé unique pour éviter l’erreur
    uploaded_file = st.file_uploader(
        "📎 Uploader un fichier CSV",
        type=["csv"],
        key="prediction_csv_uploader"
    )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("📄 Données chargées")
            st.dataframe(df.head(), use_container_width=True)

            # Supprimer la colonne prediction si elle existe déjà
            if "prediction" in df.columns:
                df = df.drop(columns=["prediction"])

            # Boutons d'action
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Annuler", use_container_width=True):
                    st.warning("Vous avez annulé la prédiction.")
                    st.session_state["show_result"] = False
                    st.session_state["df_result"] = None
                    st.rerun()  # Forcer le rafraîchissement

            with col2:
                if st.button("Prédire", type="primary", use_container_width=True):
                    try:
                        with st.spinner("Prédiction en cours..."):
                            df_result = predict_churn_proba(df)
                            df_result = generer_messages(df_result)
                            
                            # Stocker les résultats et le nom du dataset
                            st.session_state["df_result"] = df_result
                            st.session_state["dataset_name"] = uploaded_file.name
                            st.session_state["show_result"] = True
                            
                        st.success("✅ Prédiction effectuée avec succès.")
                        st.rerun()  # Forcer le rafraîchissement
                    except Exception as e:
                        st.error(f"Erreur pendant la prédiction : {e}")
                        st.session_state["show_result"] = False

            # Affichage des résultats
            if st.session_state.get("show_result") and st.session_state.get("df_result") is not None:
                st.divider()
                
                df_result = st.session_state["df_result"]
                dataset_name = st.session_state.get("dataset_name", "dataset_inconnu")
                
                # Afficher les résultats
                afficher_resultats(df_result)
                st.divider()
                
                afficher_kpis(df_result)
                st.divider()
                
                afficher_distribution_et_variables(df_result)
                st.divider()

                # Bouton de sauvegarde
                if st.button("💾 Enregistrer les résultats dans la base", type="primary", use_container_width=True):
                    try:
                        success = save_to_sqlite(df_result, dataset_name)
                        if success:
                            st.balloons()  # Animation de succès
                    except Exception as e:
                        st.error(f"Erreur lors de l'enregistrement : {e}")

                # Filtrage des résultats - SECTION CORRIGÉE
                st.subheader("🔍 Filtrer les clients")

                # Options de filtrage avec key unique
                filtre = st.radio(
                    "Sélectionnez le type de clients à afficher :",
                    options=["Tous les clients", "Clients à risque (vont quitter)", "Clients fidèles (restent)"],
                    index=0,
                    key="client_filter_radio"
                )

                # Logique de filtrage corrigée
                if filtre == "Tous les clients":
                    df_filtered = df_result
                elif filtre == "Clients à risque (vont quitter)":
                    df_filtered = df_result[df_result["prediction"] == "Client Va Quitter ⚠️"]
                else:  # "Clients fidèles (restent)"
                    df_filtered = df_result[df_result["prediction"] == "Client Retenu ✅"]

                # Affichage du nombre de clients sélectionnés
                st.info(f"📊 **{len(df_filtered)} clients sélectionnés** sur {len(df_result)} au total")

                # Affichage du tableau filtré
                if len(df_filtered) > 0:
                    st.subheader("👥 Clients sélectionnés")
                    
                    # Préparer les données pour l'affichage
                    df_display_filtered = df_filtered.copy()
                    df_display_filtered['Probabilité'] = df_display_filtered['proba'].apply(lambda x: f"{x*100:.2f}%")
                    df_display_filtered['Statut'] = df_display_filtered['prediction'].apply(lambda x: "❌ Va Quitter" if "Quitter" in x else "✅ Reste Fidèle")
                    
                    # Afficher le tableau
                    st.dataframe(
                        df_display_filtered[['ID', 'Probabilité', 'Statut', 'message']].rename(columns={'message': 'Message'}),
                        use_container_width=True,
                        height=200
                    )
                    
                    # Actions pour les clients filtrés
                    st.divider()
                    afficher_actions(df_filtered)
                else:
                    st.warning("Aucun client ne correspond aux critères de filtrage sélectionnés.")

        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {e}")
            st.exception(e)  # Afficher la stack trace complète pour debug
    else:
        # Message d'aide si aucun fichier n'est uploadé
        st.info("👆 Veuillez uploader un fichier CSV pour commencer la prédiction.")
        
        # Exemple de format attendu
        with st.expander("📋 Format attendu du fichier CSV"):
            st.markdown("""
            Votre fichier doit contenir les colonnes suivantes :
            - `ID` : Identifiant unique du client
            - `total_sessions` : Nombre total de sessions
            - `device` : Type d'appareil utilisé
            - `duration_minutes_drives` : Durée des trajets en minutes
            - `driven_km_drives` : Kilomètres parcourus
            
            *Note : D'autres colonnes peuvent être présentes et seront utilisées pour la prédiction.*
            """)

# ========== ROUTAGE PRINCIPAL ==========
if current_page == "home":
    render_home_page()
elif current_page == "notification":
    render_notification_page()
elif current_page == "profile":
    render_profile_page()
elif current_page == "prediction":
    render_prediction_page()
else:
    # Page par défaut si aucune page spécifiée
    render_home_page()
