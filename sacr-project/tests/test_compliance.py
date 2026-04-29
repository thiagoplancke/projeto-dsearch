import unittest
import os
import sqlite3
from src.auth import AuthManager
from config import DB_PATH

class TestSACR(unittest.TestCase):
    def setUp(self):
        self.auth = AuthManager()

    def test_login_admin(self):
        # Default admin password set in init_db.py was 'admin123'
        user = self.auth.login("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'ADM')

    def test_login_sector(self):
        # Default qualiddade password set in init_db.py was 'user_qualidade'
        user = self.auth.login("qualidade", "user_qualidade")
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'Qualidade')

    def test_invalid_login(self):
        user = self.auth.login("admin", "wrongpass")
        self.assertIsNone(user)

if __name__ == "__main__":
    unittest.main()
