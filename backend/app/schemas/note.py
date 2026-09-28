import uuid
from datetime import datetime

from pydantic import BaseModel


class NoteResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True 
