import { QuestionPool, Answer } from '@/types';
interface AssessmentProps {
    pool: QuestionPool | null;
    initialAnswers?: Record<string, Answer>;
    onSubmit: (answers: Record<string, Answer>) => void;
    onBack: () => void;
    onVoice?: (answers: Record<string, Answer>) => void;
}
export declare function Assessment({ pool, initialAnswers, onSubmit, onBack, onVoice, }: AssessmentProps): import("react").JSX.Element | null;
export {};
//# sourceMappingURL=Assessment.d.ts.map