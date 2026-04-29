import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
OUTPUT_DIR = BASE_DIR / "output"
TESTS_DIR = BASE_DIR / "tests"

# Specific Data Paths
BASE_LEGAL_DIR = DATA_DIR / "base_legal"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Database
DB_PATH = BASE_DIR / "database.db"

# LLM & Embeddings
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
GEMINI_MODEL = "gemini-1.5-flash"  # Using 1.5 Flash as standard stable version
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Security
SECRET_KEY = "sacr_secret_key_change_me"

# Ensure directories exist
for path in [DATA_DIR, OUTPUT_DIR, TESTS_DIR, BASE_LEGAL_DIR, UPLOADS_DIR, VECTOR_DB_DIR]:
    path.mkdir(parents=True, exist_ok=True)
