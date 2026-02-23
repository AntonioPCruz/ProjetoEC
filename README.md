# ProjetoEC — DrHouseGPT

Chatbot para apoio ao diagnóstico em saúde e ingestão de dados (inquéritos, indicadores, literatura).

---

## Como executar

### 1. Configurar o ambiente

Cria um ficheiro `.env` na raiz do projeto com base no exemplo:

```console
cp .env.example .env
```

Edita o `.env` com os valores adequados (hosts, portas, utilizadores, palavras-passe).

### 2. Levantar os serviços com Docker

```console
docker-compose up --build -d
```

Ficam disponíveis: aplicação Streamlit, PostgreSQL, MongoDB e ChromaDB (vetorial).

### 3. Aceder à aplicação

A aplicação fica disponível em: **http://localhost:8501**

### Execução local (sem Docker)

Na raiz do projeto, com as bases de dados já a correr e o `.env` configurado:

```console
PYTHONPATH=src streamlit run src/app.py
```

---

## Estrutura do repositório

Layout plano em `src/`, sem pacote de topo adicional.

```
ProjetoEC/
├── src/
│   ├── app.py                 # Ponto de entrada da aplicação Streamlit
│   ├── db_connection.py       # Ligações e testes de saúde (SQL, NoSQL, vetorial)
│   ├── assets/                # Recursos estáticos (imagens, etc.)
│   ├── ingestion/             # Ingestão de dados
│   │   ├── api/               # Ingestão via APIs HTTP (ex.: GHO → MongoDB)
│   │   └── etl/               # ETL CSV/Excel → PostgreSQL
│   └── crawlers/              # Crawlers PubMed, PMC e ingestão ChromaDB
├── tests/                     # Testes (incl. test_dbs.py para ligação às BDs)
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

### O que existe em `src/`

| Caminho | Descrição |
|--------|-----------|
| **`db_connection.py`** | Ligação e testes de saúde para PostgreSQL, MongoDB e ChromaDB (`test_sql`, `test_nosql`, `test_vector`, `get_db_connection`). Usado pela app e pelos pipelines de ingestão. |
| **`ingestion/api/`** | Ingestão baseada em APIs. Ex.: **`gho.py`** — API Global Health Observatory (GHO) → MongoDB. |
| **`ingestion/etl/`** | Pipelines ETL: CSV/Excel → PostgreSQL. **`brfss.py`**, **`cdi.py`**, **`global_health.py`**, **`symptoms.py`**, **`wuenic.py`**. |
| **`crawlers/`** | **`pubmed_crawler.py`**, **`pmc_crawler.py`**, **`pmc_crawler_simples.py`**, **`chromadb_ingest.py`**. |
| **`app.py`** | Interface Streamlit (landing + chat). Recursos estáticos em **`assets/`**. |

### Imports

O código corre com `PYTHONPATH=src`. Imports a partir do topo de `src/`:

- `from db_connection import test_sql, get_db_connection`
- `from ingestion.etl import brfss` ou `from ingestion.etl.brfss import ingest_brfss`
- `from ingestion.api import gho`

---

## Ingestão de dados

### Exemplo: dataset WUENIC

Na raiz do projeto:

```bash
PYTHONPATH=src python -c "from ingestion.etl.wuenic import ingest_wuenic; ingest_wuenic('caminho/para/ficheiro.xlsx')"
```

### Outros pipelines ETL

- **BRFSS:** `from ingestion.etl.brfss import ingest_brfss; ingest_brfss("caminho/BRFSS.csv")`
- **CDI:** `from ingestion.etl.cdi import ingest_cdi; ingest_cdi("caminho/CDI.csv")`
- **Global health stats:** `from ingestion.etl.global_health import ingest_global_stats; ingest_global_stats("caminho/global.csv")`
- **Sintomas/doenças:** `from ingestion.etl.symptoms import ingest_data; ingest_data(...)`
- **GHO (MongoDB):** `from ingestion.api.gho import ingest_to_mongo; ingest_to_mongo()`

---

## Testes

Na raiz do projeto (com `PYTHONPATH=src`):

```console
PYTHONPATH=src pytest -q
```

- **`tests/test_dbs.py`** — Testes de ligação às bases de dados (PostgreSQL, MongoDB, ChromaDB) e verificação de existência de dados (tabelas/coleções e contagens). Estes testes são ignorados (skip) quando as variáveis de ambiente correspondentes não estão definidas (ex.: CI sem contentores).
- **`tests/test_1.py`** — Testes legados/placeholder.

---

## Qualidade de código

Para verificar formatação e lint com Ruff (via container):

```console
docker-compose run app ruff format --check .
docker-compose run app ruff check .
```

Ou localmente, com as dependências de desenvolvimento instaladas:

```console
ruff format --check .
ruff check .
```

---

## Variáveis de ambiente (resumo)

| Grupo | Variáveis | Uso |
|-------|-----------|-----|
| **PostgreSQL** | `SQL_HOST`, `SQL_PORT`, `SQL_DB`, `SQL_USER`, `SQL_PASSWORD` | App e ETL |
| **MongoDB** | `MONGO_HOST`, `MONGO_PORT`, `MONGO_DB`, `MONGO_USER`, `MONGO_PASSWORD` | Ingestão GHO |
| **ChromaDB** | `VECTOR_HOST`, `VECTOR_PORT` | Base vetorial e crawlers |
| **App** | `APP_PORT` (ex.: 8501) | Porta do Streamlit no Docker |

O ficheiro `.env.example` na raiz deve listar todas as variáveis necessárias.
