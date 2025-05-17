from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ChatRequest
from app.services.rag import RAGService
from app.core.security import validate_token
from app.db.mongodb import db

router = APIRouter()
rag_service = RAGService()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, user_data=Depends(validate_token)):
    """Chat endpoint for RAG-based college assistant"""
    # Get user search history
    collection = db.db.user_searches
    user_search = await collection.find_one({"user_id": request.user_id})
    
    user_exams = None
    user_ranks = None
    
    if user_search:
        user_exams = user_search.get("exams", [])
        user_ranks = user_search.get("ranks", {})
    
    # Get last user message
    user_message = ""
    for message in reversed(request.messages):
        if message.role == "user":
            user_message = message.content
            break
    
    # Get response from RAG
    response = await rag_service.query_rag(user_message, user_exams, user_ranks)
    
    # Save chat history
    collection = db.db.chat_history
    await collection.insert_one({
        "user_id": request.user_id,
        "message": user_message,
        "response": response,
        "timestamp": datetime.now()
    })
    
    return {"response": response}