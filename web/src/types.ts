export interface Dimension {
  dimension: string
  label: string
  score: number
  tier: 'Emerging' | 'Developing' | 'Established' | 'Leading'
  color: string
  informational?: boolean
}

export interface QuickWin {
  pattern_name: string
  one_line_description: string
  what_this_would_do: string
  prerequisites_you_have: string[]
  expected_outcome_range: string
  timeline_to_value: string
  implementation_effort: string
}

export interface Finding {
  finding_id: string
  headline: string
  body: string
}

export interface RecommendedNextStep {
  body: string
  duration_estimate_weeks: string
  contact_name: string
  contact_title: string
  contact_email: string
}

export interface ValueDifficultyItem {
  opportunity: string
  value_score: number
  difficulty_score: number
  quadrant: 'high_value_low_difficulty' | 'high_value_high_difficulty' | 'low_value_low_difficulty' | 'low_value_high_difficulty'
}

export interface ExecutiveNarrative {
  headline: string
  paragraphs: string[]
}

export interface Scorecard {
  id?: string
  company_name: string
  industry_label: string
  assessment_date: string
  reviewed_by: string
  overall_score: number
  overall_tier: 'Emerging' | 'Developing' | 'Established' | 'Leading'
  overall_color: string
  peer_reference: string
  peer_benchmarks: Record<string, number>
  dimensions: Dimension[]
  findings: Finding[]
  recommended_next_step: RecommendedNextStep
  quick_wins: QuickWin[]
  value_difficulty?: ValueDifficultyItem[]
  executive_narrative?: ExecutiveNarrative
}

export interface Question {
  id: string
  dimension: string
  text: string
  type: 'single_select' | 'scale_1_5' | 'multi_select' | 'open_short'
  options?: Array<{ id: string; text: string }>
  scale_anchors?: Array<{ value: number; text: string }>
  open_answer_max_chars?: number
  skip_if?: { question: string; answer_in: string[] }
  branch_if?: { question: string; answer_in: string[] }
}

export interface QuestionPool {
  questions: Question[]
  dimensions: Record<string, { label: string }>
}

export interface Answer {
  option_id?: string
  option_ids?: string[]
  scale_value?: number
  text?: string
}

export interface FormData {
  prospect_name: string
  prospect_role: string
  prospect_email: string
  company_name_raw: string
  industry_tag: string
  industry_label: string
  size_band: string
}

export interface ConsentData {
  c2_anonymized_benchmark: boolean
  c4_cross_practice_sharing: boolean
}
