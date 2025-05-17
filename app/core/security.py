from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.core.config import settings

security = HTTPBearer()

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate Clerk JWT token"""
    token = credentials.credentials
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.CLERK_API_URL}/json",
            headers={
                "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                "Clerk-Token": token
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = response.json()
        return user_data