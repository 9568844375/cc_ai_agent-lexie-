import os
import pdfplumber
from .embedder import get_embedding
from .index_faiss import add_to_index

PDF_DIR = "./documents"

def load_pdfs():
    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            path = os.path.join(PDF_DIR, filename)
            with pdfplumber.open(path) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                embedding = get_embedding(text)
                add_to_index(text, embedding)
