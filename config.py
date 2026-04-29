import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
CHROMA_DIR = DATA_DIR / "chroma_db"

# Create directories if they don't exist
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# LLM Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3" # Pode ser alterado para 'mistral' ou outro modelo disponível localmente
LLM_TEMPERATURE = 0.1 # Baixa temperatura para reduzir alucinação

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Configuration
TOP_K_RETRIEVAL = 3
