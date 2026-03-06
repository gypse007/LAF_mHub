import torch
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class AutoWallDetector:
    """
    Uses Meta's Segment Anything Model (SAM) to find wall polygons.
    """
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        self.generator = None

    def load_model(self):
        if self.use_mock or self.generator:
            return
        logger.info(f"Loading SAM model on {self.device}...")
        from transformers import pipeline
        # Using mask-generation pipeline with SAM base model
        self.generator = pipeline("mask-generation", model="facebook/sam-vit-base", device=self.device)

    def detect_walls(self, image_path: str):
        """
        Analyzes the image and returns a list of polygons that are likely walls.
        Polygons are formatted as lists of [x, y] coordinates.
        """
        if self.use_mock:
            # Return dummy wall polygons for quick local development
            logger.info("Mocking SAM wall detection...")
            try:
                with Image.open(image_path) as img:
                    w, h = img.size
                    # Mock finding two generic walls
                    return [
                        [[int(w*0.1), int(h*0.1)], [int(w*0.9), int(h*0.1)], [int(w*0.9), int(h*0.9)], [int(w*0.1), int(h*0.9)]]
                    ]
            except Exception as e:
                logger.error(f"Failed to open image for mock detection: {e}")
                return []

        self.load_model()
        logger.info("Running SAM for auto-wall detection...")
        
        try:
            image = Image.open(image_path).convert("RGB")
            # Generate all possible masks
            outputs = self.generator(image, points_per_batch=32)
            masks = outputs["masks"]
            
            polygons = []
            img_area = image.width * image.height
            
            logger.info(f"SAM generated {len(masks)} raw masks.")
            # Post-process the masks to find large geometric shapes (heuristic for walls/floors)
            for mask in masks:
                mask_np = np.array(mask)
                mask_uint8 = (mask_np * 255).astype(np.uint8)
                contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    # Filter out small objects (less than 5% of the total image area)
                    if area > (img_area * 0.05) and area < (img_area * 0.95):
                        # Approximate polygon geometry
                        epsilon = 0.02 * cv2.arcLength(cnt, True)
                        approx = cv2.approxPolyDP(cnt, epsilon, True)
                        
                        # Only keep shapes with at least 4 vertices
                        if len(approx) >= 4:
                            poly = [[int(pt[0][0]), int(pt[0][1])] for pt in approx]
                            polygons.append(poly)
                        else:
                            logger.info(f"Discarded shape with {len(approx)} vertices.")
                    elif area >= (img_area * 0.95):
                        logger.info("Discarded shape. Too large (>95% area).")
                            
            logger.info(f"Final valid wall polygons: {len(polygons)}")
            # Sort polygons by size (largest first) to prioritize main walls
            polygons.sort(key=lambda p: cv2.contourArea(np.array(p)), reverse=True)
            
            # Fallback if no polygons found
            if len(polygons) == 0:
                logger.warning("No polygons passed filtering. Returning entire image as a fallback polygon.")
                w, h = image.width, image.height
                return [[[0, 0], [w, 0], [w, h], [0, h]]]
                
            return polygons
            
        except Exception as e:
            logger.exception("SAM wall detection failed")
            return []
