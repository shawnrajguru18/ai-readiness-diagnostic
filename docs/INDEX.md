# Documentation Index

**Updated:** 4 August 2026

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
| 2026-08-03 | [architecture_review_access_control.md](architecture/architecture_review_access_control.md) | Access-control and identity review: findings P0-1–P1-5, an invitation workflow, a four-table data model, phased plan, and decisions D1–D6. | MVP | ACTIVE |
| 2026-08-03 | [workflows_and_data_governance.md](architecture/workflows_and_data_governance.md) | Client workflow, admin workflow, and data lifetime and governance — incorporating the access-control review. | MVP | ACTIVE |
| 2026-08-03 | [workflows_and_data_governance_baseline.md](architecture/workflows_and_data_governance_baseline.md) | The same three questions answered from the project's own documentation only, with the access-control review excluded. | MVP | ACTIVE |

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
| 2026-08-04 | [2026-08-04_architecture_review_brief.md](meetings/2026-08-04_architecture_review_brief.md) | Meeting brief for the 4 Aug working session (action D4): the ten architecture topics condensed to one line each, five decisions requested from the room, blockers in the order they bite, and a sequencing recommendation. Derived from `architecture_topics.md`; reconciles it against the 2026-08-03 authentication decision. | MVP | ACTIVE |
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
schema of record, and the endpoints are described in `workflows_and_data_governance.md`.

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
