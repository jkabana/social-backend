from fastapi import APIRouter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print working directory and env variable value
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

# Redirect URI (should match exactly what's configured in Meta dashboard)
REDIRECT_URI = os.getenv("META_REDIRECT_URI") or "http://localhost:8000/auth/instagram/callback"

SCOPES = "instagram_basic,pages_show_list"

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

