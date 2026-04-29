from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP

def process_documents(documents: list[Document]) -> list[Document]:
    """
    Recebe uma lista de documentos e realiza o chunking.
    Utiliza o RecursiveCharacterTextSplitter para tentar preservar
    parágrafos e quebras de linha antes de cortar em palavras.
    """
    # Como o texto extraído do Docling é em Markdown, o RecursiveCharacterTextSplitter
    # é excelente pois por padrão corta em ["\n\n", "\n", " ", ""]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return chunks
