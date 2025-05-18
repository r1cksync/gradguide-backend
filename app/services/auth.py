# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer
# import httpx
# from app.core.config import settings
# import logging

# logger = logging.getLogger("gradguide")
# security = HTTPBearer()

# async def verify_clerk_token(token: str = Depends(security)):
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{settings.CLERK_API_URL}/users",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
#             response.raise_for_status()
#             user_data = response.json()
#             user_id = user_data.get("id")
#             if not user_id:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Invalid Clerk token"
#                 )
#             logger.info(f"Verified user: {user_id}")
#             return {"user_id": user_id}
#     except Exception as e:
#         logger.error(f"Clerk verification error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Token verification failed: {str(e)}"
#         )