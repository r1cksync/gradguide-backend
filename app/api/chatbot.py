from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.services.rag import RAGService
import logging

router = APIRouter()
logger = logging.getLogger("gradguide")

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.dict()}")
        if not request.messages or not request.messages[-1].content:
            logger.warning("Invalid message content")
            raise HTTPException(status_code=422, detail="No valid message content provided")
        rag_service = RAGService()
        response = await rag_service.query_rag(
            query=request.messages[-1].content,
            user_exams=None,
            user_ranks=None,
            user_id=request.user_id
        )
        logger.info("Chat response generated")
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")