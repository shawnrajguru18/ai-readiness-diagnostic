# DXC AI Readiness Diagnostic — V0

Prospect-facing AI readiness assessment built to **PRD V5 + Companions 01–05 + the UI brief**.
A prospect completes a 20-question assessment; the engine produces a peer-benchmarked,
six-dimension scorecard (tiers: Emerging / Developing / Established / Leading) with findings,
a recommended next step, and 90-day quick wins. A senior partner reviews before delivery.

> Built and verified end-to-end. Runs **offline** (deterministic scoring + deterministic
> agent fallbacks) or on **Claude** when `ANTHROPIC_API_KEY` is set (A2/C2/C3 enrich the output).

## Architecture (Companion-aligned)

```
Intake (A1) → Persona (A2) → [Research B1/B2/B3 — optional] → Deterministic scoring (Companion 01)
   → Synthesis C2 (findings + recommended next step) → Quick Wins C3 → Scorecard (D1) → Validation (D2)
   → Partner review
```

- **Six dimensions, weighted** (Data Foundation .20, Governance Posture .20, AI Investment Maturity .18,
  Org Change Readiness .15, Value-Pocket Clarity .17, Regulatory Complexity .10 informational).
- **Deterministic scoring**: option scores × within-dimension weights, renormalized over questions asked
  (handles skip/branch). Verified to reproduce the Companion demo scenarios (MeridianFS 52/38/61/53/46/72).
- **Model tiering** (Companion 04): Opus → C2/C3/D2, Sonnet → A2/B/D1, Haiku → A1. IDs in `app/config.py`.

## Run it

```bash
. .venv/Scripts/activate                       # venv already created with deps
cp .env.example .env                            # optional: add ANTHROPIC_API_KEY to enable LLM agents

# Web app (the investor-day demo) — React UI + API:
python -m uvicorn app.api:app --reload          # then open http://localhost:8000

# Or run the pipeline on a demo fixture from the terminal:
python -m scripts.run_chat_cli --fixture meridianfs     # also: northerncare | aureliantech

# Tests (offline, no key):
python -m pytest -q
```

## Layout

```
app/
  config.py        model tiering + llm_available()
  llm.py           Anthropic wrapper (adaptive thinking, structured outputs)
  models.py        Pydantic schemas (Companion 05 subset)
  content.py       loaders (question pool, quick-wins library, fixtures)
  scoring.py       deterministic dimension + overall scoring (Companion 01)
  agents/__init__.py  A2 / C2 / C3 / D2 (Companion 04 prompts + offline fallbacks)
  orchestrator.py  the V0 pipeline
  scorecard.py     server-side scorecard render (Companion 03) -> HTML/PDF
  api.py           FastAPI: /api/questions, /api/assess, /api/fixture/{name}, serves web/
content/
  question_pool.yaml   20 questions, options, scores, within-dimension weights (Companion 01)
  quick_wins.yaml      15 quick-win patterns (Companion 02)
fixtures/          meridianfs | northerncare | aureliantech (Companion 03 demo scenarios)
web/index.html     React UI (5 screens: Landing, Questionnaire, Submitted, Scorecard, Quick Wins)
scripts/run_chat_cli.py   terminal pipeline runner
tests/test_smoke.py       content integrity + deterministic scoring vs Companion targets
```

## Status / next
- **Done & verified:** question pool + scoring engine (offline), A2/C2/C3/D2 agents with fallbacks,
  pipeline, scorecard render, FastAPI, React UI (5 screens), three demo fixtures, tests.
- **Enrich with the API key:** set `ANTHROPIC_API_KEY` so C2 writes prospect-specific findings and the
  recommended next step, and C3 selects gap-aligned quick wins per the Companion 04 prompts.
- **Deferred (per PRD/Companions):** real research tools B1/B2/B3 (SEC EDGAR/news/tech-stack, currently
  optional/off), B4/B5, C1 industry library, D1 persona-variant PDFs, E1–E3 downstream, partner-review
  dashboard (Screen 6), peer-benchmark data (V0.5+).
```
