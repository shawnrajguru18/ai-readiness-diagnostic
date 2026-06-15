"""Run the assessment pipeline on a demo fixture and write the scorecard HTML.

  python -m scripts.run_chat_cli --fixture meridianfs
  python -m scripts.run_chat_cli --fixture northerncare
  python -m scripts.run_chat_cli --fixture aureliantech

Runs offline (deterministic) unless ANTHROPIC_API_KEY is set, in which case the
A2/C2/C3 agents enrich the output via Claude.
"""
from __future__ import annotations
import argparse

from app.content import load_fixture
from app.orchestrator import build_session, run_pipeline
from app.scorecard import save_scorecard


def main() -> None:
    ap = argparse.ArgumentParser(description="DXC AI Readiness Diagnostic — assessment runner")
    ap.add_argument("--fixture", required=True, help="meridianfs | northerncare | aureliantech")
    args = ap.parse_args()

    fx = load_fixture(args.fixture)
    session, hint = build_session(fx.get("submission", {}), fx.get("consent", {}),
                                  fx.get("responses", {}), fx.get("persona_hint"))
    print(f"== {session.submission.company_name_raw} ==")
    run_pipeline(session, persona_hint=hint, log=print)
    sc = session.scorecard
    print(f"\nOverall: {sc.overall_score} ({sc.overall_tier})")
    for d in sc.dimensions:
        print(f"  {d.label:32s} {d.score:3d}  {d.tier}")
    print("\nFindings:")
    for f in sc.findings:
        print(f"  - {f.headline}")
    print("\nQuick wins:")
    for q in sc.quick_wins:
        print(f"  - {q.pattern_name} ({q.timeline_to_value})")
    path = save_scorecard(sc)
    print(f"\nScorecard written -> {path}")


if __name__ == "__main__":
    main()
