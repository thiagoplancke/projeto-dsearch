import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.absolute()

def load_env_file(env_path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

load_env_file(BASE_DIR / ".env")

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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Security
SECRET_KEY = "sacr_secret_key_change_me"

# Ensure directories exist
for path in [DATA_DIR, OUTPUT_DIR, TESTS_DIR, BASE_LEGAL_DIR, UPLOADS_DIR, VECTOR_DB_DIR]:
    path.mkdir(parents=True, exist_ok=True)
