from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import FilterRequest, UserSearch
from app.services.rag import RAGService
from app.core.security import validate_token
from app.db.mongodb import db
from datetime import datetime

router = APIRouter()
rag_service = RAGService()

@router.post("/filter")
async def filter_colleges(request: FilterRequest, user_data=Depends(validate_token)):
    """Filter colleges based on exams and ranks"""
    # Save user search
    collection = db.db.user_searches
    user_id = user_data["id"]
    
    user_search = UserSearch(
        user_id=user_id,
        exams=request.exams,
        ranks=request.ranks
    )
    
    # Update or insert user search
    await collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "exams": request.exams,
            "ranks": request.ranks,
            "last_updated": datetime.now()
        }},
        upsert=True
    )
    
    # Get filtered colleges
    results = await rag_service.filter_colleges(request.exams, request.ranks)
    
    return {"results": results}