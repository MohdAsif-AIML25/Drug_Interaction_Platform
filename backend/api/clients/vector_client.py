import chromadb
from chromadb.utils import embedding_functions
import os
import pandas as pd
from loguru import logger

CHROMA_DATA_PATH = "data/chroma_db"
COLLECTION_NAME = "drug_interactions"

# Standard embedding function using Sentence Transformers
# This will run locally and create embeddings for our drug interaction texts
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

try:
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=embedding_func
    )
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    collection = None

def index_data(csv_paths):
    """
    Index interaction data from CSV files into ChromaDB.
    """
    if collection is None:
        return

    for path in csv_paths:
        if not os.path.exists(path):
            continue
            
        df = pd.read_csv(path)
        logger.info(f"Indexing {len(df)} rows from {path} into Vector DB")
        
        documents = []
        metadatas = []
        ids = []
        
        for i, row in df.iterrows():
            # Combine relevant info for RAG context
            text = f"Medicine: {row.get('product_name')}. Salt: {row.get('salt_composition')}. Description: {row.get('medicine_desc')}. Side Effects: {row.get('side_effects')}. Interactions: {row.get('drug_interactions')}"
            
            documents.append(text)
            metadatas.append({
                "product": str(row.get('product_name')),
                "salt": str(row.get('salt_composition')),
                "severity": "Unknown" # You might extract this from drug_interactions if available
            })
            ids.append(f"{os.path.basename(path)}_{i}")
            
        if documents:
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

def query_interactions(drug_a, drug_b, k=3):
    """
    Retrieve top-k relevant interaction passages for a drug pair.
    """
    if collection is None:
        return []
        
    query_text = f"Interaction between {drug_a} and {drug_b}"
    results = collection.query(
        query_texts=[query_text],
        n_results=k
    )
    
    return results['documents'][0] if results['documents'] else []
