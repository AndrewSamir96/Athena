from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.chat import AskRequest, AskResponse
from app.services.ollama_llm_service import generate_answer
from app.services.retrieval_service import find_relevant_chunks
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["chat"])
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    db: Session = db_dependency,
    user: User = current_user_dependency,
):
    print(f"[chat.ask] user_id={user.id} question_length={len(payload.question)}")
    chunks = find_relevant_chunks(
        db, user_id=user.id, question=payload.question, top_k=5
    )
    print(f"[chat.ask] retrieved_chunks={len(chunks)}")
    answer, citations = generate_answer(question=payload.question, chunks=chunks)
    print(f"[chat.ask] generated_answer citations={len(citations)}")
    return AskResponse(answer=answer, citations=citations)
