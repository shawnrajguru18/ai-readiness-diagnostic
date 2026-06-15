"""Offline tests (no API key): content integrity + deterministic scoring vs Companion targets."""
from app.content import load_question_pool, questions_by_id, load_quick_wins
from app.models import QuestionResponse, tier_for
from app.scoring import score_dimensions, overall_score


def _responses(fixture_name):
    from app.content import load_fixture
    fx = load_fixture(fixture_name)
    out = []
    for qid, a in fx["responses"].items():
        out.append(QuestionResponse(
            question_id=qid,
            option_id=a.get("option_id"),
            option_ids=a.get("option_ids", []),
            scale_value=a.get("scale_value"),
            text=a.get("text"),
        ))
    return out


def _dim(dims, key):
    return next(d for d in dims if d.dimension == key)


# ---------- content integrity ----------
def test_pool_has_20_questions_and_6_dimensions():
    pool = load_question_pool()
    assert len(pool["questions"]) == 20
    assert len(pool["dimensions"]) == 6


def test_within_dimension_weights_sum_to_one():
    pool = load_question_pool()
    from collections import defaultdict
    sums = defaultdict(float)
    for q in pool["questions"]:
        sums[q["dimension"]] += q["dimension_weight"]
    for dim, s in sums.items():
        assert abs(s - 1.0) < 1e-6, (dim, s)


def test_overall_dimension_weights_sum_to_one():
    pool = load_question_pool()
    s = sum(d["weight"] for d in pool["dimensions"].values())
    assert abs(s - 1.0) < 1e-6, s


def test_quick_wins_library_has_15():
    assert len(load_quick_wins()) == 15


# ---------- deterministic scoring: MeridianFS ----------
def test_meridianfs_scores_and_tiers():
    dims = score_dimensions(_responses("meridianfs"))
    got = {d.dimension: d.score for d in dims}
    target = dict(data_foundation=52, governance_posture=38, ai_investment_maturity=62,
                  org_change_readiness=55, value_pocket_clarity=48, regulatory_complexity=72)
    for k, t in target.items():
        assert abs(got[k] - t) <= 6, (k, got[k], t)
    assert _dim(dims, "governance_posture").tier == "Emerging"
    assert _dim(dims, "ai_investment_maturity").tier == "Established"
    assert _dim(dims, "regulatory_complexity").tier == "Established"
    assert tier_for(overall_score(dims)) == "Developing"


# ---------- skip logic: NorthernCare (Q3.1=A skips Q3.2/Q3.3) ----------
def test_northerncare_skip_logic_and_emerging_data():
    resp = _responses("northerncare")
    answered = {r.question_id for r in resp}
    assert "Q3.2" not in answered and "Q3.3" not in answered  # skip honored in fixture
    dims = score_dimensions(resp)
    # AI maturity scored from only Q3.1 + Q3.4 (renormalized) -> ~33, Emerging
    assert _dim(dims, "ai_investment_maturity").tier == "Emerging"
    assert _dim(dims, "data_foundation").tier == "Emerging"
    assert _dim(dims, "regulatory_complexity").tier == "Leading"  # high constraint


# ---------- AurelianTech: established, governance gap ----------
def test_aureliantech_established_with_governance_gap():
    dims = score_dimensions(_responses("aureliantech"))
    assert _dim(dims, "data_foundation").tier == "Established"
    assert _dim(dims, "org_change_readiness").tier == "Leading"
    assert _dim(dims, "governance_posture").score < 50  # the notable gap
    assert tier_for(overall_score(dims)) == "Established"
