import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function Radar({ dims, color, size = 360 }) {
    const n = dims.length;
    const cx = size / 2;
    const cy = size / 2;
    const R = size * 0.34;
    const pt = (i, frac) => {
        const a = (2 * Math.PI * i) / n - Math.PI / 2;
        return [cx + R * frac * Math.cos(a), cy + R * frac * Math.sin(a)];
    };
    const ring = (t) => dims.map((_, i) => pt(i, t).join(',')).join(' ');
    const you = dims.map((d, i) => pt(i, d.score / 100).join(',')).join(' ');
    return (_jsxs("svg", { width: size, height: size, viewBox: `0 0 ${size} ${size}`, className: "fade", children: [[0.25, 0.5, 0.75, 1].map((t, k) => (_jsx("polygon", { points: ring(t), fill: "none", stroke: "#D9D5CE", strokeWidth: "1" }, k))), dims.map((_, i) => {
                const [x, y] = pt(i, 1);
                return (_jsx("line", { x1: cx, y1: cy, x2: x, y2: y, stroke: "#E6E1DA" }, i));
            }), _jsx("polygon", { points: you, fill: color + '55', stroke: color, strokeWidth: "2.5" }), dims.map((d, i) => {
                const [x, y] = pt(i, d.score / 100);
                return (_jsx("circle", { cx: x, cy: y, r: "3.5", fill: color, stroke: "#0E1020", strokeWidth: "1" }, i));
            }), dims.map((d, i) => {
                const [x, y] = pt(i, 1.17);
                const anchor = Math.abs(x - cx) < 14 ? 'middle' : x > cx ? 'start' : 'end';
                return (_jsx("text", { x: x, y: y, fontSize: "11", fontWeight: "600", fill: "#0E1020", textAnchor: anchor, dominantBaseline: "middle", children: d.label.split(' & ')[0] }, i));
            }), dims.map((d, i) => {
                const [x, y] = pt(i, d.score / 100);
                return (_jsx("text", { x: x, y: y - 9, fontSize: "11", fontWeight: "700", fill: "#0E1020", textAnchor: "middle", children: d.score }, 's' + i));
            })] }));
}
//# sourceMappingURL=Radar.js.map