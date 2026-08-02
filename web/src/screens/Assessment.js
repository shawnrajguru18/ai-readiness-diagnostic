import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Wordmark } from '@/components/Wordmark';
import { Btn } from '@/components/Btn';
export function Assessment({ pool, initialAnswers = {}, onSubmit, onBack, onVoice, isSubmitting = false, }) {
    const all = pool?.questions || [];
    const dimLabels = pool?.dimensions || {};
    const [answers, setAnswers] = useState(initialAnswers);
    const visible = all.filter((q) => {
        if (q.skip_if) {
            const r = answers[q.skip_if.question];
            const v = r?.option_id;
            if (v && q.skip_if.answer_in.includes(v))
                return false;
        }
        if (q.branch_if) {
            const r = answers[q.branch_if.question];
            const sel = r?.option_ids || [];
            if (!sel.some((x) => q.branch_if.answer_in.includes(x)))
                return false;
        }
        return true;
    });
    const [i, setI] = useState(0);
    const q = visible[Math.min(i, visible.length - 1)];
    if (!q)
        return null;
    const pos = i + 1;
    const total = visible.length;
    const dimName = (dimLabels[q.dimension]?.label || q.dimension);
    const dimQ = visible.filter((x) => x.dimension === q.dimension);
    const dimIdx = dimQ.indexOf(q) + 1;
    const ans = answers[q.id] || {};
    const minsLeft = Math.max(1, Math.round((total - i) * 1.1));
    const setAns = (v) => {
        setAnswers({ ...answers, [q.id]: v });
    };
    const answered = () => {
        if (q.type === 'single_select')
            return !!ans.option_id;
        if (q.type === 'scale_1_5')
            return ans.scale_value != null;
        if (q.type === 'multi_select')
            return (ans.option_ids || []).length > 0;
        if (q.type === 'open_short')
            return true;
        return false;
    };
    const next = () => {
        if (i + 1 >= total) {
            onSubmit(answers);
        }
        else {
            setI(i + 1);
        }
    };
    return (_jsxs("div", { className: "min-h-screen bg-canvas", children: [_jsxs("div", { className: "max-w-3xl mx-auto px-6 py-6 flex justify-between items-center", children: [_jsx(Wordmark, {}), _jsxs("div", { className: "flex items-center gap-4", children: [onVoice && (_jsxs("button", { onClick: () => onVoice(answers), className: "text-xs font-semibold text-royal hover:underline flex items-center gap-1", children: [_jsx("span", { "aria-hidden": "true", children: "\uD83C\uDF99\uFE0F" }), " Switch to voice"] })), _jsxs("span", { className: "text-xs text-ink", children: ["~", minsLeft, " min left"] })] })] }), _jsxs("div", { className: "max-w-3xl mx-auto px-6", children: [_jsxs("div", { className: "flex items-center justify-between text-sm font-semibold text-midnight mb-2", children: [_jsxs("span", { children: [dimName, " \u00B7 ", dimIdx, " of ", dimQ.length] }), _jsxs("span", { className: "text-ink", children: [pos, "/", total] })] }), _jsx("div", { className: "h-1.5 bg-black/10 rounded-full overflow-hidden mb-10", children: _jsx("div", { className: "h-full bg-royal transition-all", style: { width: `${(pos / total) * 100}%` } }) }), _jsxs("div", { className: "fade", children: [_jsx("h2", { className: "display text-3xl font-bold leading-snug mb-8", children: q.text }), q.type === 'single_select' && (_jsx("div", { className: "space-y-3", children: q.options?.map((o) => (_jsx("button", { onClick: () => setAns({ option_id: o.id }), className: `w-full text-left px-5 py-4 rounded-xl border-2 transition ${ans.option_id === o.id
                                        ? 'border-royal bg-royal/5'
                                        : 'border-black/10 bg-white hover:border-black/25'}`, children: o.text }, o.id))) })), q.type === 'scale_1_5' && (_jsxs("div", { children: [_jsx("div", { className: "grid grid-cols-5 gap-2", children: q.scale_anchors?.map((a) => (_jsx("button", { onClick: () => setAns({ scale_value: a.value }), className: `py-5 rounded-xl border-2 font-bold text-lg ${ans.scale_value === a.value
                                                ? 'border-royal bg-royal/5'
                                                : 'border-black/10 bg-white hover:border-black/25'}`, children: a.value }, a.value))) }), _jsxs("div", { className: "flex justify-between text-xs text-ink mt-2", children: [_jsx("span", { children: q.scale_anchors?.[0]?.text }), _jsx("span", { className: "text-right", children: q.scale_anchors?.[4]?.text })] }), ans.scale_value != null && (_jsx("p", { className: "text-sm text-ink mt-3", children: q.scale_anchors?.find((a) => a.value === ans.scale_value)?.text }))] })), q.type === 'multi_select' && (_jsx("div", { className: "space-y-3", children: q.options?.map((o) => {
                                    const sel = (ans.option_ids || []).includes(o.id);
                                    return (_jsxs("button", { onClick: () => {
                                            const s = new Set(ans.option_ids || []);
                                            sel ? s.delete(o.id) : s.add(o.id);
                                            setAns({ option_ids: [...s] });
                                        }, className: `w-full text-left px-5 py-3.5 rounded-xl border-2 flex items-center gap-3 ${sel
                                            ? 'border-royal bg-royal/5'
                                            : 'border-black/10 bg-white hover:border-black/25'}`, children: [_jsx("span", { className: `w-4 h-4 rounded border ${sel ? 'bg-royal border-royal' : 'border-black/30'}` }), o.text] }, o.id));
                                }) })), q.type === 'open_short' && (_jsxs("div", { children: [_jsx("textarea", { maxLength: q.open_answer_max_chars || 500, value: ans.text || '', onChange: (e) => setAns({ text: e.target.value }), rows: 4, className: "w-full p-4 rounded-xl border-2 border-black/10 focus:border-royal focus:outline-none" }), _jsxs("div", { className: "text-xs text-ink text-right mt-1", children: [(q.open_answer_max_chars || 500) - ((ans.text || '').length), " characters left"] })] }))] }, q.id), _jsxs("div", { className: "flex justify-between mt-10 pb-16", children: [_jsx(Btn, { kind: "ghost", onClick: () => (i === 0 ? onBack() : setI(i - 1)), disabled: isSubmitting, children: "\u2190 Back" }), _jsx(Btn, { onClick: next, disabled: !answered() || isSubmitting, children: isSubmitting && i + 1 >= total ? (_jsxs("span", { className: "flex items-center gap-2", children: [_jsx("span", { className: "inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" }), "Generating scorecard..."] })) : (i + 1 >= total ? 'Submit assessment' : 'Next →') })] })] })] }));
}
//# sourceMappingURL=Assessment.js.map