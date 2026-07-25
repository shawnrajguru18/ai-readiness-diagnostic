import { Wordmark } from '@/components/Wordmark'
import { Scorecard as ScorecardType } from '@/types'

interface QuickWinsProps {
  sc: ScorecardType
  onBack: () => void
  onHome: () => void
}

export function QuickWins({ sc, onBack, onHome }: QuickWinsProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="max-w-4xl mx-auto px-8 py-6 flex justify-between items-center">
        <button onClick={onHome} title="Back to start" className="hover:opacity-70 transition">
          <Wordmark />
        </button>
        <div className="flex items-center gap-5">
          <button onClick={onBack} className="text-sm text-royal font-semibold hover:underline">
            ← Back to scorecard
          </button>
          <button onClick={onHome} className="text-sm text-ink hover:text-royal">
            ↺ New assessment
          </button>
        </div>
      </div>
      <div className="max-w-4xl mx-auto px-8 pb-24">
        <div className="text-xs uppercase tracking-widest" style={{ color: '#9a6a00' }}>
          90-day quick wins
        </div>
        <h1 className="display text-4xl font-extrabold mt-1">{sc.company_name}</h1>
        <p className="text-ink mt-3 max-w-2xl">
          Quick wins are AI patterns you can put in production in 90 days or less. Each has
          documented enterprise deployments with measurable results. They build momentum and prove
          execution capacity while the strategic roadmap takes shape through Discovery.
        </p>
        <div className="grid md:grid-cols-3 gap-5 mt-8">
          {sc.quick_wins.map((q, k) => (
            <div key={k} className="bg-white rounded-2xl border border-black/10 p-6">
              <span className="w-2.5 h-2.5 bg-royal inline-block mb-3"></span>
              <h3 className="display text-xl font-bold">{q.pattern_name}</h3>
              <p className="text-sm italic text-ink mt-1">{q.one_line_description}</p>
              <p className="text-sm mt-4">
                <b>What this would do:</b> {q.what_this_would_do}
              </p>
              <p className="text-sm mt-3 font-semibold">Prerequisites you have:</p>
              <ul className="text-sm text-ink mt-1 space-y-1">
                {(q.prerequisites_you_have || []).map((p, j) => (
                  <li key={j}>✓ {p}</li>
                ))}
              </ul>
              <div className="mt-4 text-sm">
                <b>Expected outcome:</b> {q.expected_outcome_range}
              </div>
              <div className="mt-1 text-sm">
                <b>Timeline:</b> {q.timeline_to_value} · <b>Effort:</b> {q.implementation_effort}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
