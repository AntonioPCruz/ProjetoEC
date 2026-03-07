import os
from pathlib import Path

import ollama
import yaml

LLM_MODEL = "gemma3:4b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


def load_prompt() -> str:
    """Load system prompt from YAML file."""
    prompt_path = Path(__file__).parent / "prompt.yaml"
    with open(prompt_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]


def select_tool(user_question: str) -> dict:
    """Select appropriate tool based on user question."""
    system_prompt = load_prompt()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
    ]

    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(model=LLM_MODEL, messages=messages)
    answer = response["message"]["content"].strip().upper()

    # Parse response
    if "BOTH" in answer:
        return {"tool": "both", "query": user_question}
    elif "RAG" in answer:
        return {"tool": "rag_answer", "query": user_question}
    elif "SQL" in answer:
        return {"tool": "sql_query", "query": user_question}
    else:
        return {"tool": None, "query": user_question}
