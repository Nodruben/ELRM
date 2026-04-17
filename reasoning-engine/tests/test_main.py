from fastapi.testclient import TestClient
import json

from app.main import app, IntentAnalysis

client = TestClient(app)

def test_analyze_intent_success():
    valid_llm_response = {
        "category": "electronics",
        "technical_attributes": ["smartphone", "5g", "oled"],
        "reasoning_summary": "User is looking for a 5g smartphone."
    }

    payload = {
        "query": "I need a 5g phone with an oled screen",
        "llm_response": json.dumps(valid_llm_response)
    }

    response = client.post("/analyze-intent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "electronics"
    assert data["technical_attributes"] == ["smartphone", "5g", "oled"]
    assert data["reasoning_summary"] == "User is looking for a 5g smartphone."

def test_analyze_intent_invalid_json():
    payload = {
        "query": "I need a 5g phone",
        "llm_response": "this is not valid json"
    }

    response = client.post("/analyze-intent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."

def test_analyze_intent_invalid_schema():
    invalid_schema_response = {
        "category": "electronics",
        # Missing technical_attributes
        "reasoning_summary": "Looking for phone."
    }

    payload = {
        "query": "I need a 5g phone",
        "llm_response": json.dumps(invalid_schema_response)
    }

    response = client.post("/analyze-intent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."

def test_analyze_intent_empty_response():
    payload = {
        "query": "I need a 5g phone",
        "llm_response": ""
    }

    response = client.post("/analyze-intent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "unknown"
    assert data["technical_attributes"] == []
    assert data["reasoning_summary"] == "Error parsing LLM output. Fallback used."
