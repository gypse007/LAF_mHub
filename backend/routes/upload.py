"""
Upload route — handles wall image uploads and analysis.
Uses JSON-file persistence so uploads survive server restarts.
"""

import os
import uuid
import json
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from agents.wall_agent import WallVisionAgent
from agents.wall_detector import AutoWallDetector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/wall", tags=["wall"])

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "images")
os.makedirs(STORAGE_DIR, exist_ok=True)

WALL_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "wall_store.json")

wall_agent = WallVisionAgent()
wall_detector = AutoWallDetector(use_mock=os.getenv("USE_MOCK_PIPELINE", "True").lower() == "true")


# ─── Persistent wall_store backed by JSON file ───────────────────────
def _load_store() -> dict:
    """Load the wall store from disk."""
    if os.path.exists(WALL_STORE_PATH):
        try:
            with open(WALL_STORE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_store():
    """Persist the wall store to disk."""
    try:
        with open(WALL_STORE_PATH, "w") as f:
            json.dump(wall_store, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save wall store: {e}")

# Load on startup
wall_store: dict = _load_store()
logger.info(f"Loaded {len(wall_store)} walls from persistent store.")


@router.post("/upload")
async def upload_wall(file: UploadFile = File(...)):
    """Upload a wall image and get AI analysis."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate wall ID and save file
    wall_id = str(uuid.uuid4())[:8]
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{wall_id}.{ext}"
    filepath = os.path.join(STORAGE_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Analyze the wall
    analysis = await wall_agent.analyze_wall(filepath)

    # Store wall data
    wall_store[wall_id] = {
        "wall_id": wall_id,
        "image_path": filepath,
        "filename": filename,
        "analysis": analysis,
        "tags": {},
        "print_area": None,
    }
    _save_store()

    return {
        "wall_id": wall_id,
        "filename": filename,
        "analysis": analysis,
    }


@router.post("/{wall_id}/tags")
async def update_wall_tags(wall_id: str, tags: dict):
    """Update wall tags (room type, environment, etc.)."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    wall_store[wall_id]["tags"] = tags
    _save_store()
    return {"wall_id": wall_id, "tags": tags}


@router.post("/{wall_id}/reference")
async def upload_reference_image(wall_id: str, file: UploadFile = File(...)):
    """Upload an optional style reference image for this wall."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save reference image
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"ref_{wall_id}.{ext}"
    filepath = os.path.join(STORAGE_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    wall_store[wall_id]["reference_image_path"] = filepath
    _save_store()
    return {"wall_id": wall_id, "reference_image_path": filepath}


@router.post("/{wall_id}/print-area")
async def update_print_area(wall_id: str, data: dict):
    """Update the print area coordinates."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    wall_store[wall_id]["print_area"] = data.get("print_area", [])
    _save_store()
    return {"wall_id": wall_id, "print_area": wall_store[wall_id]["print_area"]}


@router.post("/{wall_id}/detect-walls")
async def detect_walls(wall_id: str):
    """Run SAM on the wall image to find polygons representing walls."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    image_path = wall_store[wall_id]["image_path"]
    # Run SAM detection
    polygons = wall_detector.detect_walls(image_path)
    
    wall_store[wall_id]["detected_walls"] = polygons
    _save_store()
    return {"wall_id": wall_id, "detected_walls": polygons}


@router.get("/{wall_id}")
async def get_wall(wall_id: str):
    """Get wall data by ID."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    return wall_store[wall_id]
