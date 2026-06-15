"""V0 pipeline: intake -> A2 persona -> deterministic scoring -> C2 synthesis ->
C3 quick wins -> assemble scorecard -> D2 validation. Runs offline (deterministic
fallbacks) or on Claude when ANTHROPIC_API_KEY is set.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional

from .models import (
    Session, Submission, ConsentRecord, QuestionResponse, Scorecard, tier_for,
    ValueDifficultyItem,
)

_EFFORT_DIFFICULTY = {"Low": 0.3, "Medium": 0.6, "High": 0.8}


def _quadrant(value: float, difficulty: float) -> str:
    hv, ld = value >= 0.5, difficulty < 0.5
    if hv and ld:
        return "high_value_low_difficulty"
    if hv and not ld:
        return "high_value_high_difficulty"
    if not hv and ld:
        return "low_value_low_difficulty"
    return "low_value_high_difficulty"


def _value_difficulty(quick_wins, dims) -> list[ValueDifficultyItem]:
    """Light value-difficulty 2x2: quick wins (high value, low/med difficulty) plus the
    strategic move to close the weakest dimension (high value, higher difficulty)."""
    items: list[ValueDifficultyItem] = []
    for q in quick_wins:
        diff = _EFFORT_DIFFICULTY.get(q.implementation_effort, 0.5)
        val = 0.7  # quick wins are, by definition, high-confidence value
        items.append(ValueDifficultyItem(opportunity=q.pattern_name, value_score=val,
                                         difficulty_score=diff, quadrant=_quadrant(val, diff)))
    graded = [d for d in dims if not d.informational]
    if graded:
        weakest = min(graded, key=lambda d: d.score)
        items.append(ValueDifficultyItem(
            opportunity=f"Close the {weakest.label.lower()} gap",
            value_score=0.9, difficulty_score=0.7, quadrant=_quadrant(0.9, 0.7)))
    return items
from .scoring import score_dimensions, overall_score, apply_research_adjustments
from .benchmarks import peer_benchmarks, peer_reference
from . import agents


def build_session(submission: dict, consent: dict, responses: dict,
                  persona_hint: Optional[str] = None) -> tuple[Session, Optional[str]]:
    sub = Submission(**submission)
    con = ConsentRecord(**consent) if consent else ConsentRecord()
    if con.consent_timestamp is None:
        con.consent_timestamp = datetime.now(timezone.utc).isoformat()
    resp = [
        QuestionResponse(
            question_id=qid,
            option_id=a.get("option_id"),
            option_ids=a.get("option_ids", []),
            scale_value=a.get("scale_value"),
            text=a.get("text"),
        )
        for qid, a in responses.items()
    ]
    return Session(submission=sub, consent=con, responses=resp), persona_hint


def run_pipeline(session: Session, persona_hint: Optional[str] = None,
                 assessment_date: Optional[str] = None, log=lambda *_: None) -> Session:
    sub = session.submission

    # A1 — intake/consent gate
    if not session.consent.c1_use_for_scorecard:
        raise PermissionError("C-1 consent is required to produce a scorecard.")

    # A2 — persona
    session.persona = agents.a2_persona(sub, persona_hint)
    log(f"[A2] persona={session.persona.primary_persona} ({session.persona.framing_preference})")

    # B — research (B1 EDGAR / B2 news). Optional; gated by AIDIAG_ENABLE_RESEARCH.
    research: dict[str, Any] = session.research or {}
    from .config import settings as _settings
    if _settings.enable_research and not research:
        from . import research as research_mod
        research = research_mod.run_research(sub.company_name_raw)
        session.research = research
        log("[B1/B2] " + research_mod.research_summary(research))

    # Deterministic dimension scoring (Companion 01)
    dims = score_dimensions(session.responses)
    log("[score] " + ", ".join(f"{d.dimension}={d.score}" for d in dims))

    # C2 — synthesis (findings, recommendation, optional research adjustments)
    findings, rec, adjustments, attn = agents.c2_synthesis(sub, session.persona, dims, research)
    if adjustments:
        apply_research_adjustments(dims, adjustments)
    overall = overall_score(dims)

    # C3 — quick wins
    quick_wins = agents.c3_quick_wins(sub, dims)

    session.scorecard = Scorecard(
        company_name=sub.company_name_raw or "Your organization",
        industry_label=sub.industry_label,
        assessment_date=assessment_date or datetime.now(timezone.utc).strftime("%d %B %Y"),
        overall_score=overall,
        overall_tier=tier_for(overall),
        peer_reference=peer_reference(sub.industry_tag),
        peer_benchmarks=peer_benchmarks(sub.industry_tag),
        dimensions=dims,
        findings=findings,
        recommended_next_step=rec,
        quick_wins=quick_wins,
        value_difficulty=_value_difficulty(quick_wins, dims),
        partner_attention_flags=attn,
    )
    log(f"[C2/C3] overall={overall} ({session.scorecard.overall_tier}); "
        f"{len(findings)} findings, {len(quick_wins)} quick wins")

    # C4 — executive narrative (persona-framed prose; needs the assembled scorecard)
    session.scorecard.executive_narrative = agents.c4_narrative(sub, session.persona, session.scorecard)
    log(f"[C4] narrative: {len(session.scorecard.executive_narrative.paragraphs)} paragraph(s)")

    # D2 — validation
    session.validation = agents.d2_validate(session.scorecard)
    log(f"[D2] {session.validation.overall_status}; {len(session.validation.flags)} flag(s)")
    return session
