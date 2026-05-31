import operator
from uuid import uuid4
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    query: str
    proposal_text: str  # 기획서 원문
    history: list[dict] # 지금까지의 핑퐁 대화 기록
    final_answer: str
    domain: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    proposal_text: str = Field(default="", description="기획서 원문")
    history: list[dict] = Field(default_factory=list, description="이전 대화 기록")
    thread_id: str = Field(default_factory=lambda: str(uuid4()))

class ChatResponse(BaseModel):
    answer: str
    domain: str = ""

class StreamEvent(BaseModel):
    event: str = "message"
    node: str = ""
    data: str = ""