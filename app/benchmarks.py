"""Indicative peer benchmarks (V0).

Per-dimension peer averages by industry, used to plot "you vs peer" bars on the
scorecard and the per-dimension comparison in the findings appendix. These are
indicative reference figures for the diagnostic; the anonymized peer-benchmark
library (consent C-2) replaces them once volume accrues. The overall peer average
shown on the cover is derived from these figures with the same dimension weights
used for the prospect's own overall score, so the two numbers are comparable.
"""
from __future__ import annotations
from .content import load_question_pool

# dimension id -> peer average (0-100), by industry tag.
PEER_BENCHMARKS: dict[str, dict[str, int]] = {
    "FS": {"data_foundation": 62, "governance_posture": 60, "ai_investment_maturity": 55,
           "org_change_readiness": 54, "value_pocket_clarity": 56, "regulatory_complexity": 62},
    "HLS": {"data_foundation": 42, "governance_posture": 40, "ai_investment_maturity": 34,
            "org_change_readiness": 36, "value_pocket_clarity": 38, "regulatory_complexity": 44},
    "MFG": {"data_foundation": 52, "governance_posture": 46, "ai_investment_maturity": 47,
            "org_change_readiness": 48, "value_pocket_clarity": 50, "regulatory_complexity": 52},
    "All": {"data_foundation": 50, "governance_posture": 48, "ai_investment_maturity": 46,
            "org_change_readiness": 47, "value_pocket_clarity": 48, "regulatory_complexity": 50},
}

# Sample descriptor per industry tag: (cohort label, n).
PEER_COHORTS: dict[str, tuple[str, int]] = {
    "FS": ("large US financial services", 42),
    "HLS": ("large US health systems", 18),
    "MFG": ("large manufacturers", 27),
    "All": ("a cross-industry sample", 87),
}


def peer_benchmarks(industry_tag: str) -> dict[str, int]:
    return dict(PEER_BENCHMARKS.get(industry_tag, PEER_BENCHMARKS["All"]))


def peer_overall(industry_tag: str) -> int:
    """Overall peer average, weighted exactly like the prospect's overall score."""
    bm = peer_benchmarks(industry_tag)
    weights = {k: v["weight"] for k, v in load_question_pool()["dimensions"].items()}
    num = sum(bm.get(dim, 0) * w for dim, w in weights.items())
    den = sum(weights.values())
    return round(num / den) if den else 0


def peer_reference(industry_tag: str) -> str:
    label, n = PEER_COHORTS.get(industry_tag, PEER_COHORTS["All"])
    return f"Peer average for {label}: {peer_overall(industry_tag)} (n={n})"
