from typing import Any, Dict, List
import re

from utils.db_connection import get_db_connection


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE"
]


def _is_safe_query(query: str) -> bool:
    """
    Verifica se a query é segura para execução.

    Apenas são permitidas queries SELECT.
    """
    query_upper = query.upper().strip()

    if not query_upper.startswith("SELECT"):
        return False

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", query_upper):
            return False

    return True


def sql_query_tool(query: str) -> Dict[str, Any]:
    """
    Exemplo
    -------
    Query:
        SELECT name FROM diseases;

    Ou:
        SELECT d.name, s.name
        FROM diseases d
        JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
        JOIN symptoms s ON s.symptom_id = ds.symptom_id
        WHERE s.name = 'Fever';
    """

    if not _is_safe_query(query):
        raise ValueError(
            "Só se permitem queries SELECT."
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        results: List[Dict[str, Any]] = [
            dict(zip(columns, row)) for row in rows
        ]

        return {
            "columns": columns,
            "rows": results
        }

    finally:
        cursor.close()
        conn.close()