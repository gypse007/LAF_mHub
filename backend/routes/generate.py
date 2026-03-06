"""
Generate route — creates mural designs composited onto walls.
"""

import os
import uuid
import logging
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from agents.ai_pipeline import AdvancedMuralPipeline
from agents.style_agent import StyleIntelligenceAgent
from routes.upload import wall_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/wall", tags=["generate"])

# In-memory task queue (MVP)
tasks_store: dict = {}

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Use env var to decide if we mock the SDXL generation locally
use_mock = os.getenv("USE_MOCK_PIPELINE", "True").lower() == "true"
advanced_pipeline = AdvancedMuralPipeline(use_mock=use_mock)
style_agent = StyleIntelligenceAgent()

class GenerateRequest(BaseModel):
    wall_id: str
    style: str
    print_area: list[list[int]] | None = None
    wall_size: dict | None = None  # { width: float, height: float } in feet

def background_generate(task_id: str, request: GenerateRequest, wall_data: dict, print_area: list):
    """Background worker function to run the heavy AI pipeline."""
    try:
        tasks_store[task_id]["status"] = "processing"
        
        # Output paths
        output_filename = f"mural_{request.wall_id}_{task_id}.jpg"
        output_path = os.path.join(RESULTS_DIR, output_filename)
        
        panel_urls = []
        print_resolution = None

        # Get style prompt
        style_info = style_agent.get_style(request.style)
        prompt = f"{style_info['name']}, {style_info['description']}" if style_info else request.style
        
        # Get corners
        if print_area and len(print_area) == 4:
            corners = print_area
        else:
            # Fallback to full image
            from PIL import Image
            with Image.open(wall_data["image_path"]) as img:
                w, h = img.size
                corners = [[0, 0], [w, 0], [w, h], [0, h]]

        # Run the full V2 pipeline
        logger.info(f"Task {task_id}: Running Advanced Pipeline for {request.wall_id} with style {request.style}")
        result_img = advanced_pipeline.run_full_pipeline(
            wall_image_path=wall_data["image_path"],
            prompt=prompt,
            corners=corners,
            reference_image_path=wall_data.get("reference_image_path")
        )
        
        # Save preview output
        result_img.save(output_path, quality=90)

        # Print Panel Slicing (Day 5 Features)
        if request.wall_size and request.wall_size.get("width") and request.wall_size.get("height"):
            logger.info("Wall size provided. Computing print-safe 150 DPI resolution and slicing panels.")
            # Calculate 150 DPI resolution
            # 1 foot = 12 inches
            w_feet = request.wall_size["width"]
            h_feet = request.wall_size["height"]
            
            target_w = int(w_feet * 12 * 150)
            target_h = int(h_feet * 12 * 150)
            print_resolution = f"{target_w}x{target_h}"
            
            # Upscale using high-quality LANCZOS (replace with Real-ESRGAN in full prod)
            logger.info(f"Upscaling to {print_resolution} for printing...")
            from PIL import Image
            hd_img = result_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Slice into 60cm panels
            # 60cm = 23.62 inches = 3543 pixels at 150 DPI
            panel_width_px = 3543
            import numpy as np
            import cv2
            
            hd_cv = cv2.cvtColor(np.array(hd_img), cv2.COLOR_RGB2BGR)
            panels = advanced_pipeline.slice_panels(hd_cv, panel_width_px)
            
            for i, panel in enumerate(panels):
                panel_name = f"mural_{request.wall_id}_{task_id}_panel_{i+1:02d}.png"
                panel_path = os.path.join(RESULTS_DIR, panel_name)
                cv2.imwrite(panel_path, panel)
                panel_urls.append(f"/api/static/results/{panel_name}")
                
            logger.info(f"Task {task_id}: Successfully sliced {len(panels)} print panels.")

        tasks_store[task_id].update({
            "status": "completed",
            "result": {
                "result_id": task_id,
                "wall_id": request.wall_id,
                "style": request.style,
                "image_url": f"/api/static/results/{output_filename}",
                "original_image_url": f"/api/static/images/{wall_data['filename']}",
                "print_resolution": print_resolution,
                "panels": panel_urls
            }
        })
                
    except Exception as e:
        logger.exception(f"Task {task_id}: Generation failed")
        tasks_store[task_id]["status"] = "failed"
        tasks_store[task_id]["error"] = str(e)


@router.post("/generate")
async def generate_design_async(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Queue a mural design generation task."""
    wall_data = wall_store.get(request.wall_id)
    if not wall_data:
        raise HTTPException(status_code=404, detail="Wall not found. Upload a wall first.")

    # Use stored print area if not provided
    print_area = request.print_area or wall_data.get("print_area")

    task_id = str(uuid.uuid4())[:8]
    
    tasks_store[task_id] = {
        "status": "pending",
        "task_id": task_id,
        "wall_id": request.wall_id
    }
    
    # Fire off background worker
    background_tasks.add_task(background_generate, task_id, request, wall_data, print_area)
    
    return {"task_id": task_id, "status": "pending"}


@router.get("/status/{task_id}")
async def check_task_status(task_id: str):
    """Poll the status of a generation task."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return tasks_store[task_id]
