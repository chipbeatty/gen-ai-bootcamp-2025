from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = Field(default="llama2:7b")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    stream: bool = Field(default=False)

class ChatResponse(BaseModel):
    id: str
    model: str
    created: int
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class AudioRequest(BaseModel):
    audio_file: str
    model: str = Field(default="whisper:base")

class AudioSegment(BaseModel):
    text: str = Field(description="The transcribed text for this segment")
    type: str = Field(description="Type of segment (speech or pause)", default="speech")
    start_time: float = Field(description="Start time in seconds", ge=0)
    end_time: float = Field(description="End time in seconds", ge=0)

class AudioResponse(BaseModel):
    text: str = Field(description="The complete transcribed text")
    segments: List[AudioSegment] = Field(
        description="List of audio segments with timing information",
        default_factory=list
    )
