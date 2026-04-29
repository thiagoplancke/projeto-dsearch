import sqlite3
import hashlib
from config import DB_PATH

class AuthManager:
    def __init__(self):
        self.db_path = DB_PATH

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """
        Returns (user_id, role) if successful, else None
        """
        hashed_pw = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "username": username, "role": user[1]}
        return None

    def get_user_role(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role = cursor.fetchone()
        conn.close()
        return role[0] if role else None
