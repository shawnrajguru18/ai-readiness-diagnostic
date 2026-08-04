import { useEffect, useState } from 'react'
import { Landing } from './screens/Landing'
import { Assessment } from './screens/Assessment'
import { Submitted } from './screens/Submitted'
import { Scorecard } from './screens/Scorecard'
import { QuickWins } from './screens/QuickWins'
import { VoiceInterview } from './screens/VoiceInterview'
import { API, DEMO_SCORECARD } from './constants'
import { Scorecard as ScorecardType, QuestionPool, Answer, FormData, ConsentData } from './types'

export function App() {
  console.log('[App] API constant value:', API)
  const [screen, setScreen] = useState<
    'landing' | 'assessment' | 'voice' | 'submitted' | 'scorecard' | 'quickwins'
  >('landing')
  const [pool, setPool] = useState<QuestionPool | null>(null)
  const [sc, setSc] = useState<ScorecardType>(DEMO_SCORECARD)
  const [ctx, setCtx] = useState<{
    f?: FormData
    c?: ConsentData
  }>({})
  const [answers, setAnswers] = useState<Record<string, Answer>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const url = API + '/api/questions'
    console.log('[App] Fetching questions from:', url)
    fetch(url)
      .then((r) => {
        console.log('[App] Response status:', r.status)
        return r.json()
      })
      .then((data) => {
        console.log('[App] Questions loaded:', data ? 'success' : 'null')
        setPool(data)
      })
      .catch((err) => {
        console.error('[App] Failed to load questions:', err)
        setPool(null)
      })
  }, [])

  const begin = (f: FormData, c: ConsentData) => {
    setCtx({ f, c })
    if (!pool) {
      setSc(DEMO_SCORECARD)
      setScreen('submitted')
      return
    }
    setScreen('assessment')
  }

  const voice = (f: FormData, c: ConsentData) => {
    setCtx({ f, c })
    setAnswers({})
    setScreen('voice')
  }

  const home = () => {
    setAnswers({})
    setCtx({})
    setSc(DEMO_SCORECARD)
    setScreen('landing')
  }

  const voiceFinish = (answers: Record<string, Answer>) => {
    if (answers && Object.keys(answers).length) {
      submitVoice(answers)
    } else {
      alert(
        "No answers were captured by voice yet — let's finish in chat so we can generate your scorecard."
      )
      setScreen(pool ? 'assessment' : 'landing')
    }
  }

  const submitVoice = (voiceAnswers: Record<string, Answer>) => {
    setIsSubmitting(true)
    const body = {
      submission: ctx.f,
      consent: { c1_use_for_scorecard: true, ...(ctx.c || {}) },
      responses: {}, // No structured responses for voice
      voice_responses: voiceAnswers, // Send voice answers separately
      persona_hint: null,
    }
    fetch(API + '/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then((r) => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}: ${r.statusText}`)
        }
        return r.json()
      })
      .then((d) => {
        if (d.error) {
          console.error('[submitVoice] Backend error:', d.error)
          alert(`Backend error: ${d.error}`)
          setSc(DEMO_SCORECARD)
        } else {
          setSc(d)
        }
        setScreen('submitted')
      })
      .catch((err) => {
        console.error('[submitVoice] Error:', err)
        alert(`Failed to generate scorecard: ${err.message}`)
        setSc(DEMO_SCORECARD)
        setScreen('submitted')
      })
      .finally(() => setIsSubmitting(false))
  }

  const submit = (answers: Record<string, Answer>) => {
    setIsSubmitting(true)
    const responses: Record<string, Answer> = {}
    Object.entries(answers).forEach(([k, v]) => {
      responses[k] = v
    })
    const body = {
      submission: ctx.f,
      consent: { c1_use_for_scorecard: true, ...(ctx.c || {}) },
      responses,
      persona_hint: null,
    }
    fetch(API + '/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then((r) => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}: ${r.statusText}`)
        }
        return r.json()
      })
      .then((d) => {
        if (d.error) {
          console.error('[submit] Backend error:', d.error)
          alert(`Backend error: ${d.error}`)
          setSc(DEMO_SCORECARD)
        } else {
          setSc(d)
        }
        setScreen('submitted')
      })
      .catch((err) => {
        console.error('[submit] Error:', err)
        alert(`Failed to generate scorecard: ${err.message}`)
        setSc(DEMO_SCORECARD)
        setScreen('submitted')
      })
      .finally(() => setIsSubmitting(false))
  }

  if (screen === 'landing')
    return (
      <Landing
        onBegin={begin}
        onVoice={voice}
        onSample={() => {
          setSc(DEMO_SCORECARD)
          setScreen('scorecard')
        }}
      />
    )
  if (screen === 'assessment')
    return (
      <Assessment
        pool={pool}
        initialAnswers={answers}
        onSubmit={submit}
        onBack={() => setScreen('landing')}
        onVoice={(a) => {
          setAnswers(a || {})
          setScreen('voice')
        }}
        isSubmitting={isSubmitting}
      />
    )
  if (screen === 'voice')
    return (
      <VoiceInterview
        company={ctx.f?.company_name_raw}
        industry={ctx.f?.industry_label}
        name={ctx.f?.prospect_name}
        role={ctx.f?.prospect_role}
        priorAnswers={answers}
        onFinish={voiceFinish}
        onChat={(a) => {
          setAnswers(a || {})
          setScreen(pool ? 'assessment' : 'landing')
        }}
        onBack={() => setScreen('landing')}
      />
    )
  if (screen === 'submitted')
    return (
      <Submitted
        company={ctx.f?.company_name_raw || sc.company_name}
        email={ctx.f?.prospect_email}
        onView={() => setScreen('scorecard')}
      />
    )
  if (screen === 'scorecard')
    return (
      <Scorecard
        sc={sc}
        onQuickWins={() => setScreen('quickwins')}
        onHome={home}
      />
    )
  if (screen === 'quickwins')
    return (
      <QuickWins
        sc={sc}
        onBack={() => setScreen('scorecard')}
        onHome={home}
      />
    )
  return null
}
