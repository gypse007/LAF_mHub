import { useCallback, useState, useRef } from 'react';

interface UploadStepProps {
    onUpload: (file: File, preview: string) => void;
    preview: string | null;
}

export default function UploadStep({ onUpload, preview }: UploadStepProps) {
    const [isDragOver, setIsDragOver] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const cameraRef = useRef<HTMLInputElement>(null);

    const handleFile = useCallback((file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            onUpload(file, e.target?.result as string);
        };
        reader.readAsDataURL(file);
    }, [onUpload]);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    }, [handleFile]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
    }, [handleFile]);

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
                onClick={() => inputRef.current?.click()}
            >
                {preview ? (
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
