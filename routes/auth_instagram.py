from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Debugging info
print("📍 Current working directory:", os.getcwd())
print("📍 META_APP_ID from .env:", os.getenv("META_APP_ID"))

router = APIRouter()

# Load App ID with fallback
APP_ID = os.getenv("META_APP_ID")
if not APP_ID:
    print("⚠️ META_APP_ID not found in .env — falling back to hardcoded App ID.")
    APP_ID = "1569418413738608"
else:
    print(f"✅ META_APP_ID loaded: {APP_ID}")

# Load Redirect URI
REDIRECT_URI = os.getenv("META_REDIRECT_URI") or "http://localhost:8000/auth/instagram/callback"

# Scopes to request from Instagram
SCOPES = "instagram_basic,pages_show_list"

# --- LOGIN URL ---
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


# --- CALLBACK HANDLER ---
@router.get("/auth/instagram/callback")
async def instagram_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' in callback URL")

    app_secret = os.getenv("META_APP_SECRET")

    # Exchange code for access token
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "client_id": APP_ID,
        "client_secret": app_secret,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.get(token_url, params=params)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to get access token: {token_res.text}")
        token_data = token_res.json()

        # Fetch user info
        user_info_url = "https://graph.facebook.com/v19.0/me"
        user_params = {
            "fields": "id,name",
            "access_token": token_data["access_token"],
        }
        user_res = await client.get(user_info_url, params=user_params)
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to get user info: {user_res.text}")

        return {
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type"),
            "user": user_res.json(),
        }

