import { FormData, ConsentData } from '@/types';
interface LandingProps {
    onBegin: (form: FormData, consent: ConsentData) => void;
    onVoice: (form: FormData, consent: ConsentData) => void;
    onSample: () => void;
}
export declare function Landing({ onBegin, onVoice, onSample }: LandingProps): import("react").JSX.Element;
export {};
//# sourceMappingURL=Landing.d.ts.map