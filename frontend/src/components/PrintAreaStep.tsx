import { useRef, useState, useCallback, useEffect } from 'react';
import { detectWalls } from '../api';

interface PrintAreaStepProps {
    wallId: string;
    imagePreview: string;
    printArea: number[][];
    onPrintAreaChange: (area: number[][]) => void;
    wallSize: { width: number; height: number } | null;
    onWallSizeChange: (size: { width: number; height: number } | null) => void;
}

export default function PrintAreaStep({ wallId, imagePreview, printArea, onPrintAreaChange, wallSize, onWallSizeChange }: PrintAreaStepProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [startNatural, setStartNatural] = useState<{ x: number; y: number } | null>(null);
    const [currentNatural, setCurrentNatural] = useState<{ x: number; y: number } | null>(null);

    // Auto Wall Detection
    const [detectedPolygons, setDetectedPolygons] = useState<number[][][]>([]);
    const [isDetecting, setIsDetecting] = useState(false);
    const [hoveredPoly, setHoveredPoly] = useState<number | null>(null);
    const [imgNatural, setImgNatural] = useState<{ w: number; h: number } | null>(null);

    // ─── Get natural (pixel) coords from mouse/touch event ───
    const getNaturalPos = useCallback((clientX: number, clientY: number) => {
        if (!containerRef.current || !imgNatural) return null;
        const imgEl = containerRef.current.querySelector('img');
        if (!imgEl) return null;
        const rect = imgEl.getBoundingClientRect();

        const px = Math.max(0, Math.min(rect.width, clientX - rect.left));
        const py = Math.max(0, Math.min(rect.height, clientY - rect.top));

        return {
            x: Math.round((px / rect.width) * imgNatural.w),
            y: Math.round((py / rect.height) * imgNatural.h),
        };
    }, [imgNatural]);

    // ─── Pointer handlers (mouse + touch unified) ───
    const onPointerDown = useCallback((e: React.PointerEvent) => {
        if ((e.target as HTMLElement).closest('[data-polygon-index]')) return;
        e.preventDefault();
        (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
        const pos = getNaturalPos(e.clientX, e.clientY);
        if (!pos) return;
        setIsDrawing(true);
        setStartNatural(pos);
        setCurrentNatural(pos);
    }, [getNaturalPos]);

    const onPointerMove = useCallback((e: React.PointerEvent) => {
        if (!isDrawing) return;
        e.preventDefault();
        const pos = getNaturalPos(e.clientX, e.clientY);
        if (pos) setCurrentNatural(pos);
    }, [isDrawing, getNaturalPos]);

    const onPointerUp = useCallback((e: React.PointerEvent) => {
        if (!isDrawing || !startNatural) return;
        setIsDrawing(false);
        const pos = getNaturalPos(e.clientX, e.clientY);
        if (!pos) return;

        // Only register if the area is big enough (>20px in natural coords)
        if (Math.abs(pos.x - startNatural.x) > 20 && Math.abs(pos.y - startNatural.y) > 20) {
            const x1 = Math.min(startNatural.x, pos.x);
            const y1 = Math.min(startNatural.y, pos.y);
            const x2 = Math.max(startNatural.x, pos.x);
            const y2 = Math.max(startNatural.y, pos.y);
            onPrintAreaChange([[x1, y1], [x2, y1], [x2, y2], [x1, y2]]);
        }
        setStartNatural(null);
        setCurrentNatural(null);
    }, [isDrawing, startNatural, getNaturalPos, onPrintAreaChange]);

    // ─── Image load ───
    const onImgLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
        const img = e.target as HTMLImageElement;
        setImgNatural({ w: img.naturalWidth, h: img.naturalHeight });
    }, []);

    // ─── Auto wall detection ───
    useEffect(() => {
        if (!wallId || printArea.length > 0) return;
        let alive = true;
        (async () => {
            setIsDetecting(true);
            try {
                const res = await detectWalls(wallId);
                if (alive && res.detected_walls) setDetectedPolygons(res.detected_walls);
            } catch { /* ignore */ }
            finally { if (alive) setIsDetecting(false); }
        })();
        return () => { alive = false; };
    }, [wallId, printArea.length]);

    // ─── Polygon click → set bounding box as print area ───
    const onPolyClick = useCallback((poly: number[][]) => {
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        poly.forEach(([x, y]) => {
            minX = Math.min(minX, x); minY = Math.min(minY, y);
            maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
        });
        onPrintAreaChange([[minX, minY], [maxX, minY], [maxX, maxY], [minX, maxY]]);
    }, [onPrintAreaChange]);

    // ─── Compute the rect to highlight (either live-drawing or saved) ───
    const getHighlight = (): { x: number; y: number; w: number; h: number } | null => {
        if (isDrawing && startNatural && currentNatural) {
            const x = Math.min(startNatural.x, currentNatural.x);
            const y = Math.min(startNatural.y, currentNatural.y);
            return { x, y, w: Math.abs(currentNatural.x - startNatural.x), h: Math.abs(currentNatural.y - startNatural.y) };
        }
        if (printArea.length >= 4) {
            const x = printArea[0][0], y = printArea[0][1];
            const w = printArea[2][0] - x, h = printArea[2][1] - y;
            return { x, y, w: Math.abs(w), h: Math.abs(h) };
        }
        return null;
    };

    const highlight = getHighlight();
    const vb = imgNatural ? `0 0 ${imgNatural.w} ${imgNatural.h}` : undefined;

    return (
        <div className="step-container">
            <div className="step-header">
                <h2 className="step-title">Select Your Wall</h2>
                <p className="step-subtitle">
                    {isDetecting && '🔍 AI is detecting walls...'}
                    {!isDetecting && printArea.length === 0 && detectedPolygons.length > 0 && 'Tap a highlighted wall, or draw your own area'}
                    {!isDetecting && printArea.length === 0 && detectedPolygons.length === 0 && 'Draw a rectangle on the area you want the mural'}
                    {printArea.length > 0 && '✅ Wall selected! You can redraw or continue.'}
                </p>
            </div>

            {/* Instruction banner */}
            {printArea.length === 0 && !isDetecting && (
                <div className="canvas-instructions">
                    <span className="icon">👆</span>
                    {detectedPolygons.length > 0
                        ? 'Tap a purple highlighted area, or drag to draw your own'
                        : 'Tap and drag on the photo to select the wall area'}
                </div>
            )}

            {/* Canvas with image + SVG overlay */}
            <div
                className="canvas-container"
                ref={containerRef}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerUp}
                style={{ touchAction: 'none' }}
            >
                <img
                    src={imagePreview}
                    alt="Your wall"
                    onLoad={onImgLoad}
                    draggable={false}
                    style={{ display: 'block', width: '100%', height: 'auto' }}
                />

                {imgNatural && (
                    <svg
                        className="canvas-overlay"
                        viewBox={vb}
                        preserveAspectRatio="xMidYMid meet"
                        style={{ pointerEvents: 'none' }}
                    >
                        {/* Auto-detected polygons */}
                        {printArea.length === 0 && detectedPolygons.map((poly, idx) => {
                            const pts = poly.map(([x, y]) => `${x},${y}`).join(' ');
                            return (
                                <polygon
                                    key={idx}
                                    data-polygon-index={idx}
                                    points={pts}
                                    fill={hoveredPoly === idx ? 'rgba(108,92,231,0.45)' : 'rgba(108,92,231,0.2)'}
                                    stroke="#6c5ce7"
                                    strokeWidth={Math.max(2, (imgNatural?.w || 1000) / 300)}
                                    strokeLinejoin="round"
                                    strokeDasharray={hoveredPoly === idx ? 'none' : `${(imgNatural?.w || 1000) / 80},${(imgNatural?.w || 1000) / 120}`}
                                    style={{ pointerEvents: 'auto', cursor: 'pointer', transition: 'fill 0.2s, stroke-dasharray 0.3s' }}
                                    onPointerEnter={() => setHoveredPoly(idx)}
                                    onPointerLeave={() => setHoveredPoly(null)}
                                    onClick={() => onPolyClick(poly)}
                                />
                            );
                        })}

                        {/* Selected / drawing rectangle */}
                        {highlight && (
                            <>
                                {/* Dim outside */}
                                <defs>
                                    <mask id="wall-cutout">
                                        <rect width="100%" height="100%" fill="white" />
                                        <rect x={highlight.x} y={highlight.y} width={highlight.w} height={highlight.h} fill="black" />
                                    </mask>
                                </defs>
                                <rect width="100%" height="100%" fill="rgba(0,0,0,0.55)" mask="url(#wall-cutout)" />

                                {/* Border */}
                                <rect
                                    x={highlight.x} y={highlight.y}
                                    width={highlight.w} height={highlight.h}
                                    fill="none"
                                    stroke="#a29bfe"
                                    strokeWidth={Math.max(3, (imgNatural?.w || 1000) / 250)}
                                    strokeDasharray={`${(imgNatural?.w || 1000) / 60},${(imgNatural?.w || 1000) / 100}`}
                                />

                                {/* Corner circles */}
                                {[
                                    [highlight.x, highlight.y],
                                    [highlight.x + highlight.w, highlight.y],
                                    [highlight.x + highlight.w, highlight.y + highlight.h],
                                    [highlight.x, highlight.y + highlight.h],
                                ].map(([cx, cy], i) => (
                                    <circle
                                        key={i}
                                        cx={cx} cy={cy}
                                        r={Math.max(8, (imgNatural?.w || 1000) / 120)}
                                        fill="#6c5ce7"
                                        stroke="white"
                                        strokeWidth={Math.max(2, (imgNatural?.w || 1000) / 400)}
                                    />
                                ))}

                                {/* Label */}
                                <text
                                    x={highlight.x + highlight.w / 2}
                                    y={highlight.y + highlight.h / 2}
                                    textAnchor="middle"
                                    dominantBaseline="middle"
                                    fill="white"
                                    fontSize={Math.max(14, (imgNatural?.w || 1000) / 40)}
                                    fontWeight="600"
                                    opacity="0.9"
                                >
                                    Mural Area
                                </text>
                            </>
                        )}
                    </svg>
                )}
            </div>

            {/* Calibration section */}
            {printArea.length > 0 && (
                <div className="card" style={{ marginTop: 16 }}>
                    <h3 style={{ margin: '0 0 12px', fontSize: '1rem' }}>📏 Wall Dimensions (optional)</h3>
                    <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        For print-ready panels, enter the real wall size.
                    </p>
                    <div className="wall-size-inputs">
                        <input
                            type="number"
                            inputMode="decimal"
                            placeholder="Width (ft)"
                            value={wallSize?.width || ''}
                            onChange={(e) => onWallSizeChange({ width: parseFloat(e.target.value) || 0, height: wallSize?.height || 0 })}
                        />
                        <input
                            type="number"
                            inputMode="decimal"
                            placeholder="Height (ft)"
                            value={wallSize?.height || ''}
                            onChange={(e) => onWallSizeChange({ width: wallSize?.width || 0, height: parseFloat(e.target.value) || 0 })}
                        />
                    </div>
                    <div style={{ textAlign: 'center', marginTop: 16 }}>
                        <button
                            className="btn btn-secondary"
                            onClick={() => {
                                onPrintAreaChange([]);
                                setStartNatural(null);
                                setCurrentNatural(null);
                                onWallSizeChange(null);
                            }}
                        >
                            🔄 Redraw Area
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
