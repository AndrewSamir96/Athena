from app.database import get_db
from app.models import User
from app.services.llm_service import generate_answer
from app.services.retrieval_service import find_relevant_chunks
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.deps import get_current_user
from backend.app.schemas.chat import AskRequest, AskResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chunks = find_relevant_chunks(db, user_id=user.id, question=payload.question, top_k=5)
    answer, citations = generate_answer(question=payload.question, chunks=chunks)
    return AskResponse(answer=answer, citations=citations)
