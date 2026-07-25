import { jsx as _jsx } from "react/jsx-runtime";
export function Btn({ children, onClick, kind = 'primary', className = '', disabled = false, }) {
    const base = 'px-6 py-3 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-royal/40';
    const kinds = {
        primary: 'bg-royal text-white hover:bg-[#003a86]',
        ghost: 'bg-transparent text-midnight border border-midnight/20 hover:border-midnight/50',
        light: 'bg-white text-midnight border border-black/10 hover:border-black/30',
    };
    return (_jsx("button", { onClick: onClick, disabled: disabled, className: `${base} ${kinds[kind]} ${className}`, children: children }));
}
//# sourceMappingURL=Btn.js.map