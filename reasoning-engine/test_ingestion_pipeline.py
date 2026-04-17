import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import uuid

from ingestion_pipeline import generate_embedding, main
from qdrant_client.models import VectorParams, Distance, PointStruct

class TestIngestionPipeline(unittest.TestCase):

    def test_generate_embedding(self):
        text = "sample text"
        embedding = generate_embedding(text)
        self.assertEqual(len(embedding), 128)
        for val in embedding:
            self.assertGreaterEqual(val, -1.0)
            self.assertLessEqual(val, 1.0)

    @patch('ingestion_pipeline.QdrantClient')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {"id": 1, "title": "Product 1", "description": "Description 1"},
        {"id": 2, "title": "Product 2", "description": "Description 2"}
    ]))
    @patch('ingestion_pipeline.generate_embedding')
    def test_main_success(self, mock_generate_embedding, mock_file, mock_qdrant_client):
        # Mock QdrantClient instance
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Collection doesn't exist, so create_collection is called
        mock_client_instance.collection_exists.return_value = False

        # Mock generate_embedding to return a deterministic vector
        mock_generate_embedding.return_value = [0.1] * 128

        # Run main
        main()

        # Assertions
        mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
        mock_client_instance.collection_exists.assert_called_once_with("products")
        mock_client_instance.create_collection.assert_called_once_with(
            collection_name="products",
            vectors_config=VectorParams(size=128, distance=Distance.COSINE)
        )

        # Check if generate_embedding was called for both products
        self.assertEqual(mock_generate_embedding.call_count, 2)

        # Check if upsert was called with correct arguments
        mock_client_instance.upsert.assert_called_once()
        _, kwargs = mock_client_instance.upsert.call_args
        self.assertEqual(kwargs['collection_name'], "products")
        self.assertEqual(kwargs['wait'], True)
        self.assertEqual(len(kwargs['points']), 2)

        # Check points
        points = kwargs['points']
        self.assertEqual(points[0].id, str(uuid.uuid5(uuid.NAMESPACE_DNS, "1")))
        self.assertEqual(points[0].vector, [0.1] * 128)
        self.assertEqual(points[0].payload, {"id": 1, "title": "Product 1", "description": "Description 1"})

        self.assertEqual(points[1].id, str(uuid.uuid5(uuid.NAMESPACE_DNS, "2")))
        self.assertEqual(points[1].vector, [0.1] * 128)
        self.assertEqual(points[1].payload, {"id": 2, "title": "Product 2", "description": "Description 2"})

    @patch('ingestion_pipeline.QdrantClient')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_main_file_not_found(self, mock_file, mock_qdrant_client):
        # Mock QdrantClient instance
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance
        mock_client_instance.collection_exists.return_value = True # Collection exists

        # Run main and ensure it doesn't crash but exits gracefully
        main()

        # Assertions
        mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
        mock_client_instance.collection_exists.assert_called_once_with("products")
        mock_client_instance.create_collection.assert_not_called()
        mock_client_instance.upsert.assert_not_called()

if __name__ == '__main__':
    unittest.main()
