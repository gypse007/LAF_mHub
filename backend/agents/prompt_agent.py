import os
import json
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# System prompt for OpenClaw - 8 Layer Cinematic Prompt Engineer
OPENCLAW_SYSTEM_PROMPT = """You are OpenClaw, an elite AI design concierge and Prompt Engineer for a Wall Mural application.
Your goal is to talk to the user and construct a highly optimized, 8-layer cinematic prompt for Stable Diffusion XL.

The 8 layers of a perfect prompt are:
1. Subject Introduction (Who + Core Identity)
2. Environmental Context (Where + Era + Atmosphere)
3. Object Interaction (What are they doing)
4. Lighting Description (Key light + Color temp + Angle)
5. Camera Specifications (Lens + Shot type + Format)
6. Atmospheric Effects (Dust, Smoke, Rain, Texture)
7. Color Grading (Palette + Treatment)
8. Technical Amplifiers (Resolution, Render engines, Quality tags)

BEHAVIOR:
- Be conversational, brief, and highly creative.
- Do NOT ask for all 8 layers at once. 
- You should guide the user by asking 1 or 2 specific questions at a time to build up the scene.
- Once you feel you have enough information to fill out all 8 layers (or if the user says "just do it" / gives you full creative freedom), you must finalize the prompt.

FINALIZING THE PROMPT:
When the prompt is ready, you must include a JSON block at the very end of your message in exactly this format:
```json
{
  "final_prompt": "A highly detailed cinematic 8-layer prompt based on our conversation..."
}
```
If you output that JSON, the UI will automatically start generating the mural and the chat will end. Do not output it until you are ready to generate.
"""

class OpenClawAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY not found. OpenClaw cannot use OpenAI.")

    async def generate_reply(self, history: List[Dict[str, str]], wall_tags: Dict[str, str]) -> Dict[str, Any]:
        """
        Takes conversation history from frontend and returns the next AI reply,
        and optionally a 'finalPrompt' if OpenClaw decides the prompt is finished.
        """
        # Mock mode if no API key
        if not self.client:
             user_last = history[-1]['content']
             if "done" in user_last.lower() or "generate" in user_last.lower() or len(history) > 4:
                 return {
                     "reply": "I don't have an OpenAI key configured, but I'll generate a beautiful mural based on your tags!",
                     "finalPrompt": "A hyperrealistic cinematic mural, masterclass photography, 8k resolution, highly detailed, dramatic lighting, volumetric atmosphere"
                 }
             return {
                 "reply": "I'm running in mock mode because no OpenAI key is set. Tell me 'generate' to finish the prompt!",
                 "finalPrompt": None
             }

        # Build OpenAI Messages
        messages_for_llm = [
            {"role": "system", "content": OPENCLAW_SYSTEM_PROMPT}
        ]
        
        # Inject context regarding the wall's physical tags if they exist
        tag_str = ", ".join([v for v in wall_tags.values() if v])
        if tag_str:
            messages_for_llm.append({
                "role": "system", 
                "content": f"Context: This mural will be placed in a room described as: {tag_str}. Keep this physical space in mind."
            })

        for msg in history:
            messages_for_llm.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Or gpt-3.5-turbo if cost is an issue
                messages=messages_for_llm,
                temperature=0.7,
                max_tokens=500
            )
            
            reply_text = response.choices[0].message.content
            final_prompt = None

            # Look for the JSON block indicating completion
            if "```json" in reply_text:
                try:
                    json_str = reply_text.split("```json")[1].split("```")[0].strip()
                    parsed = json.loads(json_str)
                    if "final_prompt" in parsed:
                        final_prompt = parsed["final_prompt"]
                        # Remove the JSON from the user-facing reply
                        reply_text = reply_text.split("```json")[0].strip()
                except Exception as e:
                    logger.error(f"Failed to parse Final Prompt JSON from OpenClaw: {e}")

            return {
                "reply": reply_text,
                "finalPrompt": final_prompt
            }

        except Exception as e:
            logger.error(f"OpenClaw OpenAI API Error: {e}")
            raise e
