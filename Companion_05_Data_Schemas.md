---
title: "Companion 05 — Data Schemas"
status: "DRAFT V1 — for working group iteration"
parent_doc: "DXC_AI_Readiness_Diagnostic_PRD.md"
purpose: "TypeScript interface and JSON Schema definitions for all entities in the Diagnostic system. Source of truth for data structures across all 16 agents."
target: "V0 build — investor day demo. Directly consumable by Claude Code."
---

# Data Schemas

## Purpose

This document specifies all data structures used by the Diagnostic. Schemas are presented as TypeScript interfaces for engineer readability, with JSON Schema equivalents available on request. All agents conform to these schemas; the orchestrator validates inputs and outputs against them.

Schemas are V1 drafts. They will evolve through implementation as fields prove necessary or unused. Major schema changes go through working group review since they affect multiple agents.

## Design principles

**Entity identification.** Every entity has a stable UUID. References between entities use UUIDs, not natural keys.

**Timestamps.** All timestamps are ISO 8601 UTC. Capture creation and last-modified consistently.

**Confidence reporting.** Where agents produce inferred or analytical output, confidence is captured as a `Confidence` value (0.0-1.0 with optional reasoning).

**Audit-first.** Every entity has audit trail fields capturing who/what/when generated it. Critical for partner review credibility and regulatory compliance.

**Forward compatibility.** Optional fields are explicit. New fields can be added without breaking existing consumers.

**Consent enforcement at the schema level.** Records that depend on consent (E1, E2, E3 outputs) include the consent state at creation time.

## Common types

```typescript
// All entities have these
type UUID = string;  // RFC 4122 v4
type ISO8601 = string;  // e.g., "2026-05-19T14:32:00Z"

type Confidence = {
  value: number;  // 0.0 to 1.0
  reasoning?: string;
};

type AuditMetadata = {
  created_at: ISO8601;
  created_by: string;  // agent ID or user ID
  last_modified_at: ISO8601;
  last_modified_by: string;
  version: number;  // monotonic
};

type Industry = {
  naics_code: string;
  industry_label: string;
  sub_industry?: string;
};

type Geography = {
  hq_country: string;  // ISO 3166 alpha-2
  operating_jurisdictions: string[];  // ISO 3166 alpha-2
};

type SizeBand = "mid-market" | "large" | "global" | "unknown";

type Persona = "P1" | "P2" | "P3";

type DimensionId =
  | "data_foundation"
  | "governance_posture"
  | "ai_investment_maturity"
  | "org_change_readiness"
  | "value_pocket_clarity"
  | "regulatory_complexity";

type Tier = "Emerging" | "Developing" | "Established" | "Leading";
```

## Prospect record (canonical entity)

The central entity. All Diagnostic processing references a prospect record.

```typescript
type Prospect = {
  prospect_id: UUID;

  // Submission data
  submission: {
    prospect_name: string;
    prospect_role: string;
    prospect_email: string;
    company_name_raw: string;  // as entered
    company_website?: string;
    submission_timestamp: ISO8601;
    submission_source: "web_direct" | "partner_referral" | "investor_day_demo" | "test";
    referring_partner_id?: string;
  };

  // After A1 validation
  normalized?: {
    company_canonical_name: string;
    company_ticker?: string;
    company_lei?: string;
    industry: Industry;
    geography: Geography;
    size_band: SizeBand;
    company_resolution_confidence: Confidence;
  };

  // After A2 persona inference
  persona_inference?: PersonaInference;

  // Consent state at submission (immutable; updates create new ConsentRecord entries)
  initial_consent_record_id: UUID;

  // Status tracking
  processing_status: ProcessingStatus;

  audit: AuditMetadata;
};

type ProcessingStatus = {
  current_phase:
    | "intake"
    | "research_in_flight"
    | "synthesis"
    | "output_generation"
    | "validation"
    | "partner_review_queued"
    | "partner_review_in_progress"
    | "approved_for_delivery"
    | "delivered"
    | "downstream_routing"
    | "completed"
    | "error"
    | "withdrawn";
  sla_target: ISO8601;
  sla_breached: boolean;
  current_phase_started_at: ISO8601;
  error_state?: {error_code: string; description: string};
};
```

## Consent record

Consent is captured at submission time. Subsequent consent changes create new records (immutable history).

```typescript
type ConsentRecord = {
  consent_record_id: UUID;
  prospect_id: UUID;
  consent_timestamp: ISO8601;

  // The five consent categories
  c1_use_for_scorecard: true;  // REQUIRED — always true; cannot opt out
  c2_anonymized_benchmark_contribution: boolean;  // DEFAULT_ON, can opt out
  c3_internal_ai_tool_improvement: boolean;  // DEFAULT_OFF, opt-in
  c4_cross_practice_sharing: boolean;  // DEFAULT_OFF, opt-in
  c5_productized_benchmark_third_party: boolean;  // V2+; DEFAULT_OFF, opt-in

  // Legal context
  legal_basis: "consent" | "legitimate_interest" | "contract";
  applicable_jurisdictions: string[];  // ISO 3166 alpha-2 for jurisdictions whose privacy law applies
  consent_method: "web_form_v1" | "partner_facilitated" | "api";
  consent_language_version: string;  // version of consent UI text the prospect saw

  audit: AuditMetadata;
};
```

## Persona inference (A2 output)

```typescript
type PersonaInference = {
  prospect_id: UUID;

  primary_persona: Persona;
  primary_persona_confidence: Confidence;
  secondary_persona?: Persona;
  secondary_persona_confidence?: Confidence;

  likely_concerns: Concern[];
  framing_preference: "financial-quantitative" | "strategic-narrative" | "technical-operational";
  seniority: "board-facing" | "executive" | "senior-management" | "unknown";
  industry_experience_signals: string[];
  reasoning_summary: string;

  audit: AuditMetadata;
};

type Concern =
  | "revenue_growth"
  | "cost_reduction"
  | "risk_mitigation"
  | "innovation"
  | "regulatory_compliance"
  | "competitive_positioning"
  | "operational_efficiency"
  | "talent_workforce";
```

## Questionnaire structures

### Question pool entry (static reference)

```typescript
type QuestionPoolEntry = {
  question_id: string;  // e.g., "Q1.1"
  dimension: DimensionId;
  dimension_weight: number;  // 0.0-1.0, sums to 1.0 within dimension
  question_type: "single_select" | "multi_select" | "scale_1_5" | "open_short";

  default_text: string;
  framing_variants: {
    variant_id: string;  // e.g., "persona_P1", "industry_FS"
    text: string;
  }[];

  options?: QuestionOption[];  // for select/multi-select
  scale_anchors?: ScaleAnchor[];  // for scale_1_5
  open_answer_max_chars?: number;  // for open_short

  applicable_personas: Persona[];
  applicable_industries: ("FS" | "HLS" | "MFG" | "All")[];

  skip_logic?: {
    skip_if_question: string;
    skip_if_answer_includes: string[];
  };

  branching_logic?: {
    show_if_question: string;
    show_if_answer_includes: string[];
  };

  rationale: string;  // for partner reference, not prospect-facing
};

type QuestionOption = {
  option_id: string;
  option_text: string;
  score: number;  // 0-100, contribution to dimension
};

type ScaleAnchor = {
  scale_value: 1 | 2 | 3 | 4 | 5;
  anchor_text: string;
  score: number;  // 0-100
};
```

### Personalized questionnaire (A3 output, per prospect)

```typescript
type PersonalizedQuestionnaire = {
  questionnaire_id: UUID;
  prospect_id: UUID;

  selected_questions: PersonalizedQuestion[];
  total_question_count: number;
  estimated_completion_time_minutes: number;
  selection_reasoning: string;

  audit: AuditMetadata;
};

type PersonalizedQuestion = {
  question_id: string;  // references QuestionPoolEntry
  ordered_position: number;
  framing_variant: string;  // which variant was selected
  rendered_text: string;  // the actual text shown to prospect
  skip_logic_dependencies: string[];
};
```

### Questionnaire response

```typescript
type QuestionnaireResponse = {
  response_id: UUID;
  questionnaire_id: UUID;
  prospect_id: UUID;

  responses: QuestionResponse[];
  completion_timestamp: ISO8601;
  total_completion_time_seconds: number;
  partial_completion: boolean;

  audit: AuditMetadata;
};

type QuestionResponse = {
  question_id: string;
  question_rendered_text: string;  // captured for audit (text may have varied by personalization)
  answer:
    | {type: "single_select"; option_id: string; score: number}
    | {type: "multi_select"; option_ids: string[]; informational: true}
    | {type: "scale_1_5"; scale_value: 1 | 2 | 3 | 4 | 5; score: number}
    | {type: "open_short"; text: string};
  response_timestamp: ISO8601;
  response_time_seconds: number;
};
```

## Research outputs (B-agents)

### Financial research output (B1)

```typescript
type FinancialResearch = {
  research_id: UUID;
  prospect_id: UUID;
  research_status: "complete" | "partial" | "limited_public_data";

  financial_summary?: {
    revenue_latest_fy?: {value: number; currency: string; fy: number};
    revenue_3y_cagr?: number;
    operating_margin_latest_fy?: number;
    operating_margin_trajectory?: "improving" | "stable" | "declining";
    capex_pattern?: string;
    recent_capex_commitments?: string[];
  };

  ma_activity?: {
    recent_acquisitions: MAEvent[];
    recent_divestitures: MAEvent[];
  };

  ai_relevant_disclosure?: {
    mentions_in_mda?: string;
    ai_in_risk_factors?: string;
    ai_capex_signals?: string;
    earnings_call_ai_content?: string;
  };

  sources_consulted: Source[];

  confidence: {
    financial_summary: Confidence;
    ai_relevant_disclosure: Confidence;
  };

  reasoning_summary: string;
  audit: AuditMetadata;
};

type MAEvent = {
  name: string;
  date: ISO8601;
  rationale_disclosed?: string;
};

type Source = {
  type: "10-K" | "10-Q" | "8-K" | "annual_report_uk" | "news_article" | "press_release" | "vendor_case_study" | "partner_directory" | "job_posting" | "regulatory_filing" | "other";
  identifier?: string;  // e.g., SEC accession number
  url: string;
  fetched_at: ISO8601;
  fetched_by_agent: string;
};
```

### News research output (B2)

```typescript
type NewsResearch = {
  research_id: UUID;
  prospect_id: UUID;
  research_status: "complete" | "partial" | "no_significant_signals";

  ai_news_signals: AINewsSignal[];
  overall_ai_posture_assessment: string;
  leadership_signals: string;

  date_range_searched: {start: ISO8601; end: ISO8601};
  sources_consulted: Source[];

  confidence: Confidence;
  reasoning_summary: string;
  audit: AuditMetadata;
};

type AINewsSignal = {
  date: ISO8601;
  headline: string;
  summary: string;
  signal_type: "ai_investment" | "leadership_change" | "tech_partnership" | "regulatory" | "customer" | "ma" | "recognition";
  substance_level: "substantive" | "moderate" | "pr_only";
  ai_strategy_implication: string;
  source_url: string;
  source_name: string;
};
```

### Tech stack inference output (B3)

```typescript
type TechStackInference = {
  research_id: UUID;
  prospect_id: UUID;
  research_status: "complete" | "partial" | "low_signal";

  cloud_providers: {
    primary?: {provider: string; evidence: string; confidence_tier: ConfidenceTier};
    secondary: {provider: string; evidence: string; confidence_tier: ConfidenceTier}[];
    multi_cloud_posture: "single" | "multi" | "hybrid" | "unknown";
  };

  data_platforms: PlatformDetected[];
  ai_ml_platforms: PlatformDetected[];

  enterprise_platforms: {
    erp?: string;
    crm?: string;
    itsm?: string;
    hcm?: string;
  };

  ai_talent_signals: {
    ai_role_posting_volume: "high" | "moderate" | "low" | "none_detected";
    ai_role_types: string[];
    compensation_signal: "competitive" | "moderate" | "unknown";
    summary: string;
  };

  open_source_activity: {
    detected: boolean;
    notable_projects: string[];
  };

  strategic_tech_partnerships_disclosed: {
    partner: string;
    nature: string;
    disclosed_date: ISO8601;
  }[];

  sources_consulted: Source[];
  confidence: Confidence;
  reasoning_summary: string;
  audit: AuditMetadata;
};

type ConfidenceTier = "confirmed" | "probable" | "possible" | "not_detected";

type PlatformDetected = {
  platform: string;
  evidence: string;
  confidence_tier: ConfidenceTier;
};
```

### Competitor intelligence output (B4)

```typescript
type CompetitorIntelligence = {
  research_id: UUID;
  prospect_id: UUID;
  research_status: "complete" | "partial";

  competitors: CompetitorAssessment[];
  competitive_landscape_summary: string;
  value_at_risk_signal: "high" | "moderate" | "low";
  value_at_risk_reasoning: string;

  sources_consulted: Source[];
  confidence: Confidence;
  audit: AuditMetadata;
};

type CompetitorAssessment = {
  name: string;
  is_public: boolean;
  ticker?: string;
  relationship_to_prospect: "direct_competitor" | "adjacent_competitor" | "emerging_threat";
  ai_maturity_assessment: {
    tier_estimate: Tier;
    key_signals: {signal: string; date: ISO8601; source: string}[];
    production_ai_evidence: string;
    investment_posture: string;
    summary: string;
  };
};
```

### Regulatory context output (B5)

```typescript
type RegulatoryContext = {
  research_id: UUID;
  prospect_id: UUID;
  research_status: "complete" | "partial";

  applicable_frameworks: RegulatoryFramework[];
  recent_material_developments: RegulatoryDevelopment[];

  sovereign_ai_required: boolean;
  sovereign_ai_reasoning: string;
  high_risk_use_cases_flagged: HighRiskUseCase[];
  overall_regulatory_complexity_rating: "low" | "moderate" | "high" | "very_high";

  sources_consulted: Source[];
  confidence: Confidence;
  audit: AuditMetadata;
};

type RegulatoryFramework = {
  framework_name: string;
  jurisdiction: string;
  scope: "cross_sector" | "sector_specific";
  status: "in_force" | "phased_implementation" | "consultation" | "proposed";
  key_provisions_applicable: string[];
  ai_use_implications: string;
  sovereignty_implications: string;
};

type RegulatoryDevelopment = {
  framework_name: string;
  development_date: ISO8601;
  summary: string;
  implication: string;
  source: string;
};

type HighRiskUseCase = {
  use_case: string;
  reason: string;
  framework_reference: string;
};
```

## Industry library entry (C1 reference)

```typescript
type IndustryLibraryEntry = {
  process_id: string;
  process_name: string;
  tier: "T1_universal" | "T2_vertical_variant" | "T3_industry_native";
  industries_applicable: ("FS" | "HLS" | "MFG" | "All")[];
  industry_specific?: string;  // for T3

  sub_processes: SubProcess[];
  prerequisites: string[];
  typical_outcomes_when_done_well: string;

  // For Discovery handoff
  apr_playbook_reference?: string;  // links to Tier-X playbook in APR library

  audit: AuditMetadata;
};

type SubProcess = {
  sub_process_name: string;
  value_pocket_sizing: "large" | "medium" | "small";
  reinvention_archetype: "accelerate" | "restructure" | "retire" | "invent";
  ai_pattern_description: string;
};
```

### C1 output (per prospect)

```typescript
type IndustryLibraryApplication = {
  application_id: UUID;
  prospect_id: UUID;
  library_status: "full_coverage" | "partial_coverage" | "tier1_only";
  industry_match: "exact" | "adjacent" | "not_in_library";

  applicable_processes: IndustryLibraryEntry[];
  coverage_gaps: string;
  confidence: Confidence;

  audit: AuditMetadata;
};
```

## Synthesis output (C2 — analytical heart)

```typescript
type SynthesisOutput = {
  synthesis_id: UUID;
  prospect_id: UUID;

  overall_score: number;  // 0-100
  overall_tier: Tier;
  dimension_scores: DimensionScores;

  findings: Finding[];
  value_difficulty_mapping: ValueDifficultyMapping[];

  recommended_next_step: RecommendedNextStep;
  partner_attention_flags: PartnerAttentionFlag[];

  reasoning_trace: string;
  audit: AuditMetadata;
};

type DimensionScores = Record<DimensionId, DimensionScore>;

type DimensionScore = {
  score: number;  // 0-100
  tier: Tier;
  questionnaire_derived: number;
  research_adjustment: number;
  reasoning: string;
  confidence: Confidence;
  note?: string;  // e.g., "informational" for regulatory_complexity
};

type Finding = {
  finding_id: string;
  headline: string;
  body: string;
  supporting_signals: string[];
  decision_relevance: "high" | "medium" | "low";
  confidence: Confidence;
};

type ValueDifficultyMapping = {
  opportunity: string;
  process_id_ref: string;  // references IndustryLibraryEntry
  value_score: number;  // 0.0-1.0
  difficulty_score: number;  // 0.0-1.0
  quadrant: "high_value_low_difficulty" | "high_value_high_difficulty" | "low_value_low_difficulty" | "low_value_high_difficulty";
  reasoning: string;
};

type RecommendedNextStep = {
  engagement_type: "APR Discovery (scoped)" | "Foundation work first" | "Not currently a candidate";
  scope_specifics: string;
  duration_estimate_weeks: string;
  expected_deliverable: string;
  rationale: string;
  framing_persona: Persona;
  confidence: Confidence;
};

type PartnerAttentionFlag = {
  area: string;
  reason: string;
};
```

## Quick wins output (C3)

```typescript
type QuickWinsOutput = {
  output_id: UUID;
  prospect_id: UUID;

  selected_quick_wins: SelectedQuickWin[];
  patterns_considered_and_rejected: {pattern_id: string; reason_rejected: string}[];
  library_coverage_gaps: string;
  overall_confidence: Confidence;

  audit: AuditMetadata;
};

type SelectedQuickWin = {
  pattern_id: string;  // references QuickWinPattern
  pattern_name: string;
  selection_confidence: Confidence;
  selection_reasoning: string;
  prospect_specific_framing: {
    what_this_would_do: string;
    prerequisites_satisfied: PrerequisiteCheck[];
    expected_outcome_range: string;
    timeline_to_value: string;
  };
  ordering_priority: 1 | 2 | 3;
};

type PrerequisiteCheck = {
  prerequisite: string;
  evidence: string;
  satisfied: boolean | "likely";
};

// Static reference (library content)
type QuickWinPattern = {
  pattern_id: string;
  name: string;
  one_line_description: string;
  what_the_ai_does: string;
  prerequisites: string[];
  expected_outcomes: string;
  implementation_effort: "Low" | "Medium";
  timeline_to_value_weeks: string;
  applicable_industries: ("FS" | "HLS" | "MFG" | "All")[];
  applicable_sizes: SizeBand[];
  disqualifying_conditions: string[];
  peer_examples: string[];
};
```

## Output artifacts (D1)

```typescript
type ScorecardOutput = {
  output_id: UUID;
  prospect_id: UUID;

  scorecard: ScorecardContent;
  quick_wins_memo: QuickWinsMemoContent;
  findings_appendix: FindingsAppendixContent;

  metadata: {
    persona_framing_applied: Persona;
    voice_check_passed: boolean;
    confidence: Confidence;
  };

  // Rendered artifacts (populated after PDF rendering)
  rendered_artifacts?: {
    scorecard_pdf_url?: string;
    quick_wins_memo_pdf_url?: string;
    findings_appendix_pdf_url?: string;
    web_view_url?: string;
  };

  audit: AuditMetadata;
};

type ScorecardContent = {
  header: {title: "AI READINESS DIAGNOSTIC"; company_name: string; assessment_date: ISO8601};
  overall_summary: {tier_label: Tier; overall_score: number; peer_reference?: string};
  dimension_chart_data: {dimension: string; score: number; tier: Tier; tier_color: string}[];
  headline_findings: {finding_id: string; headline: string; body: string}[];
  recommended_next_step: {
    headline: "RECOMMENDED NEXT STEP";
    body: string;
    contact: {name: string; title: string; email: string};
  };
  quick_wins_indicator: {
    header: "90-DAY QUICK WINS";
    items: {pattern_name: string; one_line: string}[];
  };
};

type QuickWinsMemoContent = {
  header: string;
  intro_paragraph: string;
  pattern_cards: {
    pattern_name: string;
    one_line_description: string;
    what_this_would_do: string;
    prerequisites_you_have: string[];
    expected_outcome_range: string;
    timeline_to_value: string;
  }[];
  footer_contact: string;
};

type FindingsAppendixContent = {
  cover: {title: string; company_name: string; contents_list: string[]};
  methodology_note: string;
  dimension_details: DimensionDetail[];
  sources_consulted: Source[];
};

type DimensionDetail = {
  dimension: DimensionId;
  dimension_label: string;
  score: number;
  tier: Tier;
  what_this_dimension_captures: string;
  your_score_reasoning: string;
  questionnaire_signals: string;
  research_signals: string;
  peer_comparison?: string;
  what_strong_looks_like: string;
  actions_to_improve: string[];
};
```

## Validation output (D2)

```typescript
type ValidationOutput = {
  validation_id: UUID;
  prospect_id: UUID;
  scorecard_output_id: UUID;

  validation_summary: {
    overall_validation_status: "passed" | "passed_with_flags" | "requires_revision";
    critical_flags_count: number;
    high_flags_count: number;
    medium_flags_count: number;
    low_flags_count: number;
  };

  flags: ValidationFlag[];
  confidence_adjustments_recommended: ConfidenceAdjustment[];

  partner_review_priority: "expedited" | "standard" | "deferred";
  auto_revision_eligible: boolean;
  reasoning_summary: string;

  audit: AuditMetadata;
};

type ValidationFlag = {
  flag_id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  category: "fact_grounding" | "internal_consistency" | "numerical_sanity" | "hallucination_pattern" | "confidence_calibration" | "voice_copyright";
  location_in_output: string;
  concern: string;
  supporting_evidence: string;
  recommendation: string;
};

type ConfidenceAdjustment = {
  output_field: string;
  current_confidence: number;
  recommended_confidence: number;
  reason: string;
};
```

## Partner review record

Captures the human partner's actions during review. Used both for delivery approval and for DXC value driver 5 (partner training).

```typescript
type PartnerReviewRecord = {
  review_id: UUID;
  prospect_id: UUID;
  scorecard_output_id: UUID;
  validation_output_id: UUID;
  partner_id: UUID;

  review_started_at: ISO8601;
  review_completed_at: ISO8601;
  review_duration_seconds: number;

  partner_actions: PartnerAction[];

  final_disposition: "approved" | "sent_back_for_reprocessing" | "manually_revised_and_approved" | "rejected";
  partner_notes: string;

  // Training capture
  training_signals: TrainingSignal[];

  audit: AuditMetadata;
};

type PartnerAction =
  | {type: "field_adjustment"; field_path: string; original_value: string; new_value: string; reason?: string}
  | {type: "finding_added"; finding: Finding; reason?: string}
  | {type: "finding_removed"; finding_id: string; reason?: string}
  | {type: "framing_change"; field_path: string; original: string; new: string}
  | {type: "send_back"; reason: string};

type TrainingSignal = {
  signal_type: "adjustment_pattern" | "framing_preference" | "industry_calibration" | "persona_calibration";
  description: string;
  category_tags: string[];
};
```

## Downstream value capture (E-agents)

### Cross-practice routing (E1 output)

```typescript
type CrossPracticeRouting = {
  routing_id: UUID;
  prospect_id: UUID;
  routing_status: "completed" | "skipped_no_consent" | "no_opportunities_detected";
  consent_basis: string;

  opportunity_records: PracticeOpportunityRecord[];
  audit_trail_record: {
    prospect_id: UUID;
    consent_state_at_routing: string;
    routing_timestamp: ISO8601;
    practices_notified: string[];
  };

  audit: AuditMetadata;
};

type PracticeOpportunityRecord = {
  opportunity_id: UUID;
  practice_target: "Data services" | "Cybersecurity" | "CES" | "GIS" | "Cloud services" | "other";
  opportunity_headline: string;
  opportunity_description: string;
  confidence: Confidence;
  underlying_signals: string[];
  recommended_practice_action: string;
  diagnostic_reference_id: UUID;
  delivered_to_practice_crm: boolean;
  practice_crm_record_id?: string;
};
```

### Benchmark contribution (E2 output)

```typescript
type BenchmarkContribution = {
  contribution_id: UUID;
  prospect_id: UUID;  // stored only in audit trail, not in benchmark record
  contribution_status: "completed" | "skipped_opted_out";

  // The actual benchmark record (stored separately from prospect data)
  benchmark_record?: BenchmarkRecord;

  audit_trail_record_stored_separately: {
    prospect_id: UUID;
    benchmark_anonymous_id?: UUID;
    contribution_timestamp: ISO8601;
    consent_state: string;
  };

  audit: AuditMetadata;
};

// Stored in benchmark library; no link back to prospect except via separate audit trail
type BenchmarkRecord = {
  anonymous_id: UUID;
  industry_classification: Industry;
  geography: string;  // country level only
  size_band: SizeBand;
  revenue_bucket: string;  // range only
  employee_band: string;  // range only
  submission_quarter: string;  // e.g., "Q2_2026"

  dimension_scores: Record<DimensionId, number>;
  identified_value_pockets: string[];  // anonymized
  recommended_next_step_category: string;  // category only

  contribution_audit: {
    contributed_at: ISO8601;
    consent_record_reference: string;
  };
};
```

### Internal AI feedstock (E3 output)

```typescript
type FeedstockOutput = {
  feedstock_id: UUID;
  prospect_id: UUID;
  feedstock_status: "completed" | "skipped_opted_out";
  consent_basis: string;

  routed_records: FeedstockRecord[];
  audit_trail: {
    prospect_id: UUID;
    consent_state: string;
    tools_notified: string[];
  };

  audit: AuditMetadata;
};

type FeedstockRecord = {
  target_tool: "AxisAI" | "AxisMIND" | "agentic_context_fabric" | "playbook_library_queue" | "XAES_calibration";
  record_type: "analytical_pattern" | "governance_pattern" | "industry_process_pattern" | "workforce_pattern";
  record_content: unknown;  // tool-specific schema
  anonymization_level: "external_strict" | "internal_extended";
  feedstock_timestamp: ISO8601;
  acknowledgment_from_target?: {received_at: ISO8601; record_id_at_target: string};
};
```

## Audit log

System-wide audit log capturing all significant events.

```typescript
type AuditLogEntry = {
  entry_id: UUID;
  timestamp: ISO8601;
  prospect_id?: UUID;

  event_type:
    | "submission_received"
    | "agent_invoked"
    | "agent_completed"
    | "agent_failed"
    | "validation_completed"
    | "partner_review_assigned"
    | "partner_action_recorded"
    | "scorecard_delivered"
    | "consent_changed"
    | "downstream_routing_completed"
    | "error"
    | "manual_intervention";

  actor: string;  // agent ID or user ID
  description: string;
  metadata: Record<string, unknown>;  // event-specific structured data

  severity: "info" | "warning" | "error" | "critical";
};
```

## Entity relationships

The Diagnostic data model can be summarized as follows:

```
Prospect (1)
  ├── ConsentRecord (1+ over time)
  ├── PersonaInference (1)
  ├── PersonalizedQuestionnaire (1)
  │     └── QuestionnaireResponse (1)
  ├── Research Outputs (1 each)
  │     ├── FinancialResearch (B1)
  │     ├── NewsResearch (B2)
  │     ├── TechStackInference (B3)
  │     ├── CompetitorIntelligence (B4) [V1+]
  │     └── RegulatoryContext (B5) [V1.5+]
  ├── IndustryLibraryApplication (C1)
  ├── SynthesisOutput (C2)
  ├── QuickWinsOutput (C3)
  ├── ScorecardOutput (D1)
  ├── ValidationOutput (D2)
  ├── PartnerReviewRecord (1)
  └── Downstream (conditional on consent)
        ├── CrossPracticeRouting (E1) [V1+, conditional on C4]
        ├── BenchmarkContribution (E2) [V1+, conditional on C2]
        └── FeedstockOutput (E3) [V1+, conditional on C3]

Static References (not per-prospect):
  ├── QuestionPoolEntry (~20 entries)
  ├── QuickWinPattern (~15 entries)
  └── IndustryLibraryEntry (growing library)

System-wide:
  └── AuditLogEntry (every event)
```

## Storage recommendations

**Prospect-keyed entities** (prospect record, questionnaires, responses, outputs, reviews): standard relational store with prospect_id as foreign key. PostgreSQL recommended. Allows transactional consistency and query flexibility.

**Benchmark records** (E2 output): separate logical store from prospect data. Same database is acceptable but separate schema with no foreign key to prospects table. Anonymous IDs only. Allows independent access control and easier productization in V2.

**Audit log**: append-only store. Could be the same database with a partitioned audit_log table, or a dedicated event store. Retention per legal review.

**Static references** (question pool, quick wins library, industry library): managed as versioned content in source control with database materialization. Allows working group iteration outside engineering deployment cycle.

**Rendered artifacts** (PDFs, web views): object storage (S3 or equivalent) with secure access URLs. Linked from ScorecardOutput by URL reference.

## Migration and versioning

Schema evolution will happen. The strategy:

- **Backward-compatible additions**: new optional fields can be added freely
- **Backward-incompatible changes**: bump entity version; provide migration; document the change in working group decision log
- **Static reference content updates** (e.g., new questions added to pool): increment content version; agents reference content by version to support reproducibility of historical scorecards

Critical for partner review: a historical scorecard's reasoning must be reproducible. The schema captures enough context (which agent versions ran, which content versions were used) to support this.

---

*Companion documents: see Companion_01 through Companion_04 for the structures these schemas represent. Together, the five companion documents constitute the V0 build specification consumable by Claude Code.*
