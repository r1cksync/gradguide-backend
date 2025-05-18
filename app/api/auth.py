# from fastapi import APIRouter, Depends
# from app.core.security import validate_token

# router = APIRouter()

# @router.get("/verify")
# def verify_token(user_data=Depends(validate_token)):
#     return {"status": "success", "user_id": user_data["id"]}