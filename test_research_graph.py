
# test_research_graph.py

import json

from app.workflows.research_graph import research_graph


def main():

    question = (
        "Analyze the electric vehicle market in India. "
        "Investigate market growth, major manufacturers, "
        "charging infrastructure, and government policies."
    )

    print("\n========== RESEARCH GRAPH ==========\n")

    result = research_graph.invoke(
        {
            "question": question,
            "worker_results": [],
        },
        config={
            "max_concurrency": 3,
        },
    )

    # Research plan
    print("\n========== RESEARCH PLAN ==========\n")

    print(
        json.dumps(
            result["plan"].model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    # Worker results
    print("\n========== WORKER RESULTS ==========\n")

    for worker in result["ordered_results"]:

        print("-" * 60)
        print(f"TASK: {worker.task_id}")
        print(f"TOPIC: {worker.task_topic}")
        print(f"STATUS: {worker.status}")
        print(f"SOURCES: {len(worker.sources)}")
        print(f"CLAIMS: {len(worker.claims)}")

        if worker.error:
            print(f"ERROR: {worker.error}")

    # Evidence analysis
    print("\n========== EVIDENCE ANALYSIS ==========\n")

    analysis = result["evidence_analysis"]

    print(
        json.dumps(
            analysis.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
    )

    # Fact-check results
    print("\n========== FACT CHECK RESULTS ==========\n")

    for claim in result["fact_check_results"]:

        print("-" * 60)
        print(f"CLAIM ID: {claim.claim_id}")
        print(f"CLAIM: {claim.claim_text}")
        print(f"SOURCE: {claim.source_id}")
        print(f"VERDICT: {claim.verdict}")
        print(f"CONFIDENCE: {claim.confidence}")
        print(f"RATIONALE: {claim.rationale}")

    # Fact-check summary
    fact_checks = result["fact_check_results"]

    fact_check_summary = {
        "total_claims": len(fact_checks),
        "supported": sum(
            claim.verdict == "supported"
            for claim in fact_checks
        ),
        "contradicted": sum(
            claim.verdict == "contradicted"
            for claim in fact_checks
        ),
        "insufficient": sum(
            claim.verdict == "insufficient"
            for claim in fact_checks
        ),
    }

    print("\n========== EXECUTION SUMMARY ==========\n")

    print("Research summary:")
    print(result["summary"])

    print("\nFact-check summary:")
    print(fact_check_summary)

    print("\n========== DAY 6 TEST FINISHED ==========\n")


if __name__ == "__main__":
    main()
