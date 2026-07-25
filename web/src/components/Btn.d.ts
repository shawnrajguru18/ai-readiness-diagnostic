import { ReactNode } from 'react';
interface BtnProps {
    children: ReactNode;
    onClick?: () => void;
    kind?: 'primary' | 'ghost' | 'light';
    className?: string;
    disabled?: boolean;
}
export declare function Btn({ children, onClick, kind, className, disabled, }: BtnProps): import("react").JSX.Element;
export {};
//# sourceMappingURL=Btn.d.ts.map