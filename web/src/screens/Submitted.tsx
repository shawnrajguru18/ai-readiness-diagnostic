import { Wordmark } from '@/components/Wordmark'
import { Btn } from '@/components/Btn'

interface SubmittedProps {
  company?: string
  email?: string
  onView: () => void
}

export function Submitted({ company, email, onView }: SubmittedProps) {
  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      <div className="max-w-3xl mx-auto w-full px-6 py-6">
        <Wordmark />
      </div>
      <div className="max-w-2xl mx-auto px-6 flex-1 flex flex-col justify-center pb-24 fade">
        <div className="w-12 h-12 rounded-full border-2 border-royal border-t-transparent spin mb-8"></div>
        <h1 className="display text-4xl font-bold">Your assessment is submitted.</h1>
        <p className="text-ink mt-3">Here is what happens next.</p>
        <ol className="mt-8 space-y-4">
          {[
            `AI agents research ${company || 'your company'} — financials, news, tech posture`,
            'Our synthesis engine scores your readiness across six dimensions',
            'A DXC senior partner reviews and approves your scorecard',
          ].map((s, k) => (
            <li key={k} className="flex gap-4 items-start">
              <span className="bg-midnight text-white w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-none">
                {k + 1}
              </span>
              <span className="pt-1">{s}</span>
            </li>
          ))}
        </ol>
        <p className="mt-8 text-ink">
          You'll receive your scorecard within 24 hours at{' '}
          <b className="text-midnight">{email || 'your email'}</b>. A personal portal link will
          arrive with your results.
        </p>
        <div className="mt-8">
          <Btn onClick={onView}>Preview your scorecard →</Btn>
        </div>
      </div>
    </div>
  )
}
