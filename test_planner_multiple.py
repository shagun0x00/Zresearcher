
from app.agents.planner import planner_agent

questions = [
    "Analyze the impact of artificial intelligence on healthcare.",

    "Investigate renewable energy adoption in developing countries.",

    "Evaluate cybersecurity risks associated with cloud computing.",
]

def main():

    for index, question in enumerate(questions, start=1):

        print(f"\n{'=' * 60}")
        print(f"TEST {index}")
        print(f"QUESTION: {question}")
        print("=" * 60)

        try:
            plan = planner_agent.create_plan(question)

            print(f"TITLE: {plan.research_title}")
            print(f"OBJECTIVES: {len(plan.objectives)}")
            print(f"TASKS: {len(plan.tasks)}")

            for task in plan.tasks:
                print(
                    f"{task.task_id}. {task.topic} "
                    f"[{task.priority}]"
                )

            print("TEST PASSED")

        except Exception as exc:
            print(f"TEST FAILED: {exc}")

if __name__ == "__main__":
    main()