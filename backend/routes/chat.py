from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import traceback
import logging

from agents.prompt_agent import OpenClawAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Initialize the conversational agent
openclaw = OpenClawAgent()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    wallTags: Optional[Dict[str, str]] = {}

class ChatResponse(BaseModel):
    reply: str
    finalPrompt: Optional[str] = None

@router.post("/openclaw", response_model=ChatResponse)
async def chat_with_openclaw(request: ChatRequest):
    """
    Handles conversation with the OpenClaw prompt engineer AI.
    Builds an 8-layer cinematic prompt for SDXL.
    """
    try:
         # Convert Pydantic models to standard lists/dicts
         history = [{"role": msg.role, "content": msg.content} for msg in request.history]
         
         response_data = await openclaw.generate_reply(history, request.wallTags)
         
         return ChatResponse(
             reply=response_data.get("reply", ""),
             finalPrompt=response_data.get("finalPrompt")
         )
         
    except Exception as e:
        logger.error(f"OpenClaw Chat Error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to communicate with OpenClaw")
