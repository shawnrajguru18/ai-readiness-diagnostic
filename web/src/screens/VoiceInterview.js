import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from 'react';
import { Wordmark } from '@/components/Wordmark';
import { Btn } from '@/components/Btn';
import { ELEVENLABS_AGENT_ID } from '@/constants';
import { personaFromRole, FRAMING_FOR } from '@/utils';
export function VoiceInterview({ company, industry, name, role, priorAnswers = {}, onFinish, onChat, onBack, }) {
    const collected = useRef({ ...priorAnswers });
    const [count, setCount] = useState(Object.keys(priorAnswers).length);
    const persona = personaFromRole(role || '');
    const framing = FRAMING_FOR[persona];
    const configured = ELEVENLABS_AGENT_ID && !/REPLACE_WITH/.test(ELEVENLABS_AGENT_ID);
    useEffect(() => {
        if (!configured)
            return;
        if (!document.getElementById('convai-lib')) {
            const s = document.createElement('script');
            s.id = 'convai-lib';
            s.async = true;
            s.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
            document.body.appendChild(s);
        }
        const el = document.getElementById('convai-el');
        if (!el)
            return;
        const onCall = (e) => {
            try {
                e.detail.config.clientTools = {
                    record_answer: (p = {}) => {
                        const { question_id, option_id, scale_value, option_ids } = p;
                        if (question_id) {
                            collected.current[question_id] = { option_id, scale_value, option_ids };
                            setCount(Object.keys(collected.current).length);
                        }
                        return 'recorded';
                    },
                    finish_interview: () => {
                        onFinish(collected.current);
                        return 'completed';
                    },
                };
                e.detail.config.dynamicVariables = {
                    prospect_name: name || 'there',
                    prospect_role: role || '',
                    company_name: company || 'your organization',
                    industry: industry || '',
                    persona,
                    framing_preference: framing,
                    already_answered: Object.keys(collected.current).join(', ') || 'none',
                };
            }
            catch (err) { }
        };
        el.addEventListener('elevenlabs-convai:call', onCall);
        return () => el.removeEventListener('elevenlabs-convai:call', onCall);
    }, [configured, name, role, company, industry, persona, framing, onFinish]);
    return (_jsxs("div", { className: "min-h-screen bg-canvas text-midnight", children: [_jsxs("div", { className: "max-w-3xl mx-auto px-6 py-6 flex justify-between items-center", children: [_jsx(Wordmark, {}), _jsx("button", { onClick: onBack, className: "text-sm text-royal font-semibold hover:underline", children: "\u2190 Back" })] }), _jsxs("div", { className: "max-w-2xl mx-auto px-6 pb-24 fade", children: [_jsx("div", { className: "text-xs uppercase tracking-widest text-royal font-bold", children: "Voice interview" }), _jsx("h1", { className: "display text-4xl font-extrabold mt-1", children: "Talk it through." }), _jsxs("p", { className: "text-ink mt-3", children: ["The DXC AI interviewer will guide ", company || 'you', " through the six readiness dimensions by voice. Speak naturally; it adapts and asks follow-ups. When you finish, we score it and show your scorecard."] }), _jsxs("ol", { className: "mt-6 space-y-2 text-sm text-ink", children: [_jsx("li", { children: "1. Tap the voice assistant in the bottom-right corner and allow microphone access." }), _jsx("li", { children: "2. Answer in your own words across all six dimensions." }), _jsx("li", { children: "3. Say \"I'm done\", or click below, to generate your scorecard." })] }), !configured && (_jsxs("div", { className: "mt-6 p-4 rounded-xl border border-risk/40 bg-risk/5 text-sm", children: ["Voice agent not configured. Add an ElevenLabs ", _jsx("code", { children: "ELEVENLABS_AGENT_ID" }), " in the page, or take it by chat."] })), configured && count > 0 && (_jsxs("div", { className: "mt-6 text-sm text-royal font-semibold", children: [count, " of 20 answers captured by voice."] })), _jsxs("div", { className: "mt-8 flex flex-wrap gap-3", children: [_jsx(Btn, { onClick: () => onFinish(collected.current), children: "See my scorecard \u2192" }), _jsx(Btn, { kind: "ghost", onClick: () => onChat(collected.current), children: "Switch to chat instead" })] }), _jsx("p", { className: "mt-4 text-[12px] text-ink/60", children: "Note: the voice agent must be Public and allow this site's origin in ElevenLabs. The corner widget is the live agent." })] }), configured && (_jsx("elevenlabs-convai", { id: "convai-el", "agent-id": ELEVENLABS_AGENT_ID }))] }));
}
//# sourceMappingURL=VoiceInterview.js.map