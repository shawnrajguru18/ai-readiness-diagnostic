"""V0 agents (Companion 04). Each agent runs on Claude when ANTHROPIC_API_KEY is set,
and falls back to a deterministic implementation offline so the pipeline always produces
a scorecard. Models follow the Companion's tiering (Opus for C2/C3/D2, Sonnet for A2/B/D1)
mapped to current model IDs via app/config.py.
"""
from __future__ import annotations
import json
import logging
from typing import Any

from ..config import settings, llm_available

logger = logging.getLogger(__name__)
from ..content import quick_wins_by_id
from ..models import (
    Submission, PersonaInference, PersonaResult, DimensionScore, Finding,
    RecommendedNextStep, SelectedQuickWin, SynthesisResult, QuickWinResult,
    ValidationOutput, ValidationResult, ValidationFlag, ExecutiveNarrative, Scorecard,
)

# ---- DXC AdvisoryX voice guard (Companion 04 D1) ----
VOICE = (
    "Voice: lead with the conclusion (BLUF); specific not generic; speak with senior-partner "
    "authority; no em-dashes; avoid the words delve, tapestry, landscape, realm, leverage(verb), "
    "harness, unlock, foster, holistic, robust, transformative, paradigm, ecosystem; use 'use' not "
    "'utilize', 'help' not 'facilitate', 'method' not 'methodology'."
)


def _scores_text(dims: list[DimensionScore]) -> str:
    return "\n".join(
        f"- {d.label} ({d.dimension}): {d.score}/100 {d.tier}" + (" [informational]" if d.informational else "")
        for d in dims
    )


# ======================================================================
# A2 — Persona Inference
# ======================================================================
A2_SYS = (
    "You are a persona inference assistant for the DXC AI Readiness Diagnostic. Infer the prospect "
    "persona from role and context. P1 Executive sponsor (CEO/COO/MD): strategic, revenue, board. "
    "P2 Operational owner (CIO/CDO/CTO): technical readiness, implementation, governance. "
    "P3 Financial scrutineer (CFO/Finance): capital allocation, ROI, financial risk. Report only "
    "high-confidence inferences; use 'unknown' when signal is weak. Return JSON only."
)

def a2_persona(sub: Submission, hint: str | None = None) -> PersonaInference:
    if llm_available():
        from ..llm import parse_structured
        user = (f"Name: {sub.prospect_name}\nRole: {sub.prospect_role}\nCompany: {sub.company_name_raw}\n"
                f"Industry: {sub.industry_label}\nEmail domain: {sub.prospect_email.split('@')[-1]}")
        try:
            r: PersonaResult = parse_structured(A2_SYS, [{"role": "user", "content": user}],
                                                PersonaResult, model=settings.model_sonnet)
            logger.info("[A2] Used LLM for persona inference")
            return PersonaInference(**r.model_dump())
        except Exception as e:
            logger.warning(f"[A2] LLM failed, falling back to deterministic: {e}")
    else:
        logger.info("[A2] LLM not available, using deterministic fallback")
    return _persona_fallback(sub, hint)


def _persona_fallback(sub: Submission, hint: str | None) -> PersonaInference:
    role = (sub.prospect_role or "").lower()
    if hint in ("P1", "P2", "P3"):
        primary = hint
    elif any(k in role for k in ("cfo", "finance", "accounting", "treasurer")):
        primary = "P3"
    elif any(k in role for k in ("cio", "cto", "cdo", "digital", "data", "architect", "engineering", "technology")):
        primary = "P2"
    else:
        primary = "P1"
    framing = {"P1": "strategic-narrative", "P2": "technical-operational", "P3": "financial-quantitative"}[primary]
    concerns = {"P1": ["competitive_positioning", "revenue_growth"],
                "P2": ["operational_efficiency", "risk_mitigation"],
                "P3": ["cost_reduction", "risk_mitigation"]}[primary]
    return PersonaInference(primary_persona=primary, primary_persona_confidence=0.7,
                            likely_concerns=concerns, framing_preference=framing, seniority="executive",
                            reasoning_summary=f"Inferred from role '{sub.prospect_role}'.")


# ======================================================================
# C2 — Synthesis (findings + recommended next step). Research adjustment optional.
# ======================================================================
C2_SYS = (
    "You are the synthesis assistant for the DXC AI Readiness Diagnostic, the most analytically "
    "demanding agent. You are given six deterministic dimension scores (0-100; Emerging 0-39 / "
    "Developing 40-59 / Established 60-79 / Leading 80-100; Regulatory Complexity is informational). "
    "Produce: (1) optional per-dimension research_adjustment in [-25,25] with reasoning; "
    "(2) 3-5 findings specific to this prospect, written for the primary persona, each referencing "
    "specific dimensions; generic findings are unacceptable; (3) a recommended next step naming a "
    "specific APR Discovery scope and duration. " + VOICE + " Return JSON only."
)

def c2_synthesis(sub: Submission, persona: PersonaInference, dims: list[DimensionScore],
                 research: dict[str, Any]) -> tuple[list[Finding], RecommendedNextStep, dict[str, int], list[str]]:
    if llm_available():
        from ..llm import parse_structured
        user = (f"Prospect: {sub.company_name_raw} | Industry: {sub.industry_label} | "
                f"Primary persona: {persona.primary_persona}\n\nDimension scores:\n{_scores_text(dims)}\n\n"
                f"Research signals: {json.dumps(research)[:2000]}\n\n"
                "Produce dimension_reasoning, findings, recommended_next_step_body, duration_estimate_weeks, "
                "partner_attention_flags.")
        try:
            r: SynthesisResult = parse_structured(C2_SYS, [{"role": "user", "content": user}],
                                                  SynthesisResult, model=settings.model_opus, max_tokens=12000)
            findings = [Finding(**f.model_dump()) for f in r.findings]
            adj = {d.dimension: d.research_adjustment for d in r.dimension_reasoning}
            rec = RecommendedNextStep(body=r.recommended_next_step_body,
                                      duration_estimate_weeks=r.duration_estimate_weeks)
            logger.info(f"[C2] Used LLM for synthesis: {len(findings)} findings, duration {rec.duration_estimate_weeks}w")
            return findings, rec, adj, r.partner_attention_flags
        except Exception as e:
            logger.warning(f"[C2] LLM failed, falling back to deterministic: {e}")
    else:
        logger.info("[C2] LLM not available, using deterministic fallback")
    return _synthesis_fallback(sub, dims)


def _synthesis_fallback(sub: Submission, dims: list[DimensionScore]):
    graded = [d for d in dims if not d.informational]
    weakest = min(graded, key=lambda d: d.score)
    strongest = max(graded, key=lambda d: d.score)
    findings = [
        Finding(finding_id="F1",
                headline=f"{strongest.label} is the strongest foundation",
                body=(f"{sub.company_name_raw} scores {strongest.score}/100 on {strongest.label.lower()} "
                      f"({strongest.tier}). This is the most credible base to build near-term AI value on."),
                decision_relevance="high", confidence=0.8),
        Finding(finding_id="F2",
                headline=f"{weakest.label} is the largest gap",
                body=(f"{weakest.label} ({weakest.score}/100, {weakest.tier}) is the binding constraint. "
                      f"Addressing it is prerequisite to scaling AI value reliably."),
                decision_relevance="high", confidence=0.8),
        Finding(finding_id="F3",
                headline="Value-pocket definition needs sharpening",
                body=("AI investment converts to outcomes when value pockets are defined at scoping. "
                      "Prioritizing 2-3 high-confidence processes would lift the production conversion rate."),
                decision_relevance="medium", confidence=0.7),
    ]
    rec = RecommendedNextStep(
        body=(f"APR Discovery engagement focused on {weakest.label.lower()} and operational AI scaling. "
              f"The Discovery would size value pockets, design the sequence to close the {weakest.label.lower()} "
              f"gap, and produce a board-ready roadmap."),
        duration_estimate_weeks="6-10 weeks",
    )
    return findings, rec, {}, []


# ======================================================================
# C3 — Quick Wins (2-3 from the 15-pattern library)
# ======================================================================
def _candidate_patterns(sub: Submission) -> list[dict]:
    tag = sub.industry_tag
    size = sub.size_band
    out = []
    for p in quick_wins_by_id().values():
        inds = p.get("applicable_industries", [])
        if not (tag in inds or "All" in inds):
            continue
        sizes = p.get("applicable_sizes", [])
        if size != "unknown" and sizes and size not in sizes:
            continue
        out.append(p)
    return out


# weakest dimensions -> functional areas a quick win could shore up
_DIM_TO_AREAS = {
    "governance_posture": {"compliance"},
    "value_pocket_clarity": {"finance_ops", "customer_service"},
    "ai_investment_maturity": {"it_ops", "engineering"},
    "data_foundation": {"knowledge", "field_ops"},
    "org_change_readiness": {"productivity", "knowledge"},
}

def c3_quick_wins(sub: Submission, dims: list[DimensionScore]) -> list[SelectedQuickWin]:
    candidates = _candidate_patterns(sub)
    # gap-aligned pre-rank: prefer patterns shoring up the weakest dimensions, then Low effort
    graded = sorted((d for d in dims if not d.informational), key=lambda d: d.score)
    preferred_areas: set[str] = set()
    for d in graded[:3]:
        preferred_areas |= _DIM_TO_AREAS.get(d.dimension, set())

    def rank(p):
        aligned = 1 if p.get("functional_area") in preferred_areas else 0
        low = 1 if p.get("implementation_effort") == "Low" else 0
        return (-aligned, -low)
    ranked = sorted(candidates, key=rank)
    picks, areas = [], set()
    for p in ranked:
        area = p.get("functional_area", p["pattern_id"])
        if area in areas:
            continue
        areas.add(area)
        picks.append(p)
        if len(picks) == 3:
            break
    selected = [
        SelectedQuickWin(
            pattern_id=p["pattern_id"], pattern_name=p["name"],
            one_line_description=p["one_line_description"],
            what_this_would_do=p["what_the_ai_does"],
            prerequisites_you_have=p.get("prerequisites", [])[:3],
            expected_outcome_range=p.get("expected_outcomes", ""),
            timeline_to_value=p.get("timeline_to_value_weeks", ""),
            implementation_effort=p.get("implementation_effort", "Low"),
            ordering_priority=i + 1, selection_confidence=0.78,
        )
        for i, p in enumerate(picks)
    ]
    if llm_available():
        try:
            selected = _c3_llm_refine(sub, dims, candidates, selected)
            logger.info(f"[C3] Used LLM for quick wins: {len(selected)} selected")
        except Exception as e:
            logger.warning(f"[C3] LLM refinement failed, using deterministic: {e}")
    else:
        logger.info(f"[C3] LLM not available, using deterministic selection: {len(selected)} wins")
    return selected


C3_SYS = (
    "You are the quick wins assistant for the DXC AI Readiness Diagnostic. From the candidate "
    "quick-win library (already filtered to the prospect's industry and size), choose the 2-3 best "
    "patterns: prioritize high-confidence, low-disruption patterns that address the weakest "
    "dimensions, and ensure functional-area variety. For each, write prospect-specific framing. "
    + VOICE + " Return JSON only."
)

def _c3_llm_refine(sub, dims, candidates, deterministic):
    from ..llm import parse_structured
    lib = [{"pattern_id": p["pattern_id"], "name": p["name"], "area": p.get("functional_area"),
            "effort": p.get("implementation_effort"), "desc": p["one_line_description"]} for p in candidates]
    user = (f"Prospect: {sub.company_name_raw} | Industry: {sub.industry_label} | Size: {sub.size_band}\n"
            f"Dimension scores:\n{_scores_text(dims)}\n\nCandidate patterns: {json.dumps(lib)}\n"
            "Select 2-3 and provide prospect-specific framing.")
    r: QuickWinResult = parse_structured(C3_SYS, [{"role": "user", "content": user}],
                                         QuickWinResult, model=settings.model_opus)
    by_id = quick_wins_by_id()
    out = []
    for i, pick in enumerate(r.selected[:3]):
        p = by_id.get(pick.pattern_id)
        if not p:
            continue
        out.append(SelectedQuickWin(
            pattern_id=p["pattern_id"], pattern_name=p["name"],
            one_line_description=p["one_line_description"],
            what_this_would_do=pick.what_this_would_do or p["what_the_ai_does"],
            prerequisites_you_have=pick.prerequisites_you_have or p.get("prerequisites", [])[:3],
            expected_outcome_range=p.get("expected_outcomes", ""),
            timeline_to_value=p.get("timeline_to_value_weeks", ""),
            implementation_effort=p.get("implementation_effort", "Low"),
            ordering_priority=i + 1, selection_confidence=pick.selection_confidence,
        ))
    return out or deterministic


# ======================================================================
# C4 — Executive narrative summary (persona-framed prose)
# ======================================================================
C4_SYS = (
    "You are the executive-summary writer for the DXC AI Readiness Diagnostic. Given an assembled "
    "scorecard (overall score and tier, six dimension scores, peer benchmarks, findings, quick wins, "
    "and the recommended next step), write a short narrative summary for the primary persona. "
    "P1 Executive sponsor: competitive position, the board narrative, where the company can lead. "
    "P2 Operational owner: implementation, architecture, governance feasibility, the path to production. "
    "P3 Financial scrutineer: return, capital allocation, value at stake, financial risk. "
    "Return a headline (one sentence) and 4-5 short paragraphs (2-4 sentences each): where they stand "
    "versus peers, the strongest foundation, the binding constraint, the near-term path, and the "
    "strategic move. Be specific to this prospect; reference real scores and names. Never state tier "
    "thresholds as numbers. " + VOICE + " Return JSON only."
)


def _peer_overall_graded(sc: Scorecard, graded: list[DimensionScore]):
    gp = [sc.peer_benchmarks[d.dimension] for d in graded if d.dimension in (sc.peer_benchmarks or {})]
    return round(sum(gp) / len(gp)) if gp else None


def c4_narrative(sub: Submission, persona: PersonaInference, sc: Scorecard) -> ExecutiveNarrative:
    if llm_available():
        from ..llm import parse_structured
        user = (f"Prospect: {sc.company_name} | Industry: {sc.industry_label} | "
                f"Primary persona: {persona.primary_persona} ({persona.framing_preference})\n\n"
                f"Overall: {sc.overall_score}/100 {sc.overall_tier}. {sc.peer_reference}\n"
                f"Dimensions:\n{_scores_text(sc.dimensions)}\n\n"
                f"Findings: {json.dumps([{'h': f.headline, 'b': f.body} for f in sc.findings])[:1800]}\n"
                f"Quick wins: {json.dumps([{'n': q.pattern_name, 'o': q.expected_outcome_range} for q in sc.quick_wins])}\n"
                f"Recommended next step: {sc.recommended_next_step.body} ({sc.recommended_next_step.duration_estimate_weeks})\n\n"
                "Write the headline and paragraphs.")
        try:
            r: ExecutiveNarrative = parse_structured(C4_SYS, [{"role": "user", "content": user}],
                                                     ExecutiveNarrative, model=settings.model_opus, max_tokens=4000)
            if r.paragraphs:
                logger.info(f"[C4] Used LLM for narrative: {len(r.paragraphs)} paragraphs")
                return r
        except Exception as e:
            logger.warning(f"[C4] LLM failed, falling back to deterministic: {e}")
    else:
        logger.info("[C4] LLM not available, using deterministic fallback")
    return _narrative_fallback(sub, persona, sc)


def _narrative_fallback(sub: Submission, persona: PersonaInference, sc: Scorecard) -> ExecutiveNarrative:
    company = sc.company_name
    graded = [d for d in sc.dimensions if not d.informational]
    if not graded:
        return ExecutiveNarrative(headline=f"{company} AI readiness summary",
                                  paragraphs=[f"{company} is at the {sc.overall_tier} stage, scoring {sc.overall_score} of 100."])
    strongest = max(graded, key=lambda d: d.score)
    weakest = min(graded, key=lambda d: d.score)
    peer = _peer_overall_graded(sc, graded)
    pos = ""
    if peer is not None:
        diff = sc.overall_score - peer
        pos = (f", {abs(diff)} points {'ahead of' if diff > 0 else 'behind' if diff < 0 else 'in line with'} "
               f"the peer average of {peer}") if diff else f", in line with the peer average of {peer}"
    qw = sc.quick_wins[:3]
    qw_names = ", ".join(q.pattern_name for q in qw) or "the operational patterns identified"
    qw_outcomes = "; ".join(f"{q.pattern_name} ({q.expected_outcome_range})" for q in qw if q.expected_outcome_range)
    rec = sc.recommended_next_step
    rec_body = rec.body or "a scoped Discovery engagement."
    p = persona.primary_persona
    stand = f"{company} is at the {sc.overall_tier} stage of AI readiness, scoring {sc.overall_score} of 100{pos}."

    if p == "P3":
        headline = (f"{company} is at the {sc.overall_tier} stage of AI readiness, with near-term payback available "
                    f"and the larger value gated by {weakest.label.lower()}.")
        paras = [
            f"{stand} The relevant question for capital allocation is where investment converts to return fastest, and where risk is concentrated.",
            f"{strongest.label} ({strongest.score} of 100) is where {company} already holds the assets to capture value at low marginal cost. It is the lowest-risk place to show return.",
            f"{weakest.label} ({weakest.score} of 100) is the largest source of unrealized return and of governance risk. Spending against AI without closing it would compound cost rather than value.",
            f"In the next 90 days, {qw_outcomes or qw_names} carry near-term, measurable payback and build the track record a larger investment case rests on.",
            f"The structural move is {rec_body} Over {rec.duration_estimate_weeks} it sizes the value pockets and the investment envelope, so the board can allocate against a business case rather than a forecast.",
        ]
    elif p == "P2":
        headline = (f"{company} is at the {sc.overall_tier} stage: real experimentation, with {weakest.label.lower()} "
                    f"the constraint on scaling to production.")
        paras = [
            f"{stand} The priority now is turning experimentation into dependable production capability.",
            f"{strongest.label} ({strongest.score} of 100) is the most production-ready part of your estate, and the natural place to scale a proven pattern horizontally.",
            f"{weakest.label} ({weakest.score} of 100) is the binding constraint on scaling safely. Addressing it is prerequisite, not parallel work.",
            f"In the next 90 days, {qw_names} are high-confidence patterns with documented enterprise deployments that fit your current architecture and prove delivery.",
            f"The next step is {rec_body} Over {rec.duration_estimate_weeks} it scopes the build sequence and governance design to close the gap and put value pockets into production.",
        ]
    else:  # P1
        headline = f"{company} is at the {sc.overall_tier} stage of AI readiness, with a clear first move to take to the board."
        paras = [
            f"{stand} The question for the board is less whether to invest in AI and more where {company} can build a durable advantage first.",
            f"Your strongest ground is {strongest.label.lower()} ({strongest.score} of 100). It is the credible base for a visible early win, and the easiest part of the story to back.",
            f"The gap that most limits ambition is {weakest.label.lower()} ({weakest.score} of 100). Until it is closed, AI value stays episodic rather than compounding across the business.",
            f"In the next 90 days, {qw_names} are high-confidence moves that prove execution and build momentum without committing to a long program.",
            f"The strategic step is {rec_body} Over {rec.duration_estimate_weeks} it gives the board a sized, sequenced roadmap rather than a list of pilots.",
        ]
    return ExecutiveNarrative(headline=headline, paragraphs=paras)


# ======================================================================
# D2 — Validation / QA
# ======================================================================
def d2_validate(scorecard) -> ValidationOutput:
    flags: list[ValidationFlag] = []
    if not scorecard.findings:
        flags.append(ValidationFlag(severity="HIGH", category="internal_consistency",
                                    location="findings", concern="No findings produced."))
    if len(scorecard.findings) < 3:
        flags.append(ValidationFlag(severity="MEDIUM", category="internal_consistency",
                                    location="findings", concern="Fewer than 3 findings."))
    if not scorecard.recommended_next_step.body.strip():
        flags.append(ValidationFlag(severity="HIGH", category="internal_consistency",
                                    location="recommended_next_step", concern="Empty recommendation."))
    if not scorecard.quick_wins:
        flags.append(ValidationFlag(severity="MEDIUM", category="internal_consistency",
                                    location="quick_wins", concern="No quick wins selected."))
    for d in scorecard.dimensions:
        if not (0 <= d.score <= 100):
            flags.append(ValidationFlag(severity="CRITICAL", category="numerical_sanity",
                                        location=d.dimension, concern=f"Score out of range: {d.score}."))
    crit = any(f.severity == "CRITICAL" for f in flags)
    status = "requires_revision" if crit else ("passed_with_flags" if flags else "passed")
    prio = "expedited" if crit else "standard"
    return ValidationOutput(overall_status=status, flags=flags, partner_review_priority=prio)
