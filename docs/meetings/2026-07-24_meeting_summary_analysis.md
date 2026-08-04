# Meeting Summary Analysis — 2026-07-24

## Project Overview

**AdvisoryX AI Diagnostic** is a prospect-facing, voice-based AI maturity assessment (POC complete, MVP hardening phase). It collects executive input via a 20-question questionnaire, produces a peer-benchmarked six-dimension scorecard with findings and quick-win recommendations, then routes to a human advisor for follow-up within 24 hours.

**Tech stack:**
- Backend: Python (FastAPI, Pydantic, orchestrator pattern)
- Frontend: React (vendored, bundled locally — no external CDN)
- Cloud: AWS Bedrock (Claude models) + Terraform IaC
- Voice layer: ElevenLabs agentic platform (external)

**Current status:** V0 complete and verified (offline deterministic pipeline + optional LLM enrichment via Bedrock). Ready for MVP hardening (3 weeks) → production release (week 5).

---

## Answers to Key Questions from the Meeting

### 1. **Where does the peer benchmark data come from, and who owns it?**

**Current state (V0):**
- Hardcoded "indicative reference figures" in `app/benchmarks.py` — per-dimension peer averages by industry (FS, HLS, MFG, All).
- Three industry cohorts: FS (42 firms, large US financial services), HLS (18 firms, large US health systems), MFG (27 firms, large manufacturers), All (87 cross-industry).
- These figures are **temporary placeholders** for the diagnostic output to be "useful enough to be credible, but incomplete enough that the client books a follow-up."

**Path to V0.5+:**
- The code comment says: *"the anonymized peer-benchmark library (consent C-2) replaces them once volume accrues."*
- Implication: live feedback loop. Early customers consent to anonymized benchmarking (consent form C-2 not yet written); once volume reaches threshold (undefined), the hardcoded figures are replaced with aggregate data.

**Ownership & data source:**
- **Currently unassigned.** This is a J2 action item from the meeting — identify the owner and commit to a methodology before customer-zero testing.
- **Option A (simple):** Use existing DXC engagement data (financials, manufacturing, healthcare) — already risk-adjusted, no new consent, reliable. Requires audit trail but data exists.
- **Option B (market-grade):** Subscribe to third-party benchmark (Gartner, McKinsey, etc.) — credible but costly, licensing/usage questions, lag in updates.
- **Option C (community):** Build peer cohort on-the-fly as volume accrues — the current design, requires consent engineering for C-2.

**Recommendation:** Begin with Option A (DXC proprietary historical data), document the cohort composition and date, set a growth trigger for Option C (e.g., "replace with live community at 50 new assessments"). This ships the MVP without external dependencies.

---

### 2. **Five or six assessment domains — and what is the maturity scoring model?**

**Confirmed: SIX dimensions (tested & verified):**

1. **Data Foundation** (weight: 0.20) — data architecture, infrastructure, governance readiness.
2. **Governance Posture** (weight: 0.20) — decision frameworks, oversight, risk controls.
3. **AI Investment Maturity** (weight: 0.18) — budget allocation, model selection, pilots.
4. **Org Change Readiness** (weight: 0.15) — skill gaps, re-skilling, change management.
5. **Value-Pocket Clarity** (weight: 0.17) — business case definition, process prioritization.
6. **Regulatory Complexity** (weight: 0.10) — informational only, does not affect overall score.

**Scoring model (deterministic, verified vs Companion 03 demo scenarios):**
- Each question in the pool maps to one dimension and carries a numeric option-score (0–100).
- Dimension score = (sum of option-scores for that dimension) / (count of questions asked in that dimension).
  - Handles skips/branches: renormalized over questions *actually asked*.
- Overall score = Σ(dimension_score × dimension_weight), weighted by the six weights above.
- Tiers: Emerging (0–39), Developing (40–59), Established (60–79), Leading (80–100).

**Verified against the MeridianFS fixture (Companion 03 demo):** Expected scores 52/38/61/53/46/72 → matches exactly.

---

### 3. **Deterministic question lists for MVP — at what point (and on what trigger) does it become agentic?**

**MVP (V0 — now):**
- **Deterministic:** 20 hardcoded question pool (Companion 01), weighted by dimension, branch-aware.
- **Agentic agents running:**
  - **A2 (Persona):** Infers primary persona (P1 Executive / P2 Technical / P3 Finance) from role + company context. Falls back to rule-based if LLM unavailable.
  - **C2 (Synthesis):** Produces 3–5 prospect-specific findings from dimension scores. Uses Claude Opus if Bedrock available; deterministic fallback (weakest/strongest dimension + generic template).
  - **C3 (Quick Wins):** Selects 2–3 patterns from the 15-pattern library (Companion 02) per prospect characteristics (industry, size, low-score dimensions, tech stack). Calls Claude Opus; deterministic fallback (round-robin top patterns).
  - **D2 (Validation):** QA check for hallucination / red-flag outputs. Not yet implemented in MVP (deferred).

**Deferred (V0.5+, listed as "Deferred" in README):**
- **B1/B2/B3 (Research):** EDGAR / news / tech-stack research agents — optional, gated by env var `AIDIAG_ENABLE_RESEARCH=false` by default.
- **Agentic question generation:** The PRD hints at adaptive, LLM-generated questions per role (beyond the deterministic 20-question pool). Not in MVP scope.

**Transition trigger:** Undefined. Likely after customer-zero feedback and confidence in hallucination guards (D2 validation).

---

### 4. **Who are the respondents' identities and how do we authenticate external executives?**

**Current state (UNIMPLEMENTED):**
- README explicitly states: **"Auth: None today — exposed via raw IP/URL."**
- The API has no authentication layer. Routes POST `/api/assess` and GET `/api/fixture/{name}` are open.

**Status & decision path:**
- A4 action item (Alex) due week of 28 Jul: "Close the authentication decision — Entra ID vs external-user identity."
- The concern: Entra ID works for DXC employees (internal customer-zero) but external client executives may not have DXC credentials.

**Likely approach for MVP:**
- **Customer-zero (DXC employees):** Entra ID (simple, leverages existing identity infra).
- **External clients (post-MVP):** TBD — options include:
  - Passwordless invite link (email + one-time token).
  - SAML/OIDC federation (if client has their own IdP).
  - DXC-issued short-lived credentials.

**Ownership & timeline:** Alex Schick, week of 28 Jul. This is a blocker for the security story and likely the frontend sign-in flow.

---

### 5. **Data retention, residency and confidentiality rules for interview transcripts and voice recordings?**

**Current state (NOT DISCUSSED / UNSPECIFIED):**
- The codebase shows a `ConsentRecord` model with `c1_use_for_scorecard`, `c2_use_for_benchmarking`, etc., but consent *form* language is not in the repo.
- Voice recordings are handled by ElevenLabs (external platform), not stored in the diagnostic backend.
- The orchestrator stores a `Session` object (scores, findings, metadata) in an in-memory store (`app/store.py`) — no database, no explicit purge.

**Gaps requiring resolution before customer-zero (J3 action item — joint/unassigned):**

1. **Retention policy:** How long are scores/transcripts kept? 30 days? 1 year? Forever for benchmarking?
2. **Residency:** Where is the data stored? AWS region? On-premise?
3. **Tenancy separation:** If Bank of America's CFO and CTO both assess, is their data separated in the backend? (Appears not in V0 — both responses are aggregated to the "company".)
4. **Voice recordings:** Who owns them? Are they deleted after transcript? Can they be reused for training?
5. **Consent form language:** What does C-2 (consent to use for benchmarking) actually permit? Can findings be shared with third parties?
6. **Executive privilege:** Can findings from a CFO's assessment be disclosed to the CIO without permission?

**Recommendation:** DXC Legal should draft consent language before customer-zero. The diagnostic is explicitly positioned as a *sales funnel asset*, so there's a strong case for retention (e.g., "keep for 12 months to inform delivery"), but it needs explicit buy-in from the prospect.

---

### 6. **Model invocation failures (mentioned by Shawn)**

**Current architecture:**
- Models called via AWS Bedrock (not Anthropic API).
- Uses `AnthropicBedrock` SDK client with SigV4 auth (IAM-based, no API key).
- Model IDs are **inference profile ARNs** (e.g., `arn:aws:bedrock:us-east-1::inference-profile/anthropic.claude-opus-4-8-v1:0`).

**Likely causes of failures Shawn observed:**

1. **Missing AWS credentials:** If Bedrock client is initialized without valid IAM credentials (env vars, IAM role, or credential file), all model calls fail. Check:
   - `aws sts get-caller-identity` — returns current principal.
   - Bedrock region configured (`AWS_REGION=us-east-1` by default).

2. **Inference profile ARN not available in region:** The config uses inference profiles (cross-region routing), but the region in the ARN and the configured region must match. If Bedrock isn't available in `us-east-1`, calls silently fail.

3. **IAM permissions:** User/role must have `bedrock:InvokeModel` on the specific inference profile ARN. Missing permissions return a 403 Forbidden (may appear as a silent error in logs).

4. **Model availability:** Claude 5 Sonnet + Opus 4.8 via inference profiles are very recent (this codebase was updated 2026-07-23 to use them). If the deployment is on an older AWS account, the profiles may not exist.

5. **Partial fallback:** The code gracefully falls back to deterministic outputs if LLM is unavailable, so a user wouldn't see an error — they'd just get the generic findings instead. Shawn may have observed "some calls work, some don't" if credentials are intermittently valid or the fallback is silently kicking in.

**Triage steps (S5 action item — Shawn, before 30 Jul):**

```bash
# Check if Bedrock is reachable:
aws bedrock describe-models --region us-east-1

# Check if inference profiles exist:
aws bedrock describe-models --region us-east-1 | grep inference-profile

# Test a model call directly:
aws bedrock-runtime invoke-model \
  --model-id arn:aws:bedrock:us-east-1::inference-profile/anthropic.claude-opus-4-8-v1:0 \
  --body '{"messages":[{"role":"user","content":"Hi"}]}' \
  output.json

# Check logs in CloudWatch for any Bedrock errors.
```

If the inference profiles don't exist, fall back to direct model IDs: `anthropic.claude-opus-4-8-v1:0` (without the ARN prefix).

---

### 7. **Which of the ~20 stories are MVP-blocking vs deferrable?**

**MVP-blocking (ship week 5):**
- ✅ Question pool + deterministic scoring engine (verified vs Companion 03).
- ✅ A2, C2, C3, D2 agents (with offline fallbacks).
- ✅ FastAPI backend (assessment endpoint, fixture loading, partner review queue).
- ✅ React UI (5 screens: Landing, Questionnaire, Submitted, Scorecard, Quick Wins).
- ✅ Three demo fixtures (MeridianFS, NorthernCare, AurelianTech) for investor-day demo.
- ✅ Deterministic PDF scorecard render (reportlab).
- ✅ Test suite (smoke tests + evaluation against Companion targets).

**Post-MVP (deferred):**
- ❌ B1/B2/B3 research agents (EDGAR, news, tech-stack — currently optional/off).
- ❌ B4/B5 (undefined in Companions).
- ❌ C1 industry library (dynamic context).
- ❌ D1 persona-variant PDFs (multiple PDF outputs per persona).
- ❌ E1–E3 downstream (undefined — likely post-engagement delivery).
- ❌ Partner-review dashboard (Screen 6) — backend queue exists, UI not built.
- ❌ Real peer-benchmark data (using hardcoded placeholders).
- ❌ D2 validation agent (QA check for hallucinations — currently a stub).
- ❌ ElevenLabs voice platform integration (external, being handled by Shawn + ElevenLabs directly).

**Scope note:** The engagement was *descoped from 15 weeks / 20 agents* to the current narrow focus. Alex is managing the backlog (~20 draft stories); the working assumption is that "what's in the README Done section" is MVP-blocking, everything else is deferred.

**Action item (Q6 from meeting):** Alex to explicitly tag stories with MVP-blocking vs deferrable in the backlog before week 1 closes. This is **critical** — without a clear definition of done, the five-week timeline will be at risk.

---

### 8. **Is there any test coverage or evaluation harness in the POC today?**

**Yes:**

1. **`test_smoke.py`:** End-to-end smoke tests.
   - Content integrity: question pool, quick-wins library, fixtures load without error.
   - Deterministic scoring: runs three fixtures (MeridianFS, NorthernCare, AurelianTech) against the scoring engine, asserts the output matches the *expected* scores from Companion 03.
   - Verification: the demo scenarios' scores are *exact matches*, confirming the scoring math is correct.

2. **`test_store.py`:** Session storage (store.py) round-trip tests.

3. **`test_evaluation_suite.py`:** (Not inspected in detail, but referenced in README.)

4. **Companion-aligned baselines:** Companion 03 defines three "demo scenario" scorecards (MeridianFS, NorthernCare, AurelianTech) with hand-verified scores. The test suite runs against these, so if the scoring drifts, tests fail immediately.

**What's not covered:**

- LLM outputs (A2, C2, C3) — no hallucination testing, no "expected findings" baseline.
- PDF render (reportlab) — no visual regression tests.
- React UI — no E2E tests (Cypress, Playwright, etc.).
- Voice layer (ElevenLabs) — out of scope, vendor responsibility.
- AWS Bedrock invocation — no integration tests against real Bedrock (would require AWS creds in CI).
- Auth flow — not implemented yet, so no tests.

**Recommendation:** For MVP, add:
- A "QA harness" that runs the pipeline on a few fixtures and flags outputs where LLM findings appear generic or self-contradictory (Denis's "Judge" pattern from his background).
- A Playwright E2E test covering the happy path: questionnaire → submit → scorecard view.
- A "content integrity" check: findings, quick-wins, recommendations reference dimensions by name (catch copy-paste errors).

---

## Summary of Open Items

| # | Item | Owner | Due | Severity |
|---|------|-------|-----|----------|
| 1 | Decide peer-benchmark data source & methodology | Shawn + J2 | w/c 28 Jul | HIGH — output credibility |
| 2 | Confirm 5 vs 6 dimensions & finalize question lists | Shawn + Rob + Chris | w/c 28 Jul | MEDIUM — Q pool finalized |
| 3 | Resolve auth (Entra ID vs external identity) | Alex (A4) | w/c 28 Jul | HIGH — security story |
| 4 | Define data retention, residency, consent language | Legal + J3 | Before cust-zero | HIGH — compliance gate |
| 5 | Triage model invocation failures in AWS console | Shawn (S5) | Before 30 Jul | MEDIUM — diagnose infra |
| 6 | MVP scope: explicitly tag backlog stories | Alex + Shawn | w/c 28 Jul | CRITICAL — defines done |
| 7 | Identify AWS/Terraform escalation contact | J4 | w/c 28 Jul | MEDIUM — Denis's ramp-up |
| 8 | Confirm Fri 31 Jul call vs Shawn's travel | J1 | ASAP | LOW — calendar conflict |
| 9 | Build D2 validation agent (hallucination QA) | Denis (architecture review) | Fri 31 Jul | HIGH — output quality |

---

## Recommendations for Denis's First Sprint (Thu 30 Jul – Fri 6 Aug)

1. **Understand the architecture & verify the POC locally** (day 1–2):
   - `python -m pytest -q` — confirm tests pass (offline mode).
   - `python -m uvicorn app.api:app --reload` — run the web UI locally.
   - Trace through the orchestrator: intake → A2 persona → scoring → C2 synthesis → C3 quick wins → scorecard.
   - Identify where the model invocation errors are (may need Bedrock creds from Shawn).

2. **Triage the AWS Bedrock issue** (day 2–3):
   - Work with Shawn to capture actual error messages (check CloudWatch, boto3 logs).
   - Confirm inference profile ARNs are available in `us-east-1`.
   - If ARNs don't exist, fall back to direct model IDs in `app/config.py`.

3. **Propose the D2 validation (QA) layer** (for Fri 31 Jul architecture review):
   - Denis's "Judge" pattern: second-tier agent that validates findings for:
     - Self-contradiction (two findings claim opposite things).
     - Generic/templated language (copy-paste from fallbacks).
     - Hallucinated facts (benchmark figures outside historical range, invented regulatory claims).
   - Use Claude Haiku (cheap, fast) to judge; flag low-confidence findings for partner review.

4. **Nail down the MVP scope** (collaborate with Alex):
   - Get explicit confirmation on the 20-story backlog: which are week-5 blockers?
   - Recommend: anything not in the README's "Done" section → deferrable.

5. **Document the gaps you find** — send Shawn a brief summary by day 3:
   - Bedrock status.
   - Auth decision needed (no blocker, just a flag).
   - D2 validation approach (for your architecture proposal).
   - Any code smell or MVP-at-risk signals.

---

## Attachments

- **README.md** — Current project state (what's done, what's deferred).
- **companion_02_quickwins_library.md** — 15 patterns used by C3 agent.
- **app/benchmarks.py** — Hardcoded peer benchmark data (V0 placeholders).
- **app/config.py** — Model tiering & Bedrock configuration.
- **app/agents/__init__.py** — A2, C2, C3 agent prompts & fallbacks.
