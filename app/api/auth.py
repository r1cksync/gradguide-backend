from fastapi import APIRouter, Depends, HTTPException
from app.core.security import validate_token

router = APIRouter()

@router.get("/verify")
async def verify_token(user_data=Depends(validate_token)):
    """Verify JWT token from Clerk"""
    return {"status": "success", "user_id": user_data["id"]}