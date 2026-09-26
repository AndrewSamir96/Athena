import uuid

from sqlalchemy.orm import Session

from app.models import Note, NoteChunk
from backend.app.services.llm_service import embed_texts


def find_relevant_chunks(db: Session, user_id: uuid.UUID, question: str, top_k: int = 5) -> list[NoteChunk]:
    question_vector = embed_texts([question])[0]

    return (
        db.query(NoteChunk)
        .join(Note, Note.id == NoteChunk.note_id)
        .filter(Note.user_id == user_id, Note.status == "ready")
        .order_by(NoteChunk.embedding.cosine_distance(question_vector))
        .limit(top_k)
        .all()
    )
