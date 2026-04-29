import sqlite3
from datetime import datetime
from config import DB_PATH

class RouterService:
    def __init__(self):
        self.db_path = DB_PATH

    def register_initial_analysis(self, doc_id, ai_json):
        """
        Registers the IA result with status 'Pendente de Revisão'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update document status
        cursor.execute("""
            UPDATE documents 
            SET status = 'Pendente de Revisão', target_sector = ? 
            WHERE id = ?
        """, (ai_json.get('setor', 'Qualidade'), doc_id))
        
        # Insert into analyses table
        import json
        cursor.execute("""
            INSERT INTO analyses (doc_id, ai_raw_output) 
            VALUES (?, ?)
        """, (doc_id, json.dumps(ai_json)))
        
        conn.commit()
        conn.close()

    def finalize_analysis(self, analysis_id, final_json, admin_id):
        """
        ADM approves/finalizes the analysis. Status becomes 'Finalizado'.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get doc_id
        cursor.execute("SELECT doc_id FROM analyses WHERE id = ?", (analysis_id,))
        doc_id = cursor.fetchone()[0]
        
        # Update analysis
        import json
        cursor.execute("""
            UPDATE analyses 
            SET final_decision = ?, reviewer_id = ?, reviewed_at = ? 
            WHERE id = ?
        """, (json.dumps(final_json), admin_id, datetime.now(), analysis_id))
        
        # Update document status
        cursor.execute("""
            UPDATE documents 
            SET status = 'Finalizado', target_sector = ? 
            WHERE id = ?
        """, (final_json.get('setor', 'Qualidade'), doc_id))
        
        conn.commit()
        conn.close()

    def get_pending_reviews(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, d.filename, d.target_sector, a.ai_raw_output 
            FROM analyses a
            JOIN documents d ON a.doc_id = d.id
            WHERE d.status = 'Pendente de Revisão'
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_sector_documents(self, sector):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.filename, d.status, a.final_decision 
            FROM documents d
            JOIN analyses a ON d.id = a.doc_id
            WHERE d.status = 'Finalizado' AND d.target_sector = ?
        """, (sector,))
        results = cursor.fetchall()
        conn.close()
        return results
