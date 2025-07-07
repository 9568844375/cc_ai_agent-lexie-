# vector_store/index_faiss.py

import faiss
import numpy as np

dim = 384  # embedding vector size
index = faiss.IndexFlatL2(dim)
doc_map = []  # to store corresponding documents

def add_to_index(text: str, embedding: list):
    global index, doc_map
    embedding_np = np.array([embedding], dtype="float32")
    index.add(embedding_np)
    doc_map.append(text)

def search(query_embedding: list, k: int = 3):
    if index.ntotal == 0:
        return ["⚠️ FAISS index is empty."]
    query_np = np.array([query_embedding], dtype="float32")
    D, I = index.search(query_np, k)
    return [doc_map[i] for i in I[0] if i < len(doc_map)]

# Debug print
print("✅ index_faiss.py loaded successfully")
