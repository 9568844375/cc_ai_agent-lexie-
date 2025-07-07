# db.py

from pymongo import MongoClient
from datetime import datetime
import os

# === Config: Switch between Atlas and Local MongoDB ===
USE_ATLAS = True

if USE_ATLAS:
    client = MongoClient("mongodb+srv://unknowncreator6661:air21510@cluster0.sodqxzi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
else:
    client = MongoClient("mongodb://localhost:27017")

# === Database & Collections ===
db = client["ai_agent_lexie"]

# Suspicious logs collection
flags_collection = db["suspicious_logs"]

# Role-to-collection mapping
collection_map = {
    "student": db.students,
    "teacher": db.teachers,
    "admin": db.admins,
    "organization": db.organizations
}

# ✅ Fetch user-specific context data
async def get_user_data(role: str, user_id: str) -> dict:
    collection = None
    if collection is None:
        return {}

    # Find user document by ID
    return collection.find_one({"_id": user_id}, {"_id": 0}) or {}

# ✅ Save flagged message to DB with timestamp
async def save_flag_to_db(log: dict):
    log["timestamp"] = datetime.utcnow()
    flags_collection.insert_one(log)

# ✅ Admin summarization helpers
async def get_teacher_logs():
    return [log["message"] for log in db.logs.find({"role": "teacher"}, {"_id": 0, "message": 1})]

async def get_student_metrics():
    students = db.students.find({}, {"_id": 0, "name": 1, "cgpa": 1, "assignments": 1})
    return [f"{s['name']} has CGPA {s['cgpa']}" for s in students]

async def get_organization_requests():
    requests = db.requests.find({}, {"_id": 0, "title": 1, "status": 1})
    return [f"Request: {r['title']}, Status: {r['status']}" for r in requests]
