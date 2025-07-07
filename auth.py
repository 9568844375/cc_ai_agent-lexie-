print("✅ auth.py loaded")

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError  # ✅ Correct import location

security = HTTPBearer()
SECRET_KEY = "my_super_secret_key_123"

def get_user_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        print("✅ Decoded payload:", payload)

        role = payload.get("role")
        if not role:
            raise HTTPException(status_code=401, detail="Role missing in token")

        # Optional: enforce admin-only access here
        # if role != "admin":
        #     raise HTTPException(status_code=403, detail="Unauthorized access to admin logs")

        return role

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print("❌ JWT error:", e)
        raise HTTPException(status_code=401, detail="Token processing error")