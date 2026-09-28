import uuid

from app.database import get_db
from app.models import Note, User
from app.services.ingestion_service import ingest_note
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.schemas.note import NoteResponse

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
file_dependency = File(...)

router = APIRouter(prefix="/notes", tags=["notes"])



@router.get("", response_model=list[NoteResponse])
def list_notes(db: Session = db_dependency, user: User = current_user_dependency):
    return db.query(Note).filter(Note.user_id == user.id).all()


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: uuid.UUID, db: Session = db_dependency, user: User = current_user_dependency):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.post("/upload", response_model=NoteResponse)
def upload_note(
    file: UploadFile = file_dependency,
    db: Session = db_dependency,
    user: User = current_user_dependency,
):
    note = Note(user_id=user.id, title=file.filename, status="pending")
    db.add(note)
    db.commit()
    db.refresh(note)

    # Kept synchronous for simplicity — see the guide's note on BackgroundTasks as a later improvement.
    ingest_note(db, note, file)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: uuid.UUID, db: Session = db_dependency, user: User = current_user_dependency):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)  # cascades to note_chunks via the ON DELETE CASCADE relationship
    db.commit()
