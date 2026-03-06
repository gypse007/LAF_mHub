"""
Wall Mural AI — FastAPI Backend
Main application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.upload import router as upload_router
from routes.generate import router as generate_router
from routes.styles import router as styles_router

app = FastAPI(
    title="Wall Mural AI",
    description="AI-powered wall mural design engine",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories for serving images
storage_dir = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(os.path.join(storage_dir, "images"), exist_ok=True)
os.makedirs(os.path.join(storage_dir, "results"), exist_ok=True)

app.mount("/api/static/images", StaticFiles(directory=os.path.join(storage_dir, "images")), name="images")
app.mount("/api/static/results", StaticFiles(directory=os.path.join(storage_dir, "results")), name="results")

# Register routers
app.include_router(upload_router)
app.include_router(generate_router)
app.include_router(styles_router)


@app.get("/")
async def root():
    return {
        "app": "Wall Mural AI",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/wall/upload",
            "generate": "POST /api/wall/generate",
            "styles": "GET /api/styles",
            "suggestions": "POST /api/styles/suggestions",
            "trending": "GET /api/styles/trending",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
