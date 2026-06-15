---
title: "Companion 01 — Questionnaire Specification"
status: "DRAFT V1 — for working group iteration"
parent_doc: "DXC_AI_Readiness_Diagnostic_PRD.md"
purpose: "Specification of the 20-question prospect-facing assessment, including question text, scoring weights, persona tags, and industry applicability"
target: "V0 build — investor day demo"
---

# Questionnaire Specification

## Overview

20 questions across six dimensions. Designed for under-30-minute completion. Mix of multiple-choice (fast, scored), scale (consistent measurement), and selective open-ended (depth where needed). Each question tagged with applicable personas and industries to support Agent A3 (Question Personalization) selection logic.

Questions are presented in the order below for default flow. Agent A3 can re-order, substitute alternates, or skip questions based on persona and emerging context.

## Scoring framework

Each question contributes to one of six dimension scores on a 0-100 scale. Within a dimension, questions are weighted by their diagnostic value (how much signal they carry about that dimension). Weights sum to 1.0 within each dimension.

Final scorecard reports each dimension as: raw score (0-100), tier (Emerging / Developing / Established / Leading), peer benchmark comparison (when available, V0.5+).

Tier thresholds:
- Emerging: 0-39
- Developing: 40-59
- Established: 60-79
- Leading: 80-100

## Persona tags

- **P1**: Executive sponsor (CEO/COO) - strategic framing, less technical detail
- **P2**: Operational owner (CIO/CDO/CTO) - technical depth welcomed
- **P3**: Financial scrutineer (CFO) - financial framing prioritized

Most questions apply to all personas with adapted framing. A few are persona-specific.

## Industry tags

- **FS**: Financial services
- **HLS**: Healthcare and life sciences
- **MFG**: Manufacturing
- **All**: Industry-agnostic

V0 covers FS, HLS, MFG industries. Industry-specific question variants flagged.

---

## Dimension 1: Data Foundation

*4 questions. Weight: 0.20 of total scorecard.*

### Q1.1 — Data location and integration
**Personas:** P1, P2, P3 | **Industries:** All | **Weight in dimension:** 0.30

**Text:** Where does your enterprise's operational data primarily live?

**Type:** Multiple choice (select one)

**Options:**
- A. Fragmented across 20+ systems with limited integration *(score: 20)*
- B. Several major systems with documented but partial integration *(score: 40)*
- C. Most operations covered by integrated core platforms *(score: 65)*
- D. Unified data layer or modern lakehouse architecture in production *(score: 90)*

**Rationale:** Data fragmentation is the single most common cause of AI program failure. This question surfaces the structural condition without requiring technical detail.

---

### Q1.2 — Decision data currency
**Personas:** P1, P2, P3 | **Industries:** All | **Weight in dimension:** 0.25

**Text:** What proportion of significant business decisions today are made with current, accurate data?

**Type:** Scale (1-5)

**Anchors:**
- 1: Most decisions rely on dated or incomplete data *(score: 15)*
- 2: Some decisions have current data; many do not *(score: 35)*
- 3: Most operational decisions have current data; strategic decisions lag *(score: 55)*
- 4: Decision-grade data is generally available with effort *(score: 75)*
- 5: Real-time or near-real-time data drives most decisions *(score: 95)*

**Rationale:** Tests data utility, not just existence. An enterprise can have data and still not make decisions with it.

---

### Q1.3 — Data accessibility for AI use
**Personas:** P2 (primary), P1 (adapted) | **Industries:** All | **Weight in dimension:** 0.25

**Text:** How readily can data be accessed and prepared for AI applications?

**Type:** Multiple choice (select one)

**Options:**
- A. Each AI project requires significant data engineering work to access source systems *(score: 25)*
- B. Some standard datasets are accessible; new use cases require custom work *(score: 45)*
- C. A data platform exists that supports most AI use cases with moderate effort *(score: 70)*
- D. AI teams can self-serve data through governed APIs and feature stores *(score: 90)*

**Rationale:** Distinguishes enterprises where AI initiatives stall on data access versus those where data is available to AI teams.

---

### Q1.4 — Data quality posture
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.20

**Text:** How would your team describe the current quality of operational data?

**Type:** Multiple choice (select one)

**Options:**
- A. Significant known data quality issues; no formal quality program *(score: 20)*
- B. Quality issues acknowledged; ad hoc remediation efforts *(score: 40)*
- C. Data quality program in place for critical domains *(score: 65)*
- D. Comprehensive data quality monitoring with ownership and SLAs *(score: 85)*

**Rationale:** Tests honest self-assessment of data quality, which is often the gap between AI promise and AI delivery.

---

## Dimension 2: Governance Posture

*3 questions. Weight: 0.20 of total scorecard.*

### Q2.1 — Defined AI governance framework
**Personas:** P1, P2, P3 | **Industries:** All | **Weight in dimension:** 0.40

**Text:** Does your organization have a defined AI governance framework?

**Type:** Multiple choice (select one)

**Options:**
- A. No formal AI governance; AI decisions handled case by case *(score: 15)*
- B. Draft AI principles exist but not operationalized *(score: 35)*
- C. AI governance framework in place; ownership and controls established *(score: 65)*
- D. Mature AI governance with risk tiering, monitoring, and board oversight *(score: 90)*

**Rationale:** This is the single most diagnostic question on governance. The gap between principles and operationalization is where most AI programs hit the wall.

---

### Q2.2 — AI risk accountability
**Personas:** P1 (primary), P3 (adapted) | **Industries:** All | **Weight in dimension:** 0.30

**Text:** Who owns AI-related risk decisions in your organization today?

**Type:** Multiple choice (select one)

**Options:**
- A. No clear owner; risk emerges as issues arise *(score: 15)*
- B. Distributed across CISO, Compliance, Legal with informal coordination *(score: 35)*
- C. Designated AI risk owner with cross-functional committee *(score: 65)*
- D. AI risk integrated into enterprise risk framework with C-suite accountability *(score: 90)*

**Rationale:** Surfaces the most common governance failure mode: unclear ownership when AI risk materializes.

---

### Q2.3 — Industry-specific AI guidance
**Personas:** P1, P2 | **Industries:** FS, HLS (primary); All (adapted) | **Weight in dimension:** 0.30

**Text:** How is your organization interpreting industry-specific AI regulatory guidance?

**Type:** Multiple choice (select one)

**Options:**
- A. Awareness of guidance exists; interpretation has not started *(score: 20)*
- B. Active legal and compliance review underway *(score: 45)*
- C. Operational interpretation complete; controls being implemented *(score: 70)*
- D. Industry guidance fully operationalized; proactive engagement with regulators *(score: 90)*

**Rationale:** Particularly important for regulated industries (FS, HLS). For non-regulated industries, A3 substitutes a broader regulatory awareness question.

---

## Dimension 3: AI Investment Maturity

*4 questions. Weight: 0.18 of total scorecard.*

### Q3.1 — AI initiatives launched
**Personas:** P1, P2, P3 | **Industries:** All | **Weight in dimension:** 0.30

**Text:** How many distinct AI initiatives has your organization launched in the last 24 months?

**Type:** Multiple choice (select one)

**Options:**
- A. None or one early-stage pilot *(score: 25)*
- B. 2-5 pilots, mostly experimental *(score: 45)*
- C. 6-15 initiatives at various stages; some in production *(score: 70)*
- D. 15+ initiatives with portfolio governance *(score: 85)*

**Rationale:** Calibrates the prospect's experience base. Starting from zero versus burned by 20 failed pilots are very different starting positions.

---

### Q3.2 — Production AI today
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.30

**Text:** What AI applications are in production today, generating measurable business value?

**Type:** Multiple choice (select one)

**Options:**
- A. Nothing in production; experiments and proofs of concept only *(score: 20)*
- B. 1-2 narrow applications in limited production *(score: 45)*
- C. Several production applications with measurable value *(score: 70)*
- D. AI is integral to multiple core business processes *(score: 90)*

**Rationale:** Production AI is a leading indicator of organizational AI maturity. Production beats pilot at predicting future AI program success.

---

### Q3.3 — AI program outcomes
**Personas:** P3 (primary), P1 (adapted) | **Industries:** All | **Weight in dimension:** 0.25

**Text:** How would you describe the business outcomes from AI investment to date?

**Type:** Multiple choice (select one)

**Options:**
- A. Hard to point to material outcomes from AI investment yet *(score: 25)*
- B. Some efficiency gains documented; broader impact unclear *(score: 45)*
- C. Material outcomes documented in specific business areas *(score: 70)*
- D. AI is a material driver of business performance with attributable revenue or cost impact *(score: 90)*

**Rationale:** Tests honest assessment of AI ROI. Prospects who cannot point to outcomes are at risk of cancellation per industry data; prospects with clear outcomes are ready for more.

---

### Q3.4 — AI investment trajectory
**Personas:** P3 (primary), P1 (adapted) | **Industries:** All | **Weight in dimension:** 0.15

**Text:** How is AI investment trending in your organization for the coming year?

**Type:** Multiple choice (select one)

**Options:**
- A. Reducing or pausing AI investment to focus on data foundations *(score: 30)*
- B. Holding flat while we evaluate what has worked *(score: 50)*
- C. Increasing material investment in 2-3 specific AI initiatives *(score: 70)*
- D. Materially increasing AI investment across multiple business lines *(score: 80)*

**Rationale:** Captures momentum and confidence. Note that "reducing investment to focus on foundations" scores poorly here but well in Data Foundation dimension; surfacing the trade-off is part of the diagnostic insight.

---

## Dimension 4: Organizational Change Readiness

*3 questions. Weight: 0.15 of total scorecard.*

### Q4.1 — Change management capacity
**Personas:** P1 (primary), P2 (adapted) | **Industries:** All | **Weight in dimension:** 0.35

**Text:** How does your organization typically respond to major operational changes?

**Type:** Multiple choice (select one)

**Options:**
- A. Significant resistance; changes take 2-3x longer than planned *(score: 25)*
- B. Resistance is expected and managed; changes generally land on time *(score: 50)*
- C. Strong change management muscle; recent transformations have landed well *(score: 75)*
- D. Continuous change is the operating norm; teams adapt rapidly *(score: 90)*

**Rationale:** AI transformation success depends on change capacity more than technology. This question is highly predictive of execution likelihood.

---

### Q4.2 — Leadership alignment on AI
**Personas:** P1, P3 | **Industries:** All | **Weight in dimension:** 0.40

**Text:** How aligned is the senior leadership team on AI ambition and approach?

**Type:** Multiple choice (select one)

**Options:**
- A. Active debate at the leadership level; no shared direction yet *(score: 30)*
- B. Leadership broadly supportive; specifics still being shaped *(score: 55)*
- C. Clear leadership alignment with a defined AI strategy *(score: 75)*
- D. AI strategy is integrated into business strategy with full board engagement *(score: 90)*

**Rationale:** Without leadership alignment, AI investment falls into "principles without action" territory. This question often surfaces the gap that derails programs.

---

### Q4.3 — Workforce posture toward AI
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.25

**Text:** How is your workforce engaging with AI as a topic today?

**Type:** Multiple choice (select one)

**Options:**
- A. Workforce concerns dominate; cautious or anxious posture *(score: 30)*
- B. Mixed posture; some teams enthusiastic, others apprehensive *(score: 55)*
- C. Broadly positive engagement; active use of AI tools by individuals *(score: 75)*
- D. Workforce is helping define AI strategy and implementation *(score: 90)*

**Rationale:** The XAES "eight hidden trade-offs" framework identifies workforce trust as a critical and frequently-overlooked predictor of AI program success.

---

## Dimension 5: Value-Pocket Clarity

*3 questions. Weight: 0.17 of total scorecard.*

### Q5.1 — Identified processes for AI
**Personas:** P1, P2, P3 | **Industries:** All | **Weight in dimension:** 0.40

**Text:** Has your organization identified specific business processes where AI investment is justified?

**Type:** Multiple choice (select one)

**Options:**
- A. AI ambition is broad; specific processes not yet identified *(score: 25)*
- B. 2-3 candidate processes under evaluation *(score: 50)*
- C. Portfolio of processes prioritized with business case *(score: 75)*
- D. AI roadmap maps to enterprise value pockets with sized opportunities *(score: 90)*

**Rationale:** Distinguishes prospects who want AI in general from prospects who know where AI value sits for them specifically. The latter is materially closer to action.

---

### Q5.2 — Success metrics defined
**Personas:** P3 (primary), P1 (adapted) | **Industries:** All | **Weight in dimension:** 0.30

**Text:** For AI initiatives, what does success look like?

**Type:** Multiple choice (select one)

**Options:**
- A. Success defined by adoption or completion, not measurable business outcome *(score: 30)*
- B. Initiatives have outcome KPIs but ROI attribution is difficult *(score: 50)*
- C. Initiatives have clear baseline measurement and target outcomes *(score: 75)*
- D. AI value is tracked in business P&L with attribution methodology *(score: 90)*

**Rationale:** Surfaces the rigor of business case work. CFOs respond to this question because it directly addresses the capital allocation discipline.

---

### Q5.3 — Process reinvention vs automation framing
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.30

**Text:** When considering AI for a business process, how does your organization frame the question?

**Type:** Multiple choice (select one)

**Options:**
- A. Primarily: "How can AI automate this process more efficiently?" *(score: 35)*
- B. Mixed: some automation framing, some process redesign *(score: 55)*
- C. Primarily: "What should this process look like with AI as a participant?" *(score: 80)*
- D. Process reinvention is the default frame; automation follows redesign *(score: 95)*

**Rationale:** Tests methodological maturity. The APR thesis is that automation onto broken processes is where AI investment fails; reinvention before automation is where it succeeds. This question diagnoses the prospect's existing posture and informs the recommended next step.

---

## Dimension 6: Regulatory Complexity

*3 questions. Weight: 0.10 of total scorecard.*

### Q6.1 — Regulatory environment for AI
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.50

**Text:** What regulatory frameworks materially apply to your AI use?

**Type:** Multiple choice (select multiple)

**Options:**
- EU AI Act (now in force)
- US sectoral guidance (NIST AI RMF, NIST GAI profile, state AG guidance)
- FCA / PRA AI guidance (UK financial services)
- FINRA / SEC AI disclosure (US capital markets)
- HIPAA / FDA SaMD (US healthcare)
- Industry-specific (state insurance commissioner, manufacturing safety, etc.)
- No specific AI regulation currently applies

**Scoring:** Each selection adds to a regulatory complexity score (informational, not graded). Complexity itself is not good or bad; it determines what AI patterns are viable.

**Rationale:** Inventory question, not opinion question. Informs Agent B5 (Regulatory Context) and downstream recommended next step.

---

### Q6.2 — Data sovereignty constraints
**Personas:** P1, P2 | **Industries:** All | **Weight in dimension:** 0.30

**Text:** What data sovereignty or residency requirements constrain AI deployment?

**Type:** Multiple choice (select one)

**Options:**
- A. No specific sovereignty constraints; cloud-flexible *(score: applicable across patterns)*
- B. Preference for in-region deployment; some flexibility *(score: applicable with constraints)*
- C. Required in-region data residency; cloud restrictions apply *(score: limits AI provider options)*
- D. Sovereign AI required (on-premise, sovereign cloud, EU/UK-only models) *(score: requires sovereign AI strategy)*

**Rationale:** Determines whether prospect needs sovereign AI strategy (V1.5 capability). Particularly relevant for UK/EU prospects.

---

### Q6.3 — Cross-border data implications
**Personas:** P1 (primary), P2 (adapted) | **Industries:** All | **Weight in dimension:** 0.20

**Text:** How does your AI strategy address cross-border data flow considerations?

**Type:** Open-ended (short answer)

**Length limit:** 500 characters

**Rationale:** The only open-ended question in the assessment. Captures nuance that multiple-choice cannot. Used by Agent C2 (Synthesis) as qualitative signal; flagged for senior partner review attention.

---

## Question pool structure

The 20 questions above constitute the V0 default flow. Agent A3 (Question Personalization) selects from this pool based on persona and emerging industry inference. Specific behaviors:

**Persona-aware substitution.** Q3.3 (AI program outcomes) and Q5.2 (Success metrics) are CFO-favoring. When P3 (CFO) persona is inferred, these get framed with more financial language ("attributable revenue impact" vs "documented outcomes"). When P2 (CIO/CTO) is inferred, framing shifts to operational outcomes.

**Industry-aware substitution.** Q2.3 (Industry-specific AI guidance) is most relevant for FS and HLS. For MFG prospects, A3 substitutes a question about industrial safety regulation interpretation.

**Skip logic.** If Q3.1 (AI initiatives launched) answers A (none/one early pilot), Q3.2 (Production AI) and Q3.3 (AI outcomes) skip because they are not yet applicable. The prospect's AI investment maturity score uses Q3.1 and Q3.4 only in that case.

**Branching.** If Q6.1 (Regulatory frameworks) includes EU AI Act or FCA/PRA, Q6.2 (Data sovereignty) is asked. Otherwise, Q6.2 defaults to "no specific sovereignty constraints" and is skipped.

## Completion-time validation

Estimated time per question type:
- Multiple choice (single): 30-60 seconds
- Scale (1-5): 20-40 seconds
- Multiple choice (multiple): 60-90 seconds
- Open-ended (short): 90-180 seconds

Total estimated time for default flow (16-20 questions after skip logic): 18-26 minutes. Within the under-30-minute target with margin.

V0 internal testing: 5-8 internal users complete the assessment under realistic conditions. Median completion time and 90th percentile measured. Adjustments made based on data.

## Demo scenario calibration

For the V0 investor day demo, the questionnaire is completed against a representative scenario. Recommended scenario: a Fortune 500 financial services company (anonymized as "MeridianFS" or similar) with the following pre-determined answers:

- Data Foundation: moderate maturity (data fragmented but improving) → score range 45-55
- Governance Posture: developing (framework in draft, ownership emerging) → score range 35-50
- AI Investment Maturity: active but unstructured (15+ pilots, 2-3 in production) → score range 55-65
- Organizational Change Readiness: variable (leadership aligned, workforce mixed) → score range 50-65
- Value-Pocket Clarity: moderate (candidates identified, business case incomplete) → score range 50-60
- Regulatory Complexity: high (EU AI Act, FCA, FINRA all apply) → informational, not graded

This profile produces a "Developing" overall tier with specific findings around governance gap, value-pocket clarity gap, and recommended next step into APR Discovery scoped to AP processing or claims adjudication (FS-specific Tier 3 playbooks).

The demo scenario should produce a scorecard that is clearly differentiated by dimension (not all 50s) and lands a specific, defensible recommended next step.

---

*Companion documents: see Companion_02_QuickWins_Library.md for the 90-day quick wins memo content, Companion_03_Scorecard_Design.md for visual layout, Companion_04_Agent_Prompts.md for agent system prompts including A3 personalization logic, Companion_05_Data_Schemas.md for question-and-response data structures.*
