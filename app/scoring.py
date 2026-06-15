"""Deterministic scoring engine (Companion 01).

dimension score = weighted average of answered graded questions, with within-dimension
weights renormalized over the questions actually asked (handles skip/branch logic).
Regulatory Complexity is informational: scored from selected frameworks + sovereignty.
Overall = weighted average of the six dimension scores using the overall dimension weights.
"""
from __future__ import annotations
from typing import Iterable

from .content import load_question_pool, questions_by_id
from .models import DimensionScore, QuestionResponse, tier_for, DIMENSION_IDS, DIMENSION_LABELS


def _answer_map(responses: Iterable[QuestionResponse]) -> dict[str, QuestionResponse]:
    return {r.question_id: r for r in responses}


def _option_score(q: dict, resp: QuestionResponse) -> int | None:
    qtype = q["type"]
    if qtype == "single_select":
        if not resp.option_id:
            return None
        for o in q.get("options", []):
            if o["id"] == resp.option_id:
                return int(o["score"])
        return None
    if qtype == "scale_1_5":
        if resp.scale_value is None:
            return None
        for a in q.get("scale_anchors", []):
            if a["value"] == resp.scale_value:
                return int(a["score"])
        return None
    return None  # multi_select / open_short are not graded numerically here


def _regulatory_score(answers: dict[str, QuestionResponse]) -> tuple[int, str]:
    """Informational complexity from Q6.1 frameworks + Q6.2 sovereignty (0-100)."""
    pool = questions_by_id()
    total = 0
    selected: list[str] = []
    q61 = pool.get("Q6.1")
    r61 = answers.get("Q6.1")
    if q61 and r61 and r61.option_ids:
        comp = {o["id"]: o.get("complexity", 0) for o in q61["options"]}
        for oid in r61.option_ids:
            if oid == "none":
                continue
            total += comp.get(oid, 0)
            selected.append(oid)
    q62 = pool.get("Q6.2")
    r62 = answers.get("Q6.2")
    if q62 and r62 and r62.option_id:
        comp = {o["id"]: o.get("complexity", 0) for o in q62["options"]}
        total += comp.get(r62.option_id, 0)
    score = max(0, min(100, total))
    note = f"{len(selected)} framework(s) apply" if selected else "No specific AI regulation indicated"
    return score, note


def score_dimensions(responses: list[QuestionResponse]) -> list[DimensionScore]:
    pool = load_question_pool()
    answers = _answer_map(responses)
    questions = pool["questions"]

    out: list[DimensionScore] = []
    for dim in DIMENSION_IDS:
        if dim == "regulatory_complexity":
            score, note = _regulatory_score(answers)
            out.append(DimensionScore(
                dimension=dim, score=score, questionnaire_derived=score,
                reasoning=note, informational=True, confidence=0.85,
            ).finalize())
            continue

        dim_qs = [q for q in questions if q["dimension"] == dim]
        weighted_sum = 0.0
        weight_total = 0.0
        for q in dim_qs:
            resp = answers.get(q["id"])
            if resp is None:
                continue
            s = _option_score(q, resp)
            if s is None:
                continue
            w = float(q["dimension_weight"])
            weighted_sum += s * w
            weight_total += w
        score = round(weighted_sum / weight_total) if weight_total > 0 else 0
        out.append(DimensionScore(
            dimension=dim, score=score, questionnaire_derived=score,
            reasoning="Questionnaire-derived score (weighted by question diagnostic value).",
            confidence=0.85 if weight_total > 0 else 0.3,
        ).finalize())
    return out


def overall_score(dimensions: list[DimensionScore]) -> int:
    pool = load_question_pool()
    dim_weights = {k: v["weight"] for k, v in pool["dimensions"].items()}
    num = sum(d.score * dim_weights.get(d.dimension, 0) for d in dimensions)
    den = sum(dim_weights.get(d.dimension, 0) for d in dimensions)
    return round(num / den) if den else 0


def apply_research_adjustments(dimensions: list[DimensionScore], adjustments: dict[str, int]) -> None:
    """C2 may nudge questionnaire-derived scores using research signals (bounded ±25)."""
    for d in dimensions:
        adj = max(-25, min(25, int(adjustments.get(d.dimension, 0))))
        if adj:
            d.research_adjustment = adj
            d.score = max(0, min(100, d.questionnaire_derived + adj))
            d.finalize()
