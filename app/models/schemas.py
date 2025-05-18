from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class CollegeEntry(BaseModel):
    exam: str
    college: str
    branch: str
    cutoff_rank: int
    average_placement: Optional[int] = None
    median_placement: Optional[int] = None
    highest_placement: Optional[int] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
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

class FilterRequest(BaseModel):
    exams: List[str]
    ranks: Dict[str, int]
    min_average_placement: Optional[int] = None
    min_median_placement: Optional[int] = None
    min_highest_placement: Optional[int] = None