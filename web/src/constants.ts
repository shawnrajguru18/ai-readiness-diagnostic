console.log('[CONSTANTS] Loading constants.ts file')

import { Scorecard } from './types'

export const API = '' // empty string = same origin (production)
console.log('[CONSTANTS] API =', API)

export const ELEVENLABS_AGENT_ID = 'agent_0501kz1wxj5pfe39krrt9nbej8mr'

export const DXC_PATH = 'M220.055 60.7583C252.905 60.7583 279.643 87.4387 279.644 120.247C279.644 153.055 252.905 179.735 220.055 179.735H61V155.455H220.055C239.522 155.455 255.362 139.657 255.362 120.247C255.362 100.836 239.522 85.0396 220.055 85.0396H61V60.7583H220.055ZM798 85.0386H638.945C619.478 85.0386 603.638 100.836 603.638 120.247C603.638 139.657 619.478 155.454 638.945 155.454H798V179.735H638.945C606.08 179.735 579.357 153.054 579.356 120.247C579.356 87.4387 606.095 60.7573 638.945 60.7573H798V85.0386ZM556.104 85.0386C530.11 85.0387 511.856 96.5366 492.531 108.706C486.261 112.662 479.906 116.647 473.278 120.204C479.905 123.76 486.261 127.744 492.531 131.701C511.856 143.87 530.11 155.368 556.104 155.368V179.649C523.097 179.649 499.987 165.095 479.591 152.254C462.637 141.585 447.997 132.358 430.058 132.358C412.118 132.358 397.478 141.571 380.524 152.254C360.128 165.095 337.018 179.649 304.011 179.649V155.368C330.006 155.368 348.259 143.87 367.584 131.701C373.854 127.744 380.211 123.76 386.838 120.204C380.211 116.647 373.854 112.662 367.584 108.706C348.259 96.5366 330.006 85.0386 304.011 85.0386V60.7573C337.018 60.7573 360.128 75.3119 380.524 88.1665C397.478 98.8358 412.118 108.063 430.058 108.063V108.048C447.997 108.048 462.637 98.8364 479.591 88.1528C499.987 75.3125 523.097 60.7575 556.104 60.7573V85.0386Z'

export const TIER_COLOR: Record<string, string> = {
  Emerging: '#FFC982',
  Developing: '#FFAE41',
  Established: '#A1E6FF',
  Leading: '#4995FF',
}

export const QUAD_LABEL: Record<string, string> = {
  high_value_low_difficulty: 'quick win',
  high_value_high_difficulty: 'strategic bet',
  low_value_low_difficulty: 'fill-in',
  low_value_high_difficulty: 'deprioritize',
}

export const INDUSTRY_LABELS: Record<string, string> = {
  FS: 'Financial services',
  HLS: 'Healthcare and life sciences',
  MFG: 'Manufacturing',
  All: 'Other / cross-industry',
}

export const DEMO_SCORECARD: Scorecard = {
  company_name: 'MeridianFS Holdings, Inc.',
  industry_label: 'Financial services',
  assessment_date: '14 June 2026',
  reviewed_by: 'DXC AdvisoryX',
  overall_score: 55,
  overall_tier: 'Developing',
  overall_color: '#FFAE41',
  peer_reference: 'Peer average for large US financial services: 58 (n=42)',
  peer_benchmarks: {
    data_foundation: 62,
    governance_posture: 60,
    ai_investment_maturity: 55,
    org_change_readiness: 54,
    value_pocket_clarity: 56,
    regulatory_complexity: 62,
  },
  dimensions: [
    {
      dimension: 'data_foundation',
      label: 'Data Foundation',
      score: 52,
      tier: 'Developing',
      color: '#FFAE41',
      informational: false,
    },
    {
      dimension: 'governance_posture',
      label: 'Governance Posture',
      score: 38,
      tier: 'Emerging',
      color: '#FFC982',
      informational: false,
    },
    {
      dimension: 'ai_investment_maturity',
      label: 'AI Investment Maturity',
      score: 62,
      tier: 'Established',
      color: '#A1E6FF',
      informational: false,
    },
    {
      dimension: 'org_change_readiness',
      label: 'Organizational Change Readiness',
      score: 55,
      tier: 'Developing',
      color: '#FFAE41',
      informational: false,
    },
    {
      dimension: 'value_pocket_clarity',
      label: 'Value-Pocket Clarity',
      score: 48,
      tier: 'Developing',
      color: '#FFAE41',
      informational: false,
    },
    {
      dimension: 'regulatory_complexity',
      label: 'Regulatory Complexity',
      score: 72,
      tier: 'Established',
      color: '#A1E6FF',
      informational: true,
    },
  ],
  findings: [
    {
      finding_id: 'F1',
      headline: 'Substantial experimentation, weak production conversion',
      body: 'MeridianFS has launched 15+ AI initiatives over 24 months, but the production conversion rate trails large-FS peers by approximately 30%. The gap concentrates in initiatives that lacked clear value-pocket definition at scoping.',
    },
    {
      finding_id: 'F2',
      headline: 'Governance is the largest dimensional gap',
      body: 'AI risk ownership is distributed across CISO, Compliance, and Legal without an integrating accountability layer. FCA AI guidance interpretation is underway but not operationalized.',
    },
    {
      finding_id: 'F3',
      headline: 'Operational processes are the strongest near-term path',
      body: 'AP, IT incident management, and customer support already show measurable AI value in production. Scaling these patterns horizontally is a high-confidence path.',
    },
  ],
  recommended_next_step: {
    body: 'APR Discovery engagement focused on claims adjudication reinvention and operational AI scaling. The Discovery would size value pockets across claims sub-processes, design governance integration, and produce a board-ready 18-month roadmap.',
    duration_estimate_weeks: '6-10 weeks',
    contact_name: 'DXC AdvisoryX',
    contact_title: '',
    contact_email: 'advisoryx@dxc.com',
  },
  quick_wins: [
    {
      pattern_name: 'Intelligent Invoice Triage',
      one_line_description:
        'AI categorizes and routes invoice exceptions, reducing manual AP workload.',
      what_this_would_do:
        'Auto-resolve routine AP exceptions and route complex cases with context, freeing the AP team for vendor management.',
      prerequisites_you_have: [
        'AP system with structured exception logging',
        '6+ months of exception history',
      ],
      expected_outcome_range: 'AP exception handling time -40-60%',
      timeline_to_value: '8-10 weeks',
      implementation_effort: 'Low',
    },
    {
      pattern_name: 'IT Incident Auto-Categorization',
      one_line_description:
        'AI categorizes IT incidents, assigns severity, routes to the right tier.',
      what_this_would_do:
        'Cut mean-time-to-assignment and lift tier-1 deflection across your ServiceNow estate.',
      prerequisites_you_have: ['ITSM system', 'Service catalog documented'],
      expected_outcome_range: 'Mean time to assignment -60-80%',
      timeline_to_value: '6-10 weeks',
      implementation_effort: 'Low',
    },
    {
      pattern_name: 'Compliance Document Review',
      one_line_description:
        'AI reads regulatory documents and flags compliance issues for review.',
      what_this_would_do:
        'Lift compliance review coverage of customer communications while catching more issues, directly addressing the governance gap.',
      prerequisites_you_have: ['Document management system', 'Internal policy library'],
      expected_outcome_range: 'Issue detection +30-50%',
      timeline_to_value: '10-14 weeks',
      implementation_effort: 'Medium',
    },
  ],
  executive_narrative: {
    headline:
      'MeridianFS is at the Developing stage: real experimentation, with governance posture the constraint on scaling to production.',
    paragraphs: [
      'MeridianFS Holdings, Inc. is at the Developing stage of AI readiness, scoring 55 of 100, 2 points behind the peer average of 57. The priority now is turning experimentation into dependable production capability.',
      'AI Investment Maturity (62 of 100) is the most production-ready part of your estate, and the natural place to scale a proven pattern horizontally.',
      'Governance Posture (38 of 100) is the binding constraint on scaling safely. Addressing it is prerequisite, not parallel work.',
      'In the next 90 days, Intelligent Invoice Triage, IT Incident Auto-Categorization, and Compliance Document Review are high-confidence patterns with documented enterprise deployments that fit your current architecture and prove delivery.',
      'The next step is an APR Discovery focused on claims adjudication reinvention and operational AI scaling. Over 6-10 weeks it scopes the build sequence and governance design to close the gap and put value pockets into production.',
    ],
  },
  value_difficulty: [
    {
      opportunity: 'Intelligent Invoice Triage',
      value_score: 0.7,
      difficulty_score: 0.3,
      quadrant: 'high_value_low_difficulty',
    },
    {
      opportunity: 'IT Incident Auto-Categorization',
      value_score: 0.7,
      difficulty_score: 0.3,
      quadrant: 'high_value_low_difficulty',
    },
    {
      opportunity: 'Compliance Document Review',
      value_score: 0.7,
      difficulty_score: 0.6,
      quadrant: 'high_value_high_difficulty',
    },
    {
      opportunity: 'Close the governance posture gap',
      value_score: 0.9,
      difficulty_score: 0.7,
      quadrant: 'high_value_high_difficulty',
    },
  ],
}
