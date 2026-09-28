import uuid

from app.models import Note, NoteChunk
from app.services.ollama_llm_service import embed_texts
from sqlalchemy.orm import Session


def find_relevant_chunks(
    db: Session, user_id: uuid.UUID, question: str, top_k: int = 5
) -> list[NoteChunk]:
    print(
        f"[retrieval.find_relevant_chunks] user_id={user_id} question_length={len(question)} top_k={top_k}"
    )
    question_vector = embed_texts([question])[0]

    chunks = (
        db.query(NoteChunk)
        .join(Note, Note.id == NoteChunk.note_id)
        .filter(Note.user_id == user_id, Note.status == "ready")
        .order_by(NoteChunk.embedding.cosine_distance(question_vector))
        .limit(top_k)
        .all()
    )
    print(f"[retrieval.find_relevant_chunks] result_count={len(chunks)}")
    return chunks
