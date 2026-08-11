# DXC AI Readiness Diagnostic — V0

Prospect-facing AI readiness assessment built to **PRD V5 + Companions 01–05 + the UI brief**.
A prospect completes a 20-question assessment; the engine produces a peer-benchmarked,
six-dimension scorecard (tiers: Emerging / Developing / Established / Leading) with findings,
a recommended next step, and 90-day quick wins. A senior partner reviews before delivery.

> Built and verified end-to-end. Runs **offline** (deterministic scoring + deterministic
> agent fallbacks) or on **Claude** when `ANTHROPIC_API_KEY` is set (A2/C2/C3 enrich the output).

## Project links

| Link | What it is |
|---|---|
| [Value Realization and Program Management-AdvisoryX Agentic Transformation](https://dxcportal.sharepoint.com/:f:/r/sites/ValueRealizationandProgramManagement-AdvisoryXAgenticTransformation/Shared%20Documents/00%20DIAGNOSTIC?d=w519d611923a940aab4266323b235ae1c&csf=1&web=1&e=YyfnmR) | SharePoint — the `00 DIAGNOSTIC` folder. Source material and deliverables outside this repository. DXC sign-in required. |
| [docs/INDEX.md](docs/INDEX.md) | Every document in this repository, with date, phase and status. |
| [deploy/aws/DEPLOY_AWS.md](deploy/aws/DEPLOY_AWS.md) | Deploying to AWS, and taking it down. |
| [docs/architecture/architecture_topics.md](docs/architecture/architecture_topics.md) | The ten architectural decisions still open. |

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
  api.py           FastAPI: /api/questions, /api/assess, /api/fixture/{name}; serves web/
  config.py        model tiering + llm_available()
  llm.py           LLM wrapper (adaptive thinking, structured outputs)
  models.py        Pydantic schemas (Companion 05 subset)
  content.py       loaders (question pool, quick-wins library, fixtures)
  scoring.py       deterministic dimension + overall scoring (Companion 01)
  benchmarks.py    indicative peer benchmarks — hardcoded for V0, not yet data-driven
  research.py      B1 (SEC EDGAR financials) + B2 (news), best-effort; optional, off by default
  agents/__init__.py  A2 / C2 / C3 / D2 (Companion 04 prompts + offline fallbacks)
  orchestrator.py  the V0 pipeline
  scorecard.py     server-side scorecard render (Companion 03) -> HTML
  pdf.py           PDF deliverable (D1 render) via reportlab
  store.py         session persistence — in-memory locally, DynamoDB when AIDIAG_DDB_TABLE is set
  assets/          runtime assets (the brand-mark SVG pdf.py loads) — see app/assets/README.md
content/
  question_pool.yaml         20 questions, options, scores, within-dimension weights (Companion 01)
  quick_wins.yaml            15 quick-win patterns (Companion 02)
  interview_definition.yaml  voice-interview script for the ElevenLabs agent
  consent_copy.md            consent text C-1 to C-5
fixtures/          meridianfs | northerncare | aureliantech (Companion 03 demo scenarios)
web/
  src/screens/     Landing, Assessment, Submitted, Scorecard, QuickWins, VoiceInterview
  src/components/  Btn, DxcLogo, Wordmark, Radar, TierBadge, ValueDifficulty2x2
  index.html       Vite entry point (built by the Docker UI stage into web/dist)
  review.html      partner review dashboard — standalone, not part of the Vite build
scripts/
  run_chat_cli.py    terminal pipeline runner
  gen_voice_agent.py ElevenLabs agent config generator
tests/
  test_smoke.py             content integrity + deterministic scoring vs Companion targets
  test_store.py             session store
  test_evaluation_suite.py  audit findings — security, concurrency, data integrity
deploy/aws/        AWS provisioning, teardown and validation — see deploy/aws/DEPLOY_AWS.md
terraform/         IaC for the deployed stack: ECS Fargate, DynamoDB, ECR, IAM
docs/              all project documentation — see docs/INDEX.md
assets/            DXC brand kit (design source; nothing reads it at runtime)
```

## Status / next
- **Done & verified:** question pool + scoring engine (offline), A2/C2/C3/D2 agents with fallbacks,
  pipeline, scorecard render, FastAPI, React UI (6 screens), three demo fixtures, tests.
- **Enrich with the API key:** set `ANTHROPIC_API_KEY` so C2 writes prospect-specific findings and the
  recommended next step, and C3 selects gap-aligned quick wins per the Companion 04 prompts.
- **Deferred (per PRD/Companions):** real research tools B1/B2/B3 (SEC EDGAR/news/tech-stack, currently
  optional/off), B4/B5, C1 industry library, D1 persona-variant PDFs, E1–E3 downstream, partner-review
  dashboard (Screen 6), peer-benchmark data (V0.5+).

## Going to PROD

The application currently uses **Amazon SES in sandbox mode**, which limits email sending to verified email identities. The `/api/test-email` endpoint is live and operational with verified recipients.

**To send transactional emails to arbitrary recipients in production:**

1. **Request production access for SES:** [Moving out of the Amazon SES sandbox](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)
2. Once approved:
   - Verify the sender domain (dxc.com) with DKIM signing
   - Remove test_recipient_addresses from `terraform/terraform.tfvars`
   - Revert IAM policy in `terraform/ses.tf` to sender identity only
   - Update `terraform/ecs.tf` to configure the SES configuration set (delivery tracking, suppression list)

**Specification:** See [docs/specs/SPEC_outbound_mail.md](docs/specs/SPEC_outbound_mail.md) for the full mail transport design (§20.4 covers the IAM scope for sandbox vs. production).
