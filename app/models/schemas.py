from pydantic import BaseModel
from typing import List, Dict

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

class FilterRequest(BaseModel):
    exams: List[str]
    ranks: Dict[str, int]