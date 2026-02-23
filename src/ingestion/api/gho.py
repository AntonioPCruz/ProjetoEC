"""
Ingestão da API GHO (Global Health Observatory).
Obtém indicadores, dimensões e valores de dimensão e guarda-os em MongoDB.
"""

import os
import sys

import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

load_dotenv()

GHO_BASE_URL = "https://ghoapi.azureedge.net/api"

# Collection names for GHO data
COLLECTION_INDICATORS = "gho_indicators"
COLLECTION_DIMENSIONS = "gho_dimensions"


def _mongo_config():
    """Devolve a configuração atual do MongoDB (palavra‑passe mascarada) para debugging."""
    return {
        "MONGO_HOST": os.getenv("MONGO_HOST", "localhost"),
        "MONGO_PORT": os.getenv("MONGO_PORT", "27017"),
        "MONGO_USER": os.getenv("MONGO_USER") or "(not set)",
        "MONGO_PASSWORD": "***" if os.getenv("MONGO_PASSWORD") else "(not set)",
        "MONGO_DB": os.getenv("MONGO_DB", "db_saude_nosql"),
    }


def get_mongo_db():
    """Devolve uma instância de base de dados MongoDB usando a configuração do ambiente."""
    client = MongoClient(
        host=os.getenv("MONGO_HOST", "localhost"),
        port=int(os.getenv("MONGO_PORT", "27017")),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        serverSelectionTimeoutMS=5000,
    )
    return client[os.getenv("MONGO_DB", "db_saude_nosql")]


def verify_mongo_connection(db=None) -> tuple[bool, str]:
    """
    Verifica a ligação ao MongoDB: faz ping ao servidor e lista coleções.
    Devolve (sucesso: bool, mensagem: str). Útil para diagnosticar problemas de ligação.
    """
    try:
        if db is None:
            db = get_mongo_db()
        # Força um round-trip ao servidor (ping)
        db.client.admin.command("ping")
        # Opcional: lista coleções para garantir que conseguimos ler da base de dados
        _ = list(db.list_collection_names())
        return True, "Ligação ao MongoDB OK (ping + list_collections bem‑sucedidos)."
    except ServerSelectionTimeoutError as e:
        return False, (
            f"Falha na ligação ao MongoDB (timeout): {e}. "
            "Verifica MONGO_HOST, MONGO_PORT, a rede e se o serviço MongoDB está a correr."
        )
    except OperationFailure as e:
        return False, (
            f"Falha de autenticação/comando no MongoDB: {e}. "
            "Verifica MONGO_USER e MONGO_PASSWORD (e se o utilizador existe na BD)."
        )
    except Exception as e:
        return False, f"Erro de ligação ao MongoDB: {type(e).__name__}: {e}"


def fetch_indicators() -> list[dict]:
    """Obtém todos os indicadores a partir da API GHO."""
    url = f"{GHO_BASE_URL}/Indicator"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("value", [])


def fetch_dimensions() -> list[dict]:
    """Obtém todas as dimensões a partir da API GHO."""
    url = f"{GHO_BASE_URL}/Dimension"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("value", [])


def fetch_dimension_values(dimension_code: str) -> list[dict]:
    """Obtém os valores de dimensão para um determinado código de dimensão."""
    url = f"{GHO_BASE_URL}/DIMENSION/{dimension_code}/DimensionValues"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("value", [])


def ingest_to_mongo(db=None, skip_connection_check: bool = False):
    """
    Obtém todos os dados GHO e guarda‑os em coleções MongoDB.
    Utiliza as coleções:
      - gho_indicators
      - gho_dimensions
      - uma coleção por conjunto de valores de dimensão, por exemplo:
          gho_country_dimension_values, gho_agegroup_dimension_values, ...

    Antes de inserir novos valores de dimensão, são apagadas todas as coleções
    existentes que correspondam ao padrão gho_*_dimension_values, para evitar dados obsoletos.

    Se skip_connection_check for False (predefinição), verifica primeiro a ligação à BD
    e termina em caso de falha.
    """
    if db is None:
        db = get_mongo_db()

    if not skip_connection_check:
        ok, msg = verify_mongo_connection(db)
        if not ok:
            print("ERROR:", msg, file=sys.stderr)
            sys.exit(1)
        print("[DEBUG] Ligação ao MongoDB verificada.")

    # 1. Indicators
    indicators = fetch_indicators()
    coll_indicators = db[COLLECTION_INDICATORS]
    coll_indicators.delete_many({})
    if indicators:
        coll_indicators.insert_many(indicators)

    # 2. Dimensions
    dimensions = fetch_dimensions()
    coll_dimensions = db[COLLECTION_DIMENSIONS]
    coll_dimensions.delete_many({})
    if dimensions:
        coll_dimensions.insert_many(dimensions)

    total_dim_values = 0
    for dim in dimensions:
        code = dim.get("Code")
        if not code:
            continue
        # Normaliza o código para construir o nome da coleção, e.g. "Country" -> "gho_country_dimension_values"
        safe_code = str(code).strip().lower().replace(" ", "_")
        collection_name = f"gho_{safe_code}_dimension_values"
        try:
            values = fetch_dimension_values(code)
            for v in values:
                v["_dimension_code"] = code  # permite filtrar por dimensão
            if values:
                coll_dim_values = db[collection_name]
                coll_dim_values.delete_many({})
                coll_dim_values.insert_many(values)
                total_dim_values += len(values)
        except requests.RequestException:
            # Ignora esta dimensão se o pedido falhar
            continue

    return {
        "indicators": len(indicators),
        "dimensions": len(dimensions),
        "dimension_values": total_dim_values,
    }


if __name__ == "__main__":
    print("[DEBUG] Configuração MongoDB:", _mongo_config())
    ok, msg = verify_mongo_connection()
    print("[DEBUG]", msg)
    if not ok:
        print("A abortar: corrige a ligação e volta a executar.", file=sys.stderr)
        sys.exit(1)
    result = ingest_to_mongo()
    print("Ingestão concluída:", result)
