import { QuestionPool, Answer } from '@/types';
interface AssessmentProps {
    pool: QuestionPool | null;
    initialAnswers?: Record<string, Answer>;
    onSubmit: (answers: Record<string, Answer>) => void;
    onBack: () => void;
    onVoice?: (answers: Record<string, Answer>) => void;
    isSubmitting?: boolean;
}
export declare function Assessment({ pool, initialAnswers, onSubmit, onBack, onVoice, isSubmitting, }: AssessmentProps): import("react").JSX.Element | null;
export {};
//# sourceMappingURL=Assessment.d.ts.map