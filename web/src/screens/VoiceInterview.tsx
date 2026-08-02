import { useEffect, useRef, useState } from 'react'
import { Wordmark } from '@/components/Wordmark'
import { Btn } from '@/components/Btn'
import { ELEVENLABS_AGENT_ID } from '@/constants'
import { personaFromRole, FRAMING_FOR } from '@/utils'
import { Answer } from '@/types'

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'elevenlabs-convai': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          'agent-id'?: string
        },
        HTMLElement
      >
    }
  }
}

interface VoiceInterviewProps {
  company?: string
  industry?: string
  name?: string
  role?: string
  priorAnswers?: Record<string, Answer>
  onFinish: (answers: Record<string, Answer>) => void
  onChat: (answers: Record<string, Answer>) => void
  onBack: () => void
}

export function VoiceInterview({
  company,
  industry,
  name,
  role,
  priorAnswers = {},
  onFinish,
  onChat,
  onBack,
}: VoiceInterviewProps) {
  const collected = useRef({ ...priorAnswers })
  const [count, setCount] = useState(Object.keys(priorAnswers).length)
  const [error, setError] = useState<string>()
  const persona = personaFromRole(role || '')
  const framing = FRAMING_FOR[persona]
  const configured = ELEVENLABS_AGENT_ID && !/REPLACE_WITH/.test(ELEVENLABS_AGENT_ID)
  const isHTTP = typeof window !== 'undefined' && window.location.protocol === 'http:'

  useEffect(() => {
    if (!configured) return

    // Check for insecure context (HTTP without localhost)
    const isSecure = window.location.protocol === 'https:' ||
                     window.location.hostname === 'localhost' ||
                     window.location.hostname === '127.0.0.1'

    if (!isSecure) {
      setError('Voice interviews require HTTPS. Please access this app over a secure connection.')
      return
    }

    if (!document.getElementById('convai-lib')) {
      const s = document.createElement('script')
      s.id = 'convai-lib'
      s.async = true
      s.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed'
      document.body.appendChild(s)
    }

    const el = document.getElementById('convai-el')
    if (!el) return

    const onCall = (e: any) => {
      try {
        e.detail.config.clientTools = {
          record_answer: (p: any = {}) => {
            const { question, answer } = p
            console.log('[Voice] record_answer called:', { question, answer })
            if (question && answer) {
              // Use question text as key, store the answer as text
              collected.current[question] = { text: answer }
              const total = Object.keys(collected.current).length
              console.log(`[Voice] Stored answer. Total: ${total}`, { stored: collected.current })
              setCount(total)
            } else {
              console.log('[Voice] Missing question or answer, skipping', { question, answer })
            }
            return 'recorded'
          },
          finish_interview: () => {
            console.log('[Voice] finish_interview called. Final answers:', collected.current)
            onFinish(collected.current)
            return 'completed'
          },
        }
        e.detail.config.dynamicVariables = {
          prospect_name: name || 'there',
          prospect_role: role || '',
          company_name: company || 'your organization',
          industry: industry || '',
          persona,
          framing_preference: framing,
          already_answered: Object.keys(collected.current).join(', ') || 'none',
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err)
        if (msg.includes('getUserMedia') || msg.includes('mediaDevices')) {
          setError('Microphone access failed. This feature requires HTTPS or localhost.')
        } else {
          setError(`Voice interview error: ${msg}`)
        }
      }
    }

    const onError = (e: any) => {
      const msg = e?.detail?.message || 'Unknown error'
      if (msg.includes('mediaDevices') || msg.includes('getUserMedia')) {
        setError('Microphone access failed. This feature requires HTTPS.')
      } else {
        setError(`Voice interview error: ${msg}`)
      }
    }

    el.addEventListener('elevenlabs-convai:call', onCall)
    el.addEventListener('elevenlabs-convai:error', onError)
    return () => {
      el.removeEventListener('elevenlabs-convai:call', onCall)
      el.removeEventListener('elevenlabs-convai:error', onError)
    }
  }, [configured, name, role, company, industry, persona, framing, onFinish])

  return (
    <div className="min-h-screen bg-canvas text-midnight">
      <div className="max-w-3xl mx-auto px-6 py-6 flex justify-between items-center">
        <Wordmark />
        <button onClick={onBack} className="text-sm text-royal font-semibold hover:underline">
          ← Back
        </button>
      </div>
      <div className="max-w-2xl mx-auto px-6 pb-24 fade">
        <div className="text-xs uppercase tracking-widest text-royal font-bold">Voice interview</div>
        <h1 className="display text-4xl font-extrabold mt-1">Talk it through.</h1>
        <p className="text-ink mt-3">
          The DXC AI interviewer will guide {company || 'you'} through the six readiness dimensions
          by voice. Speak naturally; it adapts and asks follow-ups. When you finish, we score it
          and show your scorecard.
        </p>
        <ol className="mt-6 space-y-2 text-sm text-ink">
          <li>1. Tap the voice assistant in the bottom-right corner and allow microphone access.</li>
          <li>2. Answer in your own words across all six dimensions.</li>
          <li>3. Say "I'm done", or click below, to generate your scorecard.</li>
        </ol>
        {error && (
          <div className="mt-6 p-4 rounded-xl border border-risk/40 bg-risk/5 text-sm">
            <strong>Voice interview error:</strong> {error}
            {isHTTP && <div className="mt-2 text-xs">Try using HTTPS or localhost for microphone access.</div>}
            <Btn kind="ghost" onClick={() => onChat(collected.current)} className="mt-3">
              Switch to chat instead
            </Btn>
          </div>
        )}
        {!configured && !error && (
          <div className="mt-6 p-4 rounded-xl border border-risk/40 bg-risk/5 text-sm">
            <strong>Voice agent not configured.</strong> Agent ID: {ELEVENLABS_AGENT_ID ? `"${ELEVENLABS_AGENT_ID.slice(0, 20)}..."` : 'Not set'}.
            Please check your ElevenLabs account settings or use chat instead.
          </div>
        )}
        {configured && count > 0 && (
          <div className="mt-6 text-sm text-royal font-semibold">
            {count} of 20 answers captured by voice.
          </div>
        )}
        {count > 0 && (
          <div className="mt-8 flex flex-wrap gap-3">
            <Btn onClick={() => onFinish(collected.current)}>Generate my scorecard →</Btn>
            <Btn kind="ghost" onClick={() => onChat(collected.current)}>
              Switch to chat instead
            </Btn>
          </div>
        )}
        <p className="mt-4 text-[12px] text-ink/60">
          Note: the voice agent must be Public and allow this site's origin in ElevenLabs. The
          corner widget is the live agent.
        </p>
      </div>
      {configured && !error && (
        <elevenlabs-convai
          id="convai-el"
          agent-id={ELEVENLABS_AGENT_ID}
        ></elevenlabs-convai>
      )}
    </div>
  )
}
