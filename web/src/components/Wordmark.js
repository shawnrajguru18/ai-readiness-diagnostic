import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { DxcLogo } from './DxcLogo';
export function Wordmark({ onDark = false }) {
    return (_jsxs("div", { className: `flex items-center gap-2.5 ${onDark ? 'text-white' : 'text-midnight'}`, children: [_jsx(DxcLogo, { h: 20 }), _jsx("span", { className: "w-px h-4 bg-current opacity-25" }), _jsx("span", { className: `text-sm font-semibold ${onDark ? 'text-white/80' : 'text-ink'}`, children: "AdvisoryX" })] }));
}
//# sourceMappingURL=Wordmark.js.map