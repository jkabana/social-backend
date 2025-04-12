import os
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"
AUDIENCE = "authenticated"

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], audience=AUDIENCE)
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid JWT payload")
        return {"user_id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=403, detail=f"JWT error: {str(e)}")

