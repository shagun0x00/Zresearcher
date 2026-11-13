
from app.agents.planner import planner_agent
from app.services.llm_service import LLMServiceError

def main():

    research_question = """
    Analyze the electric vehicle market in India.

    Examine market growth, major manufacturers,
    charging infrastructure, government policies,
    consumer adoption, and future opportunities.
    """

    print("\n========== RESEARCH PLANNER ==========\n")
    print("Input question:")
    print(research_question)

    try:
        plan = planner_agent.create_plan(research_question)

        print("\n========== GENERATED RESEARCH PLAN ==========\n")

        print(plan.model_dump_json(indent=2))

        print("\n========== RESEARCH TASKS ==========\n")

        for task in plan.tasks:
            print(f"Task ID: {task.task_id}")
            print(f"Topic: {task.topic}")
            print(f"Priority: {task.priority}")
            print(f"Description: {task.description}")
            print(f"Expected output: {task.expected_output}")
            print("-" * 50)

        print("\nPLANNER TEST SUCCESSFUL")

    except ValueError as exc:
        print(f"INPUT ERROR: {exc}")

    except LLMServiceError as exc:
        print(f"LLM ERROR: {exc}")

    except Exception as exc:
        print(f"PLANNER ERROR: {exc}")

if __name__ == "__main__":
    main()