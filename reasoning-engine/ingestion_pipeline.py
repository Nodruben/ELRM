import json
import random
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates mock vector embeddings for the given list of texts in batch.
    In a real system, this would call an embedding model API that supports batching.
    Here we generate random 128-dimensional vectors for demonstration.
    """
    return [[random.uniform(-1.0, 1.0) for _ in range(128)] for _ in texts]


def main() -> None:
    """
    Main function to run the ingestion pipeline.
    Reads mock product data, generates embeddings, and upserts to Qdrant.
    """
    # 1. Connect to Qdrant
    print("Connecting to Qdrant at localhost:6333...")
    client = QdrantClient(url="http://localhost:6333")
    collection_name = "products"

    # Create collection if it doesn't exist
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' not found. Creating...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE),
        )
    else:
        print(f"Collection '{collection_name}' already exists.")

    # 2. Load mock data
    mock_data_path = "mock_products.json"
    print(f"Loading data from {mock_data_path}...")
    try:
        with open(mock_data_path, "r", encoding="utf-8") as f:
            products: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {mock_data_path}")
        return

    # 3. Process and upsert data
    print(f"Processing {len(products)} products...")

    # Batch generate embeddings for all products
    texts_to_embed = [f"{p['title']} {p['description']}" for p in products]
    embeddings = generate_embeddings(texts_to_embed)

    points = []
    for product, embedding in zip(products, embeddings):
        # Create a Qdrant PointStruct
        # Using a deterministic UUID based on the product ID for the point ID
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(product['id'])))

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload=product
        )
        points.append(point)

    print("Upserting records to Qdrant...")
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )

    print(f"Successfully upserted {len(points)} records.")
    print(f"Operation status: {operation_info.status}")


if __name__ == "__main__":
    main()
