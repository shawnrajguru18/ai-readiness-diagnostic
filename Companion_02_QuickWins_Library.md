---
title: "Companion 02 — Quick-Wins Library"
status: "DRAFT V1 — for working group iteration"
parent_doc: "DXC_AI_Readiness_Diagnostic_PRD.md"
purpose: "Curated library of 15 high-confidence, low-disruption AI patterns. Used by Agent C3 (Quick Wins) to identify 2-3 specific 90-day actionable recommendations per prospect."
target: "V0 build — investor day demo (conditional on this library landing in week 1-2)"
---

# Quick-Wins Library

## Purpose

Agent C3 (Quick Wins Identification) draws from this library to recommend 2-3 specific 90-day actionable AI opportunities per prospect. Quick wins are distinct from strategic AI initiatives. They share five properties:

1. **High confidence outcomes.** Each pattern has documented deployments at enterprise scale with measurable results.
2. **Low organizational disruption.** Does not require restructuring, role redesign, or extensive change management.
3. **Limited data dependencies.** Works on data the enterprise already has access to. No new data foundation prerequisite.
4. **Bounded blast radius.** If the AI errs, the failure mode is recoverable and the impact is localized.
5. **90-day implementable.** From kickoff to production value in 12-14 weeks.

Quick wins are not transformational. They are momentum builders. They give the prospect something to do tomorrow while strategic AI work follows in Discovery.

## Pattern structure

Each pattern in the library has the following fields, used by Agent C3 for selection logic and by the Output Generation Agent for the quick wins memo:

- **Pattern ID** (stable identifier)
- **Name** (prospect-facing)
- **One-line description**
- **What the AI does** (3-4 sentences, prospect-readable)
- **Prerequisites** (what the prospect must have for this to work)
- **Expected outcomes** (range of measurable results from peer deployments)
- **Implementation effort** (Low / Medium)
- **Timeline to value** (weeks)
- **Applicable industries** (subset of FS, HLS, MFG, All)
- **Applicable company sizes** (subset of Mid-market, Large enterprise, Global)
- **Disqualifying conditions** (when this pattern is *not* a good recommendation)
- **Peer examples** (anonymized, where DXC has documented experience)

## Pattern selection logic (Agent C3)

For each prospect, C3 selects 2-3 patterns from the library based on:
- Industry match
- Company size match
- Synthesis-output identified gaps (which dimensions scored low)
- Tech stack inference (B3) compatibility
- Prerequisites are likely satisfied by the prospect
- Variety (do not recommend three patterns in the same functional area)

Confidence reported per recommendation. Recommendations with confidence below threshold are flagged for senior partner attention or replaced with alternates.

---

## The 15 Patterns

---

### QW-001: Intelligent Invoice Triage

**One-line:** AI categorizes and routes invoice exceptions, reducing manual AP team workload.

**What the AI does:** Reads incoming invoice exceptions (mismatch, missing PO, unknown vendor, formatting errors), categorizes them by exception type, identifies likely resolution path, and routes to the appropriate handler with suggested resolution. Routine cases auto-resolve; complex cases reach humans with context already gathered.

**Prerequisites:** Existing AP system with structured exception logging. Sufficient historical exception data (typically 6+ months).

**Expected outcomes:** AP exception handling time reduced 40-60%. Routine exception auto-resolution rate 25-40%. Net AP team capacity gain enabling shift to vendor management work.

**Implementation effort:** Low

**Timeline to value:** 8-10 weeks

**Industries:** All

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Highly customized AP workflows; <2K invoices/month volume.

**Peer examples:** Manufacturing client with 50K invoices/month achieved 45% exception handling reduction in 10 weeks. Financial services back-office achieved 38% auto-resolution rate within 12 weeks.

---

### QW-002: Customer Support Ticket Categorization and Routing

**One-line:** AI reads inbound customer tickets, categorizes by intent, and routes to the right specialist team.

**What the AI does:** Parses inbound customer tickets (email, chat, web form), identifies the underlying request type, urgency, and product/service area, and routes directly to the team or specialist most likely to resolve quickly. Adds extracted context (customer history, related tickets) to the routed ticket so the receiving agent starts informed.

**Prerequisites:** Ticketing system with structured ticket data. Categorization taxonomy that maps to support team structure.

**Expected outcomes:** First-contact resolution rate improvement 15-25%. Average ticket resolution time reduction 20-35%. Customer satisfaction improvement on routed tickets 10-15 points.

**Implementation effort:** Low

**Timeline to value:** 6-10 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Very specialized support requiring named-agent assignment; ticket volumes below 5K/month.

**Peer examples:** Financial services client reduced average handle time 28% across 200K monthly tickets in 8 weeks. Healthcare payer improved first-contact resolution 22% on benefits inquiries.

---

### QW-003: Contract Clause Extraction

**One-line:** AI reads incoming contracts, extracts key clauses, and flags non-standard terms for review.

**What the AI does:** Parses uploaded contracts (PDF, Word), extracts standard clauses (term, termination, indemnification, IP assignment, data handling, governing law), compares against the prospect's standard templates, and flags deviations. Produces a structured summary the legal team uses to prioritize review attention.

**Prerequisites:** Standard contract templates documented. Contract volume sufficient to justify automation (typically 50+ contracts/month).

**Expected outcomes:** Legal review time per contract reduced 30-50%. Standard contract turnaround time reduced from days to hours. Coverage improvement (more contracts reviewed in detail rather than skimmed).

**Implementation effort:** Low

**Timeline to value:** 8-12 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Highly bespoke contracting (each contract substantially unique); legal teams strongly preferring full manual review.

**Peer examples:** Manufacturing client cut standard supplier contract review from 48 hours to 4 hours. Financial services institution improved deviation detection rate from 60% (manual) to 92% (AI-assisted).

---

### QW-004: Sales Call Summarization and Action Capture

**One-line:** AI summarizes sales calls, extracts action items, and updates CRM automatically.

**What the AI does:** Joins or processes recordings of sales calls, produces structured summaries (who said what, key topics, expressed objections, agreed next steps), extracts action items with owners, and updates CRM records with relevant fields populated. Sales reps end the call and the CRM is already updated.

**Prerequisites:** Sales call recording capability (compliance-cleared). CRM with API access.

**Expected outcomes:** Sales rep admin time reduction 5-8 hours per week. CRM data quality improvement (more complete records). Pipeline visibility improvement for sales management.

**Implementation effort:** Low

**Timeline to value:** 6-10 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Compliance constraints on call recording; small sales teams (<50 reps) where ROI may not justify cost.

**Peer examples:** Tech services firm with 800 sales reps recovered 6 hours/rep/week of admin time. Insurance broker improved CRM completeness from 45% to 89% of required fields.

---

### QW-005: IT Incident Auto-Categorization

**One-line:** AI reads inbound IT incident tickets, categorizes by type, and assigns severity and priority.

**What the AI does:** Processes inbound IT incident tickets, identifies the affected service, infrastructure component, and likely root cause area, assigns severity based on business impact rules, and routes to the appropriate support tier. Tier 1 handles routine; complex incidents reach tier 2 or 3 with diagnostic context attached.

**Prerequisites:** IT service management system (ServiceNow, BMC, similar). Service catalog documented. Sufficient ticket history.

**Expected outcomes:** Incident routing accuracy improvement 30-50%. Mean time to assignment reduction 60-80%. Tier 1 deflection rate improvement 20-35%.

**Implementation effort:** Low

**Timeline to value:** 6-10 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Very small IT operations (<10K tickets/year). Heavily customized ITSM workflows.

**Peer examples:** Financial services client cut mean time to assignment from 38 minutes to 6 minutes across 400K annual tickets. Healthcare system improved tier 1 deflection rate 28% in 9 weeks. *Strong candidate for the customer zero engagement (DXC's own ServiceNow estate).*

---

### QW-006: Knowledge Base Search Enhancement

**One-line:** AI improves internal knowledge base search, surfacing relevant content from imprecise queries.

**What the AI does:** Replaces keyword-based knowledge base search with semantic understanding. A user query gets matched against actual content meaning, not just keywords. Returns the most relevant documents with extracted answer snippets. Tracks which results actually answered the question and learns over time.

**Prerequisites:** Existing knowledge base with reasonable content quality. Permission to index content for search.

**Expected outcomes:** Search success rate improvement (queries that find what the user needed) 30-50%. Internal support ticket deflection 15-25%. Employee productivity gain on knowledge-dependent tasks.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** All

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Very low-quality knowledge base content (AI surfaces bad answers faster). Heavy reliance on tribal knowledge not yet captured in writing.

**Peer examples:** Insurance back-office knowledge base achieved 38% improvement in question-resolution rate. Manufacturing engineering knowledge base reduced average time-to-answer from 18 minutes to 4 minutes.

---

### QW-007: Meeting Summarization and Decision Tracking

**One-line:** AI summarizes meetings, extracts decisions and action items, distributes to attendees automatically.

**What the AI does:** Joins or processes recordings of internal meetings, produces structured summaries (key topics, decisions made, action items with owners, open questions), and distributes to attendees and relevant stakeholders. Optionally creates calendar reminders for action item due dates and updates project management tools.

**Prerequisites:** Meeting recording or transcription capability. Email/calendar integration.

**Expected outcomes:** Meeting follow-through improvement (decisions actually executed) 25-40%. Attendee time saved on minutes-taking and follow-up. Reduction in meeting-about-meeting overhead.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** All

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Meeting confidentiality constraints (board, M&A, executive sessions). Cultural resistance to AI presence in meetings.

**Peer examples:** Professional services firm reduced meeting administrative overhead 4-6 hours/week per senior staff member. Healthcare operations team improved decision execution rate from 55% to 81%.

---

### QW-008: Expense Report Categorization and Anomaly Detection

**One-line:** AI categorizes expense reports, flags anomalies for review, accelerates routine approvals.

**What the AI does:** Processes submitted expense reports, categorizes line items, validates against policy rules, identifies anomalies (unusual amounts, suspicious patterns, policy violations), and routes routine reports to fast approval while flagging exceptions for manager attention. Receipt OCR and validation included.

**Prerequisites:** Expense management system with API access. Documented expense policy.

**Expected outcomes:** Expense processing time reduction 60-80%. Anomaly detection accuracy improvement (catches more real issues, fewer false positives). Manager time per expense report cut from minutes to seconds for routine cases.

**Implementation effort:** Low

**Timeline to value:** 6-10 weeks

**Industries:** All

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Highly bespoke expense workflows. Compliance environments requiring full human review of every report.

**Peer examples:** Financial services firm reduced expense processing FTE requirement by 40% across 30K monthly reports. Manufacturing client improved policy violation detection rate from 45% to 87%.

---

### QW-009: Sales Prospect Research Automation

**One-line:** AI researches prospect companies before sales calls, prepares briefing documents automatically.

**What the AI does:** Given a prospect company name or meeting invite, autonomously researches public information (recent news, financial filings, leadership changes, public technology partnerships, social media signals), synthesizes into a one-page briefing, and delivers to the sales rep before the meeting. Updates over time as new information emerges.

**Prerequisites:** CRM with meeting data accessible. Public research API access.

**Expected outcomes:** Sales rep meeting preparation time reduction 70-85%. Meeting effectiveness improvement (better questions, more relevant pitches). Higher conversion rates on prospect calls.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Sales models that do not involve research-intensive prospect calls. Small sales teams.

**Peer examples:** Enterprise software company cut average prep time from 45 minutes to 8 minutes per meeting. Professional services firm improved first-meeting conversion rate 18%.

---

### QW-010: Code Review Assistant

**One-line:** AI reviews pull requests for code quality, security, and style issues before human reviewers see them.

**What the AI does:** Automatically reviews pull requests against the team's coding standards, identifies common bugs, security vulnerabilities, style violations, and missing tests. Adds inline comments on the PR. Human reviewers see only what AI could not resolve. Learns over time from accepted/rejected suggestions.

**Prerequisites:** Modern source control with PR workflow (GitHub, GitLab, Bitbucket). Defined coding standards.

**Expected outcomes:** Pre-review issue detection rate 60-80%. Human reviewer time per PR reduced 30-50%. Mean time to PR merge reduction 40-60%.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** All (most relevant to engineering-heavy organizations)

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Very small engineering teams (<10 developers). Legacy environments without modern PR workflows.

**Peer examples:** Financial services engineering team reduced PR review cycle time from 36 hours to 12 hours across 500 PRs/week. Manufacturing software team improved security issue detection rate 67%.

---

### QW-011: Recruiting Candidate Screening

**One-line:** AI screens incoming candidate applications against role requirements, surfaces strongest matches first.

**What the AI does:** Reads incoming resumes, compares against job requirements, scores candidate match across explicit and inferred criteria, surfaces strongest candidates first, and provides reasoning. Filters out candidates whose qualifications are far from requirements while flagging diverse candidates for explicit human review.

**Prerequisites:** Applicant tracking system with API access. Well-defined job requirements.

**Expected outcomes:** Recruiter time per role reduction 40-60%. Time-to-shortlist reduction from weeks to days. Improved candidate quality of shortlist (validated through hiring manager feedback).

**Implementation effort:** Medium *(requires bias mitigation work and ongoing monitoring)*

**Timeline to value:** 10-14 weeks

**Industries:** All

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** High-volume entry-level recruiting where simple keyword matching suffices. Bias-sensitive hiring contexts requiring documented human-led screening.

**Peer examples:** Financial services firm reduced time-to-shortlist from 18 days to 4 days on technical roles. Healthcare system improved diverse candidate progression rate while reducing recruiter screening time 50%.

---

### QW-012: Compliance Document Review

**One-line:** AI reads regulatory documents (filings, communications, policies), flags compliance issues for review.

**What the AI does:** Processes outbound regulatory documents (filings, customer communications, policy documents), checks against current regulatory requirements and the organization's policy library, flags potential compliance issues with rationale, and prioritizes by risk. Compliance team focuses on flagged items rather than reading every document.

**Prerequisites:** Document management system. Current regulatory rule library. Internal policy library.

**Expected outcomes:** Compliance review coverage improvement (more documents reviewed thoroughly). Compliance issue detection rate improvement 30-50%. Compliance team capacity gain enabling proactive work.

**Implementation effort:** Medium *(requires careful tuning to false positive rate)*

**Timeline to value:** 10-14 weeks

**Industries:** FS, HLS (primary); MFG (regulated sub-sectors)

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Very small compliance volumes. Highly bespoke compliance environments where AI false positives create more work than they save.

**Peer examples:** Financial services compliance team improved coverage from 15% to 80% of customer communications while detecting 23% more potential issues. Pharmaceutical company reduced manual review burden on adverse event reports 40%.

---

### QW-013: Marketing Copy Variant Generation

**One-line:** AI generates marketing copy variants for testing, accelerating A/B testing program throughput.

**What the AI does:** Given a marketing objective and brand voice guidelines, generates multiple copy variants for emails, landing pages, ads, and other marketing touchpoints. Variants tested against each other in market; winning patterns inform future generations. Brand voice and compliance rules enforced at generation time.

**Prerequisites:** Marketing automation platform with A/B testing capability. Documented brand voice and compliance guidelines.

**Expected outcomes:** Marketing copy variant production rate 5-10x improvement. A/B test cycle time reduction 50-70%. Net marketing performance improvement through more testing iterations.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** All (most applicable to consumer-facing businesses)

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Highly regulated marketing (pharma, financial advice) where compliance review per variant negates speed gains. Very small marketing teams.

**Peer examples:** Insurance carrier improved email campaign performance 23% through expanded testing program enabled by AI-generated variants. Consumer banking grew web conversion rate 18% over 6 months.

---

### QW-014: Product Description Generation (E-commerce)

**One-line:** AI generates product descriptions from structured product data, accelerating catalog expansion.

**What the AI does:** Takes structured product data (specifications, attributes, target audience), generates marketing-quality product descriptions in the brand voice, with SEO optimization, in multiple languages. Maintains consistency across catalog. Updates descriptions when product data changes.

**Prerequisites:** Structured product data (PIM or equivalent). Brand voice guidelines. SEO requirements documented.

**Expected outcomes:** Catalog expansion velocity 5-10x improvement. SEO performance improvement through more complete content. Translation cost reduction 60-80%.

**Implementation effort:** Low

**Timeline to value:** 4-8 weeks

**Industries:** Retail, Manufacturing (consumer products); not applicable to most FS/HLS

**Sizes:** Mid-market, Large enterprise, Global

**Disqualifying conditions:** Small catalogs (<500 products). Bespoke products requiring craft descriptions.

**Peer examples:** Consumer electronics retailer expanded catalog from 5K to 30K SKUs in 6 months without growing content team. Apparel brand reduced translation cost from $40K to $6K per market launch.

---

### QW-015: Field Service Report Standardization

**One-line:** AI processes field technician reports, structures the data, identifies emerging issues across the fleet.

**What the AI does:** Takes free-text or photo-based field service reports from technicians, extracts structured information (equipment ID, issue type, parts used, resolution), identifies patterns across the fleet (recurring issues, parts failure clusters, technician training gaps), and surfaces insights to operations and engineering teams.

**Prerequisites:** Field service management system. Technicians submitting reports (any format). Asset master data.

**Expected outcomes:** Report processing time reduction 80-95%. Pattern detection on recurring issues months earlier than manual review. Preventive maintenance program improvement.

**Implementation effort:** Medium *(requires field workflow integration)*

**Timeline to value:** 10-14 weeks

**Industries:** MFG (primary), HLS (medical device service), All (with field operations)

**Sizes:** Large enterprise, Global

**Disqualifying conditions:** Very small field operations (<50 technicians). Industries without recurring asset maintenance.

**Peer examples:** Industrial equipment manufacturer detected gearbox failure pattern 4 months before traditional analysis would have caught it, saving $12M in warranty costs. Medical device company reduced field report processing from 6 hours to 15 minutes per technician per week.

---

## Library maintenance

The quick-wins library is a living document. Each pattern is reviewed quarterly for:

- **Continued accuracy of expected outcomes.** As more deployments accumulate, the outcome ranges narrow.
- **Industry coverage gaps.** New patterns added based on observed prospect needs.
- **Disqualification refinement.** Patterns retired when prerequisites are no longer realistic or outcomes have eroded.
- **Peer example updates.** Real deployments cited as appropriate (with anonymization).

The senior partner review workflow captures partner notes on pattern selection. Patterns that partners frequently override or adjust are flagged for library refinement.

## V0 demo scenario application

For the V0 investor day demo using the MeridianFS financial services scenario, Agent C3 would select (with high confidence) from this library:

**Recommended quick win 1: QW-001 Intelligent Invoice Triage** — fits FS industry, large enterprise size, addresses operational efficiency gap surfaced in dimension scoring, peer examples reinforce credibility.

**Recommended quick win 2: QW-005 IT Incident Auto-Categorization** — fits all dimensions, particularly strong for FS prospects with ServiceNow estates, peer example from financial services lands well in the demo, ties back to DXC delivery footprint.

**Recommended quick win 3: QW-012 Compliance Document Review** — fits FS industry strongly, addresses regulatory complexity dimension specifically, demonstrates DXC's ability to support regulated workloads.

The quick wins memo in the V0 demo deliverable would show these three patterns with the prospect-specific framing, prerequisites, and expected outcomes.

---

*Companion documents: see Companion_01_Questionnaire_Specification.md for assessment input that drives quick win selection, Companion_03_Scorecard_Design.md for how the quick wins memo appears in the output, Companion_04_Agent_Prompts.md for Agent C3 system prompt and selection logic.*
