from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_pipeline import answer_query

router = APIRouter()

class Query(BaseModel):
    question: str

@router.post("/chat")
def chat(q: Query):
    try:
        answer = answer_query(q.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"answer": answer}
