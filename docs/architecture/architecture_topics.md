# Architecture Topics — Outline and Current State

**Date:** 4 August 2026
**Author:** Denis Morozov
**Status:** Outline — a skeleton to be filled in per topic
**Purpose:** Define the architectural topics the platform needs decided, and record for each what
the project's documentation already specifies, what exists today, and what is genuinely open.

**How to use this:** each topic below is scoped by the question it must answer, then split into
*specified* (what our own documents already commit to), *current* (what the code and audits record),
and *open* (what nobody has decided). The open items are the work. Citations are `file:line` so a
claim can be checked rather than trusted. Two short forms recur: `meeting_summary_analysis` is
`docs/meetings/2026-07-24_meeting_summary_analysis.md`, and `companion_0N` is the corresponding
`docs/product/companion_0N_*.md`. Root-level docs are cited by basename; see `docs/INDEX.md`
 for the name-to-path map.

**Sources:** the repository's markdown, excluding the 3 Aug access-control review (since folded into
`docs/architecture/authorization_model_phase1.md` and removed) —
consistent with `docs/workflows_and_data_governance_baseline.md`, on which this outline is built.
That review already covers topics 1 and 2 in depth and can be folded back in when we want a proposal
rather than a problem statement.

---

## Topic map

The six topics originally proposed, and where they land here:

| Proposed | Becomes |
|---|---|
| Authentication | **1** Authentication and identity — plus **2**, split out |
| Data governance, security and audit | **4** Governance and privacy, **5** Application security, audit logging into **4** |
| Logging | Audit logging → **4**; application logging → **9** |
| Observability | **9** Observability |
| LLM output verification | **6** AI/LLM architecture and output assurance, broadened |
| Deployment and operations | **10** Deployment, environments and operations |
| — | **3** Data architecture, lifecycle and consistency *(new)* |
| — | **7** Asynchronous processing and orchestration *(new)* |
| — | **8** External dependencies and data egress *(new)* |

The splits are deliberate. Authentication and authorization fail differently and the documented
problems are overwhelmingly the latter. Audit logging and application logging are different
artefacts with different retention drivers, and bundling them is how we end up specifying CloudWatch
twice and the append-only audit store not at all.

---

## 1. Authentication and identity

**Must answer:** who are the actors, how does each prove identity, and what is the credential
lifecycle?

**Specified.** `aws_reference_architecture_and_cost_model.md` commits to a two-population model: Amazon Cognito User Pools
for client executives with MFA (`architecture.md:36`), AWS IAM Identity Center for DXC advisor
access (`:37`), and JWT authentication at API Gateway (`:38`). Cognito is costed at ~300 MAU, free
under 50k (`:58`).

**Current.** No authentication on any route — "Auth: None today — exposed via raw IP/URL"
(`meeting_summary_analysis:83-84`). `POST /api/assess`, `GET /api/fixture/{name}`, and all three
`/api/review/*` routes are open. `deploy_checklist.md:430` includes a post-deploy check for "no
failed login attempts", for a system with no login.

**Open.**

1. **The IdP decision** — open item #3 / action A4, owner **Alex Schick**, due w/c 28 Jul, HIGH,
   overdue. The recorded tension: Entra ID serves DXC employees for customer-zero, but external
   client executives hold no DXC credentials. Candidates on the table
   (`meeting_summary_analysis:90-96`): passwordless invite link with a one-time token, SAML/OIDC
   federation to the client's own IdP, or DXC-issued short-lived credentials.
2. How a prospect is enrolled in the first place — self-serve signup, partner-initiated invitation,
   or both. Nothing in the documentation specifies an enrolment mechanism.
3. Whether the scorecard portal token at `/portal/[token]` is an authentication mechanism in its own
   right, and if so its lifetime, revocability, and single-use semantics. See topic 2.
4. Session lifetime and re-authentication for a 20–26 minute assessment that currently cannot
   survive a page refresh.
5. Service-to-service identity: how the backend authenticates to Bedrock, ElevenLabs, and DynamoDB,
   and where those credentials live. `aws_reference_architecture_and_cost_model.md:44` names Secrets Manager + KMS; nothing
   records what is actually in use.

---

## 2. Authorization, tenancy and isolation

**Must answer:** given an authenticated actor, what may they see and do — and how is one client's
data kept from another's, and from the wrong people inside the same client?

This is the topic most likely to be missed, because open item #3 is worded as an authentication
question. Picking an IdP resolves none of what follows.

**Specified.** Multi-tenant SaaS at 50 client orgs/month × 3–4 executives each ≈ 175
interviews/month (`architecture.md:7`). DynamoDB with **per-tenant partition keys** (`:42`).
API Gateway serving **tenant-scoped REST endpoints** (`:38`). IAM Identity Center providing advisor
"RBAC" (`:37`) — the only mention of internal roles anywhere, and unelaborated.

**Current.** No authorization layer. Specifically:

- `/api/review/queue` returns every company's assessment; the test suite annotates it exactly so —
  `"endpoint": "/api/review/queue"  # Contains all company assessments`
  (`evaluation_suite.md:512`), and lists it among endpoints reachable cross-origin under
  `allow_origins=["*"]` (`:607`).
- No tenant separation: "If Bank of America's CFO and CTO both assess, is their data separated in the
  backend? (Appears not in V0 — both responses are aggregated to the 'company'.)"
  (`meeting_summary_analysis:112`).
- The single DynamoDB table is keyed on a 10-character hex `id` with no tenant dimension
  (`performance_audit.md:79-86`).

**Open.**

1. **Executive privilege** — "Can findings from a CFO's assessment be disclosed to the CIO without
   permission?" (`meeting_summary_analysis:115`). This is a product question before it is a
   technical one, and it determines whether the tenant boundary is the organisation or the individual.
2. The internal role model. The documentation describes exactly one internal actor — the senior
   partner reviewer — and no platform administrator. Nobody owns inviting prospects, managing
   accounts, or reading the audit log, because no mechanism for any of those is specified. Decide
   whether an admin role exists, and what it may do.
3. Whether a partner sees the whole review queue or only their own referred prospects.
   `PartnerReviewRecord` carries `partner_id` and prospect records carry `referring_partner_id`
   (`companion_05:95`), so the data supports scoping; nothing says whether to apply it.
4. The tenancy mechanism: partition-key prefixing, separate tables, or separate accounts — and
   whether isolation is enforced at the data layer, the API layer, or both.
5. Portal token semantics — a URL-borne bearer credential that will be forwarded by email. Lifetime,
   revocation, whether it grants read-only access to one scorecard, and what happens after delivery.

---

## 3. Data architecture, lifecycle and consistency

**Must answer:** what is stored, in what shape, how does it change over time, and what happens under
concurrent writes?

**Specified.** `companion_05_data_schemas.md` is thorough — typed entities for the prospect record,
question responses, dimension scores, findings, consent, partner review, benchmarks, and audit
entries, each carrying `AuditMetadata` with `created_by`, `last_modified_by` and a monotonic
`version` (`companion_05:25`). Storage guidance at `:1032-1042` separates the operational store, the
benchmark store (no foreign key back to prospects, `:1036`), and the append-only audit log
(`:1038`). Content and agent versioning is required so historical reasoning is reproducible
(`:1050-1052`).

**Current.** One DynamoDB table, `ai-readiness-sessions`, partition key `id` (10-char hex),
PAY_PER_REQUEST, with two attributes: `id` and `doc` — the entire session serialized as a JSON blob
(`performance_audit.md:79-86`). Consequences worth stating plainly: a hard 400 KB ceiling per
assessment, no query path except by id, every partial update is a whole-record rewrite, and no
version attribute exists despite the schema requiring one.

**Open.**

1. **Concurrency control.** Two documented races, both rated BLOCKER: the DynamoDB write path has no
   `ConditionExpression` and no version field (`quick_reference.md:22`), and the review decision
   endpoint has no optimistic locking — concurrent approve and send-back silently lose one
   (`evaluation_suite.md:1085-1090`). The second is a governance defect in concurrency clothing:
   `PartnerReviewRecord` is meant to be the auditable record of who approved what.
2. Whether to keep the blob model or normalise to the entity model `companion_05` already specifies.
   The blob is why there is no audit log, no versioning, and no queryable review queue.
3. Client-side answer persistence. Questionnaire answers live in React state with no storage
   (`web/README.md`), so a refresh or timeout loses an 18–26 minute session
   (`ui_ux_design_audit.md:104-109`).
4. Retention enforcement — see topic 4; the mechanism is a data-architecture decision even though
   the policy is a legal one.
5. Schema evolution: how a stored assessment scored under question pool v1 is read after the pool
   changes. `companion_05:1050` requires versioned content references; nothing implements them.
6. Reconcile the question pool. `local_test_report.md:25,64,144` reports 95 questions served by
   `/api/questions` against the 20 specified in `companion_01`. Check `content/question_pool.yaml`
   before treating this as either a bug or a stale report.

---

## 4. Data governance, privacy, residency and audit

**Must answer:** what may we collect, for what purpose, held where, for how long, provable how, and
deletable how?

This is open item #4 — owner **Legal + J3**, due **before customer-zero**, HIGH
(`meeting_summary_analysis:230`), overdue.

**Specified, and specified well.** Five consent categories with defaults, legal basis
(consent / legitimate_interest / contract), applicable jurisdictions, consent method, and the version
of the language the prospect actually saw (`companion_05:142-166`). Consent records are immutable —
changes create new records. Every downstream use is gated in the agent prompts and returns an explicit
skip state rather than proceeding silently: E1 on C-4 (`companion_04:1203`), E2 on C-2 (`:1269`),
E3 on C-3 (`:1338`). Anonymization for the benchmark library is spelled out field by field
(`companion_04:1259-1271`) — remove company and personal identifiers, preserve country-level
geography and size band only, bucket specific financials. A system-wide `AuditLogEntry` with twelve
event types (`companion_05:964-993`) serves a stated audit-first principle: "Every entity has audit
trail fields capturing who/what/when generated it. Critical for partner review credibility and
regulatory compliance" (`:25`).

**Current.**

| | State | Source |
|---|---|---|
| DynamoDB records | Indefinite — no TTL attribute, no purge job | `deprovisioning_plan.md:48` |
| PITR | 35 days rolling, enabled on creation | `deprovisioning_plan.md:423` |
| CloudWatch logs | 7 days | `deprovisioning_plan.md:47` |
| Generated PDFs | No documented lifecycle | — |
| Audit log | Not implemented | — |
| Consent copy | Explicit PLACEHOLDER, covering 2 of 5 categories | `content/consent_copy.md` |
| Erasure | No API, tooling, or process | — |
| Residency | Single region `us-east-1`, no policy | `deprovisioning_plan.md:4-5` |

A DynamoDB TTL on `expires_at` exists only as a proposal, and there for cost reasons rather than
privacy (`optimization_roadmap.md:334-337`).

**Open.**

1. **Retention period** — 30 days, 1 year, or indefinite for benchmarking? The only figure written
   down is a recommendation, not a decision: because the diagnostic is a sales-funnel asset there is
   a case to "keep for 12 months to inform delivery", needing explicit prospect buy-in
   (`meeting_summary_analysis:117`).
2. **Residency** — which region, or on-premise (`:111`). Note the asymmetry: Q6.2 asks prospects what
   sovereignty constraints bind *their* AI deployment while we state no position of our own.
3. **Consent language** — Legal-reviewed text for all five categories. `content/consent_copy.md` is
   headed "MUST be replaced with DXC Legal-reviewed text before any real interview (including
   customer zero)" and its closing line describes a two-consent system.
4. **What C-2 actually permits**, including whether findings may reach third parties (`:114`).
5. **Consent withdrawal.** The only mechanism described anywhere is one line — the E2 audit trail
   retains the prospect id because it "allows tracing if consent withdrawn"
   (`companion_04:1265`) — plus a `withdrawn` processing status (`companion_05:133`). The capability
   exists by design; no workflow, owner, API or SLA connects to it.
6. **Align the C-2 field name.** The code is self-consistent on `c2_anonymized_benchmark`
   (`app/models.py:54`, `web/src/types.ts:100`, all three fixtures). Three
   documents disagree: `companion_05:154` uses `c2_anonymized_benchmark_contribution`,
   `meeting_summary_analysis:104` quotes a non-existent `c2_use_for_benchmarking`, and
   `load_test_scenarios.md:63` sends `c2_data_retention` — a different consent entirely. Fix before
   Legal drafts around it, not after.
7. **Consent path test coverage.** Every `evaluation_suite.md` fixture posts C-1 alone or
   `consent={}`. C-2's default-on behaviour and the E1/E2/E3 skip paths have no coverage.
8. **Audit log implementation** — store choice, append-only enforcement, and retention "per legal
   review" (`companion_05:1038`).
9. **Regulatory position** — GDPR, UK DPA, EU AI Act as they apply to *us*. `companion_04:592` has
   agent B5 researching exactly this for the prospect.

**Worth naming: a circular dependency.** The hardcoded peer benchmarks are to be replaced once C-2
volume accrues (`meeting_summary_analysis:27`), C-2's language is unwritten, and the volume
threshold is undefined. So the consent copy gates output credibility, not only compliance. The
recommended break is to seed from DXC proprietary historical data and set an explicit growth trigger
for the community cohort (`:36`).

---

## 5. Application security and trust boundaries

**Must answer:** where does untrusted input enter, and what does it reach?

**Current.** `master_audit_report.md:151` rates security 🔴 Restricted — "critical vulnerabilities
present; not suitable for untrusted input" — with the overall recommendation "Go to staging; NO
public traffic until Phase 1 complete" (`:155`), and specifically "NO public traffic until findings
#1, #2, #3, #5 resolved" (`:47`). `quick_reference.md` enumerates 22 findings. The ones bearing on
architecture rather than a line fix:

| Finding | Boundary crossed | Source |
|---|---|---|
| Prompt injection via `prospect_name`, `company_name_raw` | User input → LLM prompt | `quick_reference.md:11` (BLOCKER) |
| PDF content injection | User input → ReportLab document | `master_audit_report.md:486-487` (CRITICAL ×2) |
| Path traversal in `load_fixture()` | User input → filesystem; "reads arbitrary files (secrets.yaml, .env)" | `master_audit_report.md:493` |
| SSRF via `company_website` | User input → outbound HTTP; `http://169.254.169.254/latest/meta-data/` | `quick_reference.md:108-111` |
| Email header injection | User input → mail headers; `\r\nBcc: attacker@evil.com` accepted | `quick_reference.md:115-117` |
| CORS wildcard | Any origin → all endpoints incl. `/api/review/*` | `evaluation_suite.md:493,525` |
| Memory exhaustion | Unbounded request → process | `master_audit_report.md` (HIGH) |

**Open.**

1. A single input-validation layer at the boundary rather than per-call-site fixes — the same
   unvalidated fields recur across five findings.
2. The allowed-origin list per environment, replacing `allow_origins=["*"]`
   (`evaluation_suite.md:623`).
3. Prompt-injection defence strategy for topic 6: structural separation of instructions from data,
   or sanitisation, or output constraints — decide which, since user-supplied company names must
   reach the model by design.
4. Encryption of PII at the application layer. Nothing in any document mentions it; KMS covers
   storage-level encryption only.
5. Rate limiting and abuse control on an endpoint that spends Bedrock tokens per call.
6. Dependency and container scanning in CI.

---

## 6. AI/LLM architecture and output assurance

**Must answer:** which decisions does a model make, which does deterministic code make, and how do we
know the model's output is fit to send a client executive?

Broader than output verification alone — verification is one control among several.

**Specified.** The determinism boundary is the strongest design decision in the project and deserves
to be stated explicitly as architecture: **scoring is deterministic** (option scores × within-dimension
weights, renormalized over questions actually asked, `companion_01:414-424`), while narrative,
findings and framing are generative. Model tiering by task — Opus for synthesis, quick wins and
validation; Sonnet for persona, research and scorecard; Haiku for intake. A D2 validation agent gates
delivery, with severity CRITICAL defined as output that "would mislead the prospect or embarrass DXC.
Must be addressed before delivery" (`companion_04:1116`). Confidence thresholds route attention:
below 0.6 triggers validation, below 0.4 "may trigger partner review queue priority or re-processing"
(`:27`). Reasoning traces are captured for the audit log and surfaced in the review interface (`:31`).
The human gate is explicitly not a model: "The senior partner review is not an LLM agent. It is a
workflow" (`:1385`). Cost thresholds trigger kill switches (`:1431`).

**Current.** D2 is a stub — "not yet implemented in MVP (deferred)"
(`meeting_summary_analysis:70,183`), which means the flags meant to drive review priority are
never generated. Research agents B1/B2/B3 are gated off behind `AIDIAG_ENABLE_RESEARCH=false`
(`:73`). Peer benchmarks quoted as "Industry average: 58 (n=42)" are hardcoded placeholders in
`app/benchmarks.py` (`:21-24`). The partner review UI does not exist, so in practice nothing reviews
anything before the prospect sees it.

**Open.**

1. **Build D2** — open item #9, owner **Denis**, due Fri 31 Jul, HIGH. Without it there is no
   automated assurance and no input to human review priority.
2. Eval strategy: a regression set of assessments with expected outputs, and what "passing" means for
   generative text. `evaluation_suite.md` covers security and integrity, not output quality.
3. Prompt and content versioning to satisfy the reproducibility requirement — "a historical
   scorecard's reasoning must be reproducible… which agent versions ran, which content versions were
   used" (`companion_05:1052`). Nothing implements this today.
4. Hallucination surface once research agents are switched on: findings will cite external sources,
   and `companion_05:303-447` requires per-source attribution with fetch timestamps.
5. Whether the human gate is mandatory before delivery in V1, or advisory. Everything client-facing
   promises it — the voice agent, the Submitted screen, and the scorecard's own partner attestation
   (`companion_03`) — while the code delivers synchronously without it. Either build the gate or stop
   promising it.
6. Cost ceiling per assessment and the kill-switch mechanism. Target <$1.00, measured at $0.95
   (`performance_audit_summary.md:70`) against ~$0.46 modelled for Bedrock alone
   (`architecture.md:88`) — a thin margin for a control that does not yet exist.
7. Model and region availability for Bedrock, and behaviour on model deprecation.

---

## 7. Asynchronous processing and orchestration

**Must answer:** what happens between submission and delivery, and how is a 24-hour commitment
actually met?

This topic exists because its absence is the single largest gap between what we promise and what we
built.

**Specified.** AWS Step Functions orchestrates the report-build workflow (`architecture.md:21,40`).
The 24-hour SLA decomposes into per-agent latency budgets summing to under 22 hours, "leaving 2 hours
for partner review and delivery", with budget overruns surfaced to the orchestrator
(`companion_04:1427`). Thirteen processing states carry the record from `submission_received` through
`partner_review_queued`, `approved_for_delivery` and `delivered`, with `sla_target` and `sla_breached`
tracked throughout (`companion_05:120-139`).

**Current.** Synchronous. "Submitted screen shows spinner forever (until `/api/assess` returns);
Scorecard appears instantly once data arrives" (`ui_ux_design_audit.md:312`). No queue, no state
machine, no SLA tracking. A single ECS task (1 vCPU, 2 GB) "maxes at 5-7 concurrent assessments"
(`optimization_roadmap.md:12`), against a production assumption of 50–200 concurrent users
(`slo_dashboard.md:105`) — a gap of one to two orders of magnitude.

**Open.**

1. Whether V1 is synchronous-and-honest or asynchronous-as-designed. This is a product decision with
   large architectural consequences, and it determines whether the partner gate, the email delivery,
   and the 24-hour promise are in or out. Everything client-facing currently assumes asynchronous.
2. Orchestration mechanism — Step Functions as designed, or a simpler queue on the current ECS
   deployment.
3. Idempotency: a resubmitted or retried assessment must not create a duplicate prospect record or
   double-spend Bedrock tokens.
4. Retry and partial-failure semantics. If C3 quick-wins fails after C2 synthesis succeeded, is the
   assessment deliverable, retryable, or dead?
5. SLA measurement and breach alerting — nothing currently tracks the 24-hour clock.
6. Concurrency ceiling and how the gap between 5–7 and 50–200 is closed. `optimization_roadmap.md:655`
   scopes a change reaching 12–15 — still short of the production assumption.

---

## 8. External dependencies and data egress

**Must answer:** which third parties process our clients' data, under what terms, and what happens
when one is unavailable?

**Specified.** ElevenLabs Conversational AI delivers the voice interview as external SaaS, billed per
minute (`architecture.md:27,49`), at ~4,400 voice-minutes/month ≈ ~$440/mo — the dominant cost line
(`:73`). Amazon Bedrock serves all model calls (`:41`). Secrets Manager + KMS hold the keys (`:44`).

**Current.** The ElevenLabs agent is configured **Visibility: Public**, because "the embed widget
only loads public agents" (`elevenlabs_agent_setup.md:238`), with control limited to an allowed-origins
list (`:239`). Agent ID is recorded in `local_test_report.md`. Voice recordings are held by ElevenLabs
and never enter our backend (`meeting_summary_analysis:105`).

**Open.**

1. **Voice recordings** — "Who owns them? Are they deleted after transcript? Can they be reused for
   training?" (`meeting_summary_analysis:113`). These are recordings of named client executives
   discussing AI strategy, held by a third party under terms nobody has recorded.
2. Whether a public agent is acceptable for confidential executive interviews, and what mitigations
   exist if the embed model requires it — signed URLs, short-lived agent instances, or moving the
   voice path server-side.
3. Data-processing agreements and sub-processor disclosure for ElevenLabs and Bedrock, and whether
   prospects are told who processes their interview.
4. Bedrock data-handling posture — model invocation logging, and confirmation that inputs are not
   used for training.
5. Degradation behaviour: what the prospect experiences when ElevenLabs or Bedrock is unavailable
   mid-interview.
6. Whether the chat path is a genuine fallback for the voice path, given cost pressure pushes toward
   chat anyway (`architecture.md:120`).

---

## 9. Observability

**Must answer:** can we tell what the system is doing, what it cost, and that it met its targets —
without reading confidential content?

Application telemetry only. The audit log lives in topic 4; the two have different consumers,
different retention drivers, and different sensitivity.

**Specified.** CloudWatch + X-Ray for logs, metrics, tracing and usage analytics
(`architecture.md:45`). `slo_dashboard.md` sets targets across dev/staging/prod tiers: production
availability 99.5%, API p95 <8s, DB p95 <100ms, PDF generation p95 <3.5s, review-queue p95 <500ms
(`slo_dashboard.md:17-31,112-119`), at 50–200 concurrent users (`:105`). Per-agent latency budgets and
per-prospect cost are tracked at agent level and aggregated (`companion_04:1427,1431`).

**Current.** CloudWatch log group `/ecs/ai-readiness-diagnostic` at 7-day retention, ~100 MB/day
(`deprovisioning_plan.md:47,279`). Enhanced LLM error logging was added recently (commit 19a7a4e).
No documented dashboards, alarms, or trace instrumentation.

**Open.**

1. **Log content policy.** This is where observability meets governance: prompt and response logging
   puts confidential executive interview content into log storage. Decide what may be logged, what
   must be redacted, and whether 7 days is right for diagnostics that may contain PII.
2. Whether 7-day retention is sufficient for incident investigation, given it is shorter than the
   24-hour-SLA workflow's own audit needs by a wide margin.
3. Metrics to emit and alarm on, mapped to the SLO tiers — none are currently defined as alarms.
4. Cost observability per assessment, feeding the kill switches in topic 6.
5. Tracing across the agent pipeline so a slow assessment can be attributed to an agent.
6. Correlation identifier threading request, assessment, agent call, and audit entry.

---

## 10. Deployment, environments and operations

**Must answer:** how does code reach production, what environments exist, and how do we recover?

**Specified.** Separate AWS account per environment under Organizations for blast-radius isolation and
per-env billing (`architecture.md:92`), with dev/staging adding ~20–30% over prod's ~$640/mo
(`:110-114`). Prod-only hardening: VPC/NAT, GuardDuty, Security Hub, expanded WAF, geo-DR (`:96`).
CI/CD via CodePipeline/CodeBuild or GitHub Actions with Terraform/CDK across dev→staging→prod
(`:48`). CloudFront + WAF at the edge with Shield Standard (`:34`).

**Current.** Single AWS account `023138541872`, single region `us-east-1`
(`deprovisioning_plan.md:4-5`), ECS Fargate + ECR + DynamoDB, Terraform IaC.
`deploy_checklist.md` and `deprovisioning_plan.md` are both detailed and current. No CloudFront/WAF,
no GuardDuty/Security Hub, no separate environments recorded. Recent commits show startup fragility
being worked out (cbfa830, 60cb039).

**Open.**

1. Environment topology — whether to adopt account-per-environment now or defer, and what customer-zero
   runs on.
2. Edge posture: whether WAF and CloudFront are prerequisites for public traffic, given topic 5's
   findings and the `master_audit_report.md:47` hold.
3. Backup and DR versus what exists. PITR at 35 days is a backup mechanism; there is no stated RTO or
   RPO, and no restore has been rehearsed (`deprovisioning_plan.md:410-423` documents the command,
   not a drill).
4. Secrets management in practice — Secrets Manager is specified; the current source of the Bedrock
   API key and ElevenLabs credentials is not recorded.
5. Release process: migrations against the blob store, rollback, and whether deploys are zero-downtime.
6. Operational ownership — who is on call, and what the runbook is for a breached SLA or a failed
   assessment. `deprovisioning_plan.md` names an owner for teardown; nothing names one for running.
7. Cost controls as an operational practice: the levers in `architecture.md:116-128` are ranked
   sensibly (ElevenLabs first, Claude tiering second) but nothing monitors or enforces them.

---

## Sequencing

Three topics are already gating per the project's own documents, and they are not independent:

1. **Topic 5, application security** — `master_audit_report.md:47`, no public traffic until findings
   #1/#2/#3/#5 are resolved. Nothing else ships past staging until this clears, and it is the most
   self-contained work on the list (Phase 1 estimated 12–16 hours, `:87`).
2. **Topics 1 and 2, authentication and authorization** — open item #3, HIGH, overdue. Topic 2
   depends on the executive-privilege product decision, so start that conversation now rather than
   after the IdP is chosen; the IdP choice does not resolve it.
3. **Topic 4, governance** — open item #4, Legal, due before customer-zero, overdue. Legal turnaround
   is outside our control, and the consent text blocks both compliance and benchmark credibility, so
   this has the longest lead time and should be moving in parallel from today.

Then, in rough dependency order: **topic 3** (data model — it blocks the audit log, versioning, and
locking that topics 4 and 6 depend on), **topic 7** (decide synchronous-or-asynchronous, since it
determines whether the partner gate and email delivery are in V1 scope), **topic 6** (D2 and evals),
**topic 8** (dependency terms — long lead time if contracts are involved, so start early even though
it sequences late), then **9** and **10** as continuous work.

One decision unblocks a disproportionate amount: **whether V1 delivers synchronously or
asynchronously** (topic 7, open item 1). It determines whether the partner review gate, email
delivery, the portal token model, and SLA tracking are V1 concerns or V2 concerns — which in turn
scopes topics 1, 2, 6 and 9. It also settles the largest honesty gap in the product, since every
client-facing surface currently promises a partner-reviewed scorecard within 24 hours.

---

*Related: `docs/workflows_and_data_governance_baseline.md` (the analysis this outline rests on),
`docs/architecture/authorization_model_phase1.md` (topics 1 and 2 specified rather than surveyed),
`aws_reference_architecture_and_cost_model.md` (target AWS architecture and cost model),
`meetings/2026-07-24_meeting_summary_analysis.md` (open items and owners),
`master_audit_report.md` / `quick_reference.md` / `evaluation_suite.md` (security and integrity
findings), `companion_05_data_schemas.md` (entity, consent and audit schemas),
`companion_04_agent_prompts.md` (agent contracts, consent gating, SLA and cost governance).*
