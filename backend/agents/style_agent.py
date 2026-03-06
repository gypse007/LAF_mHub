"""
StyleIntelligenceAgent — Returns trending styles and tag-based suggestions.
In production, this would analyze marketplace data, user preferences, etc.
For MVP, returns curated style presets.
"""


STYLE_PRESETS = {
    "modern_abstract": {
        "id": "modern_abstract",
        "name": "Modern Abstract",
        "description": "Bold shapes and vibrant colors",
        "colors": ["#FF6B35", "#004E89", "#1A1A2E", "#F7C948"],
        "tags": ["luxury", "living_room", "office"],
    },
    "nature_landscape": {
        "id": "nature_landscape",
        "name": "Nature Landscape",
        "description": "Serene forests, mountains, and meadows",
        "colors": ["#2D6A4F", "#52B788", "#95D5B2", "#D8F3DC"],
        "tags": ["calm", "bedroom", "living_room"],
    },
    "geometric": {
        "id": "geometric",
        "name": "Geometric Patterns",
        "description": "Clean lines and mathematical beauty",
        "colors": ["#264653", "#2A9D8F", "#E9C46A", "#F4A261"],
        "tags": ["modern", "office", "entrance"],
    },
    "minimal_texture": {
        "id": "minimal_texture",
        "name": "Minimal Texture",
        "description": "Subtle textures with elegant simplicity",
        "colors": ["#E8E4D9", "#C4B7A6", "#8B7E74", "#5C5248"],
        "tags": ["minimal", "any"],
    },
    "temple_art": {
        "id": "temple_art",
        "name": "Temple Art",
        "description": "Traditional Indian temple motifs",
        "colors": ["#B8860B", "#DAA520", "#8B4513", "#F4E3B2"],
        "tags": ["cultural", "entrance", "dining_room"],
    },
    "cartoon_animals": {
        "id": "cartoon_animals",
        "name": "Cartoon Animals",
        "description": "Playful animal illustrations for kids",
        "colors": ["#FF6F91", "#FF9671", "#FFC75F", "#67E6DC"],
        "tags": ["kids", "kids_bedroom"],
    },
    "ocean_waves": {
        "id": "ocean_waves",
        "name": "Ocean Waves",
        "description": "Calming ocean and wave patterns",
        "colors": ["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8"],
        "tags": ["calm", "bathroom", "bedroom"],
    },
    "vintage_typography": {
        "id": "vintage_typography",
        "name": "Vintage Typography",
        "description": "Retro lettering and classic designs",
        "colors": ["#2B2D42", "#8D99AE", "#EDF2F4", "#D90429"],
        "tags": ["retro", "restaurant", "cafe"],
    },
    "luxury_gold": {
        "id": "luxury_gold",
        "name": "Luxury Gold",
        "description": "Opulent gold and marble textures",
        "colors": ["#1A1A2E", "#DAA520", "#FFD700", "#2C2C54"],
        "tags": ["luxury", "hotel_lobby", "dining_room"],
    },
    "botanical": {
        "id": "botanical",
        "name": "Botanical Garden",
        "description": "Lush tropical plants and flowers",
        "colors": ["#606C38", "#283618", "#FEFAE0", "#DDA15E"],
        "tags": ["nature", "kitchen", "cafe"],
    },
    "space_theme": {
        "id": "space_theme",
        "name": "Space Explorer",
        "description": "Galaxies, planets, and cosmic wonder",
        "colors": ["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1"],
        "tags": ["kids", "kids_bedroom", "office"],
    },
    "watercolor": {
        "id": "watercolor",
        "name": "Watercolor Dreams",
        "description": "Soft watercolor washes and blends",
        "colors": ["#E8D5B7", "#F0B5A1", "#A8D8EA", "#AA96DA"],
        "tags": ["soft", "bedroom", "salon"],
    },
}


class StyleIntelligenceAgent:
    """Provides style recommendations based on wall context."""

    def get_all_styles(self) -> list[dict]:
        """Return all available style presets."""
        return list(STYLE_PRESETS.values())

    def get_style(self, style_id: str) -> dict | None:
        """Get a specific style by ID."""
        return STYLE_PRESETS.get(style_id)

    def suggest_styles_for_tags(self, tags: list[str]) -> list[dict]:
        """Return styles that match the given tags."""
        if not tags:
            return list(STYLE_PRESETS.values())[:6]

        scored = []
        for style in STYLE_PRESETS.values():
            score = sum(1 for t in tags if t in style["tags"] or t in style["id"])
            if score > 0 or "any" in style["tags"]:
                scored.append((score, style))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [s for _, s in scored]

        # Always return at least 4 styles
        if len(results) < 4:
            for style in STYLE_PRESETS.values():
                if style not in results:
                    results.append(style)
                if len(results) >= 6:
                    break

        return results[:8]

    def get_trending(self) -> list[dict]:
        """Return trending styles (mock: handpicked popular ones)."""
        trending_ids = [
            "modern_abstract", "nature_landscape", "minimal_texture",
            "luxury_gold", "botanical"
        ]
        return [STYLE_PRESETS[sid] for sid in trending_ids if sid in STYLE_PRESETS]
