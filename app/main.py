
# Main entry point for our FastAPI app. Wires up all the agents and endpoints.
from fastapi import FastAPI
from datetime import datetime, timezone
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agents.planner import planner_agent
from app.schemas.research import ResearchPlan

from app.services.llm_service import (
    llm_service,
    LLMServiceError,
)

from app.agents.researcher import run_research_tasks_parallel

from app.schemas.research import (
    ResearchPlan,
    ResearchWorkerResult,
)
from app.workflows.research_graph import research_graph

from fastapi import HTTPException

from app.workflows.research_graph import research_graph
from app.services.llm_service import LLMServiceError

app = FastAPI(
    title="Autonomous AI Research Team",
    description="Multi-agent AI research application",
    version="0.1.0",
)


# Incoming prompt payload for generic LLM calls
class PromptRequest(BaseModel):
    prompt: str = Field(
        min_length=5,
        max_length=10000
    )

# Payload when someone asks a specific research question
class ResearchQuestionRequest(BaseModel):
    question: str = Field(
        min_length=5,
        max_length=2000
    )


# Quick health check for Docker/k8s probes
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "Autonomous AI Research Team",
    }


# Root check just to see if the server is awake and kicking
@app.get("/")
async def root():
    return {
        "message": "Research Agent API is running",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Simple sandbox endpoint to test raw prompts against the LLM
@app.post("/api/test-llm")
async def test_llm(request: PromptRequest):

    try:
        # Run in thread so we don't block the event loop
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

# Endpoint to kick off a brand new research plan given a topic
@app.post("/api/plan", response_model=ResearchPlan)
async def create_research_plan(
    request: ResearchQuestionRequest
):
    try:
        # Let the planner agent break down the question into concrete tasks
        plan = await asyncio.to_thread(
            planner_agent.create_plan,
            request.question,
        )

        return plan

    except ValueError as exc:
        # Bad input from the user, let them know why
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except LLMServiceError:
        # OpenRouter or the underlying provider threw a fit
        raise HTTPException(
            status_code=502,
            detail="Research planning failed because the LLM provider failed.",
        )

    except Exception:
        # Catch-all for unexpected gremlins
        raise HTTPException(
            status_code=500,
            detail="Unexpected research planner error.",
        )

@app.post(
    "/api/research",
    response_model=list[ResearchWorkerResult],
)
async def execute_research(plan: ResearchPlan):

    try:
        results = await asyncio.to_thread(
            run_research_tasks_parallel,
            plan.tasks,
        )

        return results

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Research execution failed.",
        )


@app.post("/api/research/run")
async def run_complete_research(request: ResearchQuestionRequest):

    try:
        result = await asyncio.to_thread(
            research_graph.invoke,
            {
                "question": request.question,
                "worker_results": [],
            },
            {
                "max_concurrency": 3,
            },
        )

        return {
            "success": True,

            "research_plan": result["plan"].model_dump(),

            "worker_results": [
                worker.model_dump()
                for worker in result["ordered_results"]
            ],

            "research_summary": result["summary"],

            "evidence_analysis": (
                result["evidence_analysis"].model_dump()
            ),

            "fact_check_results": [
                claim.model_dump()
                for claim in result["fact_check_results"]
            ],

            "fact_check_summary": {
                "total_claims": len(result["fact_check_results"]),

                "supported": sum(
                    claim.verdict == "supported"
                    for claim in result["fact_check_results"]
                ),

                "contradicted": sum(
                    claim.verdict == "contradicted"
                    for claim in result["fact_check_results"]
                ),

                "insufficient": sum(
                    claim.verdict == "insufficient"
                    for claim in result["fact_check_results"]
                ),
            },
        }

    except LLMServiceError:
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        )

    except Exception as exc:
        print(f"[API] Research workflow failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Research workflow failed.",
        )
