from langchain.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

from langchain.document_loaders import PyPDFLoader

embeddings = OpenAIEmbeddings(openai_api_key="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")

def load_documents_and_embed():
    loader = PyPDFLoader("documents/sample.pdf")
    pages = loader.load_and_split()
    
    vectorstore = Chroma.from_documents(pages, embedding=embeddings, persist_directory="./chroma_db")
    vectorstore.persist()
    return vectorstore

def get_vector_store():
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
