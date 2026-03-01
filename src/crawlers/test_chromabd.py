import chromadb
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "pmc_medicine_preventive"
client = chromadb.HttpClient(host="localhost", port=8001)
print(client.list_collections())  # Lista coleções
