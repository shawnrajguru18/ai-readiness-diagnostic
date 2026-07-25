import { useState } from 'react'
import { Wordmark } from '@/components/Wordmark'
import { Btn } from '@/components/Btn'
import { QuestionPool, Answer } from '@/types'

interface AssessmentProps {
  pool: QuestionPool | null
  initialAnswers?: Record<string, Answer>
  onSubmit: (answers: Record<string, Answer>) => void
  onBack: () => void
  onVoice?: (answers: Record<string, Answer>) => void
}

export function Assessment({
  pool,
  initialAnswers = {},
  onSubmit,
  onBack,
  onVoice,
}: AssessmentProps) {
  const all = pool?.questions || []
  const dimLabels = pool?.dimensions || {}
  const [answers, setAnswers] = useState<Record<string, Answer>>(initialAnswers)

  const visible = all.filter((q) => {
    if (q.skip_if) {
      const r = answers[q.skip_if.question]
      const v = r?.option_id
      if (v && q.skip_if.answer_in.includes(v)) return false
    }
    if (q.branch_if) {
      const r = answers[q.branch_if.question]
      const sel = r?.option_ids || []
      if (!sel.some((x) => q.branch_if!.answer_in.includes(x))) return false
    }
    return true
  })

  const [i, setI] = useState(0)
  const q = visible[Math.min(i, visible.length - 1)]

  if (!q) return null

  const pos = i + 1
  const total = visible.length
  const dimName = (dimLabels[q.dimension]?.label || q.dimension) as string
  const dimQ = visible.filter((x) => x.dimension === q.dimension)
  const dimIdx = dimQ.indexOf(q) + 1
  const ans = answers[q.id] || {}
  const minsLeft = Math.max(1, Math.round((total - i) * 1.1))

  const setAns = (v: Answer) => {
    setAnswers({ ...answers, [q.id]: v })
  }

  const answered = (): boolean => {
    if (q.type === 'single_select') return !!ans.option_id
    if (q.type === 'scale_1_5') return ans.scale_value != null
    if (q.type === 'multi_select') return (ans.option_ids || []).length > 0
    if (q.type === 'open_short') return true
    return false
  }

  const next = () => {
    if (i + 1 >= total) {
      onSubmit(answers)
    } else {
      setI(i + 1)
    }
  }

  return (
    <div className="min-h-screen bg-canvas">
      <div className="max-w-3xl mx-auto px-6 py-6 flex justify-between items-center">
        <Wordmark />
        <div className="flex items-center gap-4">
          {onVoice && (
            <button
              onClick={() => onVoice(answers)}
              className="text-xs font-semibold text-royal hover:underline flex items-center gap-1"
            >
              <span aria-hidden="true">🎙️</span> Switch to voice
            </button>
          )}
          <span className="text-xs text-ink">~{minsLeft} min left</span>
        </div>
      </div>
      <div className="max-w-3xl mx-auto px-6">
        <div className="flex items-center justify-between text-sm font-semibold text-midnight mb-2">
          <span>
            {dimName} · {dimIdx} of {dimQ.length}
          </span>
          <span className="text-ink">
            {pos}/{total}
          </span>
        </div>
        <div className="h-1.5 bg-black/10 rounded-full overflow-hidden mb-10">
          <div
            className="h-full bg-royal transition-all"
            style={{ width: `${(pos / total) * 100}%` }}
          ></div>
        </div>
        <div className="fade" key={q.id}>
          <h2 className="display text-3xl font-bold leading-snug mb-8">{q.text}</h2>

          {q.type === 'single_select' && (
            <div className="space-y-3">
              {q.options?.map((o) => (
                <button
                  key={o.id}
                  onClick={() => setAns({ option_id: o.id })}
                  className={`w-full text-left px-5 py-4 rounded-xl border-2 transition ${
                    ans.option_id === o.id
                      ? 'border-royal bg-royal/5'
                      : 'border-black/10 bg-white hover:border-black/25'
                  }`}
                >
                  {o.text}
                </button>
              ))}
            </div>
          )}

          {q.type === 'scale_1_5' && (
            <div>
              <div className="grid grid-cols-5 gap-2">
                {q.scale_anchors?.map((a) => (
                  <button
                    key={a.value}
                    onClick={() => setAns({ scale_value: a.value })}
                    className={`py-5 rounded-xl border-2 font-bold text-lg ${
                      ans.scale_value === a.value
                        ? 'border-royal bg-royal/5'
                        : 'border-black/10 bg-white hover:border-black/25'
                    }`}
                  >
                    {a.value}
                  </button>
                ))}
              </div>
              <div className="flex justify-between text-xs text-ink mt-2">
                <span>{q.scale_anchors?.[0]?.text}</span>
                <span className="text-right">{q.scale_anchors?.[4]?.text}</span>
              </div>
              {ans.scale_value != null && (
                <p className="text-sm text-ink mt-3">
                  {q.scale_anchors?.find((a) => a.value === ans.scale_value)?.text}
                </p>
              )}
            </div>
          )}

          {q.type === 'multi_select' && (
            <div className="space-y-3">
              {q.options?.map((o) => {
                const sel = (ans.option_ids || []).includes(o.id)
                return (
                  <button
                    key={o.id}
                    onClick={() => {
                      const s = new Set(ans.option_ids || [])
                      sel ? s.delete(o.id) : s.add(o.id)
                      setAns({ option_ids: [...s] })
                    }}
                    className={`w-full text-left px-5 py-3.5 rounded-xl border-2 flex items-center gap-3 ${
                      sel
                        ? 'border-royal bg-royal/5'
                        : 'border-black/10 bg-white hover:border-black/25'
                    }`}
                  >
                    <span
                      className={`w-4 h-4 rounded border ${
                        sel ? 'bg-royal border-royal' : 'border-black/30'
                      }`}
                    ></span>
                    {o.text}
                  </button>
                )
              })}
            </div>
          )}

          {q.type === 'open_short' && (
            <div>
              <textarea
                maxLength={q.open_answer_max_chars || 500}
                value={ans.text || ''}
                onChange={(e) => setAns({ text: e.target.value })}
                rows={4}
                className="w-full p-4 rounded-xl border-2 border-black/10 focus:border-royal focus:outline-none"
              />
              <div className="text-xs text-ink text-right mt-1">
                {(q.open_answer_max_chars || 500) - ((ans.text || '').length)} characters left
              </div>
            </div>
          )}
        </div>
        <div className="flex justify-between mt-10 pb-16">
          <Btn kind="ghost" onClick={() => (i === 0 ? onBack() : setI(i - 1))}>
            ← Back
          </Btn>
          <Btn onClick={next} disabled={!answered()}>
            {i + 1 >= total ? 'Submit assessment' : 'Next →'}
          </Btn>
        </div>
      </div>
    </div>
  )
}
