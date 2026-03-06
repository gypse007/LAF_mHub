import { useState, useEffect } from 'react';

interface GenerateStepProps {
    isLoading: boolean;
    error: string | null;
}

const STATUSES = [
    { text: 'Analyzing wall structure...', sub: 'Understanding perspective and lighting' },
    { text: 'Preparing print area...', sub: 'Creating masked template' },
    { text: 'Generating mural artwork...', sub: 'Applying selected style to wall' },
    { text: 'Compositing final preview...', sub: 'Blending mural with wall photo' },
    { text: 'Almost there...', sub: 'Final quality adjustments' },
];

export default function GenerateStep({ isLoading, error }: GenerateStepProps) {
    const [statusIndex, setStatusIndex] = useState(0);

    useEffect(() => {
        if (!isLoading) return;
        setStatusIndex(0);
        const interval = setInterval(() => {
            setStatusIndex((prev) => (prev < STATUSES.length - 1 ? prev + 1 : prev));
        }, 1500);
        return () => clearInterval(interval);
    }, [isLoading]);

    if (error) {
        return (
            <div className="step-container">
                <div className="generate-container">
                    <div style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</div>
                    <div className="generate-status" style={{ color: 'var(--danger)' }}>
                        Generation Failed
                    </div>
                    <div className="generate-substatus">{error}</div>
                </div>
            </div>
        );
    }

    return (
        <div className="step-container">
            <div className="generate-container">
                <div className="generate-spinner" />
                <div className="generate-status">
                    {STATUSES[statusIndex].text}
                </div>
                <div className="generate-substatus">
                    {STATUSES[statusIndex].sub}
                </div>

                <div style={{
                    display: 'flex',
                    gap: 6,
                    marginTop: 32,
                }}>
                    {STATUSES.map((_, i) => (
                        <div
                            key={i}
                            style={{
                                width: 40,
                                height: 4,
                                borderRadius: 2,
                                background: i <= statusIndex
                                    ? 'var(--accent)'
                                    : 'var(--border)',
                                transition: 'background 0.3s ease',
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
