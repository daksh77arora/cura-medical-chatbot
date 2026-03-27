from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import bleach

class Source(BaseModel):
    page: int
    content_preview: str  # First 150 chars
    source_file: str
    relevance_score: float

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def sanitize(cls, v: str) -> str:
        # Strip HTML/script injection
        return bleach.clean(v.strip())

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    session_id: Optional[str] = None
    is_emergency: bool = False
    disclaimer: str = "This is for educational purposes only. Not a substitute for professional medical advice."
