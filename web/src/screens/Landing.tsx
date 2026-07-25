import { useState } from 'react'
import { Wordmark } from '@/components/Wordmark'
import { INDUSTRY_LABELS } from '@/constants'
import { FormData, ConsentData } from '@/types'

interface LandingProps {
  onBegin: (form: FormData, consent: ConsentData) => void
  onVoice: (form: FormData, consent: ConsentData) => void
  onSample: () => void
}

export function Landing({ onBegin, onVoice, onSample }: LandingProps) {
  const [form, setForm] = useState({
    prospect_name: '',
    prospect_role: '',
    prospect_email: '',
    company_name_raw: '',
    industry_tag: 'FS' as keyof typeof INDUSTRY_LABELS,
    size_band: 'large',
  })

  const [consent, setConsent] = useState({
    c2_anonymized_benchmark: true,
    c4_cross_practice_sharing: false,
  })

  const updateForm = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [key]: e.target.value })
  }

  const handleBegin = () => {
    onBegin(
      {
        ...form,
        industry_label: INDUSTRY_LABELS[form.industry_tag],
      },
      consent
    )
  }

  const handleVoice = () => {
    onVoice(
      {
        ...form,
        industry_label: INDUSTRY_LABELS[form.industry_tag],
      },
      consent
    )
  }

  return (
    <div className="min-h-screen bg-canvas text-midnight">
      <div className="max-w-6xl mx-auto px-8 py-6 flex justify-between items-center">
        <Wordmark />
        <span className="text-xs text-ink uppercase tracking-widest">AI Readiness Diagnostic</span>
      </div>
      <div className="max-w-6xl mx-auto px-8 grid md:grid-cols-2 gap-16 items-center pt-10 pb-24">
        <div className="fade">
          <h1 className="display text-5xl md:text-6xl leading-tight font-extrabold">
            Know where you stand on AI. In 30 minutes.
          </h1>
          <p className="mt-6 text-lg text-ink max-w-md">
            DXC returns a peer-benchmarked AI readiness scorecard within 24 hours. No consultant
            required.
          </p>
          <div className="mt-8 flex flex-wrap gap-x-8 gap-y-3 text-sm text-ink">
            <span>✓ Reviewed by a DXC senior partner before delivery</span>
            <span>✓ 24-hour turnaround</span>
            <span>✓ Used by enterprises in 18 countries</span>
          </div>
          <button
            onClick={onSample}
            className="mt-8 text-trueblue text-sm font-semibold hover:underline"
          >
            See a sample scorecard →
          </button>
        </div>
        <div className="bg-white text-midnight rounded-2xl p-8 shadow-xl border border-black/5 fade">
          <h2 className="display text-2xl font-bold mb-5">Begin your assessment</h2>
          <div className="space-y-3">
            {[
              ['prospect_name', 'Full name'],
              ['prospect_role', 'Role title'],
              ['prospect_email', 'Business email'],
              ['company_name_raw', 'Company name'],
            ].map(([key, placeholder]) => (
              <input
                key={key}
                value={form[key as keyof typeof form]}
                onChange={updateForm(key as keyof typeof form)}
                placeholder={placeholder}
                className="w-full px-4 py-3 rounded-lg border border-black/15 focus:border-royal focus:outline-none text-[15px]"
              />
            ))}
            <div className="grid grid-cols-2 gap-3">
              <select
                value={form.industry_tag}
                onChange={updateForm('industry_tag')}
                className="px-3 py-3 rounded-lg border border-black/15 text-[15px]"
              >
                {Object.entries(INDUSTRY_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
              <select
                value={form.size_band}
                onChange={updateForm('size_band')}
                className="px-3 py-3 rounded-lg border border-black/15 text-[15px]"
              >
                <option value="mid-market">Mid-market</option>
                <option value="large">Large enterprise</option>
                <option value="global">Global</option>
              </select>
            </div>
          </div>
          <div className="mt-5 space-y-2 text-[13px] text-ink">
            <label className="flex items-center gap-2 opacity-70">
              <input type="checkbox" checked readOnly /> Use my data to produce my scorecard
              (required)
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={consent.c2_anonymized_benchmark}
                onChange={(e) =>
                  setConsent({ ...consent, c2_anonymized_benchmark: e.target.checked })
                }
              />{' '}
              Contribute anonymized data to the AdvisoryX peer benchmark library
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={consent.c4_cross_practice_sharing}
                onChange={(e) =>
                  setConsent({ ...consent, c4_cross_practice_sharing: e.target.checked })
                }
              />{' '}
              Share with DXC teams for relationship follow-up
            </label>
          </div>
          <button
            onClick={handleBegin}
            disabled={!form.company_name_raw}
            className="mt-6 w-full bg-royal text-white py-3 rounded-lg font-semibold hover:bg-[#003a86] disabled:opacity-40"
          >
            Begin assessment by chat →
          </button>
          <div className="flex items-center gap-3 my-3 text-[11px] text-ink/60 uppercase tracking-widest">
            <span className="h-px flex-1 bg-black/10"></span>
            or
            <span className="h-px flex-1 bg-black/10"></span>
          </div>
          <button
            onClick={handleVoice}
            disabled={!form.company_name_raw}
            className="w-full bg-white text-midnight border border-midnight/20 hover:border-royal hover:text-royal py-3 rounded-lg font-semibold disabled:opacity-40 flex items-center justify-center gap-2"
          >
            <span aria-hidden="true">🎙️</span> Take it by voice
          </button>
          <p className="mt-3 text-[12px] text-ink/70">
            Speak with the DXC AI interviewer; it guides you through the six dimensions
            conversationally.
          </p>
        </div>
      </div>
    </div>
  )
}
