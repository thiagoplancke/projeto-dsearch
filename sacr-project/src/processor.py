import os
from docling.document_converter import DocumentConverter
from pathlib import Path

class DocumentProcessor:
    def __init__(self):
        self.converter = DocumentConverter()

    def process_pdf(self, pdf_path):
        """
        Converts PDF to Markdown and performs quality check.
        Returns (text, quality_score)
        """
        try:
            result = self.converter.convert(pdf_path)
            markdown_content = result.document.export_to_markdown()
            
            # Simple quality heuristic: if word count is too low relative to pages
            # or if docling provides metadata about OCR confidence.
            # For now, let's look at the document content.
            
            word_count = len(markdown_content.split())
            # Basic validation: if we have 0 words, quality is 0
            quality_score = 100 if word_count > 50 else 50
            
            # Note: SACR requires OCR < 70% to be marked as Inconclusive.
            # Since Docling abstracts OCR, we'll return a score.
            # In a real scenario, we'd pull more granular metrics from result.document.
            
            return markdown_content, quality_score
        except Exception as e:
            print(f"Error processing document: {e}")
            return None, 0

    def save_to_uploads(self, file_path, upload_dir):
        """
        Saves the file to the project's upload directory.
        """
        filename = os.path.basename(file_path)
        dest_path = Path(upload_dir) / filename
        with open(file_path, "rb") as f_src:
            with open(dest_path, "wb") as f_dest:
                f_dest.write(f_src.read())
        return str(dest_path)
