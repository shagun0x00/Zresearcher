
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(
    title="Research Agent API",
    description="Multi-agent research system API",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Research Agent API is running",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Research Agent API",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
