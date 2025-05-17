from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class CollegeEntry(BaseModel):
    exam: str
    college: str
    branch: str
    cutoff_rank: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: str

class UserSearch(BaseModel):
    user_id: str
    exams: List[str]
    ranks: Dict[str, int]

class FilterRequest(BaseModel):
    exams: List[str]
    ranks: Dict[str, int]