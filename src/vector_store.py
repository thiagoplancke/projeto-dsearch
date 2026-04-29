import os
import chromadb
from chromadb.utils import embedding_functions
from config import VECTOR_DB_DIR, BASE_LEGAL_DIR, EMBEDDING_MODEL
from src.processor import DocumentProcessor

class VectorIndexManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        # Local embeddings using Sentence Transformers
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name="legal_base", 
            embedding_function=self.embedding_fn
        )
        self.processor = DocumentProcessor()

    def sync_legal_base(self):
        """
        Scans BASE_LEGAL_DIR and updates ChromaDB.
        """
        files = [f for f in os.listdir(BASE_LEGAL_DIR) if f.endswith('.pdf')]
        
        # Simple sync logic: clear and rebuild (for safety/simplicity as requested)
        # or check if already indexed. Let's go with "rebuild if change detected" 
        # but optimized by checking existing IDs.
        
        existing_ids = self.collection.get()['ids']
        
        for filename in files:
            file_path = os.path.join(BASE_LEGAL_DIR, filename)
            doc_id = filename # Using filename as ID for simplicity
            
            if doc_id not in existing_ids:
                print(f"Indexing {filename}...")
                text, quality = self.processor.process_pdf(file_path)
                if text:
                    # Split text into chunks for better retrieval
                    chunks = self.chunk_text(text)
                    for i, chunk in enumerate(chunks):
                        self.collection.add(
                            ids=[f"{doc_id}_{i}"],
                            documents=[chunk],
                            metadatas=[{"source": filename, "chunk": i}]
                        )
        print("Sync complete.")

    def chunk_text(self, text, size=1000, overlap=200):
        # Basic chunking logic
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i:i + size])
        return chunks

    def search(self, query, n_results=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

    def get_context_with_citations(self, query, n_results=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        context_parts = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                context_parts.append(f"Source: {meta['source']}\nContent: {doc}")
        
        return "\n\n---\n\n".join(context_parts)
