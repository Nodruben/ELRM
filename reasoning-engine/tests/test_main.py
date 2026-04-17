from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_analyze_intent_success():
    valid_json = {
        "category": "product_search",
        "technical_attributes": ["shoes", "running"],
        "reasoning_summary": "User wants running shoes."
    }

    response = client.post("/analyze-intent", json={
        "query": "running shoes",
        "llm_response": json.dumps(valid_json)
    })

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "product_search"
    assert data["technical_attributes"] == ["shoes", "running"]
    assert data["reasoning_summary"] == "User wants running shoes."

def test_analyze_intent_malformed_json():
    # Test fallback logic for json.JSONDecodeError
    response = client.post("/analyze-intent", json={
        "query": "running shoes",
        "llm_response": "This is not a JSON string, just plain text from the LLM"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."

def test_analyze_intent_invalid_schema():
    # Test fallback logic for ValidationError (missing required fields)
    invalid_schema_json = {
        "category": "product_search"
        # Missing technical_attributes and reasoning_summary
    }

    response = client.post("/analyze-intent", json={
        "query": "running shoes",
        "llm_response": json.dumps(invalid_schema_json)
    })

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."

def test_analyze_intent_wrong_type():
    # Test fallback logic for ValidationError (wrong types)
    invalid_type_json = {
        "category": "product_search",
        "technical_attributes": "this should be a list",
        "reasoning_summary": 123  # this should be a string
    }

    response = client.post("/analyze-intent", json={
        "query": "running shoes",
        "llm_response": json.dumps(invalid_type_json)
    })

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."
