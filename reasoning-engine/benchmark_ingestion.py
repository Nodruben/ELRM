import time
import uuid
import random
from typing import List, Dict, Any

# Mocking Qdrant PointStruct and Client
class PointStruct:
    def __init__(self, id, vector, payload):
        self.id = id
        self.vector = vector
        self.payload = payload

def generate_embedding_seq(text: str) -> List[float]:
    """Simulated sequential embedding generation with delay."""
    time.sleep(0.05)  # Simulate 50ms latency per request
    return [random.uniform(-1.0, 1.0) for _ in range(128)]

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Simulated batch embedding generation with delay."""
    # Batch call often takes slightly longer than a single call but much less than N calls.
    # We'll simulate it taking 0.1s regardless of batch size (within reason).
    time.sleep(0.1)
    return [[random.uniform(-1.0, 1.0) for _ in range(128)] for _ in texts]

def run_baseline(products: List[Dict[str, Any]]):
    start_time = time.time()
    points = []
    for product in products:
        text_to_embed = f"{product['title']} {product['description']}"
        embedding = generate_embedding_seq(text_to_embed)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(product['id'])))
        point = PointStruct(id=point_id, vector=embedding, payload=product)
        points.append(point)
    duration = time.time() - start_time
    print(f"Sequential processing took {duration:.4f} seconds.")
    return duration

def run_optimized(products: List[Dict[str, Any]]):
    start_time = time.time()
    texts_to_embed = [f"{p['title']} {p['description']}" for p in products]
    embeddings = generate_embeddings_batch(texts_to_embed)

    points = []
    for product, embedding in zip(products, embeddings):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(product['id'])))
        point = PointStruct(id=point_id, vector=embedding, payload=product)
        points.append(point)
    duration = time.time() - start_time
    print(f"Batch processing took {duration:.4f} seconds.")
    return duration

if __name__ == "__main__":
    num_products = 50
    mock_products = [
        {"id": str(i), "title": f"Product {i}", "description": f"Description for product {i}"}
        for i in range(num_products)
    ]

    baseline = run_baseline(mock_products)
    optimized = run_optimized(mock_products)

    improvement = (baseline - optimized) / baseline * 100
    print(f"Improvement: {improvement:.2f}%")
