# API Contract

Expected API endpoints and request/response formats.

## Overview

The UI expects two API endpoints from your backend:

1. **GET /api/questions** — Fetch question pool
2. **POST /api/assess** — Submit responses, return scorecard

When `API = ''` (default in `src/constants.ts`), the app runs offline using `DEMO_SCORECARD`.

---

## GET /api/questions

Fetch the full question pool with conditional branching logic.

### Request

```
GET /api/questions
```

No query parameters or body.

### Response (200 OK)

```json
{
  "questions": [
    {
      "id": "Q1.1",
      "dimension": "data_foundation",
      "text": "How mature is your data architecture?",
      "type": "single_select",
      "options": [
        { "id": "A", "text": "No structured data" },
        { "id": "B", "text": "Siloed data warehouses" },
        { "id": "C", "text": "Integrated cloud data lake" },
        { "id": "D", "text": "Real-time data mesh" }
      ]
    },
    {
      "id": "Q1.2",
      "dimension": "data_foundation",
      "text": "Rate your data quality on a scale",
      "type": "scale_1_5",
      "scale_anchors": [
        { "value": 1, "text": "Very poor" },
        { "value": 2, "text": "Poor" },
        { "value": 3, "text": "Adequate" },
        { "value": 4, "text": "Good" },
        { "value": 5, "text": "Excellent" }
      ]
    },
    {
      "id": "Q1.3",
      "dimension": "data_foundation",
      "text": "Which data challenges apply?",
      "type": "multi_select",
      "options": [
        { "id": "X", "text": "Data quality issues" },
        { "id": "Y", "text": "Siloed systems" },
        { "id": "Z", "text": "Legacy infrastructure" }
      ]
    },
    {
      "id": "Q1.4",
      "dimension": "data_foundation",
      "text": "Describe your biggest data blocker",
      "type": "open_short",
      "open_answer_max_chars": 500
    },
    {
      "id": "Q2.1",
      "dimension": "governance_posture",
      "text": "Do you have data governance in place?",
      "type": "single_select",
      "options": [
        { "id": "A", "text": "No formal governance" },
        { "id": "B", "text": "Basic policies exist" },
        { "id": "C", "text": "Documented & enforced" }
      ],
      "skip_if": {
        "question": "Q1.1",
        "answer_in": ["A"]
      }
    },
    {
      "id": "Q3.1",
      "dimension": "ai_investment_maturity",
      "text": "What AI use cases are you exploring?",
      "type": "multi_select",
      "options": [
        { "id": "1", "text": "Forecasting" },
        { "id": "2", "text": "Anomaly detection" },
        { "id": "3", "text": "NLP/document processing" }
      ],
      "branch_if": {
        "question": "Q2.1",
        "answer_in": ["B", "C"]
      }
    }
  ],
  "dimensions": {
    "data_foundation": { "label": "Data Foundation" },
    "governance_posture": { "label": "Governance Posture" },
    "ai_investment_maturity": { "label": "AI Investment Maturity" },
    "org_change_readiness": { "label": "Organizational Change Readiness" },
    "value_pocket_clarity": { "label": "Value-Pocket Clarity" },
    "regulatory_complexity": { "label": "Regulatory Complexity" }
  }
}
```

### Question Types

| Type | Expected Answer | Notes |
|------|-----------------|-------|
| `single_select` | `{ option_id: "A" }` | Mutually exclusive options |
| `scale_1_5` | `{ scale_value: 3 }` | Integer 1-5 |
| `multi_select` | `{ option_ids: ["X", "Y"] }` | Array of selected IDs |
| `open_short` | `{ text: "..." }` | Up to `open_answer_max_chars` |

### Conditional Logic

- **skip_if**: Hide question if answer to another question matches given IDs
  - Useful: "Skip governance questions if user has no data"

- **branch_if**: Show question only if answer to another question matches given IDs
  - Useful: "Show AI use cases only if governance is in place"

---

## POST /api/assess

Submit user responses and return a scored scorecard.

### Request

```json
{
  "submission": {
    "prospect_name": "John Smith",
    "prospect_role": "Chief Data Officer",
    "prospect_email": "john@company.com",
    "company_name_raw": "Acme Corp",
    "industry_label": "Financial services",
    "industry_tag": "FS",
    "size_band": "large"
  },
  "consent": {
    "c1_use_for_scorecard": true,
    "c2_anonymized_benchmark": true,
    "c4_cross_practice_sharing": false
  },
  "responses": {
    "Q1.1": { "option_id": "C" },
    "Q1.2": { "scale_value": 4 },
    "Q1.3": { "option_ids": ["X", "Z"] },
    "Q1.4": { "text": "Legacy systems are fragmented" },
    "Q2.1": { "option_id": "B" },
    "Q3.1": { "option_ids": ["1", "3"] }
  },
  "persona_hint": null
}
```

### Response (200 OK)

```json
{
  "id": "scorecard_abc123",
  "company_name": "Acme Corp",
  "industry_label": "Financial services",
  "assessment_date": "24 July 2026",
  "reviewed_by": "DXC AdvisoryX",
  "overall_score": 62,
  "overall_tier": "Established",
  "overall_color": "#A1E6FF",
  "peer_reference": "Peer average for large US financial services: 58 (n=42)",
  "peer_benchmarks": {
    "data_foundation": 62,
    "governance_posture": 60,
    "ai_investment_maturity": 55,
    "org_change_readiness": 54,
    "value_pocket_clarity": 56,
    "regulatory_complexity": 62
  },
  "dimensions": [
    {
      "dimension": "data_foundation",
      "label": "Data Foundation",
      "score": 65,
      "tier": "Established",
      "color": "#A1E6FF",
      "informational": false
    },
    {
      "dimension": "governance_posture",
      "label": "Governance Posture",
      "score": 58,
      "tier": "Developing",
      "color": "#FFAE41",
      "informational": false
    },
    {
      "dimension": "ai_investment_maturity",
      "label": "AI Investment Maturity",
      "score": 68,
      "tier": "Established",
      "color": "#A1E6FF",
      "informational": false
    },
    {
      "dimension": "org_change_readiness",
      "label": "Organizational Change Readiness",
      "score": 52,
      "tier": "Developing",
      "color": "#FFAE41",
      "informational": false
    },
    {
      "dimension": "value_pocket_clarity",
      "label": "Value-Pocket Clarity",
      "score": 48,
      "tier": "Developing",
      "color": "#FFAE41",
      "informational": false
    },
    {
      "dimension": "regulatory_complexity",
      "label": "Regulatory Complexity",
      "score": 72,
      "tier": "Established",
      "color": "#A1E6FF",
      "informational": true
    }
  ],
  "findings": [
    {
      "finding_id": "F1",
      "headline": "Strong data foundation, governance needs attention",
      "body": "Your data architecture is solid, but governance and accountability are lagging. This limits your ability to scale AI safely."
    },
    {
      "finding_id": "F2",
      "headline": "AI momentum is present but unfocused",
      "body": "You're experimenting with relevant use cases, but lack clear value pocket definition. Prioritize high-impact, low-effort wins first."
    },
    {
      "finding_id": "F3",
      "headline": "Organizational readiness is moderate",
      "body": "Change management and skills development will be critical to moving from pilot to production."
    }
  ],
  "recommended_next_step": {
    "body": "Data Governance Discovery engagement to close the governance gap and define a 90-day AI scaling roadmap.",
    "duration_estimate_weeks": "6-10 weeks",
    "contact_name": "DXC AdvisoryX",
    "contact_title": "AI Readiness Team",
    "contact_email": "advisoryx@dxc.com"
  },
  "quick_wins": [
    {
      "pattern_name": "Intelligent Invoice Triage",
      "one_line_description": "AI categorizes and routes invoice exceptions.",
      "what_this_would_do": "Reduce AP manual effort by 40-60% and improve first-pass accuracy.",
      "prerequisites_you_have": [
        "AP system with exception logging",
        "6+ months of exception history"
      ],
      "expected_outcome_range": "AP handling time -40-60%",
      "timeline_to_value": "8-10 weeks",
      "implementation_effort": "Low"
    },
    {
      "pattern_name": "IT Incident Auto-Categorization",
      "one_line_description": "AI categorizes and routes IT incidents.",
      "what_this_would_do": "Cut mean-time-to-assignment by 60-80% across ServiceNow.",
      "prerequisites_you_have": [
        "ITSM system with incident logging",
        "Service catalog documented"
      ],
      "expected_outcome_range": "MTTR -60-80%",
      "timeline_to_value": "6-10 weeks",
      "implementation_effort": "Low"
    },
    {
      "pattern_name": "Compliance Document Review",
      "one_line_description": "AI flags compliance issues in documents.",
      "what_this_would_do": "Increase compliance review coverage and catch more issues.",
      "prerequisites_you_have": [
        "Document management system",
        "Internal policy library"
      ],
      "expected_outcome_range": "Issue detection +30-50%",
      "timeline_to_value": "10-14 weeks",
      "implementation_effort": "Medium"
    }
  ],
  "executive_narrative": {
    "headline": "Acme Corp is at the Established stage: strong data foundation with moderate governance and AI experimentation.",
    "paragraphs": [
      "Acme is at the Established stage, scoring 62 of 100, in line with peer average of 58. Your strength is data infrastructure; your gap is governance and organizational alignment.",
      "Data Foundation (65) is your strongest dimension. Leverage this strength to launch AI use cases quickly.",
      "Governance Posture (58) and Organizational Change Readiness (52) are moderate but require attention before large-scale rollout.",
      "In the next 90 days, focus on Invoice Triage, Incident Categorization, and Document Review. These are proven patterns with documented ROI.",
      "The next step is a Data Governance Discovery to close the governance gap and produce a board-ready AI scaling roadmap."
    ]
  },
  "value_difficulty": [
    {
      "opportunity": "Intelligent Invoice Triage",
      "value_score": 0.75,
      "difficulty_score": 0.3,
      "quadrant": "high_value_low_difficulty"
    },
    {
      "opportunity": "IT Incident Auto-Categorization",
      "value_score": 0.7,
      "difficulty_score": 0.25,
      "quadrant": "high_value_low_difficulty"
    },
    {
      "opportunity": "Compliance Document Review",
      "value_score": 0.8,
      "difficulty_score": 0.5,
      "quadrant": "high_value_high_difficulty"
    },
    {
      "opportunity": "Governance transformation",
      "value_score": 0.95,
      "difficulty_score": 0.8,
      "quadrant": "high_value_high_difficulty"
    }
  ]
}
```

### Scorecard Fields Reference

| Field | Type | Purpose |
|-------|------|---------|
| `id` | string | Unique scorecard ID (optional, used for PDF downloads) |
| `overall_score` | number | 0-100 overall readiness score |
| `overall_tier` | string | `Emerging`, `Developing`, `Established`, `Leading` |
| `overall_color` | string | Hex color for tier (e.g., `#FFAE41`) |
| `peer_benchmarks` | object | Peer scores by dimension (for comparison lines on bar chart) |
| `dimensions` | array | 6 dimensions with scores, tiers, colors |
| `findings` | array | 3-5 key findings about the company |
| `quick_wins` | array | 3 90-day implementation patterns |
| `value_difficulty` | array | 4 opportunities plotted on value/difficulty matrix |
| `executive_narrative` | object | `headline` + `paragraphs` for report |

---

## Offline Mode (No API)

If `/api/questions` or `/api/assess` fail, the app falls back to:
- Questions: None available (Assessment screen shows empty)
- Assess: Returns `DEMO_SCORECARD` (sample MeridianFS scorecard)

To test offline, set `API = ''` in `src/constants.ts`.

---

## Testing

### Test Questions Endpoint

```bash
curl http://localhost:8000/api/questions
```

Should return valid JSON matching the structure above.

### Test Assess Endpoint

```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "submission": {"prospect_name": "Test", "company_name_raw": "Test Co", ...},
    "consent": {"c1_use_for_scorecard": true},
    "responses": {"Q1.1": {"option_id": "A"}},
    "persona_hint": null
  }'
```

Should return a valid Scorecard object.

---

## Error Handling

If either endpoint returns:
- **404** — Endpoint not found (check API URL in `src/constants.ts`)
- **500** — Server error (check backend logs)
- **Network timeout** — App falls back to demo/offline mode
- **Invalid JSON** — App shows error in console

The UI doesn't display errors directly; check browser Developer Tools (F12) → Console tab.

---

## CORS Considerations

If backend and frontend are on different domains, ensure CORS headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

Or more restrictively, whitelist the UI domain:

```
Access-Control-Allow-Origin: https://ui.example.com
```

---

## Integration Checklist

- [ ] `/api/questions` endpoint returns valid question pool
- [ ] `/api/assess` endpoint accepts submission and returns scorecard
- [ ] CORS headers allow cross-origin requests (if separate domains)
- [ ] Update `API` constant in `src/constants.ts` to backend URL
- [ ] Test in browser: DevTools → Network → Check requests complete
- [ ] Verify scorecard renders with real data, not DEMO data
