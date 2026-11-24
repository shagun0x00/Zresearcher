
# app/workflows/research_graph.py

import operator

from typing import Annotated
from typing_extensions import TypedDict, NotRequired

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from app.agents.planner import planner_agent
from app.agents.researcher import research_worker
from app.agents.evidence_analyst import evidence_analyst
from app.agents.fact_checker import fact_checker

from app.schemas.research import (
    ResearchTask,
    ResearchPlan,
    ResearchWorkerResult,
)

from app.schemas.verification import (
    EvidenceAnalysis,
    VerifiedClaim,
)


class ResearchState(TypedDict):

    question: str

    plan: NotRequired[ResearchPlan]

    worker_results: Annotated[
        list[ResearchWorkerResult],
        operator.add,
    ]

    ordered_results: NotRequired[
        list[ResearchWorkerResult]
    ]

    summary: NotRequired[dict]

    evidence_analysis: NotRequired[EvidenceAnalysis]

    fact_check_results: NotRequired[list[VerifiedClaim]]


class WorkerState(TypedDict):
    task: ResearchTask


def planner_node(state: ResearchState):
    print("\n[GRAPH] Planner node started")

    plan = planner_agent.create_plan(
        state["question"]
    )

    print(
        f"[GRAPH] Planner created {len(plan.tasks)} tasks"
    )

    return {
        "plan": plan
    }


def research_worker_node(state: WorkerState):
    task = state["task"]

    print(
        f"[GRAPH] Worker started: Task {task.task_id} - {task.topic}"
    )

    result = research_worker.research(task)

    print(
        f"[GRAPH] Worker finished: Task {task.task_id} - {result.status}"
    )

    return {
        "worker_results": [result]
    }


def dispatch_research_tasks(state: ResearchState):

    plan = state["plan"]

    if not plan or not plan.tasks:
        return []

    tasks = plan.tasks[:6]

    return [
        Send(
            "research_worker",
            {"task": task},
        )
        for task in tasks
    ]


def aggregate_results_node(state: ResearchState):

    results = sorted(
        state.get("worker_results", []),
        key=lambda result: result.task_id,
    )

    complete = sum(
        result.status == "complete"
        for result in results
    )

    partial = sum(
        result.status == "partial"
        for result in results
    )

    failed = sum(
        result.status == "failed"
        for result in results
    )

    summary = {
        "total_tasks": len(results),
        "complete": complete,
        "partial": partial,
        "failed": failed,
    }

    print("\n[GRAPH] Research aggregation completed")
    print(summary)

    return {
        "ordered_results": results,
        "summary": summary,
    }


def evidence_analyst_node(state: ResearchState):

    print("\n[GRAPH] Evidence Analyst started")

    results = state.get("ordered_results", [])

    analysis = evidence_analyst.analyze(results)

    print(
        "[GRAPH] Evidence Analyst finished: "
        f"{analysis.claims_reviewed} claims reviewed"
    )

    return {
        "evidence_analysis": analysis
    }


def fact_checker_node(state: ResearchState):

    print("\n[GRAPH] Fact Checker started")

    results = state.get("ordered_results", [])

    verified_claims = fact_checker.verify(results)

    supported = sum(
        claim.verdict == "supported"
        for claim in verified_claims
    )

    contradicted = sum(
        claim.verdict == "contradicted"
        for claim in verified_claims
    )

    insufficient = sum(
        claim.verdict == "insufficient"
        for claim in verified_claims
    )

    print(
        "[GRAPH] Fact Checker finished: "
        f"{supported} supported, "
        f"{contradicted} contradicted, "
        f"{insufficient} insufficient"
    )

    return {
        "fact_check_results": verified_claims
    }


def build_research_graph():

    workflow = StateGraph(ResearchState)

    workflow.add_node(
        "planner",
        planner_node,
    )

    workflow.add_node(
        "research_worker",
        research_worker_node,
    )

    workflow.add_node(
        "aggregate_results",
        aggregate_results_node,
    )

    workflow.add_node(
        "evidence_analyst",
        evidence_analyst_node,
    )

    workflow.add_node(
        "fact_checker",
        fact_checker_node,
    )

    workflow.add_edge(
        START,
        "planner",
    )

    workflow.add_conditional_edges(
        "planner",
        dispatch_research_tasks,
    )

    workflow.add_edge(
        "research_worker",
        "aggregate_results",
    )

    workflow.add_edge(
        "aggregate_results",
        "evidence_analyst",
    )

    workflow.add_edge(
        "evidence_analyst",
        "fact_checker",
    )

    workflow.add_edge(
        "fact_checker",
        END,
    )

    return workflow.compile()


research_graph = build_research_graph()
