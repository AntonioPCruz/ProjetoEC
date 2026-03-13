import os

import chromadb
import psycopg2
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


# --- Testes de Conexão ---
def test_sql():
    try:
        host = os.getenv("SQL_HOST") or "localhost"
        port = os.getenv("SQL_PORT") or "5432"
        conn = psycopg2.connect(
            host=host,
            port=port,
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
    try:
        client = chromadb.HttpClient(
            host=os.getenv("VECTOR_HOST"), port=int(os.getenv("VECTOR_PORT"))
        )
        client.heartbeat()
        return True
    except Exception:
        return False


# --- Funções de Conexão ---
def get_db_connection():
    """Retorna uma conexão com a base de dados PostgreSQL"""
    host = os.getenv("SQL_HOST") or "localhost"
    port = os.getenv("SQL_PORT") or "5432"
    return psycopg2.connect(
        host=host,
        port=port,
        database=os.getenv("SQL_DB"),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASSWORD"),
    )
