
from fastapi import FastAPI
from datetime import datetime, timezone
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import (
    llm_service,
    LLMServiceError,
)



app = FastAPI(
    title="Autonomous AI Research Team",
    description="Multi-agent AI research application",
    version="0.1.0",
)


class PromptRequest(BaseModel):
    prompt: str = Field(
        min_length=5,
        max_length=10000
    )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "Autonomous AI Research Team",
    }



@app.get("/")
async def root():
    return {
        "message": "Research Agent API is running",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/test-llm")
async def test_llm(request: PromptRequest):

    try:
        result = await asyncio.to_thread(
            llm_service.generate_response,
            request.prompt,
        )

        return {
            "success": True,
            "response": result,
        }

    except LLMServiceError:
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        )
