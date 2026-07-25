import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Wordmark } from '@/components/Wordmark';
import { Btn } from '@/components/Btn';
export function Submitted({ company, email, onView }) {
    return (_jsxs("div", { className: "min-h-screen bg-canvas flex flex-col", children: [_jsx("div", { className: "max-w-3xl mx-auto w-full px-6 py-6", children: _jsx(Wordmark, {}) }), _jsxs("div", { className: "max-w-2xl mx-auto px-6 flex-1 flex flex-col justify-center pb-24 fade", children: [_jsx("div", { className: "w-12 h-12 rounded-full border-2 border-royal border-t-transparent spin mb-8" }), _jsx("h1", { className: "display text-4xl font-bold", children: "Your assessment is submitted." }), _jsx("p", { className: "text-ink mt-3", children: "Here is what happens next." }), _jsx("ol", { className: "mt-8 space-y-4", children: [
                            `AI agents research ${company || 'your company'} — financials, news, tech posture`,
                            'Our synthesis engine scores your readiness across six dimensions',
                            'A DXC senior partner reviews and approves your scorecard',
                        ].map((s, k) => (_jsxs("li", { className: "flex gap-4 items-start", children: [_jsx("span", { className: "bg-midnight text-white w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold flex-none", children: k + 1 }), _jsx("span", { className: "pt-1", children: s })] }, k))) }), _jsxs("p", { className: "mt-8 text-ink", children: ["You'll receive your scorecard within 24 hours at", ' ', _jsx("b", { className: "text-midnight", children: email || 'your email' }), ". A personal portal link will arrive with your results."] }), _jsx("div", { className: "mt-8", children: _jsx(Btn, { onClick: onView, children: "Preview your scorecard \u2192" }) })] })] }));
}
//# sourceMappingURL=Submitted.js.map