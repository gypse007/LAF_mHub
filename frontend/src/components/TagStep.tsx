interface TagStepProps {
    tags: Record<string, string>;
    onTagsChange: (tags: Record<string, string>) => void;
}

const ROOM_TAGS = [
    { id: 'entrance', label: '🚪 Entrance', icon: '🚪' },
    { id: 'living_room', label: '🛋️ Living Room', icon: '🛋️' },
    { id: 'kids_bedroom', label: '🧸 Kids Bedroom', icon: '🧸' },
    { id: 'bedroom', label: '🛏️ Master Bedroom', icon: '🛏️' },
    { id: 'kitchen', label: '🍳 Kitchen', icon: '🍳' },
    { id: 'dining_room', label: '🍽️ Dining Room', icon: '🍽️' },
    { id: 'bathroom', label: '🚿 Bathroom', icon: '🚿' },
    { id: 'office', label: '💼 Office', icon: '💼' },
];

const COMMERCIAL_TAGS = [
    { id: 'restaurant', label: '🍴 Restaurant', icon: '🍴' },
    { id: 'cafe', label: '☕ Cafe', icon: '☕' },
    { id: 'hotel_lobby', label: '🏨 Hotel Lobby', icon: '🏨' },
    { id: 'salon', label: '💇 Salon', icon: '💇' },
    { id: 'gym', label: '🏋️ Gym', icon: '🏋️' },
    { id: 'store', label: '🏪 Retail Store', icon: '🏪' },
];

const ENVIRONMENT_TAGS = [
    { id: 'indoor', label: '🏠 Indoor' },
    { id: 'outdoor', label: '🌳 Outdoor' },
    { id: 'semi_outdoor', label: '🪟 Semi-Outdoor' },
];

const PROPERTY_TAGS = [
    { id: 'apartment', label: '🏢 Apartment' },
    { id: 'villa', label: '🏡 Villa' },
    { id: 'commercial', label: '🏗️ Commercial' },
    { id: 'studio', label: '🎨 Studio' },
];

export default function TagStep({ tags, onTagsChange }: TagStepProps) {
    const setTag = (key: string, value: string) => {
        onTagsChange({ ...tags, [key]: tags[key] === value ? '' : value });
    };

    return (
        <div className="step-container">
            <div className="step-header">
                <h2 className="step-title">Tag Your Wall</h2>
                <p className="step-subtitle">Help the AI understand your space for better suggestions</p>
            </div>

            <div className="card">
                <div className="tag-section">
                    <div className="tag-section-title">Room Type — Home</div>
                    <div className="tag-grid">
                        {ROOM_TAGS.map((tag) => (
                            <button
                                key={tag.id}
                                className={`tag-chip ${tags.wall_type === tag.id ? 'selected' : ''}`}
                                onClick={() => setTag('wall_type', tag.id)}
                            >
                                {tag.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="tag-section">
                    <div className="tag-section-title">Room Type — Commercial</div>
                    <div className="tag-grid">
                        {COMMERCIAL_TAGS.map((tag) => (
                            <button
                                key={tag.id}
                                className={`tag-chip ${tags.wall_type === tag.id ? 'selected' : ''}`}
                                onClick={() => setTag('wall_type', tag.id)}
                            >
                                {tag.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="tag-section">
                    <div className="tag-section-title">Environment</div>
                    <div className="tag-grid">
                        {ENVIRONMENT_TAGS.map((tag) => (
                            <button
                                key={tag.id}
                                className={`tag-chip ${tags.environment === tag.id ? 'selected' : ''}`}
                                onClick={() => setTag('environment', tag.id)}
                            >
                                {tag.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="tag-section">
                    <div className="tag-section-title">Property Type</div>
                    <div className="tag-grid">
                        {PROPERTY_TAGS.map((tag) => (
                            <button
                                key={tag.id}
                                className={`tag-chip ${tags.property_type === tag.id ? 'selected' : ''}`}
                                onClick={() => setTag('property_type', tag.id)}
                            >
                                {tag.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
