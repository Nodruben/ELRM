from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Reasoning Engine")

class HealthCheckResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="OK")
