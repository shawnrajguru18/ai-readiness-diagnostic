export function personaFromRole(role = '') {
    const r = role.toLowerCase();
    if (/cfo|finance|accounting|treasurer|controller/.test(r))
        return 'P3';
    if (/cio|cto|cdo|chief data|chief ai|digital|data|architect|engineering|technolog/.test(r))
        return 'P2';
    return 'P1';
}
export const FRAMING_FOR = {
    P1: 'strategic-narrative',
    P2: 'technical-operational',
    P3: 'financial-quantitative',
};
//# sourceMappingURL=utils.js.map