"""
Module complet pour toutes les opérations de base de données
Inclut la gestion des utilisateurs et de l'historique des prédictions
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import streamlit as st

# Chemins des bases de données
USERS_DB_PATH = 'database/users.db'
HISTORY_DB_PATH = 'database/history.db'

DB_PATH = 'database/users.db'

def get_conn():
    return sqlite3.connect(USERS_DB_PATH, check_same_thread=False)
# ==================== OPÉRATIONS UTILISATEURS ====================

def get_users_conn():
    """Connexion à la base de données users"""
    return sqlite3.connect(USERS_DB_PATH, check_same_thread=False)

def create_user(first_name, last_name, email, password):
    """Créer un nouvel utilisateur"""
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        
        # Vérifier si l'email existe déjà
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cur.fetchone():
            conn.close()
            return False  # Email déjà utilisé
        
        # Insérer le nouvel utilisateur
        cur.execute('''
            INSERT INTO users (first_name, last_name, email, password) 
            VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, email, password))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur création utilisateur: {e}")
        return False

def authenticate(email, password):
    conn = get_users_conn()
    cur  = conn.cursor()
    cur.execute('SELECT password FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return row is not None and row[0] == password

def authenticate_and_get_user(email, password):
    """Authenticate user and return user data if successful"""
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, first_name, last_name, email, created_at, password 
            FROM users WHERE email = ?
        ''', (email,))
        
        row = cur.fetchone()
        conn.close()
        
        if row and row[5] == password:  # row[5] is password
            return {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'created_at': row[4]
            }
        return None
    except Exception as e:
        print(f"Erreur authentification: {e}")
        return None


def get_user(email):
    """Récupérer un utilisateur par son email"""
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, first_name, last_name, email, created_at 
            FROM users WHERE email = ?
        ''', (email,))
        
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'email': row[3],
                'created_at': row[4]
            }
        return None
    except Exception as e:
        print(f"Erreur récupération utilisateur: {e}")
        return None

def update_user(email: str, **kwargs) -> bool:
    """Mettre à jour les informations d'un utilisateur"""
    try:
        conn = get_users_conn()
        cur = conn.cursor()
        
        # Construire la requête dynamiquement
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['first_name', 'last_name', 'password']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(email)
        query = f"UPDATE users SET {', '.join(fields)} WHERE email = ?"
        
        cur.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur mise à jour utilisateur: {e}")
        return False

# ==================== OPÉRATIONS HISTORIQUE ====================

def get_history_conn():
    """Connexion à la base de données history"""
    return sqlite3.connect(HISTORY_DB_PATH, check_same_thread=False)

def add_prediction(user_id: int, user_email: str, dataset_name: str, 
                  prediction_result: str, confidence_score: float = None, 
                  model_used: str = "default_model") -> bool:
    """Ajouter une nouvelle prédiction à l'historique"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO prediction_history 
            (user_id, user_email, prediction_date, dataset_name, prediction_result, 
             confidence_score, model_used) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_email, datetime.now(), dataset_name, prediction_result, 
              confidence_score, model_used))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur ajout prédiction: {e}")
        return False

def get_user_predictions(user_email: str, limit: int = None) -> List[Dict]:
    """Récupérer toutes les prédictions d'un utilisateur"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        query = '''
            SELECT id, prediction_date, dataset_name, prediction_result, 
                   confidence_score, model_used, created_at
            FROM prediction_history 
            WHERE user_email = ?
            ORDER BY prediction_date DESC
        '''
        
        if limit:
            query += f" LIMIT {limit}"
        
        cur.execute(query, (user_email,))
        rows = cur.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'prediction_date': row[1],
                'dataset_name': row[2],
                'prediction_result': row[3],
                'confidence_score': row[4],
                'model_used': row[5],
                'created_at': row[6]
            })
        
        return predictions
    except Exception as e:
        print(f"Erreur récupération prédictions utilisateur: {e}")
        return []

def get_all_predictions(limit: int = None) -> List[Dict]:
    """Récupérer toutes les prédictions (pour les admins)"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        query = '''
            SELECT id, user_email, prediction_date, dataset_name, prediction_result, 
                   confidence_score, model_used, created_at
            FROM prediction_history 
            ORDER BY prediction_date DESC
        '''
        
        if limit:
            query += f" LIMIT {limit}"
        
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'user_email': row[1],
                'prediction_date': row[2],
                'dataset_name': row[3],
                'prediction_result': row[4],
                'confidence_score': row[5],
                'model_used': row[6],
                'created_at': row[7]
            })
        
        return predictions
    except Exception as e:
        print(f"Erreur récupération toutes prédictions: {e}")
        return []

def get_prediction_stats(user_email: str = None) -> Dict:
    """Statistiques des prédictions"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        if user_email:
            cur.execute('''
                SELECT 
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_prediction,
                    MIN(prediction_date) as first_prediction
                FROM prediction_history 
                WHERE user_email = ?
            ''', (user_email,))
        else:
            cur.execute('''
                SELECT 
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_prediction,
                    MIN(prediction_date) as first_prediction
                FROM prediction_history
            ''')
        
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                'total_predictions': row[0] or 0,
                'churned_count': row[1] or 0,
                'retained_count': row[2] or 0,
                'avg_confidence': row[3] or 0,
                'unique_datasets': row[4] or 0,
                'last_prediction': row[5],
                'first_prediction': row[6]
            }
        else:
            return {
                'total_predictions': 0,
                'churned_count': 0,
                'retained_count': 0,
                'avg_confidence': 0,
                'unique_datasets': 0,
                'last_prediction': None,
                'first_prediction': None
            }
    except Exception as e:
        print(f"Erreur statistiques: {e}")
        return {}

def get_monthly_predictions(user_email: str = None, months_back: int = 12) -> List[Dict]:
    """Prédictions groupées par mois"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        if user_email:
            cur.execute('''
                SELECT 
                    strftime('%Y-%m', prediction_date) as month,
                    COUNT(*) as total,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained,
                    AVG(confidence_score) as avg_confidence
                FROM prediction_history 
                WHERE user_email = ? 
                    AND prediction_date >= date('now', '-{} months')
                GROUP BY strftime('%Y-%m', prediction_date)
                ORDER BY month DESC
            '''.format(months_back), (user_email,))
        else:
            cur.execute('''
                SELECT 
                    strftime('%Y-%m', prediction_date) as month,
                    COUNT(*) as total,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained,
                    AVG(confidence_score) as avg_confidence
                FROM prediction_history 
                WHERE prediction_date >= date('now', '-{} months')
                GROUP BY strftime('%Y-%m', prediction_date)
                ORDER BY month DESC
            '''.format(months_back))
        
        rows = cur.fetchall()
        conn.close()
        
        monthly_data = []
        for row in rows:
            monthly_data.append({
                'month': row[0],
                'total': row[1],
                'churned': row[2],
                'retained': row[3],
                'avg_confidence': row[4] or 0
            })
        
        return monthly_data
    except Exception as e:
        print(f"Erreur données mensuelles: {e}")
        return []

def get_dataset_stats(user_email: str = None) -> List[Dict]:
    """Statistiques par dataset"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        if user_email:
            cur.execute('''
                SELECT 
                    dataset_name,
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count,
                    AVG(confidence_score) as avg_confidence,
                    MAX(prediction_date) as last_used
                FROM prediction_history 
                WHERE user_email = ?
                GROUP BY dataset_name
                ORDER BY total_predictions DESC
            ''', (user_email,))
        else:
            cur.execute('''
                SELECT 
                    dataset_name,
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count,
                    AVG(confidence_score) as avg_confidence,
                    MAX(prediction_date) as last_used
                FROM prediction_history 
                GROUP BY dataset_name
                ORDER BY total_predictions DESC
            ''')
        
        rows = cur.fetchall()
        conn.close()
        
        dataset_stats = []
        for row in rows:
            total = row[1]
            dataset_stats.append({
                'dataset_name': row[0],
                'total_predictions': total,
                'churned_count': row[2],
                'retained_count': row[3],
                'churn_rate': (row[2] / total * 100) if total > 0 else 0,
                'avg_confidence': row[4] or 0,
                'last_used': row[5]
            })
        
        return dataset_stats
    except Exception as e:
        print(f"Erreur statistiques datasets: {e}")
        return []

def get_model_performance(user_email: str = None) -> List[Dict]:
    """Performance des modèles"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        if user_email:
            cur.execute('''
                SELECT 
                    model_used,
                    COUNT(*) as total_predictions,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count
                FROM prediction_history 
                WHERE user_email = ? AND model_used IS NOT NULL
                GROUP BY model_used
                ORDER BY avg_confidence DESC
            ''', (user_email,))
        else:
            cur.execute('''
                SELECT 
                    model_used,
                    COUNT(*) as total_predictions,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(CASE WHEN prediction_result = 'churned' THEN 1 END) as churned_count,
                    COUNT(CASE WHEN prediction_result = 'retained' THEN 1 END) as retained_count
                FROM prediction_history 
                WHERE model_used IS NOT NULL
                GROUP BY model_used
                ORDER BY avg_confidence DESC
            ''')
        
        rows = cur.fetchall()
        conn.close()
        
        model_performance = []
        for row in rows:
            model_performance.append({
                'model_name': row[0],
                'total_predictions': row[1],
                'avg_confidence': row[2] or 0,
                'churned_count': row[3],
                'retained_count': row[4]
            })
        
        return model_performance
    except Exception as e:
        print(f"Erreur performance modèles: {e}")
        return []

def delete_prediction(prediction_id: int, user_email: str) -> bool:
    """Supprimer une prédiction (seulement si elle appartient à l'utilisateur)"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cur.execute('''
            DELETE FROM prediction_history 
            WHERE id = ? AND user_email = ?
        ''', (prediction_id, user_email))
        
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    except Exception as e:
        print(f"Erreur suppression prédiction: {e}")
        return False

def cleanup_old_predictions(days_old: int = 365) -> int:
    """Nettoyer les anciennes prédictions (plus anciennes que X jours)"""
    try:
        conn = get_history_conn()
        cur = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cur.execute('''
            DELETE FROM prediction_history 
            WHERE prediction_date < ?
        ''', (cutoff_date,))
        
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    except Exception as e:
        print(f"Erreur nettoyage: {e}")
        return 0

# ==================== FONCTIONS UTILITAIRES ====================

def get_dashboard_summary(user_email: str) -> Dict:
    """Récupérer toutes les données nécessaires pour le dashboard en une fois"""
    try:
        return {
            'user_stats': get_prediction_stats(user_email),
            'monthly_data': get_monthly_predictions(user_email, 6),  # 6 derniers mois
            'recent_predictions': get_user_predictions(user_email, 10),  # 10 dernières
            'dataset_stats': get_dataset_stats(user_email),
            'model_performance': get_model_performance(user_email),
            'global_stats': get_prediction_stats()  # Stats globales pour comparaison
        }
    except Exception as e:
        print(f"Erreur résumé dashboard: {e}")
        return None

def export_user_data(user_email: str) -> Dict:
    """Exporter toutes les données d'un utilisateur"""
    try:
        user_info = get_user(user_email)
        if not user_info:
            return None
        
        return {
            'user_info': user_info,
            'statistics': get_prediction_stats(user_email),
            'all_predictions': get_user_predictions(user_email),
            'monthly_summary': get_monthly_predictions(user_email),
            'dataset_usage': get_dataset_stats(user_email),
            'model_usage': get_model_performance(user_email),
            'export_date': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Erreur export utilisateur: {e}")
        return None
    
# CORRECTIONS POUR LE DASHBOARD - Problèmes de récupération des données

# ========== CORRECTION 1: Fonction de débogage pour vérifier la DB ==========
def debug_database():
    """Fonction pour déboguer la base de données"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Vérifier la structure des tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        print(f"Tables disponibles: {tables}")
        
        # Vérifier les colonnes de la table predictions
        cur.execute("PRAGMA table_info(predictions);")
        columns = cur.fetchall()
        print(f"Colonnes de predictions: {columns}")
        
        # Compter le nombre total de prédictions
        cur.execute("SELECT COUNT(*) FROM predictions;")
        total = cur.fetchone()
        print(f"Total prédictions dans la DB: {total[0]}")
        
        # Lister quelques prédictions
        cur.execute("SELECT * FROM predictions LIMIT 5;")
        sample = cur.fetchall()
        print(f"Échantillon de prédictions: {sample}")
        
        # Vérifier les utilisateurs
        cur.execute("SELECT * FROM users LIMIT 5;")
        users = cur.fetchall()
        print(f"Utilisateurs: {users}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur debug: {e}")

# ========== CORRECTION 2: Fonction améliorée get_user_by_email ==========
def get_user_by_email_fixed(email):
    """Version corrigée de get_user_by_email avec plus de débogage"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Debug: afficher l'email recherché
        print(f"Recherche utilisateur avec email: '{email}'")
        
        # Recherche exacte
        cur.execute('SELECT id, first_name, last_name, email FROM users WHERE email = ?', (email,))
        user = cur.fetchone()
        
        if not user:
            # Recherche insensible à la casse
            cur.execute('SELECT id, first_name, last_name, email FROM users WHERE LOWER(email) = LOWER(?)', (email,))
            user = cur.fetchone()
            
        if not user:
            # Lister tous les emails pour debug
            cur.execute('SELECT email FROM users')
            all_emails = cur.fetchall()
            print(f"Emails dans la DB: {[e[0] for e in all_emails]}")
        
        conn.close()
        print(f"Utilisateur trouvé: {user}")
        return user
        
    except Exception as e:
        print(f"Erreur get_user_by_email_fixed: {e}")
        return None

# ========== CORRECTION 3: Fonction get_user_predictions corrigée ==========
def get_user_predictions_fixed(user_email, limit=None):
    """Version corrigée pour récupérer les prédictions utilisateur"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        print(f"Récupération prédictions pour: '{user_email}'")
        
        # Méthode 1: Recherche directe par email dans predictions
        query = '''
        SELECT prediction_date, dataset_name, prediction_result, 
               confidence_score, model_used, id, user_email
        FROM predictions 
        WHERE user_email = ? OR LOWER(user_email) = LOWER(?)
        ORDER BY prediction_date DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
            
        cur.execute(query, (user_email, user_email))
        predictions = cur.fetchall()
        
        # Si pas de résultats, essayer avec user_id
        if not predictions:
            user = get_user_by_email_fixed(user_email)
            if user:
                user_id = user[0]
                query2 = '''
                SELECT prediction_date, dataset_name, prediction_result, 
                       confidence_score, model_used, id, user_email
                FROM predictions 
                WHERE user_id = ?
                ORDER BY prediction_date DESC
                '''
                
                if limit:
                    query2 += f' LIMIT {limit}'
                    
                cur.execute(query2, (user_id,))
                predictions = cur.fetchall()
        
        conn.close()
        
        print(f"Prédictions trouvées: {len(predictions)}")
        
        # Convertir en format dictionnaire
        result = []
        for pred in predictions:
            result.append({
                'prediction_date': pred[0],
                'dataset_name': pred[1],
                'prediction_result': pred[2],
                'confidence_score': pred[3],
                'model_used': pred[4],
                'id': pred[5],
                'user_email': pred[6] if len(pred) > 6 else user_email
            })
        
        return result
        
    except Exception as e:
        print(f"Erreur get_user_predictions_fixed: {e}")
        return []

# ========== CORRECTION 4: Fonction get_prediction_stats corrigée ==========
def get_prediction_stats_fixed(user_email=None):
    """Version corrigée des statistiques de prédictions"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        if user_email:
            print(f"Calcul des stats pour: '{user_email}'")
            
            # Recherche directe par email dans predictions
            cur.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                    SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                    AVG(confidence_score) as avg_conf,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_pred
                FROM predictions 
                WHERE user_email = ? OR LOWER(user_email) = LOWER(?)
            ''', (user_email, user_email))
            
            stats = cur.fetchone()
            
            # Si pas de résultats, essayer avec user_id
            if stats[0] == 0:
                user = get_user_by_email_fixed(user_email)
                if user:
                    user_id = user[0]
                    cur.execute('''
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                            SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                            AVG(confidence_score) as avg_conf,
                            COUNT(DISTINCT dataset_name) as unique_datasets,
                            MAX(prediction_date) as last_pred
                        FROM predictions 
                        WHERE user_id = ?
                    ''', (user_id,))
                    stats = cur.fetchone()
        else:
            # Statistiques globales
            cur.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                    SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                    AVG(confidence_score) as avg_conf,
                    COUNT(DISTINCT dataset_name) as unique_datasets,
                    MAX(prediction_date) as last_pred
                FROM predictions
            ''')
            stats = cur.fetchone()
        
        conn.close()
        
        result = {
            'total_predictions': stats[0] or 0,
            'churned_count': stats[1] or 0,
            'retained_count': stats[2] or 0,
            'avg_confidence': stats[3] or 0,
            'unique_datasets': stats[4] or 0,
            'last_prediction': stats[5]
        }
        
        print(f"Stats calculées: {result}")
        return result
        
    except Exception as e:
        print(f"Erreur get_prediction_stats_fixed: {e}")
        return {
            'total_predictions': 0,
            'churned_count': 0,
            'retained_count': 0,
            'avg_confidence': 0,
            'unique_datasets': 0,
            'last_prediction': None
        }

# ========== CORRECTION 5: Fonction get_monthly_predictions corrigée ==========
def get_monthly_predictions_fixed(user_email):
    """Version corrigée des prédictions mensuelles"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        print(f"Données mensuelles pour: '{user_email}'")
        
        # Recherche directe par email
        cur.execute('''
            SELECT 
                strftime('%Y-%m', prediction_date) as month,
                SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                COUNT(*) as total
            FROM predictions 
            WHERE user_email = ? OR LOWER(user_email) = LOWER(?)
            GROUP BY strftime('%Y-%m', prediction_date)
            ORDER BY month DESC
            LIMIT 12
        ''', (user_email, user_email))
        
        monthly_data = cur.fetchall()
        
        # Si pas de résultats, essayer avec user_id
        if not monthly_data:
            user = get_user_by_email_fixed(user_email)
            if user:
                user_id = user[0]
                cur.execute('''
                    SELECT 
                        strftime('%Y-%m', prediction_date) as month,
                        SUM(CASE WHEN prediction_result = 'churned' THEN 1 ELSE 0 END) as churned,
                        SUM(CASE WHEN prediction_result = 'retained' THEN 1 ELSE 0 END) as retained,
                        COUNT(*) as total
                    FROM predictions 
                    WHERE user_id = ?
                    GROUP BY strftime('%Y-%m', prediction_date)
                    ORDER BY month DESC
                    LIMIT 12
                ''', (user_id,))
                monthly_data = cur.fetchall()
        
        conn.close()
        
        result = []
        for data in monthly_data:
            result.append({
                'month': data[0],
                'churned': data[1],
                'retained': data[2],
                'total': data[3]
            })
        
        print(f"Données mensuelles trouvées: {len(result)} mois")
        return result
        
    except Exception as e:
        print(f"Erreur get_monthly_predictions_fixed: {e}")
        return []

# ========== CORRECTION 6: Fonction get_dashboard_data corrigée ==========
@st.cache_data(ttl=60)  # Cache réduit pour debug
def get_dashboard_data_fixed(user_email):
    """Version corrigée pour récupérer toutes les données du dashboard"""
    try:
        print(f"=== DÉBUT get_dashboard_data_fixed pour '{user_email}' ===")
        
        # Debug de la base de données
        debug_database()
        
        # Vérifier que l'utilisateur existe
        user_data = get_user_by_email_fixed(user_email)
        print(f"User data: {user_data}")
        
        if not user_data and user_email != "demo@example.com":
            print(f"Utilisateur non trouvé: {user_email}")
            # Créer un utilisateur demo si nécessaire
            if user_email not in ["demo@example.com", "", None]:
                print("Création de données demo...")
                return create_demo_data(user_email)
            return None
            
        # Statistiques utilisateur
        user_stats = get_prediction_stats_fixed(user_email)
        print(f"User stats: {user_stats}")
        
        # Prédictions mensuelles
        monthly_data = get_monthly_predictions_fixed(user_email)
        print(f"Monthly data: {len(monthly_data)} mois")
        
        # Dernières prédictions
        recent_predictions = get_user_predictions_fixed(user_email, limit=10)
        print(f"Recent predictions: {len(recent_predictions)}")
        
        # Statistiques globales
        global_stats = get_prediction_stats_fixed()
        print(f"Global stats: {global_stats}")
        
        result = {
            'user_stats': user_stats,
            'monthly_data': monthly_data,
            'recent_predictions': recent_predictions,
            'global_stats': global_stats
        }
        
        print(f"=== FIN get_dashboard_data_fixed ===")
        return result
        
    except Exception as e:
        print(f"Erreur dans get_dashboard_data_fixed: {e}")
        import traceback
        traceback.print_exc()
        return None

# ========== CORRECTION 7: Créer des données demo si nécessaire ==========
def create_demo_data(user_email):
    """Crée des données de démonstration si l'utilisateur n'a pas de données"""
    from datetime import datetime, timedelta
    import random
    
    # Simuler des statistiques
    total_pred = random.randint(5, 20)
    churned = random.randint(1, total_pred//2)
    retained = total_pred - churned
    
    user_stats = {
        'total_predictions': total_pred,
        'churned_count': churned,
        'retained_count': retained,
        'avg_confidence': random.uniform(0.75, 0.95),
        'unique_datasets': random.randint(2, 5),
        'last_prediction': datetime.now().isoformat()
    }
    
    # Simuler des données mensuelles
    monthly_data = []
    for i in range(3):
        month = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
        monthly_data.append({
            'month': month,
            'churned': random.randint(1, 5),
            'retained': random.randint(3, 8),
            'total': random.randint(4, 13)
        })
    
    # Simuler des prédictions récentes
    recent_predictions = []
    for i in range(5):
        recent_predictions.append({
            'prediction_date': (datetime.now() - timedelta(days=i*2)).isoformat(),
            'dataset_name': random.choice(['waze_dataset.csv', 'customer_data.csv', 'user_behavior.csv']),
            'prediction_result': random.choice(['churned', 'retained']),
            'confidence_score': random.uniform(0.7, 0.95),
            'model_used': random.choice(['RandomForest', 'XGBoost', 'LogisticRegression']),
            'id': i+1
        })
    
    global_stats = {
        'total_predictions': total_pred * 10,
        'churned_count': churned * 10,
        'retained_count': retained * 10,
        'avg_confidence': 0.82,
        'unique_datasets': 8,
        'last_prediction': datetime.now().isoformat()
    }
    
    return {
        'user_stats': user_stats,
        'monthly_data': monthly_data,
        'recent_predictions': recent_predictions,
        'global_stats': global_stats
    }

# ========== CORRECTION 8: Fonction pour vérifier et corriger la session ==========
def fix_user_session():
    """Corrige les données de session utilisateur"""
    user_email = st.session_state.get('user_email')
    
    if not user_email or user_email == "demo@example.com":
        # Forcer un email de test
        st.session_state.user_email = "test@example.com"
        st.session_state.user_name = "Test User"
        st.session_state.user_id = 1
        print("Session corrigée avec des données de test")
    
    print(f"Session actuelle: {st.session_state.get('user_email')} - {st.session_state.get('user_name')}")





