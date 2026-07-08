"""The DynamoDB backend serializes each record to a JSON blob and rehydrates a
live Session on read. This verifies that round-trip without needing AWS, using a
real pipeline-produced Session (offline/deterministic)."""
from app.content import load_fixture
from app.orchestrator import build_session, run_pipeline
from app.store import _rec_to_json, _rec_from_json, _MemoryStore
from app.models import Session


def _make_record(sid="testid0001"):
    fx = load_fixture("meridianfs")
    session, hint = build_session(fx.get("submission", {}), fx.get("consent", {}),
                                  fx.get("responses", {}), fx.get("persona_hint"))
    run_pipeline(session, persona_hint=hint)
    return {
        "id": sid,
        "session": session,
        "scorecard": {"company_name": session.scorecard.company_name,
                      "overall_score": session.scorecard.overall_score},
        "created_at": "2026-01-01T00:00:00+00:00",
        "status": "partner_review_queued",
        "partner_note": "",
    }


def test_record_json_round_trip_preserves_session():
    rec = _make_record()
    restored = _rec_from_json(_rec_to_json(rec))

    assert restored["id"] == rec["id"]
    assert restored["status"] == rec["status"]
    assert isinstance(restored["session"], Session)
    # full Session equality: every nested model/field survives the round-trip
    assert restored["session"] == rec["session"]
    # scores are ints, confidences are floats — types must be preserved, not stringified
    assert restored["session"].scorecard.overall_score == rec["session"].scorecard.overall_score
    assert restored["session"].scorecard.dimensions[0].confidence == \
        rec["session"].scorecard.dimensions[0].confidence


def test_memory_store_put_get_and_mutation():
    s = _MemoryStore()
    rec = _make_record("mem0000001")
    s.put(rec)
    assert s.get("mem0000001") is rec          # live object, mutations visible
    assert s.get("missing") is None
    rec["status"] = "approved_for_delivery"
    s.save(rec)
    assert s.get("mem0000001")["status"] == "approved_for_delivery"
    assert len(s.all_records()) == 1
