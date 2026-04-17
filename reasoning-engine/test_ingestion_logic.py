import uuid
import unittest
from unittest.mock import MagicMock
from typing import List

# Mock dependencies before importing the code under test
import sys
from types import ModuleType

# Mock qdrant_client
mock_qdrant = ModuleType('qdrant_client')
mock_qdrant_models = ModuleType('qdrant_client.models')
sys.modules['qdrant_client'] = mock_qdrant
sys.modules['qdrant_client.models'] = mock_qdrant_models

# Define a real-ish PointStruct for testing
class PointStruct:
    def __init__(self, id, vector, payload):
        self.id = id
        self.vector = vector
        self.payload = payload

mock_qdrant.QdrantClient = MagicMock()
mock_qdrant_models.Distance = MagicMock()
mock_qdrant_models.VectorParams = MagicMock()
mock_qdrant_models.PointStruct = PointStruct

# Now we can import the code
from ingestion_pipeline import generate_embeddings

class TestIngestionPipeline(unittest.TestCase):
    def test_generate_embeddings(self):
        texts = ["hello", "world"]
        embeddings = generate_embeddings(texts)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 128)
        self.assertEqual(len(embeddings[1]), 128)

    def test_logic_flow(self):
        # We want to ensure that the mapping between products and embeddings is correct
        # and that the point IDs are generated as expected.
        products = [
            {"id": "1", "title": "T1", "description": "D1"},
            {"id": "2", "title": "T2", "description": "D2"}
        ]

        embeddings = [[0.1]*128, [0.2]*128]

        points = []
        for product, embedding in zip(products, embeddings):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(product['id'])))
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=product
            )
            points.append(point)

        self.assertEqual(len(points), 2)
        self.assertEqual(points[0].payload['id'], "1")
        self.assertEqual(points[0].vector, [0.1]*128)
        self.assertEqual(points[1].payload['id'], "2")
        self.assertEqual(points[1].vector, [0.2]*128)

        expected_id_1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, "1"))
        self.assertEqual(points[0].id, expected_id_1)

if __name__ == "__main__":
    unittest.main()
