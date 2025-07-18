from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_embedding(text: str):
    return embedding_model.embed_query(text)
