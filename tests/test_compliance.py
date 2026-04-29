import unittest
import os
import sqlite3
from unittest.mock import Mock, patch
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

    @patch("src.engine.VectorIndexManager")
    @patch("src.engine.genai.Client")
    def test_audit_document_uses_google_genai_client(self, mock_client_cls, mock_vector_cls):
        from src.engine import ComplianceEngine

        mock_vector = mock_vector_cls.return_value
        mock_vector.get_context_with_citations.return_value = "legal context"

        mock_response = Mock()
        mock_response.text = """
        {
          "status": "Conforme",
          "setor": "Qualidade",
          "analise_detalhada": "ok",
          "evidencias": [],
          "itens_faltantes": [],
          "confianca_ia": 0.9
        }
        """
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_response

        engine = ComplianceEngine(api_key="test-key")
        result = engine.audit_document("documento tecnico para auditoria", "doc.pdf")

        self.assertEqual(result["status"], "Conforme")
        mock_client_cls.assert_called_once_with(api_key="test-key")
        mock_client.models.generate_content.assert_called_once()

if __name__ == "__main__":
    unittest.main()
