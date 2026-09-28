from app.models import Note, NoteChunk
from app.services.ollama_llm_service import embed_texts
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlalchemy.orm import Session


def extract_text(file: UploadFile) -> str:
    print(f"[ingestion.extract_text] filename={file.filename}")
    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(file.file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        print(
            f"[ingestion.extract_text] pdf_pages={len(reader.pages)} text_length={len(text)}"
        )
        return text
    text = file.file.read().decode("utf-8")
    print(f"[ingestion.extract_text] text_length={len(text)}")
    return text


def ingest_note(db: Session, note: Note, file: UploadFile) -> None:
    print(f"[ingestion.ingest_note] note_id={note.id} filename={file.filename}")
    try:
        note.status = "processing"
        db.commit()

        text = extract_text(file)
        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = splitter.split_text(text)
        print(f"[ingestion.ingest_note] chunks={len(chunks)}")

        # Batch the embedding calls instead of one request per chunk.
        vectors = embed_texts(chunks)

        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            db.add(
                NoteChunk(
                    note_id=note.id,
                    chunk_index=index,
                    content=content,
                    embedding=vector,
                )
            )

        note.status = "ready"
        db.commit()
        print(f"[ingestion.ingest_note] ready note_id={note.id}")
    except Exception:
        db.rollback()
        note.status = "failed"
        db.commit()
        print(f"[ingestion.ingest_note] failed note_id={note.id}")
        raise
