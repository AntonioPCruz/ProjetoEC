import chromadb
import ollama
from sentence_transformers import CrossEncoder, SentenceTransformer

COLLECTION_NAME = "pmc_medicine_preventive"

embedding_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
reranker = CrossEncoder("BAAI/bge-reranker-base")

chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

LLM_MODEL = "gemma3:4b"


def rag_answer(query: str) -> str:
    # embedding
    emb = embedding_model.encode(query).tolist()

    # retrieval
    results = collection.query(query_embeddings=[emb], n_results=5)

    docs = results["documents"][0]

    # rerank
    pairs = [(query, d) for d in docs]
    scores = reranker.predict(pairs)

    ranked_docs = [d for _, d in sorted(zip(scores, docs), reverse=True)]

    contexto = "\n".join(ranked_docs[:3])

    prompt = f"""
Baseando-se nas informações abaixo, responda em português de forma médica e clara.

Contexto:
{contexto}

Pergunta: {query}
"""

    response = ollama.generate(model=LLM_MODEL, prompt=prompt)

    return response["response"]
