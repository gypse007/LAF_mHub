"""
Upload route — handles wall image uploads and analysis.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from agents.wall_agent import WallVisionAgent
from agents.wall_detector import AutoWallDetector

router = APIRouter(prefix="/api/wall", tags=["wall"])

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "images")
os.makedirs(STORAGE_DIR, exist_ok=True)

wall_agent = WallVisionAgent()
wall_detector = AutoWallDetector(use_mock=os.getenv("USE_MOCK_PIPELINE", "True").lower() == "true")

# In-memory store for wall data (MVP; use a DB in production)
wall_store: dict = {}


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
    return {"wall_id": wall_id, "reference_image_path": filepath}


@router.post("/{wall_id}/print-area")
async def update_print_area(wall_id: str, data: dict):
    """Update the print area coordinates."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    wall_store[wall_id]["print_area"] = data.get("print_area", [])
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
    return {"wall_id": wall_id, "detected_walls": polygons}


@router.get("/{wall_id}")
async def get_wall(wall_id: str):
    """Get wall data by ID."""
    if wall_id not in wall_store:
        raise HTTPException(status_code=404, detail="Wall not found")

    return wall_store[wall_id]
