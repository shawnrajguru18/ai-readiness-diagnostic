import { Wordmark } from '@/components/Wordmark'
import { TierBadge } from '@/components/TierBadge'
import { Radar } from '@/components/Radar'
import { ValueDifficulty2x2 } from '@/components/ValueDifficulty2x2'
import { Scorecard as ScorecardType } from '@/types'

interface ScorecardProps {
  sc: ScorecardType
  onQuickWins: () => void
  onHome: () => void
}

export function Scorecard({ sc, onQuickWins, onHome }: ScorecardProps) {
  const graded = sc.dimensions.filter((d) => !d.informational)
  const strongest = graded.length ? graded.reduce((a, b) => (b.score > a.score ? b : a)) : null
  const weakest = graded.length ? graded.reduce((a, b) => (b.score < a.score ? b : a)) : null

  const summary =
    `${sc.company_name} is at the ${sc.overall_tier} stage of AI readiness, scoring ${sc.overall_score} of 100.` +
    (strongest && weakest
      ? ` The strongest dimension is ${strongest.label}; the priority gap is ${weakest.label}.`
      : '')

  return (
    <div className="min-h-screen bg-canvas">
      <div className="max-w-5xl mx-auto px-8 py-6 flex justify-between items-center">
        <button onClick={onHome} title="Back to start" className="hover:opacity-70 transition">
          <Wordmark />
        </button>
        <div className="flex items-center gap-5">
          <span className="text-xs text-ink uppercase tracking-widest hidden sm:inline">
            Prepared for {sc.company_name}
          </span>
          <button onClick={onHome} className="text-sm font-semibold text-royal hover:underline">
            ↺ New assessment
          </button>
        </div>
      </div>
      <div className="max-w-5xl mx-auto px-8 pb-24">
        <div className="bg-white rounded-2xl border border-black/10 border-t-4 border-t-royal p-8 fade">
          <div className="flex flex-wrap justify-between items-start gap-6">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-royal font-bold">
                AI Readiness Diagnostic
              </div>
              <h1 className="display text-5xl font-extrabold mt-2 leading-none">
                {sc.company_name}
              </h1>
              <div className="text-sm text-ink mt-3">
                {sc.industry_label} · {sc.assessment_date}
              </div>
              <div className="text-sm text-midnight mt-1 flex items-center gap-1.5">
                <span className="text-royal font-bold">✓</span> Reviewed by{' '}
                <b>DXC AdvisoryX</b>
              </div>
            </div>
            <div className="text-right">
              <div className="mb-2">
                <TierBadge tier={sc.overall_tier} />
              </div>
              <div className="display text-7xl font-extrabold leading-none">
                {sc.overall_score}
                <span className="text-2xl font-normal text-ink"> /100</span>
              </div>
              <div className="text-xs text-ink mt-2 max-w-[230px] ml-auto">{sc.peer_reference}</div>
            </div>
          </div>
          <p className="mt-6 pt-5 border-t border-black/10 text-[15px] leading-relaxed">
            {summary}
          </p>
        </div>

        {sc.executive_narrative?.paragraphs && sc.executive_narrative.paragraphs.length > 0 && (
          <div className="mt-6 bg-white rounded-2xl border border-black/10 p-7 fade">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-2.5 h-2.5 bg-royal inline-block"></span>
              <h2 className="text-xs font-bold uppercase tracking-widest">Executive summary</h2>
            </div>
            {sc.executive_narrative.headline && (
              <p className="display text-2xl font-bold leading-snug mb-4">
                {sc.executive_narrative.headline}
              </p>
            )}
            <div className="space-y-3 text-[15px] leading-relaxed text-midnight">
              {sc.executive_narrative.paragraphs.map((t, k) => (
                <p key={k}>{t}</p>
              ))}
            </div>
          </div>
        )}

        {sc.id && (
          <div className="mt-5 bg-white rounded-2xl border border-black/10 p-5 flex flex-wrap items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-widest text-ink mr-1">
              Your report
            </span>
            <a
              download={`AI-Readiness-Scorecard-${sc.company_name}.pdf`}
              href={`/api/scorecard/${sc.id}/pdf`}
              className="px-4 py-2 rounded-lg bg-royal text-white text-sm font-semibold hover:bg-[#003a86]"
            >
              ⬇ Scorecard PDF
            </a>
            <a
              download={`Board-Brief-${sc.company_name}.pdf`}
              href={`/api/scorecard/${sc.id}/board-brief.pdf`}
              className="px-4 py-2 rounded-lg bg-white border border-midnight/20 text-sm font-semibold hover:border-royal hover:text-royal"
            >
              ⬇ Board brief
            </a>
            <a
              download={`90-Day-Action-Plan-${sc.company_name}.pdf`}
              href={`/api/scorecard/${sc.id}/action-plan.pdf`}
              className="px-4 py-2 rounded-lg bg-white border border-midnight/20 text-sm font-semibold hover:border-royal hover:text-royal"
            >
              ⬇ 90-day action plan
            </a>
            <a
              download={`Quick-Wins-Memo-${sc.company_name}.pdf`}
              href={`/api/scorecard/${sc.id}/quickwins.pdf`}
              className="px-4 py-2 rounded-lg bg-white border border-midnight/20 text-sm font-semibold hover:border-royal hover:text-royal"
            >
              ⬇ Quick-wins memo
            </a>
            <a
              download={`Findings-Appendix-${sc.company_name}.pdf`}
              href={`/api/scorecard/${sc.id}/appendix.pdf`}
              className="px-4 py-2 rounded-lg bg-white border border-midnight/20 text-sm font-semibold hover:border-royal hover:text-royal"
            >
              ⬇ Findings appendix
            </a>
          </div>
        )}
        {!sc.id && (
          <div className="mt-5 text-sm text-ink bg-white rounded-2xl border border-dashed border-black/20 p-4">
            Sample preview. Complete an assessment to generate your downloadable report — scorecard,
            board brief, 90-day action plan, quick-wins memo, and findings appendix.
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-8 items-center mt-8 bg-white rounded-2xl border border-black/10 p-6">
          <div className="flex justify-center">
            <Radar dims={sc.dimensions} color={sc.overall_color} />
          </div>
          <div className="space-y-3">
            {sc.dimensions.map((d) => {
              const peer = sc.peer_benchmarks?.[d.dimension]
              const diff = peer != null ? d.score - peer : null
              const dcol =
                diff! > 0 ? '#1f9d55' : diff === 0 ? '#8A867E' : '#c0392b'
              return (
                <div key={d.dimension}>
                  <div className="flex justify-between text-sm font-semibold">
                    <span>
                      {d.label}
                      {d.informational && (
                        <span className="text-ink font-normal"> · informational</span>
                      )}
                    </span>
                    <span>
                      {d.score} ·{' '}
                      <span style={{ color: '#0E1020' }}>{d.tier}</span>
                      {peer != null && !d.informational && (
                        <span style={{ color: dcol }}>
                          {' '}
                          · vs peer {peer} ({diff! > 0 ? '+' : ''}
                          {diff})
                        </span>
                      )}
                    </span>
                  </div>
                  <div className="relative h-2 bg-black/10 rounded mt-1">
                    <div
                      className="h-full rounded"
                      style={{ width: `${d.score}%`, background: d.color }}
                    />
                    {peer != null && (
                      <span
                        className="absolute top-[-2px] bottom-[-2px] w-0.5 bg-midnight rounded"
                        style={{ left: `${peer}%` }}
                        title={`peer average ${peer}`}
                      />
                    )}
                  </div>
                </div>
              )
            })}
            <div className="text-[11px] text-ink flex items-center gap-1.5 pt-1">
              <span className="inline-block w-0.5 h-2.5 bg-midnight" /> peer average · {sc.peer_reference}
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white rounded-2xl border border-black/10 p-7">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2.5 h-2.5 bg-royal inline-block"></span>
            <h2 className="text-xs font-bold uppercase tracking-widest">What we found</h2>
          </div>
          <ol className="space-y-4">
            {sc.findings.map((f, k) => (
              <li key={f.finding_id} className="flex gap-3">
                <span className="font-bold text-royal">{k + 1}</span>
                <span className="text-[15px] leading-relaxed">
                  <b>{f.headline}.</b> {f.body}
                </span>
              </li>
            ))}
          </ol>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <div className="bg-white rounded-2xl border-l-4 border-royal p-6">
            <h2 className="text-xs font-bold uppercase tracking-widest text-royal mb-2">
              Recommended next step
            </h2>
            <p className="text-[15px] leading-relaxed">{sc.recommended_next_step.body}</p>
            <p className="text-sm text-ink mt-3">
              Duration: {sc.recommended_next_step.duration_estimate_weeks}.
            </p>
            <a
              href={`mailto:${sc.recommended_next_step.contact_email}?subject=${encodeURIComponent(
                'AI Readiness Diagnostic — ' + sc.company_name
              )}`}
              className="inline-block mt-4 px-5 py-2.5 rounded-lg bg-royal text-white text-sm font-semibold hover:bg-[#003a86]"
            >
              Continue the conversation →
            </a>
            <div className="text-xs text-ink mt-2">
              {sc.recommended_next_step.contact_name} ·{' '}
              {sc.recommended_next_step.contact_email}
            </div>
          </div>
          <div className="bg-white rounded-2xl border border-black/10 p-6">
            <h2 className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9a6a00' }}>
              90-day quick wins
            </h2>
            <ul className="space-y-2">
              {sc.quick_wins.map((q, k) => (
                <li key={k} className="text-sm">
                  <b>{q.pattern_name}</b> — {q.one_line_description}{' '}
                  <span className="text-ink">({q.timeline_to_value})</span>
                </li>
              ))}
            </ul>
            <button
              onClick={onQuickWins}
              className="mt-4 text-royal font-semibold hover:underline text-sm"
            >
              View full quick wins memo →
            </button>
          </div>
        </div>

        {sc.value_difficulty && sc.value_difficulty.length > 0 && (
          <div className="mt-6 bg-white rounded-2xl border border-black/10 p-7">
            <h2 className="text-xs font-bold uppercase tracking-widest mb-1">
              Opportunity map · value vs difficulty
            </h2>
            <p className="text-sm text-ink mb-5">
              Where each opportunity sits by business value and effort to implement.
            </p>
            <ValueDifficulty2x2 items={sc.value_difficulty} />
          </div>
        )}

        <div className="text-xs text-ink mt-8">
          Confidential — prepared for {sc.company_name}. Prepared by DXC AdvisoryX.
        </div>
      </div>
    </div>
  )
}
