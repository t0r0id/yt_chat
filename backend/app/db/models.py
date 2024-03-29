"""
Pydantic Schemas for the API
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field,  HttpUrl, model_validator
from beanie import Document, Indexed
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

    class Config:
        validate_assignment = True

    def update_fields(self, **kwargs):
        for field_name, field_value in kwargs.items():
            setattr(self, field_name, field_value)
        self.updated_at = datetime.now()

class ChannelStatusEnum(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class Channel(Document, Base):
    id: Indexed(str) = Field(..., description='Unique YT channel id')
    title: str = Field(None, description="Title of the channel")
    description: Optional[str] = Field(None, description="Description of the channel")
    url: HttpUrl = Field(None, description="URL of the channel")
    thumbnails: Optional[List[Thumbnail]] = Field(None, description="Thumbnails of the channel")
    status: Optional[ChannelStatusEnum] = Field(ChannelStatusEnum.INACTIVE, description="Status of the channel")
    class Settings:
        name = "channels"

class TranscriptSegment(BaseModel):
    text: str = Field(None, description="Transcript text") 
    start_ms: int = Field(None, description="Start time in ms of the transcript")
    end_ms: int = Field(None, description="End time in ms of the transcript")
    chapter: Optional[str] = Field(None, description="Chapter of the transcript")

class Video(BaseModel):
    id: str = Field(..., description="Unique identifier")
    title: str = Field(None, description="Title of the video")
    channel: Channel = Field(None, description="Channel of the video")
    duration: Optional[int] = Field(None, description="Duration of the video in seconds")
    transcript: List[TranscriptSegment] = Field(None, description="Transcript of the video")

class ChannelOnBoardingRequestStatusEnum(Enum):
    PENDING = 'pending'
    REJECTED = 'rejected'
    QUEUED = 'queued'
    PROCESSING = 'processing'
    FAILED = 'failed'
    COMPLETED = 'completed'
    AUTOCOMPLETED = 'autocompleted'

class ChannelOnBoardingRequest(Document, Base):
    channel_id: str = Field(..., description="Unique YT channel id")
    requested_by: Optional[str] = Field(None, description="Requested by user id")
    status: ChannelOnBoardingRequestStatusEnum = Field(ChannelOnBoardingRequestStatusEnum.PENDING, description="Status of the request")
    class Settings:
        name = "onboarding_requests"


class ChatResponseStatusEnum(Enum):
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'
    REJECTED = 'rejected'
    REGENRATED = 'regenerated'
    FAILED = 'failed'

# Copy of LlamaIndex's ChatMessage because llamaindex uses pydantic v1 basemodel
class ChatResponse(Base):
    """Chat message."""
    role: MessageRole = Field(MessageRole.USER, description="Role of the message")
    content: Optional[str] = Field("", description="Content of the message")
    additional_kwargs: dict = Field(default_factory=dict)
    status: ChatResponseStatusEnum = Field(ChatResponseStatusEnum.COMPLETED, description="Status of the message")
    status_reason: Optional[str] = Field(None, description="Status reason of the message")

class Chat(Document, Base):
    vector_index_name: str = Field(..., description="Name of the vector index")
    vector_namespace: str = Field(..., description="Namespace of the vector index")
    chat_history: Optional[List[ChatResponse]] = Field(default_factory=list, description="Chat history of the chat")
    chat_mode: ChatMode = Field(ChatMode.CONDENSE_PLUS_CONTEXT, description="Chat mode of the chat")
    chat_kwargs: dict = Field(default_factory=dict, description="Additional chat kwargs")
    is_expired: Optional[bool] = Field(False, description="True if the chat has expired")

    class Settings:
        name = "chats"

class ActiveChatSessionMap(Document, Base):
    user_session_id: Indexed(str) = Field(..., description="User or session id")
    channel_id: Indexed(str) = Field(..., description="Channel id")
    active_chat_id: str = Field(..., description="Active chat id")

    class Settings:
        name = "active_chat_sessions"

class User(Document, Base):
    id: Indexed(str) = Field(..., description="User or session id")
    channels: Set[str] = Field(default_factory=set, description="List of added channels")

    class Settings:
        name = "users"
