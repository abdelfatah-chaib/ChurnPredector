# Churn Predictor – Projet de Prédiction de l'Abandon des Utilisateurs

Ce projet vise à prédire si un utilisateur de l'application **Waze** va **churner (quitter)** ou **rester actif**, à partir de données comportementales et historiques. L’objectif est d’aider les entreprises à anticiper les désengagements et à mettre en œuvre des actions de fidélisation.

---

## Fonctionnalités du Projet

-  **Analyse Exploratoire des Données (EDA)**  
-  **Prétraitement avancé des données :**  
  Winsorisation, QuantileTransformer, création de nouvelles variables, etc.
-  **Test de 10 modèles de classification supervisée**
-  **Gestion du déséquilibre** avec SMOTE
-  **Optimisation des hyperparamètres** (RandomizedSearchCV)
-  **Sélection des meilleurs modèles**
-  **Modèle de stacking pour meilleure performance**
-  **Application Web interactive avec Streamlit**
-  Envoi d’e-mail recommandé pour utilisateurs churnés (à venir)

---

## Technologies Utilisées

| Outil / Bibliothèque | Utilisation |
|----------------------|-------------|
| **Python**           | Langage principal |
| `pandas`, `numpy`    | Manipulation des données |
| `scikit-learn`       | Prétraitement, modèles ML, pipelines |
| `xgboost`, `lightgbm`, `catboost` | Modèles de boosting |
| `streamlit`          | Interface utilisateur Web |
| `joblib`             | Sauvegarde et chargement des modèles |
| `shap`, `seaborn`, `matplotlib` | Interprétabilité et visualisation |
| `SMOTE`              | Traitement du déséquilibre des classes |

---

## Lancer le projet localement

### 1. Cloner le dépôt
```bash
git clone https://github.com/abdelfatah-chaib/ChurnPredector.git
cd ChurnPredector
