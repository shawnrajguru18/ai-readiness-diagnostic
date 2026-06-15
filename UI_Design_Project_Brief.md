# Project Brief: DXC AI Readiness Diagnostic — UI Design

## What you are building

A professional web application for the **DXC AI Readiness Diagnostic** — an AI-driven advisory tool that takes enterprise prospects from "interested in AI" to "credible readiness scorecard" in 30 minutes of prospect time and 24 hours of DXC analysis. The product lives inside DXC AdvisoryX, DXC Technology's AI advisory practice.

This is not a startup SaaS tool. It is a premium enterprise advisory product. The UI must signal: world-class management consulting firm, AI-native capability, executive-grade outputs. The design will appear on stage at DXC's investor day and in front of Fortune 500 C-suite executives.

The V0 priority is the **demo experience**: a prospect submitting their assessment, seeing the questionnaire flow, and receiving a polished scorecard. This is what appears on the investor day stage.

---

## The product, briefly

A prospect (CEO, CIO, or CFO of a large enterprise) lands on the Diagnostic, enters their company info, completes a 20-question adaptive assessment, and receives — within 24 hours — a personalized AI readiness scorecard with dimensional scores, findings, recommended next step, and 90-day quick wins. Behind the scenes, AI agents research the prospect's company financials, news, and tech stack. A senior DXC partner reviews the output before delivery.

The output is the entry point to APR Discovery, DXC's deeper paid advisory engagement.

---

## DXC AdvisoryX brand system

Apply these exactly. They are locked.

### Color palette

| Name | Hex | Use |
|---|---|---|
| Midnight Blue | `#0E1020` | Primary backgrounds (dark), headings, body text on light |
| Canvas | `#F6F3F0` | Page background (warm off-white) |
| White | `#FFFFFF` | Card surfaces, panel backgrounds |
| Peach | `#FFC982` | Emerging tier accent |
| Gold | `#FFAE41` | Developing tier accent, 90-day quick wins |
| Melon | `#FF7E51` | Warm accent |
| Red | `#D14600` | Risk flags, caution signals |
| Sky | `#A1E6FF` | Established tier accent |
| True Blue | `#4995FF` | Leading tier accent, interactive elements |
| Royal | `#004AAC` | Primary CTA, recommended next step panels |

**Rules:** Accents are for data visualization, tier indicators, icons, and callout panels only. Never use them as large background fills on cards or sections. Midnight Blue and Canvas are the structural palette. White for surface layers.

### Tier color mapping

| Tier | Color | Hex |
|---|---|---|
| Emerging | Peach | `#FFC982` |
| Developing | Gold | `#FFAE41` |
| Established | Sky | `#A1E6FF` |
| Leading | True Blue | `#4995FF` |

### Typography

**Display / headings:** Use a strong, condensed, or high-contrast serif or display sans that reads as authoritative and editorial. Suggestions: `Playfair Display`, `Canela`, `Neue Montreal`, `Editorial New`, `Sohne Breit`, or similar premium choices. NOT Inter, NOT Roboto, NOT Arial.

**Body / UI:** A clean, precise geometric or humanist sans at high readability. Suggestions: `DM Sans`, `Söhne`, `Aktiv Grotesk`, `Untitled Sans`, `Roc Grotesk`. Something that pairs elegantly with the display choice.

**Scale:** Display headings large and confident. Body at 15-16px. Data labels small and precise.

### Voice in UI copy

- Lead with conclusions, not process
- Confident, specific, never generic
- No filler phrases ("It's important to note that...")
- Short and decisive: "Submit your assessment" not "Please fill out the form below to get started"

---

## Screen inventory (V0 priority)

Build these in order of priority for the investor day demo.

---

### Screen 1: Landing and Intake

**URL:** `/` or `/start`

**Purpose:** Convert a visiting executive into a Diagnostic submission. Fast, frictionless, high-confidence.

**What's on screen:**

- Hero statement: "Know where you stand on AI. In 30 minutes." — large, confident, editorial
- Sub-statement: "DXC returns a peer-benchmarked AI readiness scorecard within 24 hours. No consultant required."
- 4-field intake form: Full name, Role title, Business email, Company name
- Consent toggles (below the form):
  - "Use my data to produce my scorecard" — required, pre-checked, not removable
  - "Contribute anonymized data to the AdvisoryX peer benchmark library" — default on, toggleable
  - "Share with DXC teams for relationship follow-up" — default off, toggleable
- Primary CTA: "Begin assessment →"
- Trust signals: "Reviewed by a DXC senior partner before delivery" + "24-hour turnaround guaranteed" + "Used by enterprises in 18 countries"
- Minimal header: DXC AdvisoryX wordmark only

**Design notes:** The landing page should feel like a premium advisory firm's product, not a lead capture form. Think Bloomberg, McKinsey Digital, or Palantir Foundry in its visual confidence. Large typography, generous space, one clear action.

---

### Screen 2: Questionnaire Flow

**URL:** `/assessment`

**Purpose:** Guide the prospect through 15-25 adaptive questions across six dimensions in under 30 minutes.

**What's on screen:**

- Progress indicator: Dimension name + question count (e.g., "Data Foundation · 2 of 4") and an overall progress bar
- Question text — displayed large and clearly, center-weighted
- Answer options (one of three types):
  - **Single select:** Styled option cards (not radio buttons), each with the answer text. Selected state clearly distinguished.
  - **Scale 1-5:** Custom visual scale component with labeled anchors at 1 and 5
  - **Open short:** Single text area with character count remaining
- Question navigation: "Next →" primary, "← Back" secondary
- Current dimension label persistent at top left
- Time indicator (estimated minutes remaining, updates as they progress)
- No score visibility to the prospect during the assessment — deliberate. They see results after.

**Adaptive behavior (visual):** When later questions adapt based on earlier answers, show a subtle "tailored for you" indicator. The questionnaire is learning about them.

**Design notes:** This is where the prospect spends their 30 minutes. The design must reduce friction to near zero. Questions should breathe — one question fully visible at a time, no scroll needed. Smooth transitions between questions. The experience should feel like talking to a thoughtful consultant, not filling in a survey.

---

### Screen 3: Submission Confirmation

**URL:** `/submitted`

**Purpose:** Acknowledge submission, set expectations, build anticipation.

**What's on screen:**

- Confirmation message: "Your assessment is submitted." — definitive, not effusive
- What happens next (3 steps, clean visual treatment):
  1. "AI agents research [Company Name] — financials, news, tech posture"
  2. "Our synthesis engine scores your readiness across six dimensions"
  3. "A DXC senior partner reviews and approves your scorecard"
- Timeline: "You'll receive your scorecard within 24 hours at [email]"
- Portal link teaser: "A personal portal link will arrive with your results"
- Subtle animated element showing "analysis in progress" — something that communicates intelligence working behind the scenes without being gimmicky

**Design notes:** This is the moment after the prospect has invested 30 minutes. They should feel confident they did something meaningful and are in good hands. Not celebratory — dignified and assured.

---

### Screen 4: Scorecard (Prospect-Facing)

**URL:** `/portal/[token]` or `/results/[id]`

**Purpose:** The primary deliverable. What DXC delivers within 24 hours. What appears on the investor day stage.

**This is the most important screen in the product.**

**Header section:**
- Prospect company name (large)
- "AI Readiness Scorecard" label
- Assessment date
- "Reviewed by [Partner Name], Senior Partner, DXC AdvisoryX"
- Overall tier badge (Emerging/Developing/Established/Leading) with tier color

**Overall score panel:**
- Large score number (0-100)
- Tier label with color coding
- Peer comparison: "Industry average: [score] (n=[count])"

**Six-dimension radar chart:**
- Hexagonal radar/spider chart showing all six dimensions
- Each axis labeled
- Score annotated at each vertex
- Prospect's profile as filled polygon in tier color
- Peer benchmark as dashed outline (when available)
- This chart is the visual centerpiece — it must be crisp, elegant, and readable

**Dimension score breakdown:**
- Six rows: dimension name, score bar, score number, tier label
- Tier color applied to each bar

**Headline findings panel:**
- "What We Found" header
- 3-5 findings, each 1-2 sentences
- Findings must feel specific, not generic — the design should accommodate specificity, not force brevity
- Each finding numbered

**Recommended next step:**
- Royal blue left-border callout panel
- "Recommended next step" label
- 2-3 sentence recommendation
- "Continue the conversation →" CTA with partner contact

**Quick wins indicator (if quick wins memo exists):**
- Gold-accented section: "90-Day Quick Wins"
- 3 pattern names with one-line descriptions
- "View full quick wins memo →" link

**Footer:**
- Download PDF option
- "Prepared by DXC AdvisoryX"
- Confidential marking

**Design notes:** The scorecard is what investors see on stage. It must look like a premium consulting deliverable, not a dashboard widget. The radar chart is the signature visual — invest in making it beautiful. The findings must read as authoritative, specific, expert analysis. The Royal blue callout for the recommended next step should visually pop as the conversion moment.

---

### Screen 5: Quick Wins Memo

**URL:** `/portal/[token]/quick-wins`

**Purpose:** Companion to the scorecard. Shows the 3 recommended 90-day AI actions.

**What's on screen:**

- Header matching scorecard branding
- Intro paragraph (2-3 sentences on what quick wins are and how they complement the strategic recommendation)
- Three pattern cards, each containing:
  - Pattern name (large)
  - One-line description
  - "What this would do for [Company]:" — 2-3 sentences specific to the prospect
  - "Prerequisites you have:" — checkmarks on satisfied prerequisites
  - "Expected outcome:" — with peer data range
  - "Timeline to value:" — in weeks
  - Implementation effort indicator (Low/Medium)
- "Continue the conversation →" CTA at bottom

---

## Internal DXC screens (V1 — include in brief for completeness)

### Screen 6: Partner Review Dashboard

**URL:** `/review` (DXC internal, authenticated)

**Purpose:** Senior partners see pending scorecard reviews, review AI output, adjust findings, approve or return.

**What's on screen:**

- Queue of pending reviews, sorted by priority (validation flags surfaced first)
- Each queue item: company name, submission time, time remaining in SLA, flag count, overall confidence score
- Review view for a selected scorecard:
  - Full prospect-facing scorecard output (as it will appear to the prospect)
  - Side panel: AI reasoning trace per finding, validation flags, confidence per finding
  - Partner action controls: edit any text field, approve, send back with note
  - Keyboard shortcuts for fast review
- Partner notes field: captured for training data

**Design notes:** This is a professional tool for sophisticated users under time pressure. Efficiency over aesthetics, but still DXC brand quality. Dense information layout is appropriate here. The flag indicators should make the highest-risk items impossible to miss.

---

## Demo scenario for example content

For all screens, use the **MeridianFS** demo scenario as example content:

- **Company:** MeridianFS Holdings, Inc.
- **Prospect name:** Sarah Chen
- **Role:** Chief Digital Officer
- **Overall tier:** Developing
- **Overall score:** 55
- **Peer reference:** "Peer average for large US financial services: 58 (n=42)"

**Dimension scores:**
- Data Foundation: 52 (Developing, Gold)
- Governance Posture: 38 (Emerging, Peach)
- AI Investment Maturity: 62 (Established, Sky)
- Organizational Change Readiness: 55 (Developing, Gold)
- Value-Pocket Clarity: 48 (Developing, Gold)
- Regulatory Complexity: 72 (Established, Sky) — informational

**Three headline findings (use these verbatim in any mockups):**
1. "MeridianFS has launched substantial AI experimentation — 15+ initiatives over 24 months — but the production conversion rate trails large-FS peers by approximately 30%. The gap concentrates in initiatives that lacked clear value-pocket definition at scoping."
2. "Governance posture is the largest dimensional gap. AI risk ownership is distributed across CISO, Compliance, and Legal without an integrating accountability layer. FCA AI guidance interpretation is underway but not operationalized."
3. "The strongest foundation for near-term AI value is in operational processes: AP, IT incident management, and customer support already show measurable AI value in production. Scaling these patterns horizontally is a high-confidence path."

**Recommended next step:** "APR Discovery engagement (6-10 weeks) focused on claims adjudication reinvention and operational AI scaling pattern."

**Quick wins:**
1. Intelligent Invoice Triage — 8-10 weeks to value
2. IT Incident Auto-Categorization — 6-10 weeks to value
3. Compliance Document Review — 10-14 weeks to value

---

## Aesthetic direction

**The reference:** Imagine the intersection of a Bloomberg Terminal (data density, authority, precision), a McKinsey report (clarity, structure, executive confidence), and a modern fintech dashboard (interactivity, live data, clean components). Then strip the Bloomberg chaos, add warmth from the Canvas background, and center it on a single decisive insight.

**Not:** A startup landing page, a generic SaaS dashboard, a purple-gradient hero section, anything that feels like it was designed for developers.

**The one thing people should remember:** The radar chart on the scorecard. It should be the signature visual of the entire product — elegant, data-rich, instantly readable, unmistakably DXC.

**Dark and light:** The landing page can push into deep Midnight Blue if the creative direction calls for it. The questionnaire flow and scorecard live on Canvas (#F6F3F0) as the warm off-white base.

**Motion:** Purposeful only. The questionnaire transition between questions should be smooth. The scorecard should animate on load — radar chart drawing itself, scores counting up. The submission confirmation should show something elegant communicating "AI is working." Nothing gratuitous.

**Typography execution:** Display headings on the landing page should be large, confident, possibly with a slight editorial weight contrast (light + bold pairing). The scorecard findings text should read like a consulting memo — precise, confident, no visual clutter.

---

## Technical requirements

- **Framework:** React. Use Tailwind for utility classes (base stylesheet only — no custom compiler). Use Recharts for charts.
- **Available libraries:** recharts, lucide-react, lodash, d3, mathjs, shadcn/ui components
- **Radar chart:** Use Recharts `RadarChart` with `Radar` and `PolarGrid` components, or custom SVG if Recharts doesn't achieve the required visual quality
- **PDF download:** Out of scope for the UI brief — handled server-side
- **State:** React state (useState, useReducer) only — no localStorage
- **Mobile:** Responsive. The questionnaire in particular must work cleanly on mobile (executives may access this on their phone)
- **Accessibility:** Focus states visible. Color not the only indicator of meaning. ARIA labels on interactive elements.

---

## What to build for V0

For the investor day demo, the minimum deliverable is:

1. **Landing / Intake** — full, polished, demo-ready
2. **Questionnaire flow** — at least 5 questions working end-to-end with the MeridianFS answer pattern
3. **Submission confirmation** — polished
4. **Scorecard** — fully designed and populated with MeridianFS data, radar chart working
5. **Quick wins memo** — populated with MeridianFS quick wins

These five screens constitute the investor day demonstration. They must be pixel-quality, not prototype-quality.

---

## What the design must accomplish

The UI is making three arguments simultaneously:

**To the prospect:** "This is a serious, professional assessment from a firm that knows what it's doing. The output is worth acting on."

**To the investor:** "DXC has built a scalable AI advisory engine. This is what it looks like running. The design quality signals the product quality."

**To DXC internally:** "This is the front door of our AI services growth strategy. It has to be better than anything competitors can show."

The design wins if someone looks at the scorecard and thinks: "This is what a premium consulting firm's AI product looks like."

---

*This brief covers the DXC AI Readiness Diagnostic V0 UI. Full product context in DXC_AI_Readiness_Diagnostic_PRD_V4.md. Brand standards per DXC AdvisoryX v1.1 (December 2025). Demo content per Companion_03_Scorecard_Design.md.*
