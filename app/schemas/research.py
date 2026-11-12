
from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    task_id: int = Field(
        description="Unique task identifier"
    )

    topic: str = Field(
        description="Research topic"
    )

    description: str = Field(
        description="Detailed research instructions"
    )

    priority: str = Field(
        description="Task priority: low, medium, or high"
    )


class ResearchPlan(BaseModel):
    research_title: str

    objectives: list[str]

    tasks: list[ResearchTask]
