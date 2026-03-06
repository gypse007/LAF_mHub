import { useEffect, useState } from 'react';
import { getStyles, getStyleSuggestions, uploadReferenceImage } from '../api';

interface StylePreset {
    id: string;
    name: string;
    description: string;
    colors: string[];
    tags: string[];
}

interface StyleStepProps {
    wallId: string;
    selectedStyle: string;
    onStyleSelect: (styleId: string) => void;
    wallTags: Record<string, string>;
}

export default function StyleStep({ wallId, selectedStyle, onStyleSelect, wallTags }: StyleStepProps) {
    const [styles, setStyles] = useState<StylePreset[]>([]);
    const [loading, setLoading] = useState(true);
    const [refImage, setRefImage] = useState<string | null>(null);
    const [uploadingRef, setUploadingRef] = useState(false);

    const handleRefUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !wallId || wallId.startsWith('local-')) return;

        setUploadingRef(true);
        try {
            await uploadReferenceImage(wallId, file);
            setRefImage(URL.createObjectURL(file));
        } catch (err) {
            console.error('Failed to upload reference image', err);
        } finally {
            setUploadingRef(false);
        }
    };

    useEffect(() => {
        async function fetchStyles() {
            try {
                const tags = Object.values(wallTags).filter(Boolean);
                const data = tags.length > 0
                    ? await getStyleSuggestions(tags)
                    : await getStyles();
                setStyles(data.styles || []);
            } catch {
                // Fallback: hardcoded styles if API not available
                setStyles([
                    { id: 'modern_abstract', name: 'Modern Abstract', description: 'Bold shapes and vibrant colors', colors: ['#FF6B35', '#004E89', '#1A1A2E', '#F7C948'], tags: [] },
                    { id: 'nature_landscape', name: 'Nature Landscape', description: 'Serene forests and meadows', colors: ['#2D6A4F', '#52B788', '#95D5B2', '#D8F3DC'], tags: [] },
                    { id: 'geometric', name: 'Geometric Patterns', description: 'Clean lines and symmetry', colors: ['#264653', '#2A9D8F', '#E9C46A', '#F4A261'], tags: [] },
                    { id: 'minimal_texture', name: 'Minimal Texture', description: 'Subtle elegant simplicity', colors: ['#E8E4D9', '#C4B7A6', '#8B7E74', '#5C5248'], tags: [] },
                    { id: 'temple_art', name: 'Temple Art', description: 'Traditional Indian motifs', colors: ['#B8860B', '#DAA520', '#8B4513', '#F4E3B2'], tags: [] },
                    { id: 'ocean_waves', name: 'Ocean Waves', description: 'Calming ocean patterns', colors: ['#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8'], tags: [] },
                    { id: 'luxury_gold', name: 'Luxury Gold', description: 'Opulent gold textures', colors: ['#1A1A2E', '#DAA520', '#FFD700', '#2C2C54'], tags: [] },
                    { id: 'botanical', name: 'Botanical Garden', description: 'Lush tropical plants', colors: ['#606C38', '#283618', '#FEFAE0', '#DDA15E'], tags: [] },
                ]);
            } finally {
                setLoading(false);
            }
        }

        fetchStyles();
    }, [wallTags]);

    if (loading) {
        return (
            <div className="step-container">
                <div className="step-header">
                    <h2 className="step-title">Choose Your Style</h2>
                    <p className="step-subtitle">Loading personalized suggestions...</p>
                </div>
                <div className="generate-container">
                    <div className="generate-spinner" />
                </div>
            </div>
        );
    }

    return (
        <div className="step-container">
            <div className="step-header">
                <h2 className="step-title">Choose Your Style</h2>
                <p className="step-subtitle">
                    {Object.values(wallTags).some(Boolean)
                        ? 'Personalized suggestions based on your wall tags'
                        : 'Browse our curated collection of mural styles'}
                </p>
            </div>

            {/* Reference Image Upload */}
            <div style={{ marginBottom: 32, background: 'var(--surface)', padding: 24, borderRadius: 12, border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <div>
                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Have an inspiration image? 💡</h3>
                        <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Upload a reference and our AI will match its exact vibe, colors, and mood.
                        </p>
                    </div>
                </div>

                <div className="upload-zone" style={{ minHeight: 120, padding: 16 }}>
                    {refImage ? (
                        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                            <img src={refImage} alt="Reference" style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 8 }} />
                            <div>
                                <div style={{ color: 'var(--success)', fontWeight: 600, marginBottom: 8 }}>✓ Style Reference Active</div>
                                <label className="btn btn-secondary" style={{ display: 'inline-block', fontSize: '0.9rem', padding: '6px 12px' }}>
                                    Change Image
                                    <input type="file" hidden accept="image/*" onChange={handleRefUpload} />
                                </label>
                            </div>
                        </div>
                    ) : (
                        <div className="upload-content" style={{ flexDirection: 'row', gap: 16 }}>
                            <div className="upload-icon" style={{ fontSize: '2rem' }}>🎨</div>
                            <div style={{ textAlign: 'left' }}>
                                <div>{uploadingRef ? 'Uploading...' : 'Upload Inspiration (Optional)'}</div>
                                <div className="upload-subtitle">JPG/PNG</div>
                            </div>
                            <label className="btn btn-primary" style={{ marginLeft: 'auto', display: 'inline-block' }}>
                                Browse
                                <input type="file" hidden accept="image/*" onChange={handleRefUpload} disabled={uploadingRef} />
                            </label>
                        </div>
                    )}
                </div>
            </div>

            <div className="style-grid">
                {styles.map((style) => (
                    <div
                        key={style.id}
                        className={`style-card ${selectedStyle === style.id ? 'selected' : ''}`}
                        onClick={() => onStyleSelect(style.id)}
                    >
                        <div className="style-colors">
                            {style.colors.map((color, i) => (
                                <div
                                    key={i}
                                    className="style-color-dot"
                                    style={{ backgroundColor: color }}
                                />
                            ))}
                        </div>
                        <div className="style-name">{style.name}</div>
                        <div className="style-desc">{style.description}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
