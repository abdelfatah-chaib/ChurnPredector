import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder

# 🔧 Fonction de Feature Engineering
def add_features(df):
    df = df.copy()
    eps = 1e-6  # Pour éviter les divisions par zéro

    df['engagement_index']       = df['total_sessions'] / (df['n_days_after_onboarding'] + eps)
    df['avg_km_per_drive']       = df['driven_km_drives'] / (df['drives'] + eps)
    df['avg_minutes_per_drive']  = df['duration_minutes_drives'] / (df['drives'] + eps)
    df['total_fav_navigations']  = df['total_navigations_fav1'] + df['total_navigations_fav2']
    df['fav_nav_ratio']          = df['total_fav_navigations'] / (df['drives'] + eps)
    df['driving_frequency']      = df['drives'] / (df['n_days_after_onboarding'] + eps)
    df['session_to_drive_ratio'] = df['sessions'] / (df['drives'] + eps)
    df['avg_speed_kmph']         = df['driven_km_drives'] / ((df['duration_minutes_drives'] + eps) / 60)
    return df

# 📦 Fonction pour charger le modèle depuis le fichier pickle
def load_model():
    return joblib.load("model/churn_model.pkl")

# 🔮 Prédiction simple : retourne 0 ou 1
def predict_churn(df):
    model = load_model()

    # Nettoyage
    cols_to_drop = ["ID", "label", "prediction", "proba"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # Encodage de la colonne "device"
    if "device" in df.columns:
        le = LabelEncoder()
        df["device"] = le.fit_transform(df["device"])  # Android=0, iPhone=1 par défaut

    # Ajout des features
    df_processed = add_features(df)

    # Prédiction
    df["prediction"] = model.predict(df_processed)
    return df

# 🔮 Prédiction avancée avec probabilités + interprétation
def predict_churn_proba(df):
    model = load_model()

    # Nettoyage
    cols_to_drop = ["ID", "label", "prediction", "proba"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # Encodage
    if "device" in df.columns:
        le = LabelEncoder()
        df["device"] = le.fit_transform(df["device"])

    # Features
    df_processed = add_features(df)

    # Probabilités
    probas = model.predict_proba(df_processed)[:, 1]  # Proba que le client churn

    df["proba"] = probas
    df["prediction"] = df["proba"].apply(lambda p: "Client Va Quitter ⚠️" if p > 0.5 else "Client Retenu ✅")

    return df
