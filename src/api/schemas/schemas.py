from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="<user's question>")
    thread_id: Optional[str] = Field(None, description="The ID of the thread to continue the conversation "
    "in, if applicable")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="<agent's generated answer>")
    thread_id: str = Field(..., description="The ID of the thread that the response belongs to")
    sources: List[str] = Field(default=[], description="Sources that the chatbot used to generate the response")
