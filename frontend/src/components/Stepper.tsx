import React from 'react';

interface StepperProps {
    steps: string[];
    currentStep: number;
    onStepClick: (step: number) => void;
    completedSteps: number[];
}

export default function Stepper({ steps, currentStep, onStepClick, completedSteps }: StepperProps) {
    return (
        <div className="stepper">
            {steps.map((step, i) => {
                const isActive = i === currentStep;
                const isCompleted = completedSteps.includes(i);

                return (
                    <React.Fragment key={i}>
                        {i > 0 && (
                            <div className={`stepper-connector ${isCompleted || isActive ? 'active' : ''}`} />
                        )}
                        <div
                            className={`stepper-step ${isActive ? 'active' : isCompleted ? 'completed' : 'pending'}`}
                            onClick={() => (isCompleted || isActive) && onStepClick(i)}
                            role="button"
                            tabIndex={0}
                        >
                            <div className="step-number">
                                {isCompleted ? '✓' : i + 1}
                            </div>
                            <span className="step-label">{step}</span>
                        </div>
                    </React.Fragment>
                );
            })}
        </div>
    );
}
