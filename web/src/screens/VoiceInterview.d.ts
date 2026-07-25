import { Answer } from '@/types';
declare global {
    namespace JSX {
        interface IntrinsicElements {
            'elevenlabs-convai': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement> & {
                'agent-id'?: string;
            }, HTMLElement>;
        }
    }
}
interface VoiceInterviewProps {
    company?: string;
    industry?: string;
    name?: string;
    role?: string;
    priorAnswers?: Record<string, Answer>;
    onFinish: (answers: Record<string, Answer>) => void;
    onChat: (answers: Record<string, Answer>) => void;
    onBack: () => void;
}
export declare function VoiceInterview({ company, industry, name, role, priorAnswers, onFinish, onChat, onBack, }: VoiceInterviewProps): import("react").JSX.Element;
export {};
//# sourceMappingURL=VoiceInterview.d.ts.map