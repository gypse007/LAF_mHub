import { useCallback, useState, useRef } from 'react';

interface UploadStepProps {
    onUpload: (file: File, preview: string) => void;
    preview: string | null;
}

export default function UploadStep({ onUpload, preview }: UploadStepProps) {
    const [isDragOver, setIsDragOver] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const cameraRef = useRef<HTMLInputElement>(null);

    const processFile = useCallback((file: File) => {
        setIsUploading(true);
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                // In App.tsx handleUpload is async, so we await it
                await onUpload(file, e.target?.result as string);
            } finally {
                setIsUploading(false);
            }
        };
        reader.readAsDataURL(file);
    }, [onUpload]);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            processFile(file);
        }
    }, [processFile]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) processFile(file);
    }, [processFile]);

    return (
        <div className="step-container">
            <div className="step-header">
                <h2 className="step-title">Upload Your Wall</h2>
                <p className="step-subtitle">Take a photo or upload an image of the wall you want to transform</p>
            </div>

            {/* Camera button — primary action on mobile */}
            {!preview && (
                <button
                    className="btn btn-primary camera-capture-btn"
                    onClick={() => cameraRef.current?.click()}
                >
                    📷 Take a Photo of Your Wall
                </button>
            )}

            <div
                className={`upload-zone ${isDragOver ? 'dragover' : ''} ${preview ? 'has-image' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={(!isUploading) ? () => inputRef.current?.click() : undefined}
                style={{ cursor: isUploading ? 'not-allowed' : 'pointer' }}
            >
                {isUploading ? (
                    <div className="upload-loading" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                        <div className="generate-spinner" style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                        <div style={{ fontWeight: 600 }}>Analyzing Wall...</div>
                    </div>
                ) : preview ? (
                    <>
                        <img src={preview} alt="Wall preview" className="upload-preview" />
                        <div className="upload-overlay">
                            <span className="upload-overlay-text">Tap to change photo</span>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="upload-icon">🖼️</div>
                        <div className="upload-text">
                            {isDragOver ? 'Drop your photo here!' : 'Or browse from gallery'}
                        </div>
                        <div className="upload-hint">JPG, PNG, WebP up to 20MB</div>
                    </>
                )}

                {/* Gallery / file picker */}
                <input
                    ref={inputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleChange}
                    style={{ display: 'none' }}
                />

                {/* Camera capture — opens rear camera on mobile */}
                <input
                    ref={cameraRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handleChange}
                    style={{ display: 'none' }}
                />
            </div>
        </div>
    );
}
