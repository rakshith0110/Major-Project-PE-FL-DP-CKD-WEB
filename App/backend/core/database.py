"""
Database configuration and schema for Federated Learning CKD Application
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import json

DATABASE_PATH = Path(__file__).parent.parent.parent / "federated_ckd.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            login_password_hash TEXT NOT NULL,
            training_password_hash TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            last_trained_time TIMESTAMP,
            update_status TEXT DEFAULT 'No Update',
            total_records_trained INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Training logs table (per client)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            round_number INTEGER,
            epochs INTEGER,
            batch_size INTEGER,
            learning_rate REAL,
            noise_multiplier REAL,
            max_grad_norm REAL,
            accuracy REAL,
            loss REAL,
            training_time REAL,
            dataset_size INTEGER,
            metrics_json TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Global model table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_number INTEGER DEFAULT 0,
            model_path TEXT,
            accuracy REAL,
            loss REAL,
            metrics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Local models table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            model_path TEXT,
            delta_path TEXT,
            accuracy REAL,
            loss REAL,
            is_aggregated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            patient_data_json TEXT,
            prediction_result TEXT,
            confidence REAL,
            model_version INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Aggregation logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aggregation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_number INTEGER,
            clients_participated TEXT,
            num_clients INTEGER,
            previous_accuracy REAL,
            global_accuracy REAL,
            accuracy_improvement REAL,
            global_loss REAL,
            aggregation_time REAL,
            metrics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add new columns to existing aggregation_logs table if they don't exist
    cursor.execute("PRAGMA table_info(aggregation_logs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'previous_accuracy' not in columns:
        cursor.execute("ALTER TABLE aggregation_logs ADD COLUMN previous_accuracy REAL")
    
    if 'accuracy_improvement' not in columns:
        cursor.execute("ALTER TABLE aggregation_logs ADD COLUMN accuracy_improvement REAL")
    
    # Email notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT NOT NULL,
            subject TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Client datasets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            dataset_path TEXT,
            num_samples INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Client notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Admin notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default admin if not exists
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        admin_password = hash_password("admin123")
        cursor.execute("""
            INSERT INTO admin (username, password_hash, email)
            VALUES (?, ?, ?)
        """, ("admin", admin_password, "admin@hospital.com"))
    
    # Initialize global model entry
    cursor.execute("SELECT COUNT(*) FROM global_model")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO global_model (round_number, model_path)
            VALUES (?, ?)
        """, (0, None))
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DATABASE_PATH}")

if __name__ == "__main__":
    init_database()

# Made with Bob
