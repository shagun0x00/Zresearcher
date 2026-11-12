
from app.services.llm_service import gemini_service


def main():
    prompt = """
    You are an AI research assistant.

    Explain what multi-agent AI systems are
    in approximately 100 words.
    """

    response = gemini_service.generate_response(prompt)

    print("\n===== GEMINI RESPONSE =====\n")
    print(response)
    print("\n===== TEST SUCCESSFUL =====")


if __name__ == "__main__":
    main()
