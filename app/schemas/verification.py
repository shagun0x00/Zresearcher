
# app/schemas/verification.py

from typing import Literal

from pydantic import BaseModel, Field


class EvidenceAnalysis(BaseModel):
    """Structured analysis of evidence collected by research workers."""

    overview: str = Field(min_length=10)

    key_findings: list[str] = Field(default_factory=list)

    evidence_gaps: list[str] = Field(default_factory=list)

    source_quality_notes: list[str] = Field(default_factory=list)

    claims_reviewed: int = Field(ge=0)


class FactCheckDecision(BaseModel):
    """LLM assessment of whether evidence supports an individual claim."""

    verdict: Literal[
        "supported",
        "contradicted",
        "insufficient",
    ]

    rationale: str = Field(min_length=5)

    confidence: float = Field(ge=0.0, le=1.0)


class VerifiedClaim(BaseModel):
    """Fact-check result linked to its original evidence."""

    claim_id: str

    claim_text: str

    source_id: str

    supporting_passage: str

    verdict: Literal[
        "supported",
        "contradicted",
        "insufficient",
    ]

    rationale: str

    confidence: float = Field(ge=0.0, le=1.0)

    verification_method: str = "llm_evidence_assessment"
