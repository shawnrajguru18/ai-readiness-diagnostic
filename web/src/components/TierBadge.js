import { jsx as _jsx } from "react/jsx-runtime";
import { TIER_COLOR } from '@/constants';
export function TierBadge({ tier }) {
    return (_jsx("span", { className: "px-3 py-1 rounded-full text-xs font-bold text-midnight", style: { background: TIER_COLOR[tier] }, children: tier }));
}
//# sourceMappingURL=TierBadge.js.map