import json
import random
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


def generate_embedding(text: str) -> List[float]:
    """
    Generates a mock vector embedding for the given text.
    In a real system, this would call an embedding model API.
    Here we generate a random 128-dimensional vector for demonstration.
    """
    # Using a fixed seed for demonstration purposes could be done, but random is fine.
    return [random.uniform(-1.0, 1.0) for _ in range(128)]


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
    batch_size = 500
    points = []
    total_upserted = 0
    print(f"Processing {len(products)} products in batches of {batch_size}...")

    operation_info = None
    for product in products:
        # Combine title and description for the embedding
        text_to_embed = f"{product['title']} {product['description']}"
        embedding = generate_embedding(text_to_embed)

        # Create a Qdrant PointStruct
        # Using a deterministic UUID based on the product ID for the point ID
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(product['id'])))

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload=product
        )
        points.append(point)

        if len(points) >= batch_size:
            print(f"Upserting batch of {len(points)} records...")
            operation_info = client.upsert(
                collection_name=collection_name,
                wait=True,
                points=points
            )
            total_upserted += len(points)
            points = []

    if points:
        print(f"Upserting final batch of {len(points)} records...")
        operation_info = client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        total_upserted += len(points)

    print(f"Successfully upserted {total_upserted} records.")
    if operation_info:
        print(f"Operation status: {operation_info.status}")


if __name__ == "__main__":
    main()
