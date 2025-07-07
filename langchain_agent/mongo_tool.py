from pymongo import MongoClient
from langchain.tools import tool

client = MongoClient("mongodb://localhost:27017")
db = client["ai_agent_lexie"]

@tool
def find_high_cgpa_students():
    """Finds students with CGPA > 8"""
    results = list(db.students.find({"cgpa": {"$gt": 8}}, {"_id": 0}))
    return str(results)
