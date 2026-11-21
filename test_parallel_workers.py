
from app.agents.researcher import run_research_tasks_parallel

from app.schemas.research import ResearchTask


def main():

    tasks = [

        ResearchTask(
            task_id=1,
            topic="Indian EV market growth",
            description=(
                "Find market growth trends, sales data, "
                "and adoption statistics."
            ),
            priority="high",
            expected_output="Market growth findings and statistics.",
        ),

        ResearchTask(
            task_id=2,
            topic="Major electric vehicle manufacturers in India",
            description=(
                "Research major EV manufacturers, "
                "their products, and market positions."
            ),
            priority="high",
            expected_output="Competitor profiles and comparisons.",
        ),

        ResearchTask(
            task_id=3,
            topic="EV charging infrastructure in India",
            description=(
                "Investigate charging stations, "
                "infrastructure development, and challenges."
            ),
            priority="medium",
            expected_output="Charging infrastructure findings.",
        ),

        ResearchTask(
            task_id=4,
            topic="Indian government electric vehicle policies",
            description=(
                "Research central government EV policies, "
                "incentives, and relevant schemes."
            ),
            priority="high",
            expected_output="Government policy findings.",
        ),
    ]

    print("\n========== PARALLEL RESEARCH ==========\n")

    results = run_research_tasks_parallel(
        tasks=tasks,
        max_workers=3,
        max_tasks=6,
    )

    for result in results:

        print("\n" + "=" * 60)

        print(f"TASK ID: {result.task_id}")
        print(f"TOPIC: {result.task_topic}")
        print(f"STATUS: {result.status}")

        print(f"SOURCES: {len(result.sources)}")
        print(f"CLAIMS: {len(result.claims)}")

        for claim in result.claims:
            print(f"\nCLAIM: {claim.claim_text}")
            print(f"SOURCE: {claim.source_id}")

        if result.error:
            print(f"ERROR: {result.error}")

    print("\n========== PARALLEL TEST FINISHED ==========")


if __name__ == "__main__":
    main()
