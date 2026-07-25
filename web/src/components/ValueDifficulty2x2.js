import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { QUAD_LABEL } from '@/constants';
export function ValueDifficulty2x2({ items }) {
    if (!items || !items.length)
        return null;
    const s = 320;
    const pad = 58;
    const counts = {};
    const idx = {};
    const pts = items.map((it, i) => ({
        ...it,
        n: i + 1,
        key: Math.round(it.difficulty_score * 10) + '_' + Math.round(it.value_score * 10),
    }));
    pts.forEach((p) => {
        counts[p.key] = (counts[p.key] || 0) + 1;
    });
    pts.forEach((p) => {
        const m = counts[p.key];
        const k = (idx[p.key] = (idx[p.key] || 0) + 1);
        let dx = 0, dy = 0;
        if (m > 1) {
            const a = (2 * Math.PI * (k - 1)) / m;
            const r = 0.055;
            dx = Math.cos(a) * r;
            dy = Math.sin(a) * r;
        }
        p.vx = Math.min(0.92, Math.max(0.08, p.difficulty_score + dx));
        p.vy = Math.min(0.92, Math.max(0.08, p.value_score + dy));
    });
    const X = (d) => pad + d * s;
    const Y = (v) => pad + (1 - v) * s;
    return (_jsxs("div", { className: "flex flex-col lg:flex-row gap-8 items-start", children: [_jsxs("svg", { width: s + pad * 1.3, height: s + pad * 1.4, viewBox: `0 0 ${s + pad * 1.3} ${s + pad * 1.4}`, className: "flex-none", role: "img", "aria-label": "Value versus difficulty map", children: [_jsx("rect", { x: pad, y: pad, width: s / 2, height: s / 2, fill: "#EAF2FF" }), _jsx("rect", { x: pad, y: pad, width: s, height: s, fill: "none", stroke: "#C9C4BC" }), _jsx("line", { x1: pad + s / 2, y1: pad, x2: pad + s / 2, y2: pad + s, stroke: "#E6E1DA" }), _jsx("line", { x1: pad, y1: pad + s / 2, x2: pad + s, y2: pad + s / 2, stroke: "#E6E1DA" }), _jsx("text", { x: pad + 8, y: pad + 16, fontSize: "10", fontWeight: "700", fill: "#004AAC", children: "QUICK WINS" }), _jsx("text", { x: pad + s - 8, y: pad + 16, fontSize: "10", fontWeight: "700", fill: "#8A867E", textAnchor: "end", children: "STRATEGIC BETS" }), _jsx("text", { x: pad + 8, y: pad + s - 8, fontSize: "10", fontWeight: "600", fill: "#B7B1A8", children: "FILL-INS" }), _jsx("text", { x: pad + s - 8, y: pad + s - 8, fontSize: "10", fontWeight: "600", fill: "#B7B1A8", textAnchor: "end", children: "DEPRIORITIZE" }), _jsx("text", { x: pad + s / 2, y: pad + s + 26, fontSize: "11", fontWeight: "600", fill: "#3D3F50", textAnchor: "middle", children: "Implementation difficulty \u2192" }), _jsx("text", { x: 20, y: pad + s / 2, fontSize: "11", fontWeight: "600", fill: "#3D3F50", textAnchor: "middle", transform: `rotate(-90 20 ${pad + s / 2})`, children: "Business value \u2192" }), pts.map((p, i) => (_jsxs("g", { children: [_jsx("circle", { cx: X(p.vx ?? 0), cy: Y(p.vy ?? 0), r: "12", fill: "#004AAC" }), _jsx("text", { x: X(p.vx ?? 0), y: (Y(p.vy ?? 0)) + 4, fontSize: "12", fontWeight: "700", fill: "#fff", textAnchor: "middle", children: p.n })] }, i)))] }), _jsxs("div", { className: "flex-1", children: [_jsx("ol", { className: "space-y-2", children: pts.map((p, i) => (_jsxs("li", { className: "flex gap-3 text-sm items-start", children: [_jsx("span", { className: "flex-none w-6 h-6 rounded-full bg-royal text-white text-xs font-bold flex items-center justify-center", children: p.n }), _jsxs("span", { children: [_jsx("b", { children: p.opportunity }), ' ', _jsxs("span", { className: "text-ink", children: ["\u00B7 ", QUAD_LABEL[p.quadrant] || ''] })] })] }, i))) }), _jsx("p", { className: "text-xs text-ink mt-4 pt-3 border-t border-black/10", children: "Upper-left quadrant = highest value for the least effort. Start there." })] })] }));
}
//# sourceMappingURL=ValueDifficulty2x2.js.map