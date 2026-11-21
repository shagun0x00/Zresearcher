
from app.agents.researcher import research_worker

from app.schemas.research import ResearchTask


def main():

    task = ResearchTask(
        task_id=1,
        topic="Electric vehicle market growth in India",
        description=(
            "Investigate recent EV market growth in India. "
            "Look for sales trends, adoption rates, and "
            "reliable market statistics."
        ),
        priority="high",
        expected_output=(
            "Evidence-backed findings about EV market growth "
            "with source URLs and supporting passages."
        ),
    )

    print("\n========== RESEARCH WORKER ==========\n")

    result = research_worker.research(task)

    print(result.model_dump_json(indent=2))

    print("\n========== WORKER SUMMARY ==========\n")
    print(f"Task: {result.task_topic}")
    print(f"Status: {result.status}")
    print(f"Sources: {len(result.sources)}")
    print(f"Claims: {len(result.claims)}")

    for source in result.sources:
        print(f"\nSOURCE: {source.title}")
        print(f"URL: {source.url}")
        print(f"Content type: {source.content_source}")

    for claim in result.claims:
        print(f"\nCLAIM: {claim.claim_text}")
        print(f"SOURCE ID: {claim.source_id}")
        print(f"PASSAGE: {claim.supporting_passage}")

    if result.error:
        print(f"\nERROR: {result.error}")

    print("\n========== TEST FINISHED ==========")


if __name__ == "__main__":
    main()
