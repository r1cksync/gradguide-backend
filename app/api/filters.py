from fastapi import APIRouter, Depends
from app.models.schemas import FilterRequest
from app.services.rag import RAGService
from app.core.security import validate_token
from app.db.mongodb import db
from datetime import datetime
import logging

router = APIRouter()
rag_service = RAGService(data_path="./data/college_data.xlsx")
logger = logging.getLogger("gradguide")

@router.post("/filter")
def filter_colleges(request: FilterRequest, user_data=Depends(validate_token)):
    collection = db.db.user_searches
    user_id = user_data["id"]
    
    collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "exams": request.exams,
            "ranks": request.ranks,
            "last_updated": datetime.now()
        }},
        upsert=True
    )
    
    results = rag_service.filter_colleges(request.exams, request.ranks)
    return {"results": results}