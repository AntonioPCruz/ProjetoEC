import chromadb

COLLECTION_NAME = "pmc_medicine_preventive"
client = chromadb.HttpClient(host="localhost", port=8000)
print(client.list_collections())  # Lista coleções
