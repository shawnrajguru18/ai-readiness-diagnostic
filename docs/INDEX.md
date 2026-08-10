# Documentation Index

**Updated:** 6 August 2026

Every project document except the root `README.md`, which stays at the repository root by convention.

**Conventions.** Filenames are lowercase `snake_case`. `INDEX.md` and `README.md` are uppercase
because they are landmarks, not content. Documents are cited by basename throughout the analyses in
`architecture/` — this index is the basename-to-path map.

**Phase** — the delivery stage the document's content targets: `R&D` (discovery, specification and
design), `MVP` (the current hardening effort), `PROD` (production readiness and beyond).
**Status** — `ACTIVE` (authoritative) or `ARCHIVE` (historical or superseded; kept for the record).

**Document Date** is the date the document states about itself, falling back to the date it entered
git. Phase and Status are a proposed classification, not a fact drawn from the documents — review
and correct.

---

## architecture/

Target-state design, and analyses of the gap between design and build.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-06-17 | [aws_reference_architecture_and_cost_model.md](architecture/aws_reference_architecture_and_cost_model.md) | AWS reference architecture and cost model by Chris Bryson: component list, sizing (50 client orgs/month, ~175 interviews/month), lean ~$640/month production, per-environment costs, cost-control levers. Target state, largely unbuilt — it describes Cognito, Lambda, Step Functions and CloudFront, none of which exist in `terraform/`. Renamed from `architecture.md` on 2026-08-04. | PROD | ACTIVE |
| 2026-08-04 | [architecture_topics.md](architecture/architecture_topics.md) | Ten architectural topics the platform must decide, each split into specified / current / open with `file:line` citations, plus a sequencing recommendation. | MVP | ACTIVE |
| 2026-08-04 | [authorization_model_phase1.md](architecture/authorization_model_phase1.md) | **Draft specification — the single source for access control.** Passwordless email identity for all roles — single-use sign-in link plus rolling server-side session, no stored credential and no second factor in Phase 1; four roles (`user` / `power_user` / `partner` / `admin`); organizations as a first-class tenant boundary; partner assignments; capability and route matrices; bootstrap (the one password-style exception), invitation, token-lifecycle and sign-in rules; session lifetimes; findings P0-1–P1-5 and P2; enforcement rules; residual risks; Phase 1 scope cut and delivery sequence; Stage 2 parking area (erasure); open points A–H, of which **E is closed** — mail transport decided in `architecture/analysis/outbound_mail_transport.md`, whose amendments §4, §6.3, §8.1 and §12.2 now carry. Absorbed and replaced `architecture_review_access_control.md` (3 Aug) on 4 Aug. | MVP | ACTIVE |
| 2026-08-05 | [data_architecture_phase1.md](architecture/data_architecture_phase1.md) | **Draft specification — the single source for keys, indexes, versioning and concurrency.** Closes topic 3 and extends `authorization_model_phase1.md` §4. Replaces the one-table JSON blob with fourteen tables; `org_id` / `user_id` on every assessment; immutable append-only run versions with a monotone parent pointer; an input fingerprint that classifies why two runs differ (and states that reproducibility cannot be claimed); voice interviews persisted turn-by-turn; a separate invitations table; sparse per-organization review queue replacing the `Scan`; optimistic locking closing both BLOCKER races; audit log; S3 offload; and — decided 7 Aug 2026 — **no migration at all**: the legacy table holds demo and test records, so §16 is a cutover onto empty tables, which retires the backfill, the synthetic owner, the PITR dependency and the `Scan` exception, and closes open point **M**. Findings D-1–D-8 (D-1 blocking: the voice path scores a different dimension taxonomy, so a voice overall score is two-thirds Data Foundation and one-third the informational dimension; D-8: the live ElevenLabs agent does not implement its own documented tool contract, which is upstream of D-1). Proposes seven amendments to the authorization spec, registered in §4.4 and applied there — the seventh (delivery state on `auth_links` and `users`) arriving from `architecture/analysis/outbound_mail_transport.md`. Open points I–N. | MVP | ACTIVE |
| 2026-08-06 | [llm_architecture_and_output_assurance_phase1.md](architecture/llm_architecture_and_output_assurance_phase1.md) | **Draft specification — the single source for what a model decides, what untrusted content reaches a prompt, and what makes output fit to send.** Promoted from holding document on 6 Aug 2026; the promotion changed the register and added §5, and answered none of the open points. Chiefly **L-1**, prompt injection: untrusted input reaches five prompt sites unsanitized, rated BLOCKER in the audit and named in neither architecture spec. Records two surfaces the original finding predates — the third-party research payload interpolated into C2 (not reachable while `enable_research` is false) and the entire voice transcript interpolated into the voice scorer (new since `ed667aa`) — plus what contains the exposure today and what does not. Carries L-2–L-7 from `architecture_topics.md` §6: the D2 stub, the promised-but-unbuilt human gate, no eval strategy for generative text, hallucination and source attribution, the cost kill switch, and silent agent fallback. §4 fixes the boundary with the two written specs. §5 Integrations owns the ElevenLabs voice agent, benchmarked against the vendor deployment guide — findings **L-8–L-12** (the prompt generator writes to a path that no longer exists, no guardrail layer on the one agent that talks to a client executive, no standing control against contract drift, no server-side interview record, a third dimension taxonomy), requirements **R1–R7**, and a recommendation on **I2**: hybrid capture shrinks the largest injection surface rather than defending it. §6 lists the nine points not yet decided and, since 6 Aug 2026, **owns open point I2** — moved from `data_architecture_phase1.md` §19 because it decides where the determinism boundary sits for the voice channel, and it gates that document's Stage 0a and, through it, the authorization spec's Phase 2. §7 sequences delivery. | MVP | ACTIVE |
| 2026-08-03 | [workflows_and_data_governance_baseline.md](architecture/workflows_and_data_governance_baseline.md) | The same three questions answered from the project's own documentation only, with the access-control review excluded. | MVP | ACTIVE |

### architecture/analysis/

**Indexed separately — see [architecture/analysis/INDEX.md](architecture/analysis/INDEX.md).**

Decision records and investigations behind the design: why a choice was made, what was ruled out, and
what remains blocked on someone outside the team. Nothing here is normative — the requirements that
resulted are stated in the specifications, and where the two disagree the specification governs.

Holds `outbound_mail_transport.md`, the SES decision record, which lived under `specs/` until
10 August 2026 and moved when that directory became the home of the normative `SPEC_*` family.

## specs/

**Indexed separately — see [specs/INDEX.md](specs/INDEX.md).**

The normative `SPEC_*` engineering specification family: what shall be true, one subsystem per document,
plus the two shared references the family draws on (`dictionaries.md`, `role_model.md`). These are the
documents of record where they overlap anything under `architecture/`.

Individual specifications are **not listed here**. The family is large, cross-references itself heavily,
and carries its own conventions, reading order and open-item register — all of which belong in one place
beside the documents rather than duplicated into a repository-wide index that would go stale on every
amendment. This file remains the directory-level map; `specs/INDEX.md` is the document-level one.

## product/

What the product is and how it behaves. The authoritative specification for the build.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-06-14 | [companion_01_questionnaire_specification.md](product/companion_01_questionnaire_specification.md) | The 20 questions: text, options, option scores, dimension weights, skip logic, branching, and per-persona personalization rules. | R&D | ACTIVE |
| 2026-06-14 | [companion_02_quickwins_library.md](product/companion_02_quickwins_library.md) | Quick-wins pattern library: prerequisites, expected outcome ranges, timeline to value, and effort per pattern. | R&D | ACTIVE |
| 2026-06-14 | [companion_03_scorecard_design.md](product/companion_03_scorecard_design.md) | Scorecard design: the three deliverables, three audiences, layout, D1 generation steps, and the partner attestation. | R&D | ACTIVE |
| 2026-06-14 | [companion_04_agent_prompts.md](product/companion_04_agent_prompts.md) | Agent contracts A1–E3: inputs and outputs, model tiering, confidence thresholds, consent gating, anonymization rules, SLA decomposition, and cost kill switches. | R&D | ACTIVE |
| 2026-06-14 | [companion_05_data_schemas.md](product/companion_05_data_schemas.md) | Data schemas: prospect record, responses, scores, findings, consent C-1–C-5, partner review, benchmark record, audit log; storage separation and versioning guidance. | R&D | ACTIVE |
| 2026-06-14 | [ui_design_project_brief.md](product/ui_design_project_brief.md) | Five prospect-facing screens plus Screen 6, the partner review dashboard; design system, consent toggles, and copy. | R&D | ACTIVE |
| 2026-08-10 | [how_sign_in_works.md](product/how_sign_in_works.md) | **Non-technical summary of `specs/SPEC_passwordless_email_auth.md`**, for managers, marketing, legal and support. What the user experiences, session and link lifetimes, the consent gate, the four roles and the `admin`-reads-no-reports boundary, what is and is not stored, the safeguards in plain terms, and the support scenarios. Also states the four limits worth knowing before anyone presents this externally — the mailbox is the only factor, mail is the sole channel for every role including administrators, and administrative recovery runs through deployment configuration — plus a say / do-not-say list for marketing. **Not normative**; the specification governs where the two differ. | MVP | ACTIVE |

## audit/

Security, integrity and UX findings, and the plan to close them.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-07-10 | [master_audit_report.md](audit/master_audit_report.md) | Consolidated audit: YELLOW / conditional MVP-ready, security rated Restricted, phased remediation, and the hold — no public traffic until Phase 1 findings are resolved. | MVP | ACTIVE |
| 2026-07-10 | [evaluation_suite.md](audit/evaluation_suite.md) | Test specifications for the audit findings — security, concurrency and data integrity — with payloads and expected behaviour. | MVP | ACTIVE |
| 2026-07-10 | [quick_reference.md](audit/quick_reference.md) | One-page index of the 22 findings with severity, file, effort estimate and example payloads. | MVP | ACTIVE |
| 2026-07-10 | [remediation_roadmap.md](audit/remediation_roadmap.md) | Fix sequence for the audit findings, with code snippets and effort estimates. | MVP | ACTIVE |
| 2026-07-10 | [ui_ux_design_audit.md](audit/ui_ux_design_audit.md) | UX audit of the five-screen flow: happy path, gaps, error states, and accessibility. | MVP | ACTIVE |
| 2026-07-25 | [local_test_report.md](audit/local_test_report.md) | Local smoke-test record. Point-in-time snapshot; reports 95 questions served by `/api/questions` against the 20 specified, still unreconciled. | MVP | ARCHIVE |

## performance/

Latency, capacity, cost and service targets.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-07-10 | [performance_audit.md](performance/performance_audit.md) | Performance analysis: DynamoDB table configuration, latency profile, and CPU saturation at 5–7 concurrent assessments. | MVP | ACTIVE |
| 2026-07-10 | [performance_audit_summary.md](performance/performance_audit_summary.md) | Executive summary of the performance audit, including cost per assessment at $0.95 against a <$1.00 target. | MVP | ACTIVE |
| 2026-07-10 | [load_test_scenarios.md](performance/load_test_scenarios.md) | Load-test scenarios and payloads with target thresholds. | MVP | ACTIVE |
| 2026-07-10 | [optimization_roadmap.md](performance/optimization_roadmap.md) | Scaling and cost-optimization proposals, including the DynamoDB TTL proposal and a 12–15 concurrency target. | PROD | ACTIVE |
| 2026-07-10 | [slo_dashboard.md](performance/slo_dashboard.md) | SLO targets across dev, staging and production: availability, latency percentiles, review-queue latency, and concurrency assumptions. | PROD | ACTIVE |

## ci_cd/

Build and release automation.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-07-10 | [ci_cd_pipeline.md](ci_cd/ci_cd_pipeline.md) | Pipeline design: stages, quality gates, and environment promotion. | MVP | ACTIVE |
| 2026-07-10 | [setup_ci_cd.md](ci_cd/setup_ci_cd.md) | Setup instructions for the pipeline. | MVP | ACTIVE |
| 2026-07-10 | [ci_cd_pipeline_summary.md](ci_cd/ci_cd_pipeline_summary.md) | Condensed summary of the pipeline design. Redundant with `ci_cd_pipeline.md`. | MVP | ARCHIVE |
| 2026-07-10 | [ci_cd_deliverables.md](ci_cd/ci_cd_deliverables.md) | Checklist of what the CI/CD workstream delivered. Historical record. | MVP | ARCHIVE |

## deployment/

Target-agnostic release process. AWS-specific runbooks live with the AWS scripts — see
[deploy/aws/](#deployaws) below.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-07-10 | [deploy_checklist.md](deployment/deploy_checklist.md) | Pre- and post-deploy checklist covering functional and security checks. Target-agnostic — gates a release, not a particular cloud. **Referenced by `.github/workflows/deploy.yml` — update that path if this file moves.** | MVP | ACTIVE |

## deploy/aws/

Documents that describe *this* AWS account and *these* scripts, so they sit beside them rather than
here. Paths below leave `docs/`.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| — | [DEPLOY_AWS.md](../deploy/aws/DEPLOY_AWS.md) | How to deploy to AWS via the shell path, plus the directory inventory and the two-provisioning-path resource-name comparison. **Undated.** | MVP | ACTIVE |
| 2026-07-22 | [terraform_deployment.md](../deploy/aws/terraform_deployment.md) | Record of the 2026-07-22 migration from bash scripts to Terraform: what was created, and the live URL at the time. Point-in-time — the IP it records is stale. | MVP | ACTIVE |
| 2026-07-10 | [deprovisioning_plan.md](../deploy/aws/deprovisioning_plan.md) | Teardown plan: resource inventory, retention facts (7-day logs, 35-day PITR), cost, and pre-destroy verification steps. Also the de-facto record of data retention, which is why the architecture analyses cite it. | PROD | ACTIVE |
| 2026-07-10 | [pre_destroy_checklist.md](../deploy/aws/pre_destroy_checklist.md) | Checks to complete before any teardown: data export, test-only confirmation, credential and account guards, dependency checks, sign-off. Converted from `pre_destroy_checklist.txt`. | PROD | ACTIVE |
| 2026-07-10 | [post_destroy_validation.md](../deploy/aws/post_destroy_validation.md) | Post-teardown verification. Sections 1–3 automated by `deploy/aws/post_destroy_validation.sh`; billing review, backup archival and sign-off remain manual. Converted from `post_destroy_validation.txt`. | PROD | ACTIVE |

## integrations/

External services.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-06-14 | [elevenlabs_agent_setup.md](integrations/elevenlabs_agent_setup.md) | ElevenLabs voice agent configuration: full system prompt, client tool contract, dynamic variables, compressed mode, visibility and allowed origins. | MVP | ACTIVE |

## meetings/

Decision records.

| Document Date | Name | Description | Phase | Status |
|---|---|---|---|---|
| 2026-08-03 | [2026-08-03_meeting_summary.md](meetings/2026-08-03_meeting_summary.md) | Kickoff. **Resolves authentication:** username and password for V1, email MFA for V2, Delivery ID and Okta dropped, no client self-provisioning — DXC issues time-limited registration invitations — and Entra ID for internal and admin roles. Also: HTTPS on a real DNS name is the critical path (URL and certificate already exist); QA and production environments required; architect for phase one of a roadmap; Catalyst optional and not to be built around. Transcript is partial — ~20 of 63 minutes missing. | MVP | ACTIVE |
| 2026-07-24 | [2026-07-24_meeting_summary_analysis.md](meetings/2026-07-24_meeting_summary_analysis.md) | Gap analysis of the scoping call: nine open items with owners and severities. Item #3 (authentication) is now closed by the 2026-08-03 kickoff; items #1, #4, #6 and #9 remain open. | R&D | ACTIVE |
| 2026-07-24 | [2026-07-24_meeting_summary.md](meetings/2026-07-24_meeting_summary.md) | Intro and scoping call record. Superseded on scope, timeline and authentication by the 2026-08-03 kickoff. | R&D | ARCHIVE |

---

## Known staleness

The 2026-08-03 kickoff post-dates the two workflow analyses and `architecture_topics.md`, and it
**closes decisions those documents still record as open**:

- **Topic 1, authentication** — decided: username and password for V1, email-based MFA for V2,
  Entra ID for internal and admin roles.
- **Topic 1, prospect enrolment** — decided: no client self-provisioning; a DXC employee uploads
  names and emails and the system issues time-limited registration invitations. This is the
  mechanism `workflows_and_data_governance_baseline.md` records as unspecified.
- **Topic 2, internal roles** — partly decided: an internal/admin population exists and is served by
  Entra ID, which answers the baseline analysis's finding that no admin role was specified anywhere.
- **Topic 10, environments** — decided: at least QA and production.

Those three documents have not yet been revised to reflect it.

## Not under docs/

Deliberately kept beside the code they describe:

- `README.md` — root landmark.
- `web/README.md`, `web/QUICKSTART.md`, `web/USAGE.md`, `terraform/README.md`,
  `content/consent_copy.md`.
- `deploy/aws/*.md` — the five AWS documents listed above.

**`web/` was reduced to three documents on 2026-08-04.** It had carried ten, a parallel doc set with
its own index and its own AWS deployment guide, none of it in this file. Deleted: `READY_FOR_GIT.md`
and `BUILD_VERIFICATION.md` (one-off agent session reports), `REFACTORING.md` (the single-file-HTML
to React migration, long since done), `DOCS_INDEX.md` (a second index, for a doc set that no longer
exists), and `AWS_DEPLOYMENT.md` + `DEPLOYMENT_CHECKLIST.md` (an S3 + CloudFront design that was
never built — the app ships as one container serving `web/dist` from FastAPI, per
`deploy/aws/DEPLOY_AWS.md`). `API_CONTRACT.md` went with them; `app/models.py` is the request/response
schema of record, and every route as built is tabulated in
`architecture/authorization_model_phase1.md` §8.2.

**The dividing line.** A document lives under `docs/` when it would still be true if the project
moved off AWS; it lives with the code when it names this account, these resources, or these scripts.
That is why `deploy_checklist.md` stayed (it gates a release: tests, security scans, sign-off) while
the four teardown and Terraform documents moved (account `023138541872`, `us-east-1`, specific
cluster and table names, specific script invocations).

**Citations are unaffected.** The architecture analyses cite `deprovisioning_plan.md:48` and similar
by basename, not path — this index is the basename-to-path map, so those references stay valid after
the move. Nothing else in the repository linked to the moved files except
`.github/workflows/deploy.yml`, which points only at `deploy_checklist.md` and did not move.

Generated artifacts at the root reference the old uppercase filenames. `DOCUMENTATION_REVIEW.json`,
`audit_dashboard.html`, `security_review.json` and `SECURITY_GUARDRAILS_REVIEW.json` have since been
deleted from the working tree; `quality-gates.json` and `performance_benchmarks.json` remain. None
were rewritten — rewriting generated output invites drift. Regenerate or retire what is left.

**Retired 2026-08-04.** `EXECUTIVE_BRIEF.txt` was deleted: every one of its five findings is present
in [master_audit_report.md](audit/master_audit_report.md), which carries the full set.
`pre_destroy_checklist.txt` and `post_destroy_validation.txt` were converted to the two markdown
documents above, and the mechanical half of the latter became
`deploy/aws/post_destroy_validation.sh`. `requirements.txt` is the only remaining root `.txt` — it
must stay there, as `Dockerfile`, `Makefile` and three CI workflows read it from that path.

**Consolidated 2026-08-04.** Every AWS operations script now lives in `deploy/aws/`, so the
repository root holds no operational scripts at all:

| Script | Provisioning path it acts on |
|---|---|
| `01-bootstrap.sh` → `02-deploy.sh` → `03-teardown.sh` (+ `config.sh`) | shell path — `ai-readiness-cluster`, `ai-readiness-sessions` |
| `deploy.ps1`, `push-image.ps1`, `destroy_terraform.sh` | Terraform path — `ai-readiness-diagnostic-*` |
| `post_destroy_validation.sh` | **both** — it verifies either name set is gone |

The two paths name resources differently, so a teardown script from one reports success while
deleting nothing from the other. Each script now carries a header saying which set it touches;
`pre_destroy_checklist.md` step 2.3 is the check that resolves which one you need.
`deploy/aws/DEPLOY_AWS.md` carries the full resource-name comparison.

The DXC brand assets moved from the root into `assets/DXC Logo/` (62 files, 20 MB — SVG, EPS, PNG and
JPG in brand-mark and tagline-lockup variants). That directory is now the **source of truth for design
work only**; nothing at runtime reads from it.

The one file the application needs is vendored into `app/assets/dxc-brand-mark-dark.svg` (1.4 KB) and
loaded by `app/pdf.py` from a package-relative path, documented in `app/assets/README.md`. This also
fixed the `Dockerfile`, which previously copied the entire 20 MB brand kit into the image with
`COPY ["DXC Logo", "/app/DXC Logo"]` — a line that had become a build failure once the directory
moved. `COPY app ./app` now carries the single SVG instead.

`app/scorecard.py` and the `web/` components embed the mark as an inline SVG path rather than reading
any file, so they were unaffected.

`deploy/aws/iam/forcemfa_policy_v2.json` holds the force-MFA policy the two `.ps1` scripts assume.
`forcemfa_policy_updated.json` was deleted as a strict subset of it — same `AllowIAMOperations` and
`AllowECROperationsWithMFA`, minus the ECS, CloudWatch Logs, EC2-networking and ELB statements, and
with a narrower `DenyNonMFAOperations` list. Recoverable from git if ever needed.
