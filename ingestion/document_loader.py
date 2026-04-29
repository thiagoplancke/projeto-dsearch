import os
from langchain_core.documents import Document
from docling.document_converter import DocumentConverter

def load_document(file_path: str) -> list[Document]:
    """
    Carrega um documento (PDF, DOCX) usando o Docling e retorna uma lista
    de objetos Document do LangChain, onde cada item pode ser um nó/elemento
    extraído do documento (ex: texto, tabela, etc).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
    converter = DocumentConverter()
    result = converter.convert(file_path)
    
    # Docling permite exportar o documento processado para markdown facilmente.
    # Vamos extrair o markdown do documento para usá-lo na indexação, pois ele
    # retém estrutura (títulos, tabelas, etc).
    
    markdown_text = result.document.export_to_markdown()
    
    doc = Document(
        page_content=markdown_text,
        metadata={
            "source": os.path.basename(file_path),
            "file_path": file_path
        }
    )
    
    return [doc]
