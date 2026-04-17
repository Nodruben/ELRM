from fastapi import FastAPI
from pydantic import BaseModel, ValidationError
from typing import List
import json

app = FastAPI(title="Reasoning Engine")

class HealthCheckResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="OK")

# Model representing the expected structure from the LLM
class IntentAnalysis(BaseModel):
    category: str
    technical_attributes: List[str]
    reasoning_summary: str

# Request model for the /analyze-intent endpoint
class AnalyzeIntentRequest(BaseModel):
    query: str
    llm_response: str = "" # Simulate the raw text response from the LLM

@app.post("/analyze-intent", response_model=IntentAnalysis)
async def analyze_intent(request: AnalyzeIntentRequest) -> IntentAnalysis:
    # Attempt to parse the LLM response into the expected Pydantic model
    try:
        # Assuming the LLM returns a JSON string, we load it first
        parsed_json = json.loads(request.llm_response)

        # Validate the parsed JSON using the Pydantic model
        analysis = IntentAnalysis(**parsed_json)
        return analysis

    except (json.JSONDecodeError, ValidationError, TypeError):
        # Fallback to a default structure if parsing or validation fails
        return IntentAnalysis(
            category="unknown",
            technical_attributes=[],
            reasoning_summary="Error parsing LLM output. Fallback used."
        )
