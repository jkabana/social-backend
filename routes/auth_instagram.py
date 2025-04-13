from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import requests
from supabase import create_client, Client
from jose import jwt

load_dotenv()
router = APIRouter()

# 🔐 Meta App Info
APP_ID = os.getenv("META_APP_ID", "1569418413738608")
APP_SECRET = os.getenv("META_APP_SECRET")
REDIRECT_URI = os.getenv("META_REDIRECT_URI")
SCOPES = "instagram_basic,pages_show_list"

# 🗝️ Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔐 JWT Config for Supabase user verification
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")

# 🔗 Login URL Route
@router.get("/auth/instagram/login-url")
def get_instagram_login_url():
    login_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
        f"&response_type=code"
    )
    return {"login_url": login_url}

# 🔁 Callback Route
@router.get("/auth/instagram/callback")
def instagram_callback(request: Request, authorization: str = Header(None)):
    # 🔐 Extract and verify Supabase JWT
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience=JWT_AUDIENCE)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

    # 🛠 Get code from query param
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    # 🔄 Exchange code for access token
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    token_response = requests.get(token_url, params=params)
    token_data = token_response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return JSONResponse(content={"error": "Failed to retrieve access token"}, status_code=400)

    # 👤 Get user info
    user_info = requests.get(
        "https://graph.facebook.com/v19.0/me",
        params={"access_token": access_token}
    ).json()

    instagram_user_id = user_info.get("id")
    instagram_username = user_info.get("name", "unknown")

    # 💾 Save to Supabase
    result = supabase.table("instagram_accounts").insert({
        "user_id": user_id,
        "instagram_user_id": instagram_user_id,
        "username": instagram_username,
        "access_token": access_token,
        "token_type": "bearer",
    }).execute()

    return JSONResponse(content={"message": "Instagram account connected!", "data": result.data})

