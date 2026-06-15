"""Pydantic data models — aligned to Companion 05 (V0 subset used by the pipeline + UI).

Six dimensions, 0-100 scores, four tiers (Emerging/Developing/Established/Leading).
This replaces the earlier adaptive-interview model set.
"""
from __future__ import annotations
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field

# ---------- enums / constants ----------
DIMENSION_IDS = [
    "data_foundation", "governance_posture", "ai_investment_maturity",
    "org_change_readiness", "value_pocket_clarity", "regulatory_complexity",
]
DIMENSION_LABELS = {
    "data_foundation": "Data Foundation",
    "governance_posture": "Governance Posture",
    "ai_investment_maturity": "AI Investment Maturity",
    "org_change_readiness": "Organizational Change Readiness",
    "value_pocket_clarity": "Value-Pocket Clarity",
    "regulatory_complexity": "Regulatory Complexity",
}
Tier = Literal["Emerging", "Developing", "Established", "Leading"]
TIER_THRESHOLDS = [("Emerging", 0, 39), ("Developing", 40, 59), ("Established", 60, 79), ("Leading", 80, 100)]
TIER_COLORS = {  # UI brief tier color mapping
    "Emerging": "#FFC982", "Developing": "#FFAE41", "Established": "#A1E6FF", "Leading": "#4995FF",
}
Persona = Literal["P1", "P2", "P3"]


def tier_for(score: int) -> Tier:
    for name, lo, hi in TIER_THRESHOLDS:
        if lo <= score <= hi:
            return name  # type: ignore[return-value]
    return "Leading"


# ---------- intake / consent ----------
class Submission(BaseModel):
    prospect_name: str = ""
    prospect_role: str = ""
    prospect_email: str = ""
    company_name_raw: str = ""
    company_website: str = ""
    industry_label: str = ""          # FS / HLS / MFG / All-ish label
    industry_tag: Literal["FS", "HLS", "MFG", "All"] = "All"
    size_band: Literal["mid-market", "large", "global", "unknown"] = "unknown"
    hq_country: str = ""
    submission_source: str = "web_direct"


class ConsentRecord(BaseModel):
    c1_use_for_scorecard: bool = True          # required, always true
    c2_anonymized_benchmark: bool = True       # default on
    c3_internal_ai_improvement: bool = False   # opt-in
    c4_cross_practice_sharing: bool = False     # opt-in
    consent_timestamp: Optional[str] = None
    consent_language_version: str = "web_form_v1"


# ---------- persona (A2) ----------
class PersonaInference(BaseModel):
    primary_persona: Persona = "P1"
    primary_persona_confidence: float = 0.5
    secondary_persona: Optional[Persona] = None
    likely_concerns: list[str] = []
    framing_preference: Literal["financial-quantitative", "strategic-narrative", "technical-operational"] = "strategic-narrative"
    seniority: Literal["board-facing", "executive", "senior-management", "unknown"] = "executive"
    reasoning_summary: str = ""


# ---------- questionnaire responses ----------
class QuestionResponse(BaseModel):
    question_id: str
    # single_select/multi_select: option id(s); scale_1_5: int; open_short: text
    option_id: Optional[str] = None
    option_ids: list[str] = []
    scale_value: Optional[int] = None
    text: Optional[str] = None


# ---------- scoring (C2 / deterministic) ----------
class DimensionScore(BaseModel):
    dimension: str
    label: str = ""
    score: int = Field(ge=0, le=100)
    tier: Tier = "Emerging"
    questionnaire_derived: int = 0
    research_adjustment: int = 0
    reasoning: str = ""
    confidence: float = 0.8
    informational: bool = False

    def finalize(self) -> "DimensionScore":
        self.label = DIMENSION_LABELS.get(self.dimension, self.dimension)
        self.score = max(0, min(100, self.score))
        self.tier = tier_for(self.score)
        return self


class Finding(BaseModel):
    finding_id: str
    headline: str
    body: str
    decision_relevance: Literal["high", "medium", "low"] = "high"
    confidence: float = 0.8


class RecommendedNextStep(BaseModel):
    engagement_type: str = "APR Discovery (scoped)"
    body: str = ""
    duration_estimate_weeks: str = "6-10 weeks"
    contact_name: str = "DXC AdvisoryX"
    contact_title: str = ""
    contact_email: str = "advisoryx@dxc.com"


class SelectedQuickWin(BaseModel):
    pattern_id: str
    pattern_name: str
    one_line_description: str = ""
    what_this_would_do: str = ""
    prerequisites_you_have: list[str] = []
    expected_outcome_range: str = ""
    timeline_to_value: str = ""
    implementation_effort: str = "Low"
    ordering_priority: int = 1
    selection_confidence: float = 0.8


class ValueDifficultyItem(BaseModel):
    opportunity: str
    value_score: float = 0.5        # 0..1
    difficulty_score: float = 0.5   # 0..1
    quadrant: str = "high_value_low_difficulty"


class Scorecard(BaseModel):
    company_name: str = ""
    industry_label: str = ""
    assessment_date: str = ""
    reviewed_by: str = "DXC AdvisoryX"
    overall_score: int = 0
    overall_tier: Tier = "Emerging"
    peer_reference: str = ""
    dimensions: list[DimensionScore] = []
    findings: list[Finding] = []
    recommended_next_step: RecommendedNextStep = RecommendedNextStep()
    quick_wins: list[SelectedQuickWin] = []
    value_difficulty: list[ValueDifficultyItem] = []
    partner_attention_flags: list[str] = []


# ---------- validation (D2) ----------
class ValidationFlag(BaseModel):
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    category: str
    location: str
    concern: str
    recommendation: str = ""


class ValidationOutput(BaseModel):
    overall_status: Literal["passed", "passed_with_flags", "requires_revision"] = "passed"
    flags: list[ValidationFlag] = []
    partner_review_priority: Literal["expedited", "standard", "deferred"] = "standard"


# ---------- session (orchestrator state) ----------
class Session(BaseModel):
    submission: Submission = Submission()
    consent: ConsentRecord = ConsentRecord()
    persona: PersonaInference = PersonaInference()
    responses: list[QuestionResponse] = []
    research: dict[str, Any] = {}        # B1/B2/B3 outputs (raw)
    scorecard: Optional[Scorecard] = None
    validation: Optional[ValidationOutput] = None
    partner_approved: bool = False


# ---------- agent I/O schemas (messages.parse) ----------
class PersonaResult(BaseModel):
    primary_persona: Persona
    primary_persona_confidence: float
    secondary_persona: Optional[Persona] = None
    likely_concerns: list[str]
    framing_preference: Literal["financial-quantitative", "strategic-narrative", "technical-operational"]
    seniority: Literal["board-facing", "executive", "senior-management", "unknown"]
    reasoning_summary: str


class FindingOut(BaseModel):
    finding_id: str
    headline: str
    body: str
    decision_relevance: Literal["high", "medium", "low"]
    confidence: float


class DimReasoning(BaseModel):
    dimension: str
    research_adjustment: int = Field(ge=-25, le=25)
    reasoning: str
    confidence: float


class SynthesisResult(BaseModel):
    dimension_reasoning: list[DimReasoning]
    findings: list[FindingOut]
    recommended_next_step_body: str
    duration_estimate_weeks: str
    partner_attention_flags: list[str]


class QuickWinPick(BaseModel):
    pattern_id: str
    what_this_would_do: str
    prerequisites_you_have: list[str]
    selection_confidence: float


class QuickWinResult(BaseModel):
    selected: list[QuickWinPick]


class ValidationResult(BaseModel):
    overall_status: Literal["passed", "passed_with_flags", "requires_revision"]
    flags: list[ValidationFlag]
    partner_review_priority: Literal["expedited", "standard", "deferred"]
