import os
import shutil
from pathlib import Path
from config import DOCS_DIR

def save_uploaded_file(uploaded_file) -> str:
    """
    Salva um arquivo enviado via Streamlit no diretório local.
    Retorna o caminho absoluto do arquivo salvo.
    """
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def get_saved_files() -> list[str]:
    """
    Retorna uma lista com os nomes dos arquivos já salvos localmente.
    """
    return [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]

def delete_file(filename: str) -> bool:
    """
    Deleta um arquivo do diretório local.
    """
    file_path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def clear_all_files():
    """
    Remove todos os documentos do diretório local.
    """
    for filename in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
