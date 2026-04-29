import os
import json
from google import genai
from google.genai import types
from config import GEMINI_MODEL
from src.vector_store import VectorIndexManager

class ComplianceEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else genai.Client()
        self.vector_store = VectorIndexManager()
        
        self.system_prompt = """
        Você é um Auditor de Conformidade Regulatória (SACR).
        Seu objetivo é analisar documentos técnicos frente a normas RDC (Nacional) e ISO (Internacional).

        REGRAS CRÍTICAS:
        1. Prioridade: RDC > ISO. Em caso de conflito, a norma nacional prevalece.
        2. Citação Obrigatória: Nunca classifique como "Conforme" sem copiar o trecho exato da lei que sustenta a decisão.
        3. Strict Mode: Não alucine. Se não encontrar evidência, marque como "Inconclusivo".
        4. Roteamento: Defina o setor responsável (Engenharia, Qualidade ou Produção).
        5. Saída: Retorne APENAS um JSON no formato abaixo.

        FORMATO DE SAÍDA:
        {
          "status": "Conforme" | "Não Conforme" | "Inconclusivo",
          "setor": "Engenharia" | "Qualidade" | "Produção",
          "analise_detalhada": "Descrição técnica da análise",
          "evidencias": [
            {"item_norma": "Referência da norma", "trecho_lei": "Citação direta", "conclusao": "Por que cumpre ou não"}
          ],
          "itens_faltantes": ["Lista de requisitos não encontrados"],
          "confianca_ia": 0.0 a 1.0
        }
        """

    def audit_document(self, doc_text, filename):
        # 1. Search for relevant legal context
        # We'll use the filename or first paragraph as context search
        search_query = doc_text[:500] 
        context = self.vector_store.get_context_with_citations(search_query, n_results=10)
        
        prompt = f"""
        {self.system_prompt}

        BASE LEGAL DISPONÍVEL:
        {context}

        DOCUMENTO PARA AUDITORIA ({filename}):
        {doc_text}
        
        Inicie a auditoria e retorne o JSON:
        """
        
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in AI Audit: {e}")
            return {
                "status": "Inconclusivo",
                "setor": "Qualidade",
                "analise_detalhada": f"Erro no processamento da IA: {str(e)}",
                "evidencias": [],
                "itens_faltantes": [],
                "confianca_ia": 0.0
            }
