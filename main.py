from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.simple_chatbot import SimpleChatbot
from app.db.mongodb import db
from app.api import filters
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

app = FastAPI(title="GradGuide API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gradguide")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://gradguide-frontend.onrender.com" , "https://gradguide-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simple_chatbot = SimpleChatbot()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_message: Optional[str]
    last_updated: datetime

class SessionsResponse(BaseModel):
    sessions: List[SessionInfo]

class MessagesResponse(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/api/chatbot/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.user_id or not request.session_id:
            logger.warning("Missing user_id or session_id")
            raise HTTPException(status_code=422, detail="user_id and session_id are required")

        history = list(db.db.chat_history.find(
            {"user_id": request.user_id, "session_id": request.session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("timestamp", 1).limit(5))

        query = request.messages[-1]["content"]
        logger.info(f"Received chat request: {request.dict()}, History: {history}")

        response = await simple_chatbot.query(query, request.user_id, request.session_id, history)
        logger.info("Chat response generated")

        user_message = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow()
        }
        assistant_message = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow()
        }
        db.db.chat_history.insert_many([user_message, assistant_message])

        db.db.chat_sessions.update_one(
            {"user_id": request.user_id, "session_id": request.session_id},
            {
                "$set": {
                    "last_message": query,
                    "last_updated": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.info(f"Stored chat messages and session metadata for user {request.user_id}, session {request.session_id}")

        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/chatbot/sessions/{user_id}", response_model=SessionsResponse)
async def get_sessions(user_id: str):
    try:
        sessions = list(db.db.chat_sessions.find(
            {"user_id": user_id},
            {"_id": 0, "session_id": 1, "created_at": 1, "last_message": 1, "last_updated": 1}
        ))
        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
        return SessionsResponse(sessions=sessions)
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/chatbot/messages/{user_id}/{session_id}", response_model=MessagesResponse)
async def get_session_messages(user_id: str, session_id: str):
    try:
        messages = list(db.db.chat_history.find(
            {"user_id": user_id, "session_id": session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("timestamp", 1))
        logger.info(f"Retrieved {len(messages)} messages for user {user_id}, session {session_id}")
        return MessagesResponse(messages=messages)
    except Exception as e:
        logger.error(f"Get session messages error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

app.include_router(filters.router, prefix="/api/filters")

@app.on_event("startup")
def startup_event():
    try:
        db.connect_to_database()
        db.db.chat_history.create_index([("user_id", 1), ("session_id", 1), ("timestamp", -1)])
        db.db.chat_sessions.create_index([("user_id", 1), ("session_id", 1)])
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

@app.on_event("shutdown")
def shutdown_event():
    db.close_database_connection()
    logger.info("MongoDB connection closed")

@app.get("/")
async def root():
    return {"message": "Welcome to GradGuide API", "status": "online"}

@app.get("/health")
def health_check():
    try:
        db.db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "data": "available",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}