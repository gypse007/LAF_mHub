import { useState, useRef, useCallback } from 'react';

interface ResultStepProps {
    originalImageUrl: string;
    generatedImageUrl: string;
    onRegenerate: (style: string) => void;
    onStartOver: () => void;
    panels?: string[];
    printResolution?: string;
}

const REGEN_STYLES = [
    { id: 'modern_abstract', label: '🎨 Modern Abstract' },
    { id: 'nature_landscape', label: '🌿 Nature' },
    { id: 'geometric', label: '📐 Geometric' },
    { id: 'luxury_gold', label: '✨ Luxury Gold' },
    { id: 'ocean_waves', label: '🌊 Ocean' },
    { id: 'botanical', label: '🌺 Botanical' },
    { id: 'temple_art', label: '🕌 Temple Art' },
    { id: 'watercolor', label: '🎨 Watercolor' },
];

export default function ResultStep({
    originalImageUrl,
    generatedImageUrl,
    onRegenerate,
    onStartOver,
    panels = [],
    printResolution,
}: ResultStepProps) {
    const [sliderPos, setSliderPos] = useState(50);
    const containerRef = useRef<HTMLDivElement>(null);
    const isDragging = useRef(false);

    const updateSlider = useCallback((clientX: number) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const x = clientX - rect.left;
        const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
        setSliderPos(pct);
    }, []);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        isDragging.current = true;
        updateSlider(e.clientX);
    }, [updateSlider]);

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        if (!isDragging.current) return;
        updateSlider(e.clientX);
    }, [updateSlider]);

    const handleMouseUp = useCallback(() => {
        isDragging.current = false;
    }, []);

    const handleTouchMove = useCallback((e: React.TouchEvent) => {
        updateSlider(e.touches[0].clientX);
    }, [updateSlider]);

    const handleDownload = useCallback(() => {
        const a = document.createElement('a');
        a.href = generatedImageUrl;
        a.download = 'wall-mural-preview.jpg';
        a.click();
    }, [generatedImageUrl]);

    return (
        <div className="step-container">
            <div className="step-header">
                <h2 className="step-title">Your Mural Preview</h2>
                <p className="step-subtitle">Drag the slider to compare before and after</p>
            </div>

            {/* Before/After Slider */}
            <div
                className="before-after"
                ref={containerRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onTouchMove={handleTouchMove}
                onTouchStart={(e) => updateSlider(e.touches[0].clientX)}
            >
                {/* After image (full width) */}
                <img src={generatedImageUrl} alt="After — with mural" />

                {/* Before image (clipped) */}
                <div
                    className="before-image"
                    style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
                >
                    <img src={originalImageUrl} alt="Before — original wall" />
                </div>

                {/* Slider line */}
                <div className="slider-line" style={{ left: `${sliderPos}%` }} />

                {/* Slider handle */}
                <div
                    className="slider-handle"
                    style={{ left: `${sliderPos}%` }}
                >
                    ⟷
                </div>

                {/* Labels */}
                <div className="result-label before">BEFORE</div>
                <div className="result-label after">AFTER</div>
            </div>

            {/* Actions */}
            <div className="result-actions">
                <button className="btn btn-success" onClick={handleDownload}>
                    ⬇️ Download Preview
                </button>
                <button className="btn btn-primary" onClick={onStartOver}>
                    📸 New Wall
                </button>
            </div>

            {/* Print Panels Section */}
            {panels.length > 0 && (
                <div style={{ marginTop: 40, borderTop: '1px solid var(--border)', paddingTop: 32 }}>
                    <div style={{ textAlign: 'center', marginBottom: 24 }}>
                        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', color: 'var(--success)' }}>
                            🖨️ Print-Ready Pipeline Generated
                        </h3>
                        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Calculated Target Resolution: <strong>{printResolution} (150 DPI)</strong> <br />
                            Split into <strong>{panels.length} panels</strong> (60cm width each) for commercial printing.
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 16 }}>
                        {panels.map((p, i) => (
                            <div key={i} style={{ minWidth: 100, flex: '0 0 auto', textAlign: 'center' }}>
                                <img src={p} alt={`Panel ${i + 1}`} style={{ width: 100, height: 250, objectFit: 'cover', borderRadius: 4, border: '1px solid var(--border)' }} />
                                <div style={{ fontSize: '0.8rem', marginTop: 8, color: 'var(--text-secondary)' }}>
                                    Panel {i + 1}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Regenerate with different styles */}
            <div style={{ textAlign: 'center', marginTop: 48 }}>
                <div style={{
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    color: 'var(--text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: 1,
                    marginBottom: 12,
                }}>
                    Try a Different Style
                </div>
                <div className="regen-styles">
                    {REGEN_STYLES.map((style) => (
                        <button
                            key={style.id}
                            className="regen-chip"
                            onClick={() => onRegenerate(style.id)}
                        >
                            {style.label}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
