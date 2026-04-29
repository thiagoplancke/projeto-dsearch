from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

def get_embedder() -> HuggingFaceEmbeddings:
    """
    Inicializa e retorna o modelo de embeddings do HuggingFace.
    O modelo será baixado na primeira execução e armazenado em cache localmente.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return embeddings
