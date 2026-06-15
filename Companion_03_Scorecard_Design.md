---
title: "Companion 03 — Scorecard Output Design"
status: "DRAFT V1 — for working group iteration and design partner refinement"
parent_doc: "DXC_AI_Readiness_Diagnostic_PRD.md"
purpose: "Visual specification of the prospect-facing scorecard deliverable, with brand application, layout details, and three populated demo scenarios"
target: "V0 build — investor day demo"
---

# Scorecard Output Design

## Purpose

This document specifies what the prospect actually sees at the end of the Diagnostic. It is the most demo-visible artifact in the V0 build. The design has three audiences:

1. **The prospect**, who consumes it as a decision document.
2. **The senior partner**, who reviews it before delivery.
3. **The investor day audience**, who sees it as the visible proof of AdvisoryX's capability.

The scorecard must work for all three. This document specifies layout, content, brand application, and three populated demo examples.

## Output formats

The Diagnostic produces three connected artifacts:

**Primary deliverable: One-page PDF scorecard.** What the prospect receives via email. What appears on the investor day stage. Designed for executive consumption.

**Secondary deliverable: Quick wins memo (PDF, one page).** Companion to the scorecard. Names the 2-3 recommended 90-day actions.

**Tertiary deliverable: Findings appendix (PDF, 5-8 pages).** Full reasoning, dimension-by-dimension detail, source data, methodology note. For prospects who want depth. Generated automatically; included as appendix to the scorecard email.

## Brand application

Brand standards per DXC PowerPoint v1.1 (December 2025), adapted for document context.

**Background.** Canvas #F6F3F0 for the document body. White #FFFFFF for content panels and chart backgrounds.

**Primary text.** Midnight Blue #0E1020 for headings, key findings, and emphasis. Soft gray #3D3F50 for body copy.

**Accent palette** (used for data visualization, never as panel backgrounds):
- Peach #FFC982 — Emerging tier
- Gold #FFAE41 — Developing tier
- Sky #A1E6FF — Established tier
- True Blue #4995FF — Leading tier
- Royal #004AAC — emphasis and recommended next step callouts
- Red #D14600 — only for critical risk flags

**Fonts.** GT Standard L Extended for major headings (28pt+, all caps). Inter for body copy (14pt minimum). Falls back to Arial where GT Standard not available.

**Branding placement.** DXC logo top-left in muted gray. AdvisoryX wordmark bottom-right at smaller scale. "Confidential" mark in footer.

## Page 1: The Scorecard

Single page, US Letter portrait orientation. Five sections in vertical flow.

### Section 1: Header (top 12% of page)

**Left side:**
- "AI READINESS DIAGNOSTIC" in GT Standard L 14pt all caps, Midnight Blue
- Below: prospect company name in Inter Bold 22pt
- Below: assessment date in Inter Regular 10pt, gray

**Right side:**
- DXC AdvisoryX wordmark, height 28px
- Beneath in 8pt gray: "Prepared by DXC Technology"

A 1px Midnight Blue divider below this section separates header from content.

### Section 2: Overall readiness summary (top-right, ~15% of page)

A small panel sized for an at-a-glance read.

**Content:**
- Overall tier label (Emerging / Developing / Established / Leading) in 18pt bold, color-matched to tier accent
- "Overall AI readiness" subtitle in 9pt gray uppercase
- Overall score (composite of six dimensions, weighted) as a large numeric (e.g., "58") in 36pt
- Industry peer reference text: "Peer average for [industry]: [score]" (V0.5+; placeholder in V0)

### Section 3: Six-dimension scorecard (center, ~35% of page)

The visual centerpiece of the deliverable.

**Visual:** Radial chart (hexagonal radar plot) showing all six dimensions on one diagram.

**Specification:**
- Hexagonal grid with six axes
- Each axis labeled with dimension name in 9pt Midnight Blue
- Scale rings at 25, 50, 75, 100
- Prospect's score plotted as a filled hexagon, color-coded to overall tier
- Peer benchmark plotted as a dashed outline (V0.5+; placeholder reference line in V0)
- Dimension scores annotated at each vertex in 11pt Midnight Blue bold

**Right of chart**: vertical list of the six dimensions with score and tier.

```
Data Foundation          52   Developing
Governance Posture       38   Emerging
AI Investment Maturity   62   Established
Org Change Readiness     55   Developing
Value-Pocket Clarity     48   Developing
Regulatory Complexity    72   Established  (informational)
```

Tier labels colored to match accent palette.

### Section 4: Headline findings (middle, ~20% of page)

Three to five findings, each one short and decision-relevant. Written for executive consumption (P1 framing default; persona-adapted by Agent D1).

**Layout:**
- "WHAT WE FOUND" header in 11pt GT Standard L all caps, Midnight Blue, with small Royal accent square preceding
- Three to five findings as numbered items
- Each finding: 1-2 sentences, Inter Regular 11pt, Midnight Blue
- Findings should be specific, not generic ("Your governance posture lags peer financial services institutions by approximately 20 points, concentrated in operational AI risk ownership" rather than "improve governance")

**Number of findings:** Three for strong-signal prospects, five for prospects with multiple distinct gaps. Agent D1 selects.

### Section 5: Recommended next step (bottom-right, ~12% of page)

The conversion-relevant content. Where the funnel goes from Diagnostic to Discovery.

**Layout:**
- Royal-bordered panel (left border 4px Royal)
- "RECOMMENDED NEXT STEP" in 11pt GT Standard L all caps, Royal
- Body: 2-3 sentences identifying the specific scoped engagement, the value pockets it would address, and the expected duration. Inter Regular 11pt.
- Below body: "Continue the conversation: [partner name] | [contact]" in 9pt gray

**Recommendation specificity:**
- Names a specific area (process, function, or capability gap) rather than generic "AI engagement"
- References dimension findings explicitly
- Indicates engagement type (typically "APR Discovery scoped to [area]")
- Suggests duration (typically "6-10 weeks")

### Section 6: Quick wins indicator (bottom-left, ~6% of page)

A small panel pointing to the quick wins memo.

**Layout:**
- "90-DAY QUICK WINS" header in 11pt GT Standard L all caps, Gold
- Three short lines (one per recommended quick win): pattern name in bold + one-line description
- Reference to the full quick wins memo: "Full memo attached" in 9pt italic gray

### Section 7: Footer (bottom 4% of page)

- Left: "Confidential — Prepared for [Company Name]" in 8pt gray
- Right: "Page 1 of 1 (scorecard) | Quick wins memo and findings appendix attached"

## Page-level visual hierarchy

The reader's eye should flow as:

1. **First glance (1-2 seconds):** Overall tier and score in top-right. Tells them where they stand.
2. **Quick scan (5-10 seconds):** Hexagonal radar chart shows dimensional breakdown at a glance.
3. **Substantive read (30-60 seconds):** Findings list and recommended next step. Where the decision-relevant content lives.
4. **Reference reads:** Quick wins indicator and full appendix for deeper consumption.

## Demo scenario 1: MeridianFS (Financial Services)

Sample populated scorecard for the V0 investor day demo.

**Header:**
- Title: AI READINESS DIAGNOSTIC
- Company: MeridianFS Holdings, Inc.
- Date: 14 June 2026

**Overall summary:**
- Tier: Developing
- Score: 55
- Peer reference: "Peer average for large US financial services: 58 (n=42)"

**Six-dimension scores:**
- Data Foundation: 52 (Developing)
- Governance Posture: 38 (Emerging)
- AI Investment Maturity: 62 (Established)
- Organizational Change Readiness: 55 (Developing)
- Value-Pocket Clarity: 48 (Developing)
- Regulatory Complexity: 72 (Established, informational)

**Headline findings:**
1. MeridianFS has launched substantial AI experimentation (15+ initiatives over 24 months) but the production conversion rate trails large-FS peers by approximately 30%. The gap concentrates in initiatives that lacked clear value-pocket definition at scoping.
2. Governance posture is the largest dimensional gap. AI risk ownership is distributed across CISO, Compliance, and Legal without an integrating accountability layer. FCA AI guidance interpretation is underway but not operationalized.
3. The strongest foundation for near-term AI value is in operational processes: AP, IT incident management, and customer support already show measurable AI value in production. Scaling these patterns horizontally is a high-confidence path.
4. Significant unaddressed opportunity in claims-adjacent processes (fraud detection, underwriting support) where MeridianFS's data foundation is stronger than the institutional AI investment posture would suggest.
5. Workforce posture is mixed: leadership alignment is strong on AI ambition but operational teams show variance from enthusiastic to apprehensive depending on function. Change management capacity is sufficient for targeted programs but not for enterprise-wide transformation without investment.

**Recommended next step:**
> APR Discovery engagement (6-10 weeks) focused on claims adjudication reinvention and operational AI scaling pattern. The Discovery would size value pockets across claims sub-processes, identify reinvention archetypes (Restructure or Retire candidates), design governance integration, and produce a board-ready 18-month roadmap. Continue the conversation: Chris Bryson, Senior Partner | christopher.bryson@dxc.com

**Quick wins (referenced):**
- QW-001 Intelligent Invoice Triage — 8-10 weeks to value
- QW-005 IT Incident Auto-Categorization — 6-10 weeks to value
- QW-012 Compliance Document Review — 10-14 weeks to value

## Demo scenario 2: NorthernCare Health (Healthcare)

Sample populated scorecard for a healthcare prospect.

**Header:**
- Title: AI READINESS DIAGNOSTIC
- Company: NorthernCare Health System
- Date: 22 June 2026

**Overall summary:**
- Tier: Emerging
- Score: 41
- Peer reference: "Peer average for large US health systems: 39 (n=18)"

**Six-dimension scores:**
- Data Foundation: 35 (Emerging)
- Governance Posture: 45 (Developing)
- AI Investment Maturity: 32 (Emerging)
- Organizational Change Readiness: 48 (Developing)
- Value-Pocket Clarity: 42 (Developing)
- Regulatory Complexity: 85 (Leading, informational - high constraint)

**Headline findings:**
1. NorthernCare's AI program is early-stage. Few initiatives have moved beyond proof of concept, and outcomes attribution is difficult. This is typical for large health systems and does not preclude rapid acceleration with focused investment.
2. Data foundation is the binding constraint. EHR data is accessible but operational and ancillary data sit in 30+ systems with limited integration. AI initiatives consistently hit data access friction. Foundation work is prerequisite to AI scale.
3. Regulatory complexity is high (HIPAA, FDA SaMD for clinical AI, state-level mandates) which appropriately constrains AI patterns. Strong regulatory posture is an asset, not a liability, when paired with the right AI strategy.
4. Highest-confidence near-term value: administrative and operational AI (revenue cycle, scheduling, supply chain) where clinical regulatory complexity does not apply. These patterns can produce measurable value while data foundation work matures the path to clinical AI.
5. Leadership alignment exists at the executive level but operational implementation capacity is thin. Significant change-management investment will be required for enterprise AI adoption.

**Recommended next step:**
> APR Discovery engagement (8-12 weeks) focused on revenue cycle and administrative AI patterns, paired with data foundation roadmap design for clinical AI readiness. The Discovery would identify near-term value pockets in non-clinical operations, design the data foundation investment sequence, and prepare governance for HIPAA-compliant clinical AI in 2027. Continue the conversation: Chris Bryson, Senior Partner | christopher.bryson@dxc.com

**Quick wins (referenced):**
- QW-006 Knowledge Base Search Enhancement — 4-8 weeks to value
- QW-008 Expense Report Categorization — 6-10 weeks to value
- QW-002 Customer Support Ticket Categorization — 6-10 weeks to value

## Demo scenario 3: AurelianTech (Mid-market Tech Services)

Sample populated scorecard for a tech-forward prospect with strong AI posture but governance gaps.

**Header:**
- Title: AI READINESS DIAGNOSTIC
- Company: AurelianTech Solutions
- Date: 8 July 2026

**Overall summary:**
- Tier: Established
- Score: 68
- Peer reference: "Peer average for mid-market tech services: 54 (n=11)"

**Six-dimension scores:**
- Data Foundation: 78 (Established)
- Governance Posture: 42 (Developing)
- AI Investment Maturity: 75 (Established)
- Organizational Change Readiness: 80 (Leading)
- Value-Pocket Clarity: 70 (Established)
- Regulatory Complexity: 35 (Emerging, informational - low constraint)

**Headline findings:**
1. AurelianTech is significantly ahead of mid-market peers on AI capability. Strong data foundation, mature AI investment portfolio, and exceptional change readiness create rare conditions for rapid scaling.
2. The single notable gap is governance. AI investment has moved faster than governance maturity. As AurelianTech expands AI use into customer-facing and revenue-impacting contexts, governance becomes the binding constraint on continued scale.
3. Value-pocket clarity is strong for current AI program (well-defined initiatives with KPIs), but the next horizon is undefined. Strategic AI use cases for the next 24 months are not yet shaped. This is the right moment to design that horizon before AI investment becomes opportunistic rather than directed.
4. Regulatory complexity is low currently but increasing rapidly (state-level AI laws, EU AI Act implications for any EU customer). Proactive regulatory posture would be a strategic differentiator.
5. The Established overall tier and Leading change readiness create conditions where APR Discovery can move quickly: less change management investment, less data foundation work, more focus on strategic direction and governance architecture.

**Recommended next step:**
> APR Discovery engagement (6-8 weeks) focused on AI governance architecture and 24-month strategic AI direction. The Discovery would design the governance framework AurelianTech needs as AI scales into customer-facing contexts, identify the next-horizon value pockets, and produce a sequenced strategic AI investment plan. Continue the conversation: Chris Bryson, Senior Partner | christopher.bryson@dxc.com

**Quick wins (referenced):**
- QW-010 Code Review Assistant — 4-8 weeks to value
- QW-007 Meeting Summarization — 4-8 weeks to value
- QW-009 Sales Prospect Research Automation — 4-8 weeks to value

## Quick wins memo: design specification

The quick wins memo is the secondary deliverable. One page, attached to the scorecard email.

**Layout:**

**Header.** "90-DAY QUICK WINS — [Company Name]" in GT Standard L 14pt all caps. Same brand framing as scorecard.

**Intro paragraph (3-4 sentences).** Frame what quick wins are and how they fit alongside the broader Discovery recommendation. Example: "Quick wins are AI patterns the organization can implement in 90 days or less. Each pattern has documented enterprise deployments with measurable results. They are not transformational, but they build momentum and prove organizational AI execution capacity while the strategic AI roadmap takes shape through Discovery."

**Three pattern cards.** Each card occupies roughly 25% of remaining page.

Per card:
- Pattern name in 13pt bold (e.g., "Intelligent Invoice Triage")
- One-line description in 11pt italic
- "What this would do for [Company]:" with 2-3 sentences specific to the prospect's situation
- "Prerequisites you have:" with checked items
- "Expected outcome range:" with peer data
- "Timeline to value:" with weeks
- Small Royal accent square at the top-left of each card

**Footer.** "Continue the conversation: Chris Bryson, Senior Partner | christopher.bryson@dxc.com"

## Findings appendix: design specification

The findings appendix is the tertiary deliverable. 5-8 pages. Generated automatically. Provides full reasoning.

**Structure:**

**Cover page.** Same header treatment as scorecard. Title: "Findings Appendix." Lists the contents.

**Page 2-3: Methodology note.** How the assessment works. What sources contributed (questionnaire, public research, peer benchmarks where applicable). Confidence ranges and limitations. Senior partner attestation that the output has been reviewed.

**Pages 4-7: Dimension-by-dimension detail.** One page per dimension. Each page includes:
- Dimension definition (what it captures)
- The prospect's score with reasoning
- Specific questionnaire responses that drove the score
- Public research signals that informed the score
- Peer comparison (V0.5+; placeholder in V0)
- What strong performance on this dimension looks like
- Specific actions the prospect could take to improve this dimension

**Page 8: Sources and acknowledgments.** What public sources were consulted. Disclaimer. DXC contact information.

## Visual mockup notes for the design partner

Robb's design work needs to deliver:

1. **A figma file or equivalent** with the scorecard layout, quick wins memo layout, and findings appendix template.
2. **Three populated examples** matching the demo scenarios above. These become the V0 investor day demo content.
3. **Brand-compliant chart styling** for the hexagonal radar chart. The chart visual quality determines investor day impression more than the prose.
4. **PDF export specification** that engineering implements (probably using ReportLab, Pandoc, or equivalent Python PDF library).

The radar chart specifically is worth design attention. A weak radar chart visualization undermines the entire scorecard. Reference: ServiceNow's executive summary outputs and Adobe's Customer Experience reports both have strong examples of dimensional radar visualizations.

## Engineering implementation notes for Claude Code

The Output Generation Agent (D1) produces the scorecard by:

1. Receiving synthesis output (six-dimension scores, findings, recommended next step, quick wins) and persona profile from upstream agents.
2. Selecting the appropriate scorecard template variant (V0: one default template; V0.5+: persona-adapted variants).
3. Populating the template with the prospect's specific data.
4. Generating the PDF via a templating layer (recommended: WeasyPrint or ReportLab in Python; or a headless browser with HTML/CSS templates).
5. Storing the generated PDF in the prospect record store.
6. Delivering via email with appropriate metadata.

The chart specifically should be generated server-side (matplotlib or plotly to image, or an SVG-to-PDF conversion). Client-side generation introduces fragility for V0.

Demo scenarios above can serve as test fixtures for Claude Code's implementation. Each scenario should produce a scorecard PDF that matches the populated examples described.

---

*Companion documents: see Companion_01_Questionnaire_Specification.md for input data structures, Companion_02_QuickWins_Library.md for quick win pattern details, Companion_04_Agent_Prompts.md for Output Generation Agent system prompt, Companion_05_Data_Schemas.md for synthesis output and scorecard data structures.*
