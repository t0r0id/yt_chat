"""
Pydantic Schemas for the API
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field,  HttpUrl
from beanie import Document, Indexed, Link
import pymongo


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

class Channel(Document, Base):
    id: Indexed(str) = Field(..., description='Unique YT channel id')
    title: str = Field(None, description="Title of the channel")
    description: Optional[str] = Field(None, description="Description of the channel")
    url: HttpUrl = Field(None, description="URL of the channel")
    thumbnails: Optional[List[Thumbnail]] = Field(None, description="Thumbnails of the channel")
    channel_status: ChannelStatus = Field(ChannelStatus.INACTIVE, description="Status of the channel")
    class Settings:
        name = "channels"

class TranscriptSegment(BaseModel):
    text: str = Field(None, description="Transcript text") 
    start_ms: int = Field(None, description="Start time in ms of the transcript")
    end_ms: int = Field(None, description="End time in ms of the transcript")
    chapter: Optional[str] = Field(None, description="Chapter of the transcript")

class Video(Document, Base):
    id: Indexed(str) = Field(..., description="Unique identifier")
    title: str = Field(None, description="Title of the video")
    channel: Link[Channel] = Field(None, description="Channel of the video")
    transcript: List[TranscriptSegment] = Field(None, description="Transcript of the video")
    class Settings:
        name = "videos"

class ChannelOnBoardingRequestStatus(Enum):
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    QUEUED = 'Queued'
    PROCESSING = 'Processing'
    FAILED = 'Failed'
    COMPLETED = 'Completed'

    
class ChannelOnBoardingRequest(Document, Base):
    channel_id: str = Field(..., description="Unique YT channel id")
    requested_by: Optional[str] = Field(None, description="Requested by user id")
    status: ChannelOnBoardingRequestStatus = Field(ChannelOnBoardingRequestStatus.PENDING, description="Status of the request")
    class Settings:
        name = "onboarding_requests"
    
