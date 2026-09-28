from app.database import get_db
from app.models import User
from app.services.openai_llm_service import generate_answer
from app.services.retrieval_service import find_relevant_chunks
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.schemas.chat import AskRequest, AskResponse

router = APIRouter(prefix="/chat", tags=["chat"])
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)



@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = db_dependency, user: User = current_user_dependency):
    chunks = find_relevant_chunks(db, user_id=user.id, question=payload.question, top_k=5)
    answer, citations = generate_answer(question=payload.question, chunks=chunks)
    return AskResponse(answer=answer, citations=citations)
