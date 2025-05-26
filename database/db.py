"""
Module complet pour toutes les opérations de base de données
Inclut la gestion des utilisateurs et de l'historique des prédictions
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Chemins des bases de données
USERS_DB_PATH = 'database/users.db'
HISTORY_DB_PATH = 'database/history.db'

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