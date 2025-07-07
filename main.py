# Lexi AI Agent – Main FastAPI Server
from pydantic import BaseModel
class ChatRequest(BaseModel):
    user_id: str
    message: str

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Request, Depends, HTTPException, Header  # Include Header for token
from fastapi.middleware.cors import CORSMiddleware
from auth import get_user_role  # Role-based authentication
from chat_agent import generate_response  # ChatGPT response generator
from db import get_user_data, save_flag_to_db  # MongoDB functions
from routes.admin import admin_router  # ✅ This will fix the error
from routes.chat import router as chat_router
from langchain_agent.vector_store import load_documents_and_embed
from vector_store.load_documents import load_pdfs
from routes.voice_chat import router as voice_router
import uvicorn
import redis.asyncio as redis
import asyncio
from datetime import datetime

from vector_store.index_faiss import search, add_to_index
from vector_store.embedder import get_embedding

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def rate_limit(user_id: str):
    key = f"rate:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    if count > 20:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

async def log_suspicious_activity(user_id: str, message: str, role: str):
    if any(term in message.lower() for term in ["password", "admin access", "student data"]):
        log = {
            "user_id": user_id,
            "role": role,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await redis_client.lpush("suspicious_logs", str(log))
        await save_flag_to_db(log)  # Save to MongoDB permanently

async def store_chat_memory(user_id: str, user_query: str, lexi_reply: str):
    chat_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": user_query,
        "answer": lexi_reply
    }
    await redis_client.lpush(f"chat_memory:{user_id}", str(chat_log))
    await redis_client.ltrim(f"chat_memory:{user_id}", 0, 4)

async def get_chat_memory(user_id: str):
    history = await redis_client.lrange(f"chat_memory:{user_id}", 0, 4)
    return "\n\n".join(history)

@app.get("/memory/{user_id}")
async def view_user_memory(user_id: str):
    memory = await redis_client.lrange(f"chat_memory:{user_id}", 0, 4)
    return {"user_id": user_id, "memory": memory}

@app.delete("/memory/{user_id}")
async def clear_user_memory(user_id: str):
    await redis_client.delete(f"chat_memory:{user_id}")
    return {"status": "cleared", "user_id": user_id}

app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(voice_router)

@app.post("/chat")
async def chat_with_lexi(payload: ChatRequest, role: str = Depends(get_user_role)):
    user_id = payload.user_id
    user_query = payload.message

    if not user_query or not user_id:
        raise HTTPException(status_code=400, detail="Missing message or user ID")

    await log_suspicious_activity(user_id, user_query, role)

    cache_key = f"context:{role}:{user_id}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        context_data = eval(cached_data)
    else:
        context_data = await get_user_data(role, user_id)
        await redis_client.set(cache_key, str(context_data), ex=300)

    # 🧠 Chat memory
    chat_history = await get_chat_memory(user_id)

    # 🔍 Vector Search
    query_embedding = get_embedding(user_query)
    related_docs = search(query_embedding, k=3)  # You can change k=3 to control match count

    # 🧠 Combine memory + vector matches + user input
    enriched_query = f"{chat_history}\n\nTop Related Docs:\n{'. '.join(related_docs)}\n\nUser: {user_query}"

    # 🤖 Generate final response
    reply = await generate_response(enriched_query, context_data, role)

    # 🗾 Store chat history
    await store_chat_memory(user_id, user_query, reply)

    return {"response": reply}

@app.on_event("startup")
def on_startup():
    import os

    # 🥹 Clean temp/ folder
    temp_folder = "temp"
    if os.path.exists(temp_folder):
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # 🧠 Embed static documents into FAISS
    def load_documents_and_embed():
        documents = [
            "Physics assignment is due July 10.",
            "Computer Science project demo is on July 15.",
            "Mathematics homework: Chapter 6 problems.",
        ]
        for doc in documents:
            emb = get_embedding(doc)
            add_to_index(doc, emb)

    # 📅 Load and embed
    load_documents_and_embed()

@app.get("/")
async def root():
    return {"message": "Welcome to Lexi AI Agent 🚀", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
