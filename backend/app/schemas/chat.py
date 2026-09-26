import uuid

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    note_id: uuid.UUID
    chunk_id: uuid.UUID
    title: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
