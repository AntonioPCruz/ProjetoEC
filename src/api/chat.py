from fastapi import APIRouter
from pydantic import BaseModel

from rag.pipeline import rag_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(req: ChatRequest):
    reply = rag_answer(req.message)
    return {"response": reply}
