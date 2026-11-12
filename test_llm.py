
from app.services.llm_service import (
    llm_service,
    LLMServiceError,
)


def main():
    prompt = """
    Explain multi-agent AI systems.

    Include:
    1. What they are
    2. How agents communicate
    3. Their advantages
    4. Their limitations

    Keep the explanation around 150 words.
    """

    try:
        response = llm_service.generate_response(prompt)

        print("\n========== MODEL RESPONSE ==========\n")
        print(response)

        print("\n========== TEST SUCCESSFUL ==========")

    except LLMServiceError as exc:
        print(f"\nTEST FAILED: {exc}")


if __name__ == "__main__":
    main()
