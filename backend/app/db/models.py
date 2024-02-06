"""
Pydantic Schemas for the API
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field,  HttpUrl
from beanie import Document, Indexed, Link
from llama_index.core.llms.types import MessageRole
from llama_index.chat_engine.types import ChatMode

class Thumbnail(BaseModel):
    url: HttpUrl  # URL of the thumbnail image
    width: int    # Width of the thumbnail image
    height: int   # Height of the thumbnail image

class Base(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation datetime")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update datetime")

class ChannelStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

class Channel(Document, BaseModel):
    id: Indexed(str) = Field(..., description='Unique YT channel id')
    title: str = Field(None, description="Title of the channel")
    description: Optional[str] = Field(None, description="Description of the channel")
    url: HttpUrl = Field(None, description="URL of the channel")
    thumbnails: Optional[List[Thumbnail]] = Field(None, description="Thumbnails of the channel")
    status: Optional[ChannelStatus] = Field(ChannelStatus.INACTIVE, description="Status of the channel")
    class Settings:
        name = "channels"

class TranscriptSegment(Base):
    text: str = Field(None, description="Transcript text") 
    start_ms: int = Field(None, description="Start time in ms of the transcript")
    end_ms: int = Field(None, description="End time in ms of the transcript")
    chapter: Optional[str] = Field(None, description="Chapter of the transcript")

class Video(Base):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(None, description="Title of the video")
    channel: Link[Channel] = Field(None, description="Channel of the video")
    duration: Optional[int] = Field(None, description="Duration of the video in seconds")
    transcript: List[TranscriptSegment] = Field(None, description="Transcript of the video")

class ChannelOnBoardingRequestStatus(Enum):
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    QUEUED = 'Queued'
    PROCESSING = 'Processing'
    FAILED = 'Failed'
    COMPLETED = 'Completed'

class ChannelOnBoardingRequest(Document, BaseModel):
    channel_id: str = Field(..., description="Unique YT channel id")
    requested_by: Optional[str] = Field(None, description="Requested by user id")
    status: ChannelOnBoardingRequestStatus = Field(ChannelOnBoardingRequestStatus.PENDING, description="Status of the request")
    class Settings:
        name = "onboarding_requests"

# Copy of LlamaIndex's ChatMessage because llamaindex uses pydantic v1 basemodel
class ChatMessage(BaseModel):
    """Chat message."""

    role: MessageRole = MessageRole.USER
    content: Optional[str] = ""
    additional_kwargs: dict = Field(default_factory=dict)

class Chat(Document, BaseModel):
    vector_index_name: str = Field(..., description="Name of the vector index")
    vector_namespace: str = Field(..., description="Namespace of the vector index")
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Chat history of the chat")
    chat_mode: ChatMode = Field(ChatMode.CONDENSE_PLUS_CONTEXT, description="Chat mode of the chat")
    chat_kwargs: dict = Field(default_factory=dict, description="Additional chat kwargs")
    is_expired: Optional[bool] = Field(False, description="True if the chat has expired")

    class Settings:
        name = "chats"
    
