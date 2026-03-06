"""
Styles route — returns available style presets and suggestions.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from agents.style_agent import StyleIntelligenceAgent

router = APIRouter(prefix="/api/styles", tags=["styles"])

style_agent = StyleIntelligenceAgent()


class SuggestionRequest(BaseModel):
    tags: list[str] = []


@router.get("")
async def get_all_styles():
    """Get all available style presets."""
    return {"styles": style_agent.get_all_styles()}


@router.post("/suggestions")
async def get_style_suggestions(request: SuggestionRequest):
    """Get style suggestions based on tags."""
    return {"styles": style_agent.suggest_styles_for_tags(request.tags)}


@router.get("/trending")
async def get_trending_styles():
    """Get currently trending styles."""
    return {"styles": style_agent.get_trending()}
