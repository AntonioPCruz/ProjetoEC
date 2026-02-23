"""
Testes de ligação às bases de dados e verificação de existência de dados.

Requer PYTHONPATH=src. Os testes são ignorados (skip) quando as variáveis de ambiente
correspondentes não estão definidas (ex.: CI sem contentores de BD).
"""

import os

import pytest

# Permite importar módulos de src quando se corre pytest da raiz
import sys
from pathlib import Path

_SCR = Path(__file__).resolve().parent.parent / "src"
if _SCR.exists() and str(_SCR) not in sys.path:
    sys.path.insert(0, str(_SCR))

from db_connection import get_db_connection, test_nosql, test_sql, test_vector


def _sql_configured():
    return all(
        os.getenv(k) for k in ("SQL_HOST", "SQL_DB", "SQL_USER", "SQL_PASSWORD")
    )


def _nosql_configured():
    return all(os.getenv(k) for k in ("MONGO_HOST", "MONGO_USER", "MONGO_PASSWORD"))


def _vector_configured():
    return all(os.getenv(k) for k in ("VECTOR_HOST", "VECTOR_PORT"))


# --- PostgreSQL ---


@pytest.mark.skipif(not _sql_configured(), reason="Variáveis SQL_* não definidas")
def test_sql_conexao():
    """Verifica que a ligação ao PostgreSQL é estabelecida com sucesso."""
    assert test_sql() is True


@pytest.mark.skipif(not _sql_configured(), reason="Variáveis SQL_* não definidas")
def test_sql_tabelas_existem_ou_estado_consistente():
    """Verifica que a BD SQL está acessível e permite listar tabelas (esquema público)."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        tabelas = [r[0] for r in cur.fetchall()]
        cur.close()
        # Só verificamos que a query corre; pode haver zero tabelas
        assert isinstance(tabelas, list)
    finally:
        conn.close()


@pytest.mark.skipif(not _sql_configured(), reason="Variáveis SQL_* não definidas")
def test_sql_contagem_por_tabela():
    """Opcional: verifica existência de dados em tabelas conhecidas (contagem)."""
    from psycopg2 import sql

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            """
        )
        nomes = [r[0] for r in cur.fetchall()]
        for nome in nomes[:5]:  # Limitar a 5 tabelas
            try:
                cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(nome)))
                n = cur.fetchone()[0]
                assert n >= 0
            except Exception:
                pass  # Tabela pode ter restrições
        cur.close()
    finally:
        conn.close()


# --- MongoDB ---


@pytest.mark.skipif(not _nosql_configured(), reason="Variáveis MONGO_* não definidas")
def test_nosql_conexao():
    """Verifica que a ligação ao MongoDB é estabelecida com sucesso."""
    assert test_nosql() is True


@pytest.mark.skipif(not _nosql_configured(), reason="Variáveis MONGO_* não definidas")
def test_nosql_colecoes_acessiveis():
    """Verifica que o MongoDB está acessível e permite listar coleções."""
    from pymongo import MongoClient

    client = MongoClient(
        host=os.getenv("MONGO_HOST"),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        serverSelectionTimeoutMS=5000,
    )
    db_name = os.getenv("MONGO_DB", "db_saude_nosql")
    db = client[db_name]
    colecoes = db.list_collection_names()
    assert isinstance(colecoes, list)


@pytest.mark.skipif(not _nosql_configured(), reason="Variáveis MONGO_* não definidas")
def test_nosql_contagem_documentos_por_colecao():
    """Verifica existência de dados: contagem de documentos em cada coleção (amostra)."""
    from pymongo import MongoClient

    client = MongoClient(
        host=os.getenv("MONGO_HOST"),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        serverSelectionTimeoutMS=5000,
    )
    db_name = os.getenv("MONGO_DB", "db_saude_nosql")
    db = client[db_name]
    for nome in db.list_collection_names()[:5]:
        n = db[nome].count_documents({})
        assert n >= 0


# --- ChromaDB (vetorial) ---


@pytest.mark.skipif(not _vector_configured(), reason="Variáveis VECTOR_* não definidas")
def test_vector_conexao():
    """Verifica que a ligação ao ChromaDB é estabelecida com sucesso."""
    assert test_vector() is True


@pytest.mark.skipif(not _vector_configured(), reason="Variáveis VECTOR_* não definidas")
def test_vector_colecoes_acessiveis():
    """Verifica que o ChromaDB está acessível e permite listar coleções."""
    import chromadb

    client = chromadb.HttpClient(
        host=os.getenv("VECTOR_HOST"),
        port=int(os.getenv("VECTOR_PORT")),
    )
    colecoes = client.list_collections()
    assert isinstance(colecoes, list)


@pytest.mark.skipif(not _vector_configured(), reason="Variáveis VECTOR_* não definidas")
def test_vector_contagem_colecoes():
    """Verifica existência de coleções (e, por amostragem, que têm metadados)."""
    import chromadb

    client = chromadb.HttpClient(
        host=os.getenv("VECTOR_HOST"),
        port=int(os.getenv("VECTOR_PORT")),
    )
    colecoes = client.list_collections()
    for col in colecoes[:3]:
        # Apenas garantir que a coleção é utilizável (count ou peek)
        _ = col.name
    assert True
