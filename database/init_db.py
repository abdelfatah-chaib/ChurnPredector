#!/usr/bin/env python3
"""
Script d'initialisation complète des bases de données
Exécuter ce script pour configurer toutes les bases de données nécessaires
"""

import os
import sqlite3
from datetime import datetime
import random


def create_users_database():
    """Créer la base de données users"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name  TEXT NOT NULL,
        email      TEXT NOT NULL UNIQUE,
        password   TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base users.db créée")

def create_history_database():
    """Créer la base de données history"""
    conn = sqlite3.connect('history.db')
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_email TEXT NOT NULL,
        prediction_date DATETIME NOT NULL,
        dataset_name TEXT NOT NULL,
        prediction_result TEXT NOT NULL,  -- 'churned' ou 'retained'
        confidence_score REAL,  -- Score de confiance de la prédiction (0-1)
        model_used TEXT,  -- Nom du modèle utilisé
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base history.db créée")

def create_demo_users():
    """Créer des utilisateurs de démonstration"""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    demo_users = [
        (1, 'Demo', 'User', 'demo@example.com', 'password123'),
        (2, 'John', 'Doe', 'john.doe@test.com', 'password123'),
        (3, 'Jane', 'Smith', 'jane.smith@test.com', 'password123'),
        (4, 'Admin', 'User', 'admin@company.com', 'admin123')
    ]
    
    for user_id, first_name, last_name, email, password in demo_users:
        try:
            cur.execute('''
                INSERT OR REPLACE INTO users (id, first_name, last_name, email, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, first_name, last_name, email, password))
        except sqlite3.IntegrityError:
            print(f"⚠️  Utilisateur {email} existe déjà")
    
    conn.commit()
    conn.close()
    print("✅ Utilisateurs de démonstration créés")

def create_sample_predictions():
    """Créer des prédictions d'exemple pour la démonstration"""
    conn = sqlite3.connect('history.db')
    cur = conn.cursor()
    
    # Utilisateurs pour lesquels créer des données
    users_data = [
        (1, 'demo@example.com'),
        (2, 'john.doe@test.com'),
        (3, 'jane.smith@test.com'),
        (4, 'admin@company.com')
    ]
    
    datasets = [
        "waze_dataset.csv",
        "customer_data.csv", 
        "user_behavior.csv",
        "mobile_app_data.csv",
        "subscription_data.csv"
    ]
    
    models = [
        "RandomForest",
        "XGBoost", 
        "LogisticRegression",
        "NeuralNetwork",
        "SVM"
    ]
    
    results = ["churned", "retained"]
    
    # Générer des prédictions pour chaque utilisateur
    for user_id, email in users_data:
        num_predictions = random.randint(10, 25)  # Entre 10 et 25 prédictions par utilisateur
        
        for i in range(num_predictions):
            # Date aléatoire dans les 90 derniers jours
            days_ago = random.randint(1, 90)
            prediction_date = datetime.now() - timedelta(days=days_ago)
            
            dataset_name = random.choice(datasets)
            prediction_result = random.choice(results)
            
            # Biais réaliste: plus de retained que de churned
            if random.random() < 0.7:  # 70% de chance d'être retained
                prediction_result = "retained"
            else:
                prediction_result = "churned"
            
            confidence_score = random.uniform(0.65, 0.95)
            model_used = random.choice(models)
            
            cur.execute('''
                INSERT INTO prediction_history 
                (user_id, user_email, prediction_date, dataset_name, 
                 prediction_result, confidence_score, model_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email, prediction_date, dataset_name, 
                  prediction_result, confidence_score, model_used))
    
    conn.commit()
    conn.close()
    print("✅ Prédictions d'exemple créées")

def verify_databases():
    """Vérifier que les bases de données sont correctement créées"""
    print("\n📊 Vérification des bases de données:")
    
    # Vérifier users.db
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        conn.close()
        print(f"   👥 Users: {user_count} utilisateurs")
    except Exception as e:
        print(f"   ❌ Erreur users.db: {e}")
    
    # Vérifier history.db
    try:
        conn = sqlite3.connect('history.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM prediction_history")
        prediction_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned,
                COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained
            FROM prediction_history
        """)
        churned, retained = cur.fetchone()
        conn.close()
        
        print(f"   📈 History: {prediction_count} prédictions total")
        print(f"      - 🔴 Churned: {churned}")
        print(f"      - 🟢 Retained: {retained}")
    except Exception as e:
        print(f"   ❌ Erreur history.db: {e}")

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation des bases de données...")
    print("=" * 50)
    
    # Étape 2: Créer les bases de données
    create_users_database()
    create_history_database()
    
    # Étape 3: Ajouter des données de démonstration
    create_demo_users()
    create_sample_predictions()
    
    # Étape 4: Vérifier les installations
    verify_databases()
    
    print("\n" + "=" * 50)
    print("✅ Initialisation terminée avec succès!")
    print("\n📋 Comptes de test disponibles:")
    print("   • demo@example.com / password123")
    print("   • john.doe@test.com / password123") 
    print("   • jane.smith@test.com / password123")
    print("   • admin@company.com / admin123")
    
    print("\n📁 Structure créée:")
    print("   • database/users.db - Gestion des utilisateurs")
    print("   • database/history.db - Historique des prédictions")

if __name__ == "__main__":
    from datetime import timedelta
    main()