# Workflows and Data Governance — Baseline Analysis

**Date:** 3 August 2026
**Author:** Denis Morozov
**Status:** Analysis — baseline reading of the project's own documentation
**Scope:** Three questions — (1) the assumed client workflow, (2) the assumed admin workflow,
(3) collected-data lifetime and governance

**Sources:** all `*.md` files in the repository **except** `docs/architecture_review_access_control.md`,
which is deliberately excluded so that this document reflects only what the project specified for
itself, with no proposals from that review folded in. Where this analysis reaches a conclusion the
access-control review also reached, it is because the underlying project documents say so
independently.

Two citation short forms recur: `meeting_summary_analysis` is
`docs/meetings/2026-07-24_meeting_summary_analysis.md`, and `companion_0N` is the corresponding
`docs/product/companion_0N_*.md`. Root-level docs are cited by basename; see `docs/INDEX.md`
 for the name-to-path map.

> Everything below is what the documentation states. Specification, implementation status, and open
> questions are kept separate throughout — the gap between them is the substance.

---

## 1. Client (prospect) workflow

### 1.1 The specified flow

Three documents define it: `ui_design_project_brief.md` (screens), `companion_01_questionnaire_specification.md`
(question logic), `README.md:14-17` (pipeline). `aws_reference_architecture_and_cost_model.md` defines the target platform.

**Path A — self-serve web**

| # | Screen | URL | Content |
|---|---|---|---|
| 1 | Landing / Intake | `/` | Hero, then 4 fields: full name, role title, business email, company name. Shipped version adds industry and company size (`web/USAGE.md:96`). Three consent toggles. Trust signals: "Reviewed by a DXC senior partner before delivery", "24-hour turnaround guaranteed". |
| 2 | Questionnaire | `/assessment` | 20 questions, six dimensions, one question per screen. Progress indicator, dimension label, estimated time remaining. No score shown during the assessment — deliberate (`ui_design_project_brief.md:114`). |
| 3 | Submitted | `/submitted` | "Your assessment is submitted." Three-step "what happens next": agents research the company → synthesis engine scores → **a DXC senior partner reviews and approves**. Timeline: "You'll receive your scorecard within 24 hours at [email]". Teaser: "A personal portal link will arrive with your results". |
| 4 | Scorecard | `/portal/[token]` or `/results/[id]` | Radar chart, six dimension bars, 3–5 findings, Royal-blue recommended-next-step callout, quick-wins teaser, PDF download, confidential marking. |
| 5 | Quick Wins memo | `/portal/[token]/quick-wins` | Three pattern cards: what it would do for this company, prerequisites satisfied, expected outcome range, timeline to value, effort. |

**Questionnaire logic** (`companion_01:414-424`):

- Four question types — `single_select`, `scale_1_5`, `multi_select`, `open_short`.
- **Skip:** if Q3.1 (AI initiatives launched) = A, Q3.2 and Q3.3 are skipped as not yet applicable;
  AI Investment Maturity then scores from Q3.1 and Q3.4 only.
- **Branch:** Q6.2 (data sovereignty) is asked only when Q6.1 includes EU AI Act, FCA/PRA, or
  HIPAA/FDA; otherwise it defaults to "no specific sovereignty constraints".
- Scores are renormalized over questions *actually asked*.
- Agent A3 may re-order, substitute, or re-frame questions by persona and industry — Q3.3 and Q5.2
  are CFO-favouring and get financial language for P3; Q2.3 is substituted for MFG prospects.
- Estimated 18–26 minutes for the 16–20 questions surviving skip logic, against an under-30-minute
  target.

**Path B — voice interview** (`elevenlabs_agent_setup.md`)

A ~20-minute conversation covering the same 20 items, run on ElevenLabs Conversational AI:

- Opens by stating the shape ("about 20 minutes, six short topics") and reassuring once: "Your
  responses are reviewed by a DXC senior partner before any scorecard is produced, and aren't shared
  outside this assessment."
- Persona-adapted framing (P1 strategy/board, P2 architecture/governance feasibility, P3 ROI/capital
  allocation) and industry-specific examples.
- Never reads answer options aloud; maps each answer to the best-fitting option internally.
- Confirm-back after substantive answers; clarify-on-demand; graceful skip ("do not record that
  item"); corrections via a fresh `record_answer` for the same question id.
- **Compressed mode** if the executive signals time pressure: one highest-signal question per
  remaining dimension, inference confirmed in a line.
- `already_answered` variable prevents re-asking anything captured in chat.
- Two client tools: `record_answer({question_id, option_id | scale_value | option_ids})` and
  `finish_interview()`.
- Never states numeric scores or tiers. Closes on the 24-hour partner-reviewed promise.

**Pipeline behind both paths** (`README.md:14-17`):

```
Intake (A1) → Persona (A2) → [Research B1/B2/B3 — optional] → Deterministic scoring (Companion 01)
   → Synthesis C2 (findings + recommended next step) → Quick Wins C3 → Scorecard (D1)
   → Validation (D2) → Partner review
```

**Deliverables the prospect receives** (`companion_03:23-29`): a one-page PDF scorecard (primary,
by email), a one-page quick-wins memo (secondary), and a 5–8 page findings appendix (tertiary,
generated automatically, attached to the same email). D1 stores the PDF in the prospect record store
and delivers "via email with appropriate metadata" (`companion_03:325-331`).

### 1.2 As built — what the project's own testing and audits record

| Specified | Recorded state | Source |
|---|---|---|
| Scorecard within 24 hours after partner review | Returned **synchronously**: "Submitted screen shows spinner forever (until `/api/assess` returns); Scorecard appears instantly once data arrives" | `ui_ux_design_audit.md:312` |
| Delivered by email; personal portal link | No email capability documented anywhere in the project; delivery is an in-browser screen transition | `companion_03:331` (spec) vs `ui_ux_design_audit.md:325` (linear in-app flow) |
| "AI agents research [Company] — financials, news, tech posture" | B1/B2/B3 gated off behind `AIDIAG_ENABLE_RESEARCH=false`; listed as deferred | `meeting_summary_analysis:73`, `README.md:68-70` |
| Peer comparison "Industry average: 58 (n=42)" | Hardcoded indicative placeholders in `app/benchmarks.py`; three cohorts (FS n=42, HLS n=18, MFG n=27, All n=87) | `meeting_summary_analysis:21-24` |
| Prospect identity | "Auth: None today — exposed via raw IP/URL." `POST /api/assess` and `GET /api/fixture/{name}` are open | `meeting_summary_analysis:83-84` |
| 20-question pool | Local test reports "Question pool loading from API (95 questions)" | `local_test_report.md:63` |
| D2 validation before partner review | "Not yet implemented in MVP (deferred)" / "currently a stub" | `meeting_summary_analysis:70,183` |

The 95-vs-20 question count is unexplained by any document and is worth a direct check against
`content/question_pool.yaml` before it is treated as either a bug or a stale report.

### 1.3 Client-flow gaps recorded in the UX audit

`ui_ux_design_audit.md` §2 records these independently of any security review:

- **No review-before-submit step** — the prospect never sees their answers as a set before committing
  (`:263`).
- **Answers are immutable once submitted** — no way to revise and resubmit without starting a new
  assessment (`:337-342`).
- **No email validation** on the intake form (`:275`).
- **No way to return to the assessment after Submitted** (`:331`).
- Submit is disabled only until `company_name_raw` is populated; no other field is enforced (`:284`).

To these the project adds one more, from the LOAD/perf side: the questionnaire holds answers in React
state with no persistence, so any refresh, timeout, or navigation loses them — implied by the state
model described at `ui_ux_design_audit.md:104-109` and confirmed by the absence of any storage layer
in `web/README.md`.

### 1.4 The target platform's client model

`aws_reference_architecture_and_cost_model.md` — the AWS reference architecture — assumes something materially more
structured than what exists:

- **Multi-tenant SaaS**, sized at 50 client orgs/month × 3–4 executives each ≈ 175 interviews/month.
- **Amazon Cognito secures executive sign-in with MFA** (component 3).
- **API Gateway with JWT auth**, described as "tenant-scoped REST endpoints" (component 5).
- **DynamoDB with per-tenant partition keys** (component 9).
- **Amazon SES (optional)** to send report links to executives (component 13).
- Step Functions orchestrating the report build asynchronously (component 7) — which is what makes a
  24-hour turnaround coherent, versus the synchronous request the app actually serves.

So a client identity model, tenant isolation, and asynchronous delivery are all in the project's own
target architecture. None of them is implemented, and `meeting_summary_analysis` item #4 records
the identity decision as still open.

---

## 2. Admin / internal workflow

### 2.1 There is one internal role in the project documents, not two

The project documents describe a **senior partner reviewer**. They do not describe a separate
platform administrator with user-management duties. `aws_reference_architecture_and_cost_model.md:37` comes closest: "IAM
Identity Center handles DXC advisor access — advisor access, RBAC, SSO". That is a single "DXC
advisor" population with unspecified internal RBAC, not a partner/admin split.

This matters for scoping: **there is currently no specified owner for inviting prospects, managing
accounts, or reading an audit log** — because there is no specified mechanism for any of those
things. The absence is a gap in the specification, not just in the code.

### 2.2 Partner review — thoroughly specified

**Screen 6, Partner Review Dashboard** (`ui_design_project_brief.md:225-242`), marked V1, `/review`,
annotated "DXC internal, authenticated":

- Queue of pending reviews sorted by priority, validation flags surfaced first.
- Each queue item: company name, submission time, time remaining in SLA, flag count, overall
  confidence score.
- Review view: the full prospect-facing scorecard as the prospect will see it, plus a side panel with
  AI reasoning trace per finding, validation flags, and confidence per finding.
- Actions: edit any text field, approve, send back with a note. Keyboard shortcuts for fast review.
- Partner notes field, "captured for training data".
- Design note: "a professional tool for sophisticated users under time pressure… the flag indicators
  should make the highest-risk items impossible to miss."

**Data model** (`companion_05:816-855`) — `PartnerReviewRecord`:

- `review_started_at`, `review_completed_at`, `review_duration_seconds`, `partner_id`;
- typed `PartnerAction`s: `field_adjustment` (with original and new value), `finding_added`,
  `finding_removed`, `framing_change`, `send_back`;
- `final_disposition`: `approved` | `sent_back_for_reprocessing` | `manually_revised_and_approved` |
  `rejected`;
- `TrainingSignal[]` — adjustment patterns, framing preferences, industry and persona calibration —
  explicitly serving "DXC value driver 5 (partner training)".

**Processing states the partner moves a record through** (`companion_05:120-139`):
`validation` → `partner_review_queued` → `partner_review_in_progress` → `approved_for_delivery` →
`delivered` → `downstream_routing` → `completed`, with `sla_target` and `sla_breached` tracked
throughout.

**Two LLM assists around the human** (`companion_04:1383-1405`) — the review itself is explicitly not
an agent ("It is a workflow that consumes D1 output, D2 validation flags, and supporting data"):

- *Pre-review summarizer* (Sonnet): a one-paragraph briefing preparing the partner for a 15–30 minute
  review, surfacing prospect context, headline findings, the most critical validation flags, and where
  partner judgment is most needed.
- *Post-review training capture* (Haiku): structures the partner's adjustments and reasoning for
  downstream agent-training analysis.

**What routes attention to the partner:**

- D2 validation flags, severity CRITICAL → "would mislead the prospect or embarrass DXC. Must be
  addressed before delivery" (`companion_04:1116`).
- `partner_review_priority`: `expedited` | `standard` | `deferred` (`companion_05:791`).
- Confidence below 0.6 triggers validation attention; below 0.4 "may trigger partner review queue
  priority or re-processing" (`companion_04:27`).
- `PartnerAttentionFlag[]` emitted by C2 synthesis (`companion_05:634-638`).
- Q6.3, the only open-ended question, is "flagged for senior partner review attention"
  (`companion_01:410`).
- A1 flags test data, placeholder companies, and anything malformed or fraudulent rather than
  rejecting it (`companion_04:66-68`).

**SLA** (`companion_04:1427`): 24 hours total, decomposed into per-agent budgets summing to under
22 hours, "leaving 2 hours for partner review and delivery".

### 2.3 As built

| Aspect | State | Source |
|---|---|---|
| Review API routes | Present and functional — `GET /api/review/queue`, `GET /api/review/{id}`, `POST /api/review/{id}/decision` | `local_test_report.md:47-49`, `deploy_checklist.md:375-379` |
| Review dashboard UI | Deferred, not built — "backend queue exists, UI not built" | `README.md:70`, `meeting_summary_analysis:181` |
| Conflicting claim | "Partner review dashboard operational"; MVP checklist requires "Screen 6 functional with sample scorecards" | `master_audit_report.md:19,346` |
| Authentication | None on any route | `meeting_summary_analysis:83-84` |
| Approval integrity | **No optimistic locking on the decision endpoint.** Two partners deciding concurrently: "one decision overwrites the other" — one approving while the other sends back | `evaluation_suite.md:1085-1090`, `quick_reference.md:23` (test 2.2, rated BLOCKER) |
| Queue exposure | `/api/review/queue` identified in testing as "Contains all company assessments" and reachable cross-origin under `allow_origins=["*"]` | `evaluation_suite.md:512,526,607` |
| D2 validation feeding the queue | Stub; flags that should drive queue priority are not generated | `meeting_summary_analysis:183` |

The concurrency finding is a governance issue as much as a data-integrity one: `PartnerReviewRecord`
is designed to be the auditable record of who approved what, and a silent last-write-wins overwrite
destroys exactly that.

### 2.4 The open decision

`meeting_summary_analysis` item #3 / action A4, owner **Alex Schick**, due w/c 28 Jul, severity
HIGH: "Close the authentication decision — Entra ID vs external-user identity."

The stated tension: Entra ID works for DXC employees (internal customer-zero), but external client
executives have no DXC credentials. The candidate approaches recorded there (`:90-96`):

- **Customer-zero (DXC employees):** Entra ID.
- **External clients (post-MVP):** passwordless invite link (email + one-time token), SAML/OIDC
  federation to the client's own IdP, or DXC-issued short-lived credentials.

Noted as "a blocker for the security story and likely the frontend sign-in flow."

---

## 3. Collected data — lifetime and governance

**Short answer: unspecified, and recorded as a compliance gate before customer-zero.**
`meeting_summary_analysis:230`, open item #4: "Define data retention, residency, consent
language" — owner *Legal + J3*, due *before customer-zero*, severity HIGH.

Item #5 of the same analysis (`:101-117`) states the position plainly: retention, residency and
confidentiality for transcripts and voice recordings were **not discussed** and are unspecified.

### 3.1 What is collected

**Identifying data per submission** (`companion_05:86-95`): `prospect_name`, `prospect_role`,
`prospect_email`, `company_name_raw`, `company_website`, `submission_timestamp`,
`submission_source`, `referring_partner_id`.

**Derived and inferred:** canonical company name, ticker, LEI, NAICS industry, HQ country and
operating jurisdictions, size band (A1); persona, seniority, likely concerns, framing preference
(A2); all questionnaire responses with per-question timestamps and response times; six dimension
scores; findings; reasoning traces; validation flags; quick wins.

Note that `QuestionResponse` captures `question_rendered_text` per answer "for audit (text may have
varied by personalization)" (`companion_05:292`) — a deliberate and good decision that also means
the store holds the full personalized transcript, not just option ids.

**Research data on the company** (B1/B2/B3, currently off): financial summaries, M&A activity,
AI-relevant disclosure from filings, news signals, inferred cloud/data/AI platforms, **AI talent
signals from job postings**, open-source activity, and named strategic partnerships — all attributed
to specific sources with fetch timestamps (`companion_05:303-447`).

**Voice recordings** are handled by **ElevenLabs**, an external SaaS, and are not stored in the
diagnostic backend (`meeting_summary_analysis:105`). The ElevenLabs agent is configured
**Visibility: Public** because "the embed widget only loads public agents"
(`elevenlabs_agent_setup.md:238`), with control limited to an allowed-origins list.

### 3.2 Actual lifetimes today

| Store | Lifetime | Source |
|---|---|---|
| DynamoDB `ai-readiness-sessions` | **Indefinite** — no TTL attribute, no purge job documented | `deprovisioning_plan.md:48`, `performance_audit.md:79-86` |
| DynamoDB point-in-time recovery | 35 days rolling, enabled on creation | `deprovisioning_plan.md:423` |
| CloudWatch logs `/ecs/ai-readiness-diagnostic` | 7 days | `deprovisioning_plan.md:47` |
| ECR images | Lifecycle policy attached | `deprovisioning_plan.md:50` |
| In-memory store (local / fallback) | Process lifetime; ephemeral, "no database, no explicit purge" | `meeting_summary_analysis:106` |
| Generated PDFs | No documented lifecycle | — |
| Audit log | Not implemented; spec says "Retention per legal review" | `companion_05:1038` |

A DynamoDB TTL on an `expires_at` attribute exists **only as a proposal**, and there for performance
reasons rather than privacy ones — "Enable TTL for auto-deletion of old records"
(`optimization_roadmap.md:334-337`). Nothing enforces retention in the deployed stack.

The one place a retention position appears at all is a recommendation, not a decision
(`meeting_summary_analysis:117`): because the diagnostic is explicitly positioned as a sales-funnel
asset, there is a strong case for retention — "keep for 12 months to inform delivery" — but it needs
explicit buy-in from the prospect.

**Deprovisioning assumes there is nothing to protect.** The pre-destroy checklist verifies
"DynamoDB contains ONLY test fixtures" and "No customer PII or sensitive data"
(`deprovisioning_plan.md:221-225`) — sound for the current test deployment, but it is a manual
verification step, not a control, and it will silently become wrong the first time a real prospect
completes an assessment.

### 3.3 Consent model

Five categories, immutable append-only records — "Consent is captured at submission time. Subsequent
consent changes create new records (immutable history)" (`companion_05:142-166`):

| | Field | Default | Meaning |
|---|---|---|---|
| C-1 | `c1_use_for_scorecard` | **Required, always true, cannot opt out** | Produce this prospect's scorecard |
| C-2 | `c2_anonymized_benchmark_contribution` | On, opt-out | Contribute to the AdvisoryX peer benchmark library |
| C-3 | `c3_internal_ai_tool_improvement` | Off, opt-in | Internal DXC AI tool training and calibration |
| C-4 | `c4_cross_practice_sharing` | Off, opt-in | Route opportunities to other DXC practices |
| C-5 | `c5_productized_benchmark_third_party` | Off, opt-in (V2+) | Third-party productized benchmark |

Each record also carries `legal_basis` (consent / legitimate_interest / contract),
`applicable_jurisdictions`, `consent_method` (web_form_v1 / partner_facilitated / api), and
`consent_language_version` — the version of the consent text the prospect actually saw.

**Consent gating is enforced at the schema level and in the agent prompts.** Each downstream E-agent
returns an explicit skip state rather than silently proceeding:

| Agent | Gated on | Prompt instruction | Skip state |
|---|---|---|---|
| E1 cross-practice routing | C-4 | "only run if consent flag C-4 is granted. If not granted, return empty result with explanation" (`companion_04:1203`) | `skipped_no_consent` |
| E2 benchmark contribution | C-2 | "Only run if C-2 is granted. If C-2 was opted out, skip this agent and log skip event" (`:1269`) | `skipped_opted_out` |
| E3 internal feedstock | C-3 | "C-3 is separate from C-2 because data use is different. C-3 default is OFF; requires explicit opt-in" (`:1338`) | `skipped_opted_out` |

**Anonymization for the benchmark library is specified in detail** (`companion_04:1259-1271`,
`companion_05:914-932`):

- *Remove:* company name, prospect name, email, role title, any quote that could identify the company.
- *Preserve:* industry classification, country-level geography only, size band, six dimension scores,
  value pockets, next-step category.
- *Transform:* specific financials → range buckets; competitor names → industry-segment references.
- The `BenchmarkRecord` carries an `anonymous_id` and **no foreign key back to the prospect**;
  storage guidance requires a separate logical store with no FK to the prospects table
  (`companion_05:1036`).

**The only consent-withdrawal mechanism described anywhere** is a single line in the E2 prompt: the
separately-stored audit trail retains the "Original prospect ID (**allows tracing if consent
withdrawn**)" (`companion_04:1265`). No withdrawal API, UI, workflow, or owner is specified. The
capability to unwind a benchmark contribution exists by design; the process to trigger it does not.

### 3.4 Three problems with the consent implementation

**(a) The consent text does not exist.** `content/consent_copy.md` is 13 lines of explicit
PLACEHOLDER, headed: "MUST be replaced with DXC Legal-reviewed text before any real interview
(including customer zero)." It covers only C-1 and C-2, against a five-category schema. Its closing
line — "The engine records only whether C-1 and C-2 were accepted, by whom, and when" — describes a
two-consent system, not a five-consent one.

**(b) The C-2 field is named four different things across four documents.** These are not cosmetic
variants; the last one describes a different consent entirely:

| Name | Where | Means |
|---|---|---|
| `c2_anonymized_benchmark_contribution` | `companion_05:154` — the schema of record | Anonymized benchmark contribution |
| `c2_anonymized_benchmark` | the **implemented** name — `app/models.py:54`, `web/src/types.ts:100`, all three fixtures | Same, abbreviated |
| `c2_use_for_benchmarking` | `meeting_summary_analysis:104`, *quoting* the code | Same, third spelling — and a misquote; no such identifier exists |
| `c2_data_retention` | `load_test_scenarios.md:63` | **Data retention** — a different thing |
| "Contribute anonymized data to the AdvisoryX peer benchmark library" | `ui_design_project_brief.md:87` | The prospect-facing wording |

The code is at least self-consistent: `c2_anonymized_benchmark` runs cleanly from the Pydantic model
through the TypeScript types, the landing-page toggle, and the fixtures. The drift
is in the documentation around it — the schema of record uses a longer name, the meeting analysis
quotes an identifier that does not exist, and the load-test payload uses a name that means something
else entirely. A consent flag that means "benchmark contribution" in the schema and "data retention"
in the load tests is the kind of drift that produces a defensible-looking audit record attesting to
something the prospect was never asked. Reconcile to the implemented name before Legal drafts the
text around it, not after.

**(c) The consent paths are untested.** Across `evaluation_suite.md` every fixture posts either
`{"c1_use_for_scorecard": True}` alone (`:50,67,84,123,158,1711,2149`) or `consent={}`
(`:703,726,742,759,782,865,887,912,936`). C-2 through C-5 are never exercised, so neither the
default-on behaviour of C-2 nor the skip paths of E1/E2/E3 have any test coverage. The UI, meanwhile,
presents three toggles (`ui_design_project_brief.md:85-88`) and the request model accepts four —
C-1 through C-4, no C-5 (`app/models.py:52-56`).

**A circular dependency worth naming.** The hardcoded peer benchmarks are meant to be replaced once
C-2 volume accrues — "the anonymized peer-benchmark library (consent C-2) replaces them once volume
accrues" (`meeting_summary_analysis:27`). C-2's language is unwritten, and the volume threshold is
undefined. So the placeholder figures cannot begin to be replaced until Legal ships the text: the
consent copy is a dependency of output credibility, not only of compliance. The same analysis
recommends breaking the loop by starting with DXC proprietary historical data (Option A) and setting
an explicit growth trigger for the community cohort (`:36`).

### 3.5 Audit trail

Specified thoroughly; **not implemented**.

`companion_05:964-993` defines a system-wide `AuditLogEntry` with twelve event types — including
`submission_received`, `consent_changed`, `partner_action_recorded`, `scorecard_delivered`, and
`downstream_routing_completed` — each with actor, severity, and event-specific metadata. Every entity
additionally carries `AuditMetadata` (created_by, last_modified_by, monotonic version).

The stated design principle is unambiguous: "**Audit-first.** Every entity has audit trail fields
capturing who/what/when generated it. Critical for partner review credibility and regulatory
compliance" (`companion_05:25`). Reproducibility is called out as a requirement: "a historical
scorecard's reasoning must be reproducible. The schema captures enough context (which agent versions
ran, which content versions were used)" (`:1052`).

Against that, nothing in the audit reports, deployment checklists, or test suites references an audit
log implementation. `deploy_checklist.md:430` includes "No failed login attempts" as a post-deploy
security check — for a system with no login. The store record is described in
`meeting_summary_analysis:106` as a `Session` object of scores, findings and metadata, with no
audit entity alongside it.

### 3.6 Residency, tenancy, isolation

- **Residency.** Single region, `us-east-1`, AWS account `023138541872`
  (`deprovisioning_plan.md:4-5`). No policy documented. `meeting_summary_analysis:111` lists
  "Where is the data stored? AWS region? On-premise?" as unresolved. Worth noting the asymmetry: Q6.2
  asks prospects what sovereignty and residency requirements constrain *their* AI deployment, and
  Q6.3 asks how they address cross-border data flow, while the diagnostic states no position of its
  own. `companion_04:592` has B5 researching GDPR, UK DPA, and country-specific residency law for the
  prospect.
- **Tenancy.** `aws_reference_architecture_and_cost_model.md` assumes multi-tenant SaaS with per-tenant DynamoDB partition
  keys and tenant-scoped API endpoints. Not implemented.
  `meeting_summary_analysis:112` records the gap: "If Bank of America's CFO and CTO both assess,
  is their data separated in the backend? (Appears not in V0 — both responses are aggregated to the
  'company'.)"
- **Executive privilege.** Open, and listed as a Legal question: "Can findings from a CFO's
  assessment be disclosed to the CIO without permission?" (`:115`).
- **Third-party sharing.** Also open: "What does C-2 actually permit? Can findings be shared with
  third parties?" (`:114`).
- **Voice recordings.** "Who owns them? Are they deleted after transcript? Can they be reused for
  training?" (`:113`).

### 3.7 Security posture bearing on data governance

From the project's own audits, independent of any access-control review:

| Finding | Detail | Source |
|---|---|---|
| No authentication | "Auth: None today — exposed via raw IP/URL." No auth layer on any route | `meeting_summary_analysis:83-84` |
| CORS wildcard | `allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]` — "Any origin can make requests, including POST to /api/assess and /api/review endpoints"; `/api/review/queue` named as "Contains all company assessments" | `evaluation_suite.md:512-526`, rated HIGH |
| Prompt injection | `prospect_name`, `company_name_raw` flow unsanitized into agent prompts | `quick_reference.md:11` (BLOCKER), `evaluation_suite.md` test 1.1 |
| PDF content injection | `company_name`, tier, labels, findings, contact fields embedded unescaped into ReportLab | `master_audit_report.md:486-487` (CRITICAL ×2) |
| Path traversal | `load_fixture()` unvalidated — "Attacker reads arbitrary files (secrets.yaml, .env)" | `master_audit_report.md:167,493`, `quick_reference.md:96` |
| SSRF via `company_website` | `http://169.254.169.254/latest/meta-data/` listed as a live payload | `quick_reference.md:108-111` |
| Email header injection | `prospect_email` accepts `\r\nBcc: attacker@evil.com` — no format validation | `quick_reference.md:115-117`, `ui_ux_design_audit.md:275` |
| Review decision race | No optimistic locking; concurrent approve/send-back silently loses one | `evaluation_suite.md:1085-1090` (BLOCKER) |
| DynamoDB write race | No `ConditionExpression`, no version field | `quick_reference.md:22` (BLOCKER) |
| Application-layer encryption | Not mentioned anywhere for the PII fields | — |

`master_audit_report.md:47` states the resulting position: "**NO** public traffic until findings #1,
#2, #3, #5 resolved", with security rated 🔴 Restricted and the overall verdict "Go to staging; NO
public traffic until Phase 1 complete".

### 3.8 Erasure

No erasure tooling, API, or process is described in any document. `companion_05` provides a
`withdrawn` processing status (`:133`) and E2 retains the prospect id specifically to permit tracing
on consent withdrawal (`companion_04:1265`) — the two hooks a deletion process would need — but
nothing connects them to an actual workflow, owner, or SLA.

---

## 4. Open items bearing on these three questions

From `meeting_summary_analysis` "Summary of Open Items", unchanged and restated:

| # | Item | Owner | Due | Severity |
|---|---|---|---|---|
| 1 | Decide peer-benchmark data source and methodology | Shawn + J2 | w/c 28 Jul | HIGH — output credibility |
| 3 | Resolve auth — Entra ID vs external identity | Alex (A4) | w/c 28 Jul | HIGH — security story |
| 4 | Define data retention, residency, consent language | Legal + J3 | Before customer-zero | HIGH — compliance gate |
| 6 | MVP scope: explicitly tag backlog stories | Alex + Shawn | w/c 28 Jul | CRITICAL — defines done |
| 9 | Build D2 validation agent (hallucination QA) | Denis | Fri 31 Jul | HIGH — output quality |

Sub-questions recorded under item #4 (`:110-116`), all unanswered:

1. Retention period — 30 days? 1 year? Forever for benchmarking?
2. Residency — which region, or on-premise?
3. Tenancy separation between two executives at the same client.
4. Voice recordings — ownership, deletion after transcript, reuse for training.
5. What C-2 actually permits, including third-party sharing.
6. Executive privilege — CFO's findings disclosed to the CIO?

Added by this analysis, as specification defects rather than decisions:

7. Align the documentation on the implemented C-2 field name, `c2_anonymized_benchmark`, before
   Legal drafts around it — three documents currently disagree with the code and with each other
   (§3.4b).
8. Define the consent-withdrawal workflow that `companion_04:1265` assumes exists (§3.3).
9. Resolve the 20-vs-95 question-count discrepancy between `companion_01` and `local_test_report.md:63`.
10. Resolve the conflicting claims on partner-dashboard status between `master_audit_report.md:19`
    and `README.md:70`.

---

## 5. Summary

**Client.** Well specified and coherent: intake → 20-question adaptive assessment, by web form or a
20-minute voice interview → scorecard, quick-wins memo, and findings appendix delivered by email
within 24 hours, after a senior partner has reviewed and approved. As built: the scorecard returns
synchronously in-browser, unreviewed, with no login, no email, no research agents, placeholder peer
benchmarks, and no way to revise answers. The project's own target architecture
(`aws_reference_architecture_and_cost_model.md`) assumes Cognito sign-in with MFA, tenant-scoped endpoints, SES delivery, and
Step Functions doing the report build asynchronously — which is the version of the system in which
the 24-hour promise makes sense.

**Admin.** The project specifies one internal role — the senior partner reviewer — in real depth:
queue, priority, reasoning trace, typed adjustment actions, dispositions, training capture, and two
LLM assists around the human. It has backend routes and no UI, no authentication, and no locking on
the approval decision. A separate platform-administrator role, and any mechanism for inviting
prospects or managing accounts, is **not specified anywhere** — the closest thing is a single line
giving DXC advisors RBAC through IAM Identity Center. That absence is a specification gap, and it sits
directly on top of open item #3.

**Data.** The governance *design* is genuinely strong: five consent categories with defaults and
legal basis, immutable consent history, schema-level gating of every downstream use, strict
anonymization rules for the benchmark library with no foreign key back to the prospect, an
audit-first principle, and reproducibility of historical scorecards. Almost none of it is
implemented, and three parts of it are internally inconsistent — the consent copy is a placeholder
covering two of five categories, the C-2 field carries four different names across four documents
(one of which means something else entirely), and no test exercises any consent beyond C-1. Alongside
that: indefinite retention with no TTL, no residency policy, no tenant isolation, no audit log, no
erasure process, and a security posture the project's own master audit rates 🔴 Restricted with an
explicit hold on public traffic.

The documentation is candid throughout. Retention, residency and consent are open item #4, owned by
Legal, due before customer-zero, and overdue.

---

*Related: `aws_reference_architecture_and_cost_model.md` (AWS reference architecture — the target multi-tenant model),
`meetings/2026-07-24_meeting_summary_analysis.md` (open items and owners),
`companion_05_data_schemas.md` (entity, consent, audit and partner-review schemas),
`companion_04_agent_prompts.md` (consent gating and anonymization rules in the E-agents),
`master_audit_report.md` and `evaluation_suite.md` (security and data-integrity findings),
`content/consent_copy.md` (placeholder consent text).*

*A companion analysis that additionally incorporates `docs/architecture_review_access_control.md`
is at `docs/workflows_and_data_governance.md`.*
