import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Landing } from './screens/Landing';
import { Assessment } from './screens/Assessment';
import { Submitted } from './screens/Submitted';
import { Scorecard } from './screens/Scorecard';
import { QuickWins } from './screens/QuickWins';
import { VoiceInterview } from './screens/VoiceInterview';
import { API, DEMO_SCORECARD } from './constants';
export function App() {
    const [screen, setScreen] = useState('landing');
    const [pool, setPool] = useState(null);
    const [sc, setSc] = useState(DEMO_SCORECARD);
    const [ctx, setCtx] = useState({});
    const [answers, setAnswers] = useState({});
    useEffect(() => {
        fetch(API + '/api/questions')
            .then((r) => r.json())
            .then(setPool)
            .catch(() => setPool(null));
    }, []);
    const begin = (f, c) => {
        setCtx({ f, c });
        if (!pool) {
            setSc(DEMO_SCORECARD);
            setScreen('submitted');
            return;
        }
        setScreen('assessment');
    };
    const voice = (f, c) => {
        setCtx({ f, c });
        setAnswers({});
        setScreen('voice');
    };
    const home = () => {
        setAnswers({});
        setCtx({});
        setSc(DEMO_SCORECARD);
        setScreen('landing');
    };
    const voiceFinish = (answers) => {
        if (answers && Object.keys(answers).length) {
            submit(answers);
        }
        else {
            alert("No answers were captured by voice yet — let's finish in chat so we can generate your scorecard.");
            setScreen(pool ? 'assessment' : 'landing');
        }
    };
    const submit = (answers) => {
        const responses = {};
        Object.entries(answers).forEach(([k, v]) => {
            responses[k] = v;
        });
        const body = {
            submission: ctx.f,
            consent: { c1_use_for_scorecard: true, ...(ctx.c || {}) },
            responses,
            persona_hint: null,
        };
        fetch(API + '/api/assess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        })
            .then((r) => r.json())
            .then((d) => {
            setSc(d);
            setScreen('submitted');
        })
            .catch(() => {
            setSc(DEMO_SCORECARD);
            setScreen('submitted');
        });
    };
    if (screen === 'landing')
        return (_jsx(Landing, { onBegin: begin, onVoice: voice, onSample: () => {
                setSc(DEMO_SCORECARD);
                setScreen('scorecard');
            } }));
    if (screen === 'assessment')
        return (_jsx(Assessment, { pool: pool, initialAnswers: answers, onSubmit: submit, onBack: () => setScreen('landing'), onVoice: (a) => {
                setAnswers(a || {});
                setScreen('voice');
            } }));
    if (screen === 'voice')
        return (_jsx(VoiceInterview, { company: ctx.f?.company_name_raw, industry: ctx.f?.industry_label, name: ctx.f?.prospect_name, role: ctx.f?.prospect_role, priorAnswers: answers, onFinish: voiceFinish, onChat: (a) => {
                setAnswers(a || {});
                setScreen(pool ? 'assessment' : 'landing');
            }, onBack: () => setScreen('landing') }));
    if (screen === 'submitted')
        return (_jsx(Submitted, { company: ctx.f?.company_name_raw || sc.company_name, email: ctx.f?.prospect_email, onView: () => setScreen('scorecard') }));
    if (screen === 'scorecard')
        return (_jsx(Scorecard, { sc: sc, onQuickWins: () => setScreen('quickwins'), onHome: home }));
    if (screen === 'quickwins')
        return (_jsx(QuickWins, { sc: sc, onBack: () => setScreen('scorecard'), onHome: home }));
    return null;
}
//# sourceMappingURL=App.js.map