from fastapi import APIRouter
from pydantic import BaseModel

from agents.mongo_tool import mongo_query
from agents.tool_selection_agent import select_tool
from api.rules import apply_rules
from rag.pipeline import rag_answer

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(req: ChatRequest):
    rule_response = apply_rules(req.message)
    if rule_response:
        return {"response": rule_response}

    decision = select_tool(req.message)
    tool = decision["tool"]

    if tool == "rag_answer":
        reply = rag_answer(req.message)
    elif tool == "both":
        # RAG part only for now; SQL will be added later
        reply = rag_answer(req.message)
    elif tool == "sql_query":
        reply = "[SQL tool not implemented yet]"
    elif tool == "mongo_query":
        reply = mongo_query(req.message)
    else:
        reply = "Desculpe, não consigo responder a essa pergunta."

    return {"response": reply, "tool_used": tool}
