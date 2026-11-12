
from app.services.llm_service import (
    llm_service,
    LLMServiceError,
)

from app.schemas.research import ResearchPlan


def main():

    prompt = """
    Create a research plan for:

    Analyze the electric vehicle market in India.

    Include these research areas:
    1. Market growth
    2. Major competitors
    3. Charging infrastructure
    4. Government policies

    Generate exactly four research tasks.

    Each task must have:
    - A unique integer task_id
    - A topic
    - A detailed description
    - A priority
    """

    try:
        result = llm_service.generate_structured_response(
            prompt=prompt,
            schema=ResearchPlan,
        )

        print("\n========== STRUCTURED RESULT ==========\n")
        print(result.model_dump_json(indent=2))

        print("\n========== VALIDATION SUCCESSFUL ==========")

    except LLMServiceError as exc:
        print(f"\nSTRUCTURED TEST FAILED: {exc}")


if __name__ == "__main__":
    main()
