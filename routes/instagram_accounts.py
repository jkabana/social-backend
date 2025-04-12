from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_id(token: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        user = supabase.auth.get_user(token.credentials)
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/instagram/token")
def store_instagram_token(payload: dict, user_id: str = Depends(get_user_id)):
    payload["user_id"] = user_id
    response = supabase.table("instagram_accounts") \
        .upsert(payload, on_conflict=["user_id"]) \
        .execute()

    if response.error:
        raise HTTPException(status_code=500, detail=response.error.message)

    return {"message": "Instagram account updated", "data": response.data}

@router.get("/instagram/account")
def get_instagram_account(user_id: str = Depends(get_user_id)):
    response = supabase.table("instagram_accounts") \
        .select("*") \
        .eq("user_id", user_id) \
        .single() \
        .execute()

    if response.error:
        raise HTTPException(status_code=404, detail="Instagram account not found")

    return {"account": response.data}

class InstagramPostPayload(BaseModel):
    caption: str
    media_url: str  # URL to an image or video

@router.post("/instagram/post")
async def post_to_instagram(payload: InstagramPostPayload, user_id: str = Depends(get_user_id)):
    response = supabase.table("instagram_accounts") \
        .select("access_token, instagram_user_id") \
        .eq("user_id", user_id) \
        .single() \
        .execute()

    if response.error or not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instagram account not found for user."
        )

    ig_data = response.data
    access_token = ig_data["access_token"]
    instagram_user_id = ig_data["instagram_user_id"]

    return {
        "message": "Post request received",
        "caption": payload.caption,
        "media_url": payload.media_url,
        "instagram_user_id": instagram_user_id,
        "access_token_last4": access_token[-4:]  # Obfuscate for logs/debugging
    }

