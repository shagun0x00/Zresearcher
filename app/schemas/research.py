
from typing import Literal

from pydantic import BaseModel, Field

class ResearchTask(BaseModel):
    task_id: int = Field(
        description="Unique integer identifier for this task"
    )

    topic: str = Field(
        min_length=3,
        description="Specific research topic"
    )

    description: str = Field(
        min_length=10,
        description="Detailed instructions describing what to investigate"
    )

    priority: Literal["low", "medium", "high"] = Field(
        description="Priority of this research task"
    )

    expected_output: str = Field(
        min_length=5,
        description="Expected findings or deliverable from this task"
    )

class ResearchPlan(BaseModel):
    research_title: str = Field(
        description="Clear title for the research project"
    )

    research_question: str = Field(
        description="Original research question"
    )

    objectives: list[str] = Field(
        min_length=2,
        description="Main objectives of the research"
    )

    tasks: list[ResearchTask] = Field(
        min_length=3,
        max_length=8,
        description="Independent research tasks"
    )

    scope: str = Field(
        description="Research boundaries and areas covered"
    )

    assumptions: list[str] = Field(
        description="Assumptions or uncertainties to consider"
    )

