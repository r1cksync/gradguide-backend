from fastapi import APIRouter, Depends
from app.models.schemas import ChatRequest
from app.services.rag import RAGService
from app.core.security import validate_token
from app.db.mongodb import db
from datetime import datetime
import logging

router = APIRouter()
rag_service = RAGService(data_path="./data/college_data.xlsx")
logger = logging.getLogger("gradguide")

@router.post("/chat")
def chat_endpoint(request: ChatRequest, user_data=Depends(validate_token)):
    collection = db.db.user_searches
    user_search = collection.find_one({"user_id": request.user_id})
    
    user_exams = user_search.get("exams", []) if user_search else None
    user_ranks = user_search.get("ranks", {}) if user_search else None
    
    user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), "")
    response = rag_service.query_rag(user_message, user_exams, user_ranks)
    
    collection = db.db.chat_history
    collection.insert_one({
        "user_id": request.user_id,
        "message": user_message,
        "response": response,
        "timestamp": datetime.now()
    })
    
    return {"response": response}