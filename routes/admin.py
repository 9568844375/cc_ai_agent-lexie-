# routes/admin.py
from fastapi import APIRouter, Header, HTTPException
import redis.asyncio as redis
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from db import get_teacher_logs, get_student_metrics, get_organization_requests
from utils.summarize import summarize_data

admin_router = APIRouter(tags=["Admin"])


# JWT secret key used to sign the token
SECRET_KEY = "my_super_secret_key_123"  # Make sure this matches the one used in token generation

# Initialize Redis client
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

@admin_router.get("/admin/logs")
async def get_suspicious_logs(authorization: str = Header(None)):
    print("Authorization header received:", authorization)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Missing or malformed Authorization header")

    try:
        token = authorization.split(" ")[1]  # Extract token after 'Bearer'
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Decoded payload:", payload)

        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Forbidden: Not an admin")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

    try:
        logs = await redis_client.lrange("suspicious_logs", 0, 19)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    return {"flagged_logs": logs}


@admin_router.get("/admin/summary")
async def get_admin_summary():
    try:
        teacher_logs = await get_teacher_logs()
        student_stats = await get_student_metrics()
        org_requests = await get_organization_requests()

        teacher_summary = await summarize_data(teacher_logs, "teacher activities")
        student_summary = await summarize_data(student_stats, "student performance")
        org_summary = await summarize_data(org_requests, "organization requests")

        return {
            "teacher_summary": teacher_summary,
            "student_summary": student_summary,
            "organization_summary": org_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
