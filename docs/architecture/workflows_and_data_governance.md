# Workflows and Data Governance — Documentation Analysis

**Date:** 3 August 2026
**Author:** Denis Morozov
**Status:** Analysis — derived entirely from the repository's markdown documentation
**Scope:** Three questions — (1) the assumed client workflow, (2) the assumed admin workflow,
(3) collected-data lifetime and governance
**Sources:** all 43 `*.md` files in the repository (root, `docs/`, `web/`, `content/`, `terraform/`,
`deploy/`). Two citation short forms recur: `meeting_summary_analysis` is
`docs/meetings/2026-07-24_meeting_summary_analysis.md`, and `companion_0N` is the corresponding
`docs/product/companion_0N_*.md`. Root-level docs are cited by basename; see `docs/INDEX.md`
 for the name-to-path map.

> This document reports what the documentation *says*, and separates it explicitly from what the
> documentation says is *built*. Where the two disagree, both are recorded. Nothing here is a new
> decision; the open decisions are restated with their existing owners.

---

## 1. Client (prospect) workflow

### 1.1 The designed flow

Documented in `ui_design_project_brief.md`, `README.md:14-17`, and `companion_01_questionnaire_specification.md`.
Two entry paths converge on one pipeline.

**Path A — self-serve web (built)**

| # | Screen | URL | What happens |
|---|---|---|---|
| 1 | Landing / Intake | `/` | 4-field form: full name, role title, business email, company name. The shipped React version adds industry and size band (`web/USAGE.md:95-97`). Three consent toggles below the form (`ui_design_project_brief.md:85-88`). |
| 2 | Questionnaire | `/assessment` | 20 questions, six dimensions, 18–26 min target (`companion_01:434`). Four types: `single_select`, `scale_1_5`, `multi_select`, `open_short`. |
| 3 | Submitted | `/submitted` | "Scorecard within 24 hours at [email]"; teaser that "a personal portal link will arrive with your results". |
| 4 | Scorecard | `/portal/[token]` | Radar chart, six dimension bars, 3–5 findings, recommended next step, quick-wins teaser, PDF download. |
| 5 | Quick Wins memo | `/portal/[token]/quick-wins` | Three patterns with prerequisites, timeline, effort. |

Conditional logic in the questionnaire (`companion_01:422-424`):

- **Skip:** if Q3.1 (AI initiatives launched) = A, then Q3.2 and Q3.3 are skipped; AI Investment
  Maturity scores from Q3.1 and Q3.4 only.
- **Branch:** Q6.2 (data sovereignty) is asked only if Q6.1 includes EU AI Act, FCA/PRA, or HIPAA/FDA.
- Scores are renormalized over questions *actually asked*.

No score is shown to the prospect during the assessment — deliberate (`ui_design_project_brief.md:114`).

**Path B — voice interview (built, ElevenLabs)**

`elevenlabs_agent_setup.md` specifies a ~20-minute executive conversation covering the same 20 items:

- Persona-adapted framing (P1 executive sponsor / P2 operational owner / P3 financial scrutineer) and
  industry-specific language.
- Confirm-back after substantive answers; clarify-on-demand; graceful skip; answer correction via a
  new `record_answer` for the same question id.
- Compressed mode when the executive signals time pressure — one highest-signal question per
  remaining dimension, inference confirmed in a line.
- Two client tools: `record_answer({question_id, option_id | scale_value | option_ids})` and
  `finish_interview()`.
- `already_answered` dynamic variable prevents re-asking anything captured in chat.
- Close restates the 24-hour, partner-reviewed scorecard promise.

**Pipeline behind both paths** (`README.md:14-17`):

```
Intake (A1) → Persona (A2) → [Research B1/B2/B3 — optional, off] → Deterministic scoring
   → Synthesis C2 (findings + recommended next step) → Quick Wins C3 → Scorecard (D1)
   → Validation (D2) → Partner review
```

### 1.2 Where the as-built flow diverges from the promise

| Promised to the prospect | Actual |
|---|---|
| "Scorecard within 24 hours, after partner review" | Returned **synchronously** from `POST /api/assess`; the prospect sees it before any partner has looked at it |
| "A personal portal link will arrive" | No email capability exists anywhere in the project (`architecture_review_access_control.md:256-258`) |
| "AI agents research [Company] — financials, news, tech posture" | B1/B2/B3 gated off behind `AIDIAG_ENABLE_RESEARCH=false` (`meeting_summary_analysis:73`) |
| Identified prospect, personal portal | **No authentication at all**; `POST /api/assess` is fully public (`architecture_review_access_control.md:80`) |
| "Industry average: X (n=42)" | Hardcoded indicative placeholders in `app/benchmarks.py` (`meeting_summary_analysis:21-24`) |

Two durability gaps affecting the prospect directly:

- **Web:** answers live only in React state; a refresh loses them
  (`architecture_review_access_control.md:165-167`).
- **Voice:** `VoiceInterview.tsx` accumulates answers in a ref and submits only at the end; a dropped
  call loses a 20-minute executive conversation (`:680-681`).

A third, upstream of both: assessments are persisted only after the full pipeline returns, so a task
replacement mid-request loses the submission and the SPA presents that failure as success
(`:676-679`).

### 1.3 The proposed future client flow

`docs/architecture_review_access_control.md` §5 — designed, **not built**:

```
Admin designates an email address
  → system sends a single-use invitation link (24h TTL) to that mailbox
  → recipient opens GET /invite/<token>      (validation only, NO state change)
  → POST /invite/<token> with name + job_title  (conditional update consumes the token)
  → user record created, account_role read FROM THE INVITATION, never from a form field
  → session cookie (HttpOnly, Secure, SameSite=Lax, 30d rolling)
  → assessment begins, intake pre-filled from the profile
```

Design points that matter:

- **Auth before the interview, not after.** Sidesteps merging anonymous responses into a newly
  identified account, deciding who owns pre-consent data, and reconciling a mismatched email (§5d).
- **Consume on `POST`, never on `GET`.** Corporate mail security (Mimecast, Proofpoint, Defender)
  pre-fetches inbound links and would otherwise burn the token before the human clicks.
- **24-hour TTL makes self-service re-request mandatory.** A C-suite recipient will routinely miss a
  24-hour window; the expired-link page must offer "send me a new link", keyed off the *expired token*
  and never off a user-supplied address, rate-limited with a `resend_count` cap.
- **Public surface shrinks to:** landing page, sample scorecard (so sales can demo without an
  invitation), `/health`, `/ping`, `/invite/*`. Everything else authenticated (D5).

---

## 2. Admin / internal workflow

Two distinct internal roles. One exists in partial form; the other does not exist at all.

### 2.1 Partner (senior reviewer) — backend present, UI absent, unauthenticated

**Specified** in `ui_design_project_brief.md:225-242` as Screen 6:

- Queue of pending reviews sorted by priority, validation flags surfaced first.
- Each item: company name, submission time, time remaining in SLA, flag count, overall confidence.
- Review view: the full prospect-facing scorecard, plus a side panel with AI reasoning trace per
  finding, validation flags, and per-finding confidence.
- Actions: edit any text field, approve, send back with a note. Keyboard shortcuts for speed.
- Partner notes captured **as training data**.

**Data model** (`companion_05:816-855`) — `PartnerReviewRecord` with:

- typed `PartnerAction`s: `field_adjustment`, `finding_added`, `finding_removed`, `framing_change`,
  `send_back`;
- `final_disposition`: `approved` | `sent_back_for_reprocessing` | `manually_revised_and_approved` |
  `rejected`;
- `TrainingSignal[]` for the DXC value-driver-5 feedback loop.

**Two LLM assists around the human** (`companion_04:1383-1405`) — the review itself is explicitly not
an agent:

- *Pre-review summarizer* (Sonnet): one-paragraph briefing surfacing prospect context, headline
  findings, critical validation flags, and where partner judgment is most needed.
- *Post-review training capture* (Haiku): structures partner adjustments and reasoning for agent
  improvement.

**SLA:** 24 hours total, decomposed into per-agent budgets summing to <22 hours, leaving 2 hours for
partner review and delivery (`companion_04:1427`).

**Status conflict in the docs.** `master_audit_report.md:19` calls the partner review dashboard
"operational"; `README.md:70` lists "partner-review dashboard (Screen 6)" as deferred. The
access-control review resolves it: the routes exist, the UI does not.

**Security posture.** All four review routes are unauthenticated —
`/review`, `GET /api/review/queue`, `GET /api/review/{id}`, `POST /api/review/{id}/decision`. The
access-control review rates this **worse than the open intake form**: an open intake form leaks
nothing, whereas this exposes the entire prospect pipeline (company, score, tier, validation flags,
per-dimension reasoning) and lets a stranger approve or send back any scorecard
(`architecture_review_access_control.md:55-59`, finding **P0-2**).

### 2.2 Admin — does not exist

Introduced as a **new** role in `architecture_review_access_control.md:379`. Proposed workflow:

1. Admin signs in through Entra ID SSO.
2. `POST /api/admin/invitations` with a designated email address.
3. Confirm-before-send step showing the address, warning when the domain does not match the expected
   client domain.
4. System sends; the admin never handles the link. Out-of-band sharing (Slack, forwarded mail,
   copy-paste) was considered and explicitly dropped.
5. Admin sees delivery status (`sent` / `delivered` / `bounced` / `complained`), can resend, and can
   revoke any unconsumed invitation.
6. Every send is audit-logged.

Recommendation is to **extend `/review`** rather than build a second dashboard — it already lists
every record with status, flags, and priority — adding user management, cross-user browsing on a
status GSI, and the audit log (Phase 3, 5–8 days).

**The `role` naming trap, resolved in review** (§5b). Two unrelated fields both want the word "role":

| Field | Meaning | Source | Used for |
|---|---|---|---|
| `job_title` | Position in the firm — "Group CFO" | User, at registration | A2 persona inference, document framing |
| `account_role` | `prospect` / `partner` / `admin` | **The invitation**, set by an admin | Authorization |

Two rules that must survive into the implementation ticket: `account_role` is never accepted from a
form field, and neither field is derived from the other.

### 2.3 Role matrix

| Role | Population | Can do |
|---|---|---|
| `prospect` | External executive, invited | Complete an assessment; view own assessments, scorecards, PDFs |
| `partner` | DXC | Everything a prospect can, plus the review queue: read any assessment, approve or send back |
| `admin` | DXC | Everything a partner can, plus create/revoke invitations, manage users, read the audit log |

Proposed identity split (**D1**, owner Alex Schick, due w/c 28 Jul, overdue):

| Population | IdP | Password stored by DXC |
|---|---|---|
| Admin, Partner (DXC staff) | Entra ID OIDC — MFA already enforced | None |
| Prospect (external executives) | Cognito / invitation link | None recommended (**D2**) |

Net conclusion of §5a: **the system may not need to store a single password.** Invitation tokens
become a prospect-only mechanism, which removes the highest-privilege accounts from the email path
entirely.

---

## 3. Collected data — lifetime and governance

**Short answer: undefined, and explicitly flagged as a compliance gate before customer-zero.**
`meeting_summary_analysis:230` lists "Define data retention, residency, consent language" as open
item #4 — owner *Legal + J3*, severity HIGH — still open as of the 3 Aug access-control review.

### 3.1 What is collected

**Per assessment** (`app/models.py:39`, per `architecture_review_access_control.md:96-98`):
`prospect_name`, `prospect_email`, `prospect_role`, `company_name_raw`, `company_website`,
`hq_country` — **unencrypted at the application layer and unassociated with any account.**

Plus: all questionnaire responses, six dimension scores, LLM-generated findings, quick wins,
reasoning traces, validation flags. The whole session is one JSON blob in a `doc` attribute
(`performance_audit.md:80-86`).

**Voice recordings** are handled by **ElevenLabs**, an external SaaS, and are not stored in the
diagnostic backend. Ownership, deletion after transcription, and reuse for training are all listed as
unresolved (`meeting_summary_analysis:113`).

### 3.2 Actual lifetimes today

| Store | Lifetime | Source |
|---|---|---|
| DynamoDB `ai-readiness-sessions` | **Indefinite** — no TTL attribute, no purge job | `deprovisioning_plan.md:48` |
| DynamoDB PITR backups | 35 days rolling | `deprovisioning_plan.md:423` |
| CloudWatch logs `/ecs/ai-readiness-diagnostic` | 7 days | `deprovisioning_plan.md:47` |
| ECR images | Lifecycle policy attached | `deprovisioning_plan.md:50` |
| In-memory store (local / fallback path) | Process lifetime; ephemeral | `meeting_summary_analysis:106` |
| Generated PDFs | No documented lifecycle | — |

A DynamoDB TTL on `expires_at` exists only as a *proposal* (`optimization_roadmap.md:334-337`).
Nothing enforces retention in the deployed stack.

**Recommended, not decided.** **D4** proposes **12 months**, on the sales-funnel rationale already
documented ("keep for 12 months to inform delivery"), scheduled for Phase 4
(`architecture_review_access_control.md:668`).

**Implementation constraint carried from the review** (§5c): DynamoDB's native TTL is garbage
collection, not enforcement — items delete *within roughly 48 hours* of the expiry timestamp, not at
it. `expires_at` must be checked in application code on every validation, for invitations and
sessions alike. TTL is cleanup only.

### 3.3 Consent model

Five categories, immutable append-only records (`companion_05:146-166`):

| | Consent | Default |
|---|---|---|
| C-1 | `c1_use_for_scorecard` | **Required — always true, cannot opt out** |
| C-2 | `c2_anonymized_benchmark_contribution` | On, opt-out |
| C-3 | `c3_internal_ai_tool_improvement` | Off, opt-in |
| C-4 | `c4_cross_practice_sharing` | Off, opt-in |
| C-5 | `c5_productized_benchmark_third_party` | Off, opt-in (V2+) |

Each record carries `legal_basis` (consent / legitimate_interest / contract),
`applicable_jurisdictions`, `consent_method`, and `consent_language_version` — the version of the
consent UI text the prospect actually saw.

**Consent gating is enforced at the schema level.** Downstream E-agents return an explicit skip state
rather than silently proceeding:

| Agent | Output | Gated on | Skip state |
|---|---|---|---|
| E1 | `CrossPracticeRouting` | C-4 | `skipped_no_consent` |
| E2 | `BenchmarkContribution` | C-2 | `skipped_opted_out` |
| E3 | `FeedstockOutput` | C-3 | `skipped_opted_out` |

**Benchmark de-linking is designed properly** (`companion_05:893-932`). `BenchmarkRecord` holds an
`anonymous_id`, country-level geography only, revenue and employee *buckets*, and submission
*quarter* rather than date — with **no foreign key back to the prospect**. The link exists only in a
separately-stored audit trail. Storage guidance reinforces this: a separate logical store, separate
schema, no FK to the prospects table (`companion_05:1036`).

**But the consent text does not exist.** `content/consent_copy.md` is 13 lines of explicit
PLACEHOLDER, headed with a warning that it "MUST be replaced with DXC Legal-reviewed text before any
real interview (including customer zero)". It covers only two consents (C-1, C-2) against a
five-category schema and a three-toggle UI. The UI wording differs again
(`ui_design_project_brief.md:85-88`): C-2 appears as "Contribute anonymized data to the AdvisoryX peer
benchmark library", C-4 as "Share with DXC teams for relationship follow-up".

**A circular dependency worth naming.** The hardcoded peer benchmarks are meant to be replaced once
C-2 volume accrues (`meeting_summary_analysis:26-28`). C-2's language is unwritten. So the
placeholder figures cannot begin to be replaced until Legal ships the text — which makes the consent
copy a dependency of output credibility, not only of compliance.

**One further wrinkle** (`architecture_review_access_control.md:169-170`): consent today is
per-submission. Accounts introduce a *second* consent surface (terms accepted at registration) that
must not be conflated with C-1..C-4.

### 3.4 Audit trail

Designed thoroughly; **not implemented**.

`companion_05:964-993` specifies a system-wide `AuditLogEntry` with 12 event types — including
`consent_changed`, `partner_action_recorded`, and `scorecard_delivered` — plus `AuditMetadata`
(created_by, last_modified_by, monotonic version) on every entity. The stated design principle is
"audit-first… critical for partner review credibility and regulatory compliance"
(`companion_05:25`), and reproducibility of a historical scorecard's reasoning is called out as a
requirement (`:1052`).

Reality: **P1-5**, "No audit log of who accessed/modified records — no compliance trail for sensitive
assessments." The review notes this stops being hygiene and becomes a requirement the moment an admin
console can read every prospect's assessment.

### 3.5 Residency, tenancy, isolation

- **Residency.** Single region, `us-east-1`, AWS account `023138541872`
  (`deprovisioning_plan.md:4-5`). No documented policy. Worth noting the asymmetry: the diagnostic
  asks prospects (Q6.2) what sovereignty and residency requirements constrain *their* AI deployment,
  while having no stated position of its own.
- **Tenancy.** None. Two executives at the same client aggregate to the company. **D3** recommends
  per-user scope by default with explicit opt-in sharing, reasoning that per-company "cannot be walked
  back once someone has seen a colleague's scorecard". Requires a stable `company_id`;
  `company_name_raw` is free text and will not group reliably.
- **The blocking question** (§6): *can findings from a CFO's assessment be disclosed to the CIO of the
  same company without permission?* This blocks the profile schema, not just policy.
- **Multi-tenancy proper** — per-client isolation, separate encryption keys, region pinning — is
  explicitly out of scope so far (§11).

### 3.6 Access-control posture bearing on data governance

Every route is currently ungated (`architecture_review_access_control.md` §3). Beyond §2.1 above:

| Finding | Detail |
|---|---|
| **P0-1** | **No TLS anywhere.** No ALB, ACM certificate, CloudFront, or Route 53 in `terraform/`. ECS task runs `assign_public_ip = true`, security group opens port 8080 to `0.0.0.0/0`. Plain HTTP to a raw public IP — a hard blocker on the entire auth story |
| **P0-3** | `GET /api/fixture/{name}` runs the full four-model pipeline (three Opus) with no auth and no rate limit, and writes into the partner queue. Being a `GET`, a crawler or Slack unfurl triggers it — unbounded spend amplification plus queue pollution |
| **P0-4** | `/api/debug/aws` returns the AWS account id, first 10 chars of the active access key, model IDs, and the result of a live Bedrock invoke |
| **P1-1** | `CORSMiddleware(allow_origins=["*"])` is incompatible with cookie auth and cannot simply reflect the origin without opening CSRF |
| **P1-3** | No owner field; `all_records()` is a full table `Scan`. A profile view built on scan-then-filter is a data-leak footgun — one forgotten predicate returns every prospect's scorecard |
| **P1-4** | Assessment ids are `uuid4().hex[:10]` — **40 bits, currently acting as bearer tokens** for scorecard PDFs, since nothing checks authorization |

Also relevant from the earlier audits: prompt injection via `prospect_name` / `company_name_raw`, PDF
content injection, and path traversal in `load_fixture()` (`quick_reference.md:9-17`,
`master_audit_report.md:482-495`).

### 3.7 Erasure

No tooling exists. Today a data-subject request touches one record. After the planned auth work it
spans users, invitations, sessions, assessments, audit entries, and any cached PDFs
(`architecture_review_access_control.md:171-172`). Scheduled for Phase 4, blocked on **D4**.

---

## 4. Open decisions bearing on these three questions

Restated from `architecture_review_access_control.md` §10 and `meeting_summary_analysis`
"Summary of Open Items". No new decisions are introduced here.

| # | Decision | Owner | Blocks | Standing recommendation |
|---|---|---|---|---|
| **D1** | Entra ID vs external IdP — open item #3, **overdue** | Alex Schick | Identity foundation | Both, split by role: Entra for staff, Cognito for prospects |
| **D2** | Do prospects get passwords, or passwordless invitation + session? | Alex + Denis | Profile space | Passwordless, 30-day rolling session, `password_hash` nullable |
| **D3** | Profile scope — per-user or per-company? (executive privilege) | Legal + Product | Profile schema | Per-user default, explicit opt-in sharing |
| **D4** | Assessment retention period | Legal, open item #4 | Retention TTL, erasure tooling | 12 months, consistent with the sales-funnel rationale |
| **D5** | Is public guest/sample mode retained for demos? | Product | Route policy | Yes — keep landing and sample scorecard public |
| **D6** | How does the system send invitation email? | Denis + Alex (needs DNS, possibly DXC IT) | Invitation delivery | Amazon SES; Microsoft Graph if sending as a real DXC mailbox materially helps executive trust |
| — | Consent language C-1..C-5 | DXC Legal | Customer-zero, and peer-benchmark replacement | Blocking; `content/consent_copy.md` is a placeholder |
| — | Peer-benchmark data source and methodology | Shawn + J2 | Output credibility | Start with DXC proprietary historical data; growth trigger to community cohort |
| — | Data residency | Legal, open item #4 | Multi-tenancy, vendor selection | Unstated |

---

## 5. Summary

**Client.** Intake → 20-question assessment (web or voice) → scorecard plus quick-wins memo, promised
within 24 hours after senior-partner review. As built: returned instantly and unreviewed, with no
login, no email delivery, no research agents, and placeholder peer benchmarks. A gated
invitation-based flow is fully designed and unbuilt.

**Admin.** Two roles. *Partner* review is thoroughly specified, has backend routes and a data model,
but no UI and no authentication — its mutation endpoint is world-writable. *Admin* does not exist;
it is proposed as Entra-authenticated invitation issuance and user management layered onto the
existing `/review` surface.

**Data.** Collected freely, stored indefinitely and unencrypted at the application layer, under a
carefully designed five-category consent model whose actual legal text is a placeholder. The audit
log exists only in the schema. There is no retention policy (12 months recommended), no residency
policy, no tenant isolation, no erasure tooling, and no TLS.

The documentation is internally consistent and candid about all of this: it is open item #4, a hard
compliance gate before customer-zero, and it is overdue.

---

*Related: `docs/architecture_review_access_control.md` (access control, identity, user spaces),
`aws_reference_architecture_and_cost_model.md` (AWS reference architecture and cost model),
`meetings/2026-07-24_meeting_summary_analysis.md` (open items and owners),
`companion_05_data_schemas.md` (entity and consent schemas),
`content/consent_copy.md` (placeholder consent text).*
