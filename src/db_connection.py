"""Funções de ligação e verificação de saúde para bases de dados SQL, NoSQL e vetoriais."""

import os

import chromadb
import psycopg2
from pymongo import MongoClient


# --- Verificações de saúde das ligações ---


def test_sql():
    """Verifica a ligação ao PostgreSQL. Devolve True em caso de sucesso."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("SQL_HOST"),
            database=os.getenv("SQL_DB"),
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASSWORD"),
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        return False


def test_nosql():
    """Verifica a ligação ao MongoDB. Devolve True se o ping for bem‑sucedido."""
    try:
        client = MongoClient(
            host=os.getenv("MONGO_HOST"),
            username=os.getenv("MONGO_USER"),
            password=os.getenv("MONGO_PASSWORD"),
            serverSelectionTimeoutMS=3000,
        )
        client.admin.command("ping")
        return True
    except Exception:
        return False


def test_vector():
    """Verifica a ligação ao ChromaDB (base vetorial). Devolve True se o heartbeat tiver sucesso."""
    try:
        client = chromadb.HttpClient(
            host=os.getenv("VECTOR_HOST"), port=int(os.getenv("VECTOR_PORT"))
        )
        client.heartbeat()
        return True
    except Exception:
        return False


# --- Fábricas de ligações ---


def get_db_connection():
    """Devolve uma ligação à base de dados PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("SQL_HOST"),
        database=os.getenv("SQL_DB"),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASSWORD"),
    )
