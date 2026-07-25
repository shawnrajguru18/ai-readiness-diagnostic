import { jsx as _jsx } from "react/jsx-runtime";
import { DXC_PATH } from '@/constants';
export function DxcLogo({ h = 22, className = '' }) {
    return (_jsx("svg", { viewBox: "0 0 860 240", height: h, style: { width: (860 / 240) * h, display: 'block' }, className: className, role: "img", "aria-label": "DXC", children: _jsx("path", { d: DXC_PATH, fill: "currentColor" }) }));
}
//# sourceMappingURL=DxcLogo.js.map