import chromadb
from ollama import Client as OllamaClient
from sentence_transformers import CrossEncoder, SentenceTransformer

COLLECTION_NAME = "pmc_medicine_preventive"
embbeding_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
reranker = CrossEncoder("BAAI/bge-reranker-base")

client_chromadb = chromadb.HttpClient(host="localhost", port=8001)
collection = client_chromadb.get_or_create_collection(name=COLLECTION_NAME)
llm_model = "gemma3:4b"
ollama = OllamaClient(host="http://localhost:11434")

while True:
    input_query = input("> Faça uma pergunta:").strip()
    if input_query == "exit":
        break
    query_emb = embbeding_model.encode(input_query, normalize_embeddings=True)

    results = collection.query(query_embeddings=[query_emb], n_results=5)

    docs = results["documents"][0]
    pares = [(input_query, doc) for doc in docs]
    scores = reranker.predict(pares)
    print("\n--- SCORES RERANKER ---")
    for i, (score, doc) in enumerate(zip(scores, docs)):
        print(f"\nScore {score:.4f}")
        print(doc[:200])
    docs_classificados = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]

    contexto = "\n".join(docs_classificados[:3])

    prompt_final = f"""
    Responde em português de Portugal com base no contexto científico abaixo.
    Contexto:
    {contexto}

    Pergunta: {input_query}
    """

    resposta = ollama.generate(model=llm_model, prompt=prompt_final)
    print("\n Resposta:\n" + resposta["response"])
