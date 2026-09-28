import uuid

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Note, User
from app.schemas.note import NoteResponse
from app.services.ingestion_service import ingest_note
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
file_dependency = File(...)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
def list_notes(db: Session = db_dependency, user: User = current_user_dependency):
    print(f"[notes.list] user_id={user.id}")
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    print(f"[notes.list] count={len(notes)}")
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: uuid.UUID,
    db: Session = db_dependency,
    user: User = current_user_dependency,
):
    print(f"[notes.get] user_id={user.id} note_id={note_id}")
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        print("[notes.get] note not found")
        raise HTTPException(status_code=404, detail="Note not found")
    print(f"[notes.get] found status={note.status}")
    return note


@router.post("/upload", response_model=NoteResponse)
def upload_note(
    file: UploadFile = file_dependency,
    db: Session = db_dependency,
    user: User = current_user_dependency,
):
    print(f"[notes.upload] user_id={user.id} filename={file.filename}")
    note = Note(user_id=user.id, title=file.filename, status="pending")
    db.add(note)
    db.commit()
    db.refresh(note)

    ingest_note(db, note, file)
    print(f"[notes.upload] completed note_id={note.id} status={note.status}")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: uuid.UUID,
    db: Session = db_dependency,
    user: User = current_user_dependency,
):
    print(f"[notes.delete] user_id={user.id} note_id={note_id}")
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        print("[notes.delete] note not found")
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    print(f"[notes.delete] deleted note_id={note_id}")
