from langchain_chroma import Chroma
from langchain_core.documents import Document
from embedding.embedder import get_embedder
from config import CHROMA_DIR

def get_vectorstore() -> Chroma:
    """
    Retorna a instância do banco vetorial Chroma configurado
    com persistência no diretório local.
    """
    embedder = get_embedder()
    
    vectorstore = Chroma(
        collection_name="dsearch_docs",
        embedding_function=embedder,
        persist_directory=str(CHROMA_DIR)
    )
    
    return vectorstore

def add_documents_to_store(documents: list[Document]):
    """
    Adiciona os documentos (chunks) ao ChromaDB.
    """
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)

def clear_vectorstore():
    """
    Limpa todos os dados armazenados no ChromaDB recriando a coleção.
    """
    vectorstore = get_vectorstore()
    vectorstore.delete_collection()
