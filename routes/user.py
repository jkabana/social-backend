from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer
from auth import verify_token

security = HTTPBearer()

router = APIRouter()

@router.get("/me", tags=["User"])
def get_current_user(
    token_data: dict = Depends(verify_token),
    _=Security(security)  # 🔒 This tells FastAPI this route requires Bearer auth
):
    return {"user_id": token_data["user_id"]}

