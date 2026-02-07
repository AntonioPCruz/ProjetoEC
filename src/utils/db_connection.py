import os
import psycopg2
from pymongo import MongoClient
import chromadb


# --- Testes de Conexão ---
def test_sql():
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
