"""
DesignAgent — Generates mural designs composited onto the wall.
In production, this would use Stable Diffusion + ControlNet.
For MVP, creates gradient/pattern overlays using Pillow and composites
them onto the print area of the wall image.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from agents.style_agent import STYLE_PRESETS


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class DesignAgent:
    """Generates mural designs and composites them onto wall images."""

    async def generate(
        self,
        wall_image_path: str,
        style_id: str,
        print_area: list[list[int]] | None = None,
        output_path: str = "output.jpg",
    ) -> str:
        """
        Generate a mural design and composite it onto the wall.

        Args:
            wall_image_path: Path to the uploaded wall image
            style_id: ID of the style preset to use
            print_area: List of [x, y] coordinates defining the print area polygon
            output_path: Where to save the composited result

        Returns:
            Path to the generated composite image
        """
        # Load wall image
        wall = Image.open(wall_image_path).convert("RGBA")
        w, h = wall.size

        # Determine the print area bounds
        if print_area and len(print_area) >= 2:
            xs = [p[0] for p in print_area]
            ys = [p[1] for p in print_area]
            x1 = max(0, min(xs))
            y1 = max(0, min(ys))
            x2 = min(w, max(xs))
            y2 = min(h, max(ys))
        else:
            # Default: center 60% of the wall
            margin_x = int(w * 0.2)
            margin_y = int(h * 0.2)
            x1, y1 = margin_x, margin_y
            x2, y2 = w - margin_x, h - margin_y

        area_w = x2 - x1
        area_h = y2 - y1

        if area_w < 10 or area_h < 10:
            area_w = max(area_w, 100)
            area_h = max(area_h, 100)

        # Get style colors
        style = STYLE_PRESETS.get(style_id, STYLE_PRESETS.get("modern_abstract"))
        colors = [hex_to_rgb(c) for c in style["colors"]]

        # Generate the mural artwork
        mural = self._generate_mural(area_w, area_h, colors, style_id)

        # Create mask for the print area
        mask = Image.new("L", wall.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        if print_area and len(print_area) >= 3:
            polygon = [tuple(p) for p in print_area]
            mask_draw.polygon(polygon, fill=255)
        else:
            mask_draw.rectangle([x1, y1, x2, y2], fill=255)

        # Slight feathering on mask edges
        mask = mask.filter(ImageFilter.GaussianBlur(radius=3))

        # Create the mural layer (full image size, mural placed in print area)
        mural_layer = Image.new("RGBA", wall.size, (0, 0, 0, 0))
        mural_resized = mural.resize((area_w, area_h), Image.LANCZOS)
        mural_layer.paste(mural_resized, (x1, y1))

        # Composite: blend mural onto wall using mask
        result = Image.composite(mural_layer, wall, mask)

        # Save as RGB JPEG
        result_rgb = result.convert("RGB")
        result_rgb.save(output_path, "JPEG", quality=92)

        return output_path

    def _generate_mural(
        self, width: int, height: int, colors: list[tuple], style_id: str
    ) -> Image.Image:
        """Generate a mural artwork based on style."""
        img = Image.new("RGBA", (width, height), (*colors[0], 255))
        draw = ImageDraw.Draw(img)

        if "geometric" in style_id:
            self._draw_geometric(draw, width, height, colors)
        elif "nature" in style_id or "botanical" in style_id or "ocean" in style_id:
            self._draw_organic(draw, width, height, colors)
        elif "abstract" in style_id or "watercolor" in style_id:
            self._draw_abstract(draw, width, height, colors)
        elif "cartoon" in style_id or "space" in style_id:
            self._draw_playful(draw, width, height, colors)
        elif "luxury" in style_id or "gold" in style_id or "temple" in style_id:
            self._draw_luxury(draw, width, height, colors)
        elif "vintage" in style_id or "typography" in style_id:
            self._draw_vintage(draw, width, height, colors)
        else:
            self._draw_abstract(draw, width, height, colors)

        return img

    def _draw_geometric(self, draw, w, h, colors):
        """Geometric patterns: triangles, lines, circles."""
        # Background gradient
        for y in range(h):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / h)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / h)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # Draw triangles
        for _ in range(15):
            cx, cy = random.randint(0, w), random.randint(0, h)
            size = random.randint(30, min(w, h) // 3)
            color = random.choice(colors) + (random.randint(100, 200),)
            points = [
                (cx, cy - size),
                (cx - size, cy + size),
                (cx + size, cy + size),
            ]
            draw.polygon(points, fill=color)

        # Draw circles
        for _ in range(8):
            cx, cy = random.randint(0, w), random.randint(0, h)
            r = random.randint(10, min(w, h) // 5)
            color = random.choice(colors) + (random.randint(80, 180),)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

        # Draw lines
        for _ in range(10):
            x1, y1 = random.randint(0, w), random.randint(0, h)
            x2, y2 = random.randint(0, w), random.randint(0, h)
            color = random.choice(colors) + (random.randint(100, 220),)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(2, 6))

    def _draw_organic(self, draw, w, h, colors):
        """Organic: flowing curves, leaf shapes, waves."""
        # Gradient background
        for y in range(h):
            r = int(colors[0][0] + (colors[-1][0] - colors[0][0]) * y / h)
            g = int(colors[0][1] + (colors[-1][1] - colors[0][1]) * y / h)
            b = int(colors[0][2] + (colors[-1][2] - colors[0][2]) * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # Wave pattern
        for wave in range(5):
            points = []
            y_base = int(h * (wave + 1) / 6)
            for x in range(0, w, 4):
                y = y_base + int(30 * math.sin(x / 40 + wave))
                points.append((x, y))
            if len(points) >= 2:
                color = colors[wave % len(colors)] + (120,)
                draw.line(points, fill=color, width=3)

        # Elliptical leaf shapes
        for _ in range(20):
            cx, cy = random.randint(0, w), random.randint(0, h)
            rw = random.randint(10, 40)
            rh = random.randint(20, 60)
            color = random.choice(colors[1:]) + (random.randint(80, 160),)
            draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=color)

    def _draw_abstract(self, draw, w, h, colors):
        """Abstract: large color blocks, splatters, gradients."""
        # Multi-color gradient
        band_h = h // len(colors)
        for i, color in enumerate(colors):
            y1 = i * band_h
            y2 = (i + 1) * band_h if i < len(colors) - 1 else h
            next_color = colors[(i + 1) % len(colors)]
            for y in range(y1, y2):
                t = (y - y1) / max(1, (y2 - y1))
                r = int(color[0] + (next_color[0] - color[0]) * t)
                g = int(color[1] + (next_color[1] - color[1]) * t)
                b = int(color[2] + (next_color[2] - color[2]) * t)
                draw.line([(0, y), (w, y)], fill=(r, g, b, 200))

        # Large circles (splatters)
        for _ in range(12):
            cx, cy = random.randint(0, w), random.randint(0, h)
            r = random.randint(20, min(w, h) // 3)
            color = random.choice(colors) + (random.randint(60, 150),)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    def _draw_playful(self, draw, w, h, colors):
        """Playful: stars, circles, bright shapes."""
        # Bright background
        draw.rectangle([0, 0, w, h], fill=(*colors[0], 255))

        # Stars
        for _ in range(30):
            cx, cy = random.randint(0, w), random.randint(0, h)
            size = random.randint(5, 25)
            color = random.choice(colors) + (220,)
            self._draw_star(draw, cx, cy, size, color)

        # Circles
        for _ in range(15):
            cx, cy = random.randint(0, w), random.randint(0, h)
            r = random.randint(10, 50)
            color = random.choice(colors) + (random.randint(100, 220),)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*colors[-1], 255), width=2)

    def _draw_luxury(self, draw, w, h, colors):
        """Luxury: radial gradients, gold lines, diamond patterns."""
        # Dark base
        draw.rectangle([0, 0, w, h], fill=(*colors[0], 255))

        # Gold diagonal lines
        for i in range(-h, w + h, 20):
            color = colors[1] + (random.randint(40, 100),)
            draw.line([(i, 0), (i + h, h)], fill=color, width=1)

        # Diamond lattice
        spacing = 40
        for x in range(0, w, spacing):
            for y in range(0, h, spacing):
                size = 15
                points = [
                    (x, y - size), (x + size, y),
                    (x, y + size), (x - size, y),
                ]
                color = colors[2] + (random.randint(30, 80),)
                draw.polygon(points, fill=color, outline=(*colors[1], 60))

        # Center radial glow
        cx, cy = w // 2, h // 2
        for r in range(min(w, h) // 2, 0, -5):
            alpha = int(80 * (1 - r / (min(w, h) // 2)))
            color = colors[1] + (alpha,)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    def _draw_vintage(self, draw, w, h, colors):
        """Vintage: muted tones, horizontal lines, retro feel."""
        # Muted background
        draw.rectangle([0, 0, w, h], fill=(*colors[2], 255))

        # Horizontal stripes
        stripe_h = 8
        for y in range(0, h, stripe_h * 2):
            color = colors[0] + (40,)
            draw.rectangle([0, y, w, y + stripe_h], fill=color)

        # Large circles (retro dots)
        for _ in range(8):
            cx, cy = random.randint(0, w), random.randint(0, h)
            r = random.randint(30, 80)
            color = random.choice(colors[:2]) + (random.randint(80, 160),)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

        # Frame border
        border = 10
        draw.rectangle([border, border, w - border, h - border],
                       outline=(*colors[3], 200), width=3)

    def _draw_star(self, draw, cx, cy, size, color):
        """Draw a simple 5-pointed star."""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = size if i % 2 == 0 else size // 2
            x = cx + int(r * math.cos(angle))
            y = cy + int(r * math.sin(angle))
            points.append((x, y))
        draw.polygon(points, fill=color)
