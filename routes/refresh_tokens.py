from fastapi import APIRouter, Request, HTTPException
from supabase import create_client, Client
import httpx, os
from datetime import datetime, timedelta, timezone

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Secure: only use on the server side
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/refresh-tokens")
async def refresh_instagram_tokens(request: Request):
    # Optional: Secure this route with a secret header
    cron_secret = os.getenv("CRON_SECRET")
    request_secret = request.headers.get("X-CRON-SECRET")

    if cron_secret and request_secret != cron_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.now(timezone.utc)
    soon = now + timedelta(days=7)

    # Fetch accounts with tokens expiring within the next 7 days
    res = supabase.table("instagram_accounts").select("*").lte("expires_at", soon.isoformat()).execute()
    accounts = res.data

    if not accounts:
        return {"message": "No tokens need refreshing"}

    refreshed = []

    async with httpx.AsyncClient() as client:
        for account in accounts:
            old_token = account["access_token"]
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": old_token
            }
            url = "https://graph.instagram.com/refresh_access_token"

            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                new_data = resp.json()
                new_token = new_data["access_token"]
                expires_in = new_data["expires_in"]

                # Calculate new expiration time
                expires_at = (now + timedelta(seconds=expires_in)).isoformat()

                # Update Supabase
                supabase.table("instagram_accounts").update({
                    "access_token": new_token,
                    "expires_at": expires_at,
                    "last_refreshed_at": now.isoformat()
                }).eq("id", account["id"]).execute()

                refreshed.append(account["id"])

            except Exception as e:
                print(f"Failed to refresh token for account {account['id']}: {e}")

    return {"refreshed_accounts": refreshed}

