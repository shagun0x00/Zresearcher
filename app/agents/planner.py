
from app.services.llm_service import (
    llm_service,
    LLMServiceError,
)

from app.schemas.research import ResearchPlan

class PlannerAgent:

    def __init__(self):
        self.name = "Research Planner Agent"

    def create_plan(self, research_question: str) -> ResearchPlan:

        if not research_question or not research_question.strip():
            raise ValueError("Research question cannot be empty.")

        if len(research_question) > 2000:
            raise ValueError(
                "Research question must be under 2000 characters."
            )

        prompt = f"""
You are an expert research planning agent.

Your responsibility is to convert a user's research question
into a structured and actionable research plan.

USER RESEARCH QUESTION:
{research_question}

INSTRUCTIONS:

1. Understand the central research question.
2. Identify the main research objectives.
3. Break the question into 3 to 8 independent research tasks.
4. Each task must investigate a distinct aspect of the topic.
5. Avoid unnecessary overlap between tasks.
6. Assign each task a priority: low, medium, or high.
7. Describe exactly what each task should investigate.
8. Define the expected output of each task.
9. Define the scope and boundaries of the research.
10. Identify assumptions and uncertainties.

IMPORTANT RULES:

- Do not answer the research question.
- Do not invent statistics, facts, or sources.
- Do not claim that research has already been performed.
- Create tasks that can be assigned independently to research workers.
- Keep tasks specific, actionable, and relevant.
- Return a structured research plan matching the required schema.

The output will be used by other AI agents to conduct research.
"""

        try:
            plan = llm_service.generate_structured_response(
                prompt=prompt,
                schema=ResearchPlan,
            )

            return plan

        except LLMServiceError:
            raise

        except Exception as exc:
            raise RuntimeError(
                f"Planner agent failed: {exc}"
            ) from exc

# Shared planner instance
planner_agent = PlannerAgent()