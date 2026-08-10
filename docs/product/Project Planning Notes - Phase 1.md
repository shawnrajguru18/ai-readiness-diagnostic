# AI Readiness Diagnostic Project Overview

**Document owner:** Alex Schick  
**Technical owner:** Denis Morozov  
**Product owners:** Chris Bryson, Shawn Rajguru, Robb Shally  
**Phase:** Phase 1 MVP  
**Status:** ACTIVE  
**Last updated:** 2026-08-10  
**Current position:** Starting Week 2, Build the Foundation  

> This document is the concise project source of truth for current scope, delivery direction, decisions, risks, and immediate actions. Detailed product, architecture, audit, and meeting records remain in their existing repository documents.

## 1. Project Objective

Evolve the existing AI Readiness Diagnostic demo into a secure, usable end-to-end MVP that supports:

- Controlled respondent onboarding and access
- Text and voice interviews
- Persistent interview progress and results
- System-generated draft scorecard/report
- Human Partner curation before final delivery
- Basic participation tracking
- Controlled internal testing and deployment

**Phase 1 stretch goal:** Demonstrate a practical level of adaptive questioning without delaying the required end-to-end workflow.

## 2. Current Status

### Week 1 completed

- Reviewed the high-level Phase 1 roadmap and confirmed it should remain an evolving plan subject to technical validation.
- Established the initial technical and functional design direction.
- Completed the authentication process design and related diagrams.
- Advanced the data-structure and governance design; remaining discrepancies between authentication and data stages are being resolved.
- Confirmed that Week 2 should begin with the data foundation.
- Identified Partner curation, scorecard/report requirements, and multi-interview synthesis as areas requiring additional definition.

### Week 2 focus

- Begin implementation of the organization, respondent, interview, and report data foundation.
- Review the data architecture and early implementation with the team.
- Finalize how immutable interview results, system-generated drafts, and Partner-curated report versions are stored.
- Define the minimum Partner review and curation workflow.
- Continue authentication and onboarding implementation as sequencing permits.
- Confirm the Week 3 scorecard/report format and workflow before it creates data-model rework.

### Current implementation baseline

The existing demo includes text and voice interview capabilities, scoring, AI-supported analysis, and report generation. The team still needs to validate and harden the exact implemented behavior, including:

- Deterministic versus agentic interview logic
- Question-library alignment
- Text and voice differences
- Current persistence and logging behavior
- Current scoring and report outputs

## 3. Phase 1 Delivery Plan

| Timeline | Focus | Intended outcome | Status |
|---|---|---|---|
| **Week 1** | Align and Design | Confirm technical and functional direction, scope, dependencies, and build plan | Complete at a high level |
| **Week 2** | Build the Foundation | Implement the core data model, controlled access, respondent onboarding, persistence, and minimum Partner view | Current |
| **Week 3** | Complete the MVP Flow | Connect interview, scoring, draft report, Partner curation, result delivery, and the basic dashboard | Planned; details evolving |
| **Week 4** | Test and Deploy | Complete integration testing, controlled deployment, internal validation, critical fixes, and stretch goals if capacity remains | Planned |

### Week 1: Align and Design

- Confirm the current demo baseline and reusable functionality.
- Establish the high-level technical and functional design direction.
- Complete the authentication process design.
- Advance the data-structure and governance design.
- Confirm the initial Phase 1 scope and implementation sequence.
- Identify email, infrastructure, security, governance, and ElevenLabs dependencies.

### Week 2: Build the Foundation

#### 1. Data Foundation and Versioning

**Goal:** Reliably associate organizations, respondents, interviews, system outputs, and Partner-curated reports.

- Implement the organization, respondent, interview/session, and report records.
- Keep completed interview inputs and system-generated results immutable.
- Support a separate, versioned Partner-curated report rather than overwriting the original interview or system output.
- Preserve the original system-generated draft and the final Partner-curated version.
- Consider capturing Partner notes or the reason for material changes so the differences can support future analysis and improvement.
- Track invitation, interview, report, and Partner-review status.
- Enforce organization-level data separation and access rules.
- Capture basic audit and activity events.

#### 2. Authentication, User Access, and Roles

**Goal:** Ensure that only approved users can access the application.

- Implement email magic-link authentication with no stored passwords.
- Implement the approved Phase 1 roles and permissions.
- Support invitation validation, expiration, resend, session expiration, and re-entry.
- Prevent unrestricted public access.
- Align authentication records and states with the data model.

#### 3. Respondent Onboarding and Invitations

**Goal:** Allow a DXC Partner to initiate a controlled assessment.

- Support manual respondent entry for Phase 1.
- Capture name, email, standardized interview persona, and actual job title.
- Generate and send controlled invitations through the approved email path.
- Track invitation status and support resend or reminder behavior.
- Define a configurable reminder interval, with a simple default for the initial MVP.

#### 4. Minimum Partner View

**Goal:** Provide the minimum workflow visibility needed before the full Partner curation experience is built.

- Allow Partners to view respondents and invitation status.
- Allow Partners to view interviews that are not started, in progress, or completed.
- Make the system-generated draft available for review when ready.
- Provide status fields that support the later Partner curation and delivery workflow.

### Week 3: Complete the MVP Flow

#### 1. Text and Voice Interview Integration

**Goal:** Deliver a reliable interview for authenticated respondents.

- Connect authenticated respondents to text and voice interviews.
- Validate baseline questions, response capture, persistence, and fallback behavior.
- Confirm required text and voice behavior.
- Validate the 15-to-20-minute interview target.
- Incorporate selected ElevenLabs improvements where they support the required flow.

#### 2. Scoring and System-Generated Draft

**Goal:** Produce a useful draft result that can be curated by a Partner.

- Validate scoring inputs and calculations.
- Confirm the minimum scorecard/report content and format.
- Generate the system draft, narrative summary, and recommended next steps.
- Define how uncertainty or incomplete information is represented.
- Preserve the system-generated draft as an immutable version.
- Do not show an immediate final result to the respondent; display a follow-up message indicating that results will be returned after review.

#### 3. Partner Curation and Result Delivery

**Goal:** Support a two-step process consisting of a system-generated draft followed by human Partner curation.

- Allow the Partner to review and manually refine the draft.
- Store the curated report as a new version rather than changing the original interview or system output.
- Determine whether the MVP uses an in-application form, an offline editable file, or a simple upload/re-upload process.
- Record approval and final-delivery status.
- Confirm the final delivery format and method.
- Preserve the difference between the original draft and curated output for future evaluation and improvement.

#### 4. Participation Dashboard and Test Preparation

**Goal:** Provide basic workflow visibility and prepare for integration testing.

- Show invited, accepted, not started, in-progress, completed, and report-review status.
- Include reminder status where implemented.
- Prepare test users, scenarios, expected outputs, and the initial feedback process.
- Define how defects and feedback are assigned to Phase 1 fixes or Phase 2 backlog items.

### Week 4: Test and Deploy

- Execute end-to-end integration testing.
- Validate authentication, data separation, persistence, interview, scoring, draft generation, Partner curation, dashboard, and delivery.
- Validate AI behavior through human review of relevance, reasonableness, unsupported claims, fallback behavior, and guardrails.
- Deploy to the approved controlled environment using the interim working URL.
- Conduct Round 1 testing with individual internal users.
- Begin Round 2 testing with a DXC IT customer-zero group if entry criteria are met.
- Resolve critical defects and retest.
- Prepare the leadership demonstration.
- Attempt adaptive questioning, enhanced guardrails, reminders, and other low-risk stretch items only after the required MVP is stable.

## 4. Confirmed Decisions

| Item | Status | Current direction | Needed next |
|---|---|---|---|
| Roadmap status | Confirmed | Treat the roadmap as an evolving plan; weekly placement may change as implementation is validated | Keep status and current week visible |
| Week 2 starting point | Confirmed | Begin with the data foundation | Review data architecture and early implementation with the team |
| Working URL | Resolved | Use `air.catalyst.one` for the near-term QA and MVP environment; defer the DXC-managed domain until the long-term product name is agreed | Confirm provisioning and certificate ownership |
| Authentication | Resolved | Email magic links with no stored passwords | Align implementation with the data model |
| User roles | Resolved | User, Power User, Partner, Admin | Confirm detailed permissions and minimum roles used in the MVP |
| User invitation | Resolved | DXC Partner enters approved respondents and the application sends controlled invitations | Use manual entry in Phase 1; consider spreadsheet upload later |
| Interview records | Resolved | Completed interviews and original system outputs remain immutable | Implement immutable records and version references |
| Partner-curated output | Direction agreed; design open | The system produces a draft; the Partner manually refines it; the curated output is stored as a new version | Decide form versus offline edit and re-upload workflow |
| Immediate respondent result | Resolved for MVP | Do not provide an immediate final result; show a message that results will follow after review | Confirm final wording and expected response window |
| Reminder timing | Direction agreed | Make reminder timing configurable, with a simple default for the first release | Confirm default interval and number of reminders |
| Multi-interview synthesis | Deferred to Phase 2 | Do not include in the four-week MVP because it requires additional synthesis, batching, and evaluation design | Add detailed Phase 2 backlog item |
| Cross-client knowledge base | Phase 2 backlog | Build a future knowledge base across clients, industries, functions, and use cases | Define governance and retrieval approach later |
| Partner review | In scope | Human curation is part of the foreseeable delivery process | Define minimum editing, notes, approval, file format, and delivery steps |
| Partner edits as learning data | Proposed | Preserve original and curated versions, and capture the delta or Partner notes for future improvement | Confirm data fields and whether reason-for-change is required |
| Dashboard | Resolved | Include basic Phase 1 participation and workflow data | Add report-review and reminder status |
| Customer zero | Direction agreed; details open | Round 1 uses individual internal testers; Round 2 uses a more realistic DXC IT group | Identify sponsor, respondents, schedule, and feedback method |
| Job-role capture | Resolved | Use a standardized high-level persona dropdown plus a free-text actual title | Finalize the persona list and mapping rules |
| Supporting-document upload | Phase 2 | Treat document ingestion and synthesis as a separate, larger capability | Define supported formats, processing, storage, and governance later |
| Voice visual | Simple MVP direction | Use a simple non-lip-synced visual or bubble unless a reusable option is immediately available | Confirm whether an existing reusable asset is available |

## 5. Open Questions, Risks, and Dependencies

### Week 2 decisions needed

- What data fields and version relationships are required for the original interview, system-generated draft, and Partner-curated report?
- Should the Partner curate through an in-application form or edit a generated file offline and upload the final version?
- Should the Partner provide notes or a reason when materially changing the system draft?
- What is the default reminder interval and how many reminders are included in Phase 1?
- What respondent-facing message and expected response window should appear after interview completion?
- Which report format is most practical for Partner curation and final delivery?

### Risks

| Risk | Impact | Next action |
|---|---|---|
| Partner-review requirements remain incomplete | Data model or Week 3 implementation may require rework | Resolve the minimum curation workflow while the data foundation is being implemented |
| Re-running probabilistic models is treated as deterministic regression | Model-quality testing may produce misleading conclusions | Use human expert evaluation of reasonableness and quality across model versions |
| Partner edits overwrite the original output | Auditability and future learning value are lost | Keep original and curated outputs as separate immutable versions |
| Multi-interview synthesis enters Phase 1 | Additional batching, synthesis, conflict-resolution, and evaluation work could exceed the current window | Keep the capability in Phase 2 |
| Sensitive data is combined across clients without governance | Confidentiality and legal concerns | Define access, retention, and reuse rules before cross-client knowledge-base work |
| Foundation effort exceeds the current plan | Testing or stretch scope may move | Review progress and critical path after the data architecture walkthrough |
| Documentation and implementation diverge | Scope and backlog may rely on stale assumptions | Update active documentation when decisions change |

### Dependencies

- Final data architecture and versioning approach
- Minimum Partner-curation and delivery workflow
- Approved DXC outbound email service and sender configuration
- Interim URL, certificate, and environment provisioning
- Internal test users and DXC IT customer-zero participants
- Report/scorecard content gathered from comparable internal teams
- ElevenLabs integration and guardrail decisions

## 6. Phase 2 Confirmed Direction

The following capabilities were directly identified in team discussions and notes. Sequence and timing are not yet committed.

- Multi-interview synthesis into an organization-level output
- Batching and controlled synthesis across larger interview sets
- Methods for resolving differences while preserving individual interview records
- Cross-client knowledge base organized by client, industry, function, and use case
- Richer adaptive interviews and follow-up questioning
- Role-misclassification and anomaly detection
- Client-side participant administration, if needed
- Spreadsheet respondent upload
- Supporting-document upload, extraction, storage, and synthesis
- Client-ready retention, deletion, consent, privacy, and legal controls
- Context-rich analysis using approved documents and client-system data
- Additional interview rounds for clarification and follow-up
- Expanded dashboards, reporting, and operational visibility

## 7. Immediate Actions

| Action | Owner | Timing / next step |
|---|---|---|
| Start the data-foundation implementation | Denis | Week 2 priority |
| Review the data architecture and early implementation | Denis / Alex / team | Tuesday work session, as discussed in the roadmap review |
| Update the roadmap with changes discussed in the roadmap review call | Alex | Done |
| Define the minimum Partner-curation workflow | Alex / Chris / Shawn / Denis | Week 2 discussion |
| Propose versioning for original interview, system draft, and curated report | Denis | Bring recommendation to the Week 2 review |
| Confirm no immediate final result is shown to respondents | Alex / Denis | Update requirements and user-flow documentation |
| Confirm configurable reminder behavior and initial default | Chris / Denis | Week 2 |
| Gather examples of comparable reports and scorecards | Chris | Continue research and share relevant examples |
| Define minimum scorecard/report content | Chris / Shawn / Robb / Alex / Denis | Dedicated Week 2 session |
| Add multi-interview synthesis to Phase 2 | Alex | Completed in this update; confirm with team |
| Add cross-client knowledge base to Phase 2 backlog | Alex | Completed in this update; confirm with team |
| Identify internal testers and DXC IT customer-zero group | Shawn / Robb / Alex | Confirm sponsor, participants, and feedback process |
| Check for an immediately reusable simple voice visual | Andre | Follow up with the relevant internal contact; keep out of critical path |

## 8. Week 2 Meeting Focus

### Data architecture review

1. Review the implemented organization, respondent, interview, and report structures.
2. Confirm immutable interview and system-output records.
3. Confirm versioning for Partner-curated reports.
4. Confirm status fields needed for the dashboard and workflow.
5. Identify data-model changes required by the proposed Partner curation process.

### Product and scorecard session

1. Define the minimum system-generated draft.
2. Define what the Partner is expected to modify.
3. Decide whether curation occurs in the application or offline.
4. Define what is returned to the respondent and in what format.
5. Confirm the completion message and expected review window.
6. Confirm whether Partner notes or reason-for-change data is required.

### Delivery check

1. Confirm which Week 2 capabilities are in progress, complete, or blocked.
2. Validate whether Week 3 remains achievable at a high level.
3. Identify any work that should move to Week 4 or Phase 2.
4. Confirm the internal-test preparation required before Week 4.

## 9. Change Log

| Date | Updated by | Change |
|---|---|---|
| 2026-08-05 | Alex Schick | Created initial MVP delivery baseline |
| 2026-08-06 | Alex Schick | Added the four-week delivery plan, decisions, risks, ElevenLabs direction, Phase 2 items, and updated actions |
| 2026-08-10 | Alex Schick | Updated for the start of Week 2 using the August 7 roadmap review: data foundation first, immutable interview records, versioned Partner-curated reports, delayed respondent results, configurable reminders, multi-interview synthesis deferred to Phase 2, knowledge-base backlog, and Week 2 actions |
