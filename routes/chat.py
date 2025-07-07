from fastapi import APIRouter, Body, Request
from pymongo import MongoClient

# FAISS-based vector search
from vector_store.embedder import get_embedding
from vector_store.index_faiss import search,add_to_index

# LangChain agent with Redis memory
from langchain_agent.hybrid_agent import get_context_aware_hybrid_agent

router = APIRouter()

# MongoDB setup
client = MongoClient("mongodb+srv://unknowncreator6661:air21510@cluster0.sodqxzi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ai_agent_lexie"]

# Helper: Check if query is for structured data
def is_structured_query(q):
    keywords = ["student", "project", "cgpa", "email", "department", "assignments"]
    return any(k in q.lower() for k in keywords)

@router.post("/chat")
async def hybrid_chat(query: str = Body(...), request: Request = None):
    try:
        # 🧠 Extract user ID from header (or fallback)
        user_id = request.headers.get("X-User-ID", "default_user") if request else "default_user"

        # 🚀 Create LangChain agent with memory per user
        agent = get_context_aware_hybrid_agent(user_id)

        if is_structured_query(query):
            # 📊 Handle MongoDB structured query
            result = list(db.students.find({"cgpa": {"$gt": 8}}, {"_id": 0}))
            return {"response": f"Structured data: {result}"}
        
        else:
            # 📚 First try FAISS document search
            query_embedding = get_embedding(query)
            matches = search(query_embedding)
            
            if matches:
                return {"response": f"Semantic matches from documents: {matches}"}
            
            # 💬 Fallback to full LangChain agent with memory
            langchain_response = agent.run(query)
            return {"response": f"LangChain agent fallback: {langchain_response}"}

    except Exception as e:
        return {"error": str(e)}
