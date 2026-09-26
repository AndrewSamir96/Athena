from app.models import Note, NoteChunk
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.app.services.llm_service import embed_texts


def extract_text(file: UploadFile) -> str:
    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return file.file.read().decode("utf-8")


def ingest_note(db: Session, note: Note, file: UploadFile) -> None:
    try:
        note.status = "processing"
        db.commit()

        text = extract_text(file)
        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = splitter.split_text(text)

        # Batch the embedding calls instead of one request per chunk.
        vectors = embed_texts(chunks)

        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            db.add(NoteChunk(note_id=note.id, chunk_index=index, content=content, embedding=vector))

        note.status = "ready"
        db.commit()
    except Exception:
        note.status = "failed"
        db.commit()
        raise
