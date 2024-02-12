from json import JSONEncoder
from uuid import UUID
from datetime import datetime
from app.db.models import ChatResponseStatusEnum

class UUIDEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, ChatResponseStatusEnum):
            return ChatResponseStatusEnum(obj).name
        return super().default(obj)