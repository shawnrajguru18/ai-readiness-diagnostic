import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Wordmark } from '@/components/Wordmark';
import { INDUSTRY_LABELS } from '@/constants';
export function Landing({ onBegin, onVoice, onSample }) {
    const [form, setForm] = useState({
        prospect_name: '',
        prospect_role: '',
        prospect_email: '',
        company_name_raw: '',
        industry_tag: 'FS',
        size_band: 'large',
    });
    const [consent, setConsent] = useState({
        c2_anonymized_benchmark: true,
        c4_cross_practice_sharing: false,
    });
    const updateForm = (key) => (e) => {
        setForm({ ...form, [key]: e.target.value });
    };
    const handleBegin = () => {
        onBegin({
            ...form,
            industry_label: INDUSTRY_LABELS[form.industry_tag],
        }, consent);
    };
    const handleVoice = () => {
        onVoice({
            ...form,
            industry_label: INDUSTRY_LABELS[form.industry_tag],
        }, consent);
    };
    return (_jsxs("div", { className: "min-h-screen bg-canvas text-midnight", children: [_jsxs("div", { className: "max-w-6xl mx-auto px-8 py-6 flex justify-between items-center", children: [_jsx(Wordmark, {}), _jsx("span", { className: "text-xs text-ink uppercase tracking-widest", children: "AI Readiness Diagnostic" })] }), _jsxs("div", { className: "max-w-6xl mx-auto px-8 grid md:grid-cols-2 gap-16 items-center pt-10 pb-24", children: [_jsxs("div", { className: "fade", children: [_jsx("h1", { className: "display text-5xl md:text-6xl leading-tight font-extrabold", children: "Know where you stand on AI. In 30 minutes." }), _jsx("p", { className: "mt-6 text-lg text-ink max-w-md", children: "DXC returns a peer-benchmarked AI readiness scorecard within 24 hours. No consultant required." }), _jsxs("div", { className: "mt-8 flex flex-wrap gap-x-8 gap-y-3 text-sm text-ink", children: [_jsx("span", { children: "\u2713 Reviewed by a DXC senior partner before delivery" }), _jsx("span", { children: "\u2713 24-hour turnaround" }), _jsx("span", { children: "\u2713 Used by enterprises in 18 countries" })] }), _jsx("button", { onClick: onSample, className: "mt-8 text-trueblue text-sm font-semibold hover:underline", children: "See a sample scorecard \u2192" })] }), _jsxs("div", { className: "bg-white text-midnight rounded-2xl p-8 shadow-xl border border-black/5 fade", children: [_jsx("h2", { className: "display text-2xl font-bold mb-5", children: "Begin your assessment" }), _jsxs("div", { className: "space-y-3", children: [[
                                        ['prospect_name', 'Full name'],
                                        ['prospect_role', 'Role title'],
                                        ['prospect_email', 'Business email'],
                                        ['company_name_raw', 'Company name'],
                                    ].map(([key, placeholder]) => (_jsx("input", { value: form[key], onChange: updateForm(key), placeholder: placeholder, className: "w-full px-4 py-3 rounded-lg border border-black/15 focus:border-royal focus:outline-none text-[15px]" }, key))), _jsxs("div", { className: "grid grid-cols-2 gap-3", children: [_jsx("select", { value: form.industry_tag, onChange: updateForm('industry_tag'), className: "px-3 py-3 rounded-lg border border-black/15 text-[15px]", children: Object.entries(INDUSTRY_LABELS).map(([k, v]) => (_jsx("option", { value: k, children: v }, k))) }), _jsxs("select", { value: form.size_band, onChange: updateForm('size_band'), className: "px-3 py-3 rounded-lg border border-black/15 text-[15px]", children: [_jsx("option", { value: "mid-market", children: "Mid-market" }), _jsx("option", { value: "large", children: "Large enterprise" }), _jsx("option", { value: "global", children: "Global" })] })] })] }), _jsxs("div", { className: "mt-5 space-y-2 text-[13px] text-ink", children: [_jsxs("label", { className: "flex items-center gap-2 opacity-70", children: [_jsx("input", { type: "checkbox", checked: true, readOnly: true }), " Use my data to produce my scorecard (required)"] }), _jsxs("label", { className: "flex items-center gap-2", children: [_jsx("input", { type: "checkbox", checked: consent.c2_anonymized_benchmark, onChange: (e) => setConsent({ ...consent, c2_anonymized_benchmark: e.target.checked }) }), ' ', "Contribute anonymized data to the AdvisoryX peer benchmark library"] }), _jsxs("label", { className: "flex items-center gap-2", children: [_jsx("input", { type: "checkbox", checked: consent.c4_cross_practice_sharing, onChange: (e) => setConsent({ ...consent, c4_cross_practice_sharing: e.target.checked }) }), ' ', "Share with DXC teams for relationship follow-up"] })] }), _jsx("button", { onClick: handleBegin, disabled: !form.company_name_raw, className: "mt-6 w-full bg-royal text-white py-3 rounded-lg font-semibold hover:bg-[#003a86] disabled:opacity-40", children: "Begin assessment by chat \u2192" }), _jsxs("div", { className: "flex items-center gap-3 my-3 text-[11px] text-ink/60 uppercase tracking-widest", children: [_jsx("span", { className: "h-px flex-1 bg-black/10" }), "or", _jsx("span", { className: "h-px flex-1 bg-black/10" })] }), _jsxs("button", { onClick: handleVoice, disabled: !form.company_name_raw, className: "w-full bg-white text-midnight border border-midnight/20 hover:border-royal hover:text-royal py-3 rounded-lg font-semibold disabled:opacity-40 flex items-center justify-center gap-2", children: [_jsx("span", { "aria-hidden": "true", children: "\uD83C\uDF99\uFE0F" }), " Take it by voice"] }), _jsx("p", { className: "mt-3 text-[12px] text-ink/70", children: "Speak with the DXC AI interviewer; it guides you through the six dimensions conversationally." })] })] })] }));
}
//# sourceMappingURL=Landing.js.map