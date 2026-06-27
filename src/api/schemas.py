
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="The message to send to the chatbot")
    thread_id: Optional[str] = Field(None, description="The ID of the thread to continue the conversation "
    "in, if applicable")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The chatbot's response to the message")
    thread_id: str = Field(..., description="The ID of the thread that the response belongs to")
    sources: List[str] = Field(default=[], description="Sources that the chatbot used to generate the response")
