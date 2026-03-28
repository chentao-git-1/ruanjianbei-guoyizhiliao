import json

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

DOC_DIR = CONFIG['documentBaseDir']
QDRANT_URL = CONFIG['url']
QDRANT_COLLECTION = CONFIG['collectionName']
LLM_API_BASE = CONFIG['llm']['apiBase']
LLM_API_KEY = CONFIG['llm']['apiKey']

embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

client = QdrantClient(url=QDRANT_URL)
if not client.collection_exists(QDRANT_COLLECTION):
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        )
    )
    print(f"Collection {QDRANT_COLLECTION} initialized.")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings,
)
print("Vector Database Loaded.")
