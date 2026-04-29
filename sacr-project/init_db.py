import sqlite3
import hashlib
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL -- ADM, Engenharia, Qualidade, Produção
    )
    ''')

    # Documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_path TEXT NOT NULL,
        status TEXT NOT NULL, -- Pendente, Pendente de Revisão, Finalizado
        target_sector TEXT, -- Engenharia, Qualidade, Produção
        uploader_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uploader_id) REFERENCES users (id)
    )
    ''')

    # Analyses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL,
        ai_raw_output TEXT, -- JSON original da IA
        final_decision TEXT, -- JSON validado pelo ADM
        reviewer_id INTEGER,
        reviewed_at TIMESTAMP,
        evidence_quotes TEXT, -- Trechos das leis
        FOREIGN KEY (doc_id) REFERENCES documents (id),
        FOREIGN KEY (reviewer_id) REFERENCES users (id)
    )
    ''')

    # Create default ADM if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Password 'admin123'
        hashed_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ('admin', hashed_pw, 'ADM'))
        
        # Create some sector users for testing
        for sector in ['Engenharia', 'Qualidade', 'Produção']:
            hpw = hashlib.sha256(f'user_{sector.lower()}'.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (sector.lower(), hpw, sector))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
