import os
import re
from urllib.parse import quote_plus

from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama

FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
]


def _is_safe_query(query: str) -> bool:
    query_upper = query.upper().strip()

    if not query_upper.startswith("SELECT"):
        return False

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", query_upper):
            return False

    return True


def _extract_sql(raw_output: str) -> str:
    """Extract SQL from LangChain output that may include helper tags/code fences."""
    text = raw_output.strip()

    code_block = re.search(r"```sql\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if code_block:
        return code_block.group(1).strip()

    labelled = re.search(r"SQLQuery\s*:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
    if labelled:
        text = labelled.group(1).strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""

    candidate = " ".join(lines)
    candidate = candidate.rstrip(";")
    return candidate


def _build_postgres_uri() -> str:
    host = os.getenv("SQL_HOST", "localhost")
    port = os.getenv("SQL_PORT", "5432")
    database = os.getenv("SQL_DB", "")
    user = quote_plus(os.getenv("SQL_USER", ""))
    password = quote_plus(os.getenv("SQL_PASSWORD", ""))

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def sql_query(user_question: str) -> str:
    """Generate and run a safe SQL query from a natural-language question."""
    db = SQLDatabase.from_uri(_build_postgres_uri())

    llm = ChatOllama(
        model=os.getenv("SQL_LLM_MODEL", "gemma3:4b"),
        base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434"),
        temperature=0,
    )

    chain = create_sql_query_chain(llm, db)
    raw_sql = chain.invoke({"question": user_question})
    generated_sql = _extract_sql(raw_sql)

    if not generated_sql or not _is_safe_query(generated_sql):
        return "Não consegui gerar uma query SQL segura (apenas SELECT é permitido)."

    if "LIMIT" not in generated_sql.upper():
        generated_sql = f"{generated_sql} LIMIT 100"

    result = db.run_no_throw(generated_sql)

    if isinstance(result, str) and result.strip().startswith("Error"):
        return f"A query SQL falhou: {result}"

    if result in ("", "[]", [], None):
        return "Não encontrei resultados para essa pergunta na base de dados."

    explain_prompt = (
        "Responde em português europeu de forma breve e clara. "
        "Com base na pergunta e nos resultados SQL, dá a resposta final ao utilizador.\n\n"
        f"Pergunta: {user_question}\n"
        f"SQL: {generated_sql}\n"
        f"Resultados: {result}"
    )
    final = llm.invoke(explain_prompt)
    return final.content if hasattr(final, "content") else str(final)