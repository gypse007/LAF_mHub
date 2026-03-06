"""
WallVisionAgent — Analyzes uploaded wall images.
In production, this would use a vision model (GPT-4V, Gemini Vision, etc.)
For MVP, returns mock but realistic analysis based on image properties.
"""

import random
from PIL import Image


ROOM_TYPES = [
    "living_room", "bedroom", "kids_bedroom", "kitchen",
    "dining_room", "office", "entrance", "bathroom",
    "restaurant", "cafe", "hotel_lobby", "salon"
]

WALL_COLORS = [
    "#F5F5DC",  # Beige
    "#FFFFFF",  # White
    "#D3D3D3",  # Light Gray
    "#FFF8DC",  # Cornsilk
    "#FAF0E6",  # Linen
    "#F0EAD6",  # Eggshell
    "#E8E4D9",  # Warm White
    "#C4B7A6",  # Taupe
]


class WallVisionAgent:
    """Analyzes wall images and returns structured data."""

    async def analyze_wall(self, image_path: str) -> dict:
        """
        Analyze a wall image and return structured analysis.
        In production: call vision API (OpenAI, Gemini, etc.)
        MVP: derive basic info from image + mock intelligence.
        """
        try:
            img = Image.open(image_path)
            width, height = img.size

            # Sample dominant color from center of image
            center_pixel = img.getpixel((width // 2, height // 2))
            if isinstance(center_pixel, tuple) and len(center_pixel) >= 3:
                hex_color = "#{:02x}{:02x}{:02x}".format(*center_pixel[:3])
            else:
                hex_color = random.choice(WALL_COLORS)

            # Estimate wall size category
            if width * height > 4_000_000:
                size_estimate = "large"
            elif width * height > 1_000_000:
                size_estimate = "medium"
            else:
                size_estimate = "small"

            room_type = random.choice(ROOM_TYPES)

            return {
                "wall_color": hex_color,
                "room_type": room_type,
                "wall_size_estimate": size_estimate,
                "image_dimensions": {"width": width, "height": height},
                "lighting": random.choice(["natural", "warm", "cool", "mixed"]),
                "recommended_styles": self._suggest_styles(room_type),
            }
        except Exception as e:
            return {
                "wall_color": "#FFFFFF",
                "room_type": "living_room",
                "wall_size_estimate": "medium",
                "image_dimensions": {"width": 800, "height": 600},
                "lighting": "natural",
                "recommended_styles": self._suggest_styles("living_room"),
                "error": str(e),
            }

    def _suggest_styles(self, room_type: str) -> list[str]:
        """Return style suggestions based on room type."""
        style_map = {
            "living_room": ["modern_abstract", "nature_landscape", "geometric", "minimal_texture"],
            "bedroom": ["calm_nature", "abstract_soft", "celestial", "watercolor"],
            "kids_bedroom": ["cartoon_animals", "space_theme", "jungle", "superhero"],
            "kitchen": ["botanical", "food_art", "modern_tiles", "rustic"],
            "dining_room": ["vintage_art", "wine_culture", "abstract_gold", "classic"],
            "office": ["motivational", "city_skyline", "geometric", "minimal"],
            "entrance": ["welcome_abstract", "nature", "modern_art", "cultural"],
            "bathroom": ["ocean", "zen", "tropical", "marble_texture"],
            "restaurant": ["vintage_typography", "street_mural", "coffee_art", "industrial"],
            "cafe": ["coffee_culture", "retro", "botanical", "sketch_art"],
            "hotel_lobby": ["luxury_abstract", "gold_marble", "panoramic", "cultural_art"],
            "salon": ["fashion", "floral", "modern_beauty", "abstract_color"],
        }
        return style_map.get(room_type, ["modern_abstract", "nature", "geometric", "minimal"])
