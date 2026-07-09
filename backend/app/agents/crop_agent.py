# =====================================================================
# FILE: backend/app/agents/crop_agent.py
# DESCRIPTION: Crop Agent that coordinates fetching agronomic knowledge,
#              soil fertility guidelines, and crop cultivation data using
#              NVIDIA Nemotron.
# =====================================================================

import logging
from typing import Dict, Any, Optional, List
from app.services.nvidia_service import generate_text

logger = logging.getLogger(__name__)

class CropAgentException(Exception):
    """Custom exception raised when the Crop Agent fails to perform its workflow."""
    pass

def get_crop_recommendation(
    user_query: str,
    history: Optional[List[Dict[str, str]]] = None,
    session_crop: Optional[str] = None
) -> str:
    """
    Generates specialized agricultural advice for crops, soil fertility,
    fertilizers, crop rotation, sowing, and harvesting.
    """
    logger.info(f"Crop Agent starting recommendation workflow for query: '{user_query}'")

    # Build history context if present
    history_str = ""
    if history:
        for msg in history[-6:]:
            role = "Farmer" if msg.get("role") == "user" else "AgriCore AI"
            content = msg.get("content", "")
            history_str += f"{role}: {content}\n"
    else:
        history_str = "No prior messages.\n"

    crop_context_str = f"Previously discussed crop: {session_crop}" if session_crop else "No crop context in session."

    prompt = f"""You are AgriCore AI's Crop Agent, an expert agronomist and crop specialist.
Analyze the farmer's query and provide professional, practical, and highly detailed agricultural guidance.

Guidelines:
1. Tone: Authoritative, professional, scientific, yet easy for a farmer to understand.
2. Structure: Use structured bullet points, clear headings, bold text, and relevant agricultural emojis (e.g. 🌿, 🌾, 🚜). Keep response under 350 words.
3. Agronomic accuracy: Use precise terms like "NPK ratio", "soil structure", "soil organic matter", "rhizobia", "transplanting", "water requirements".
4. Focus: Do NOT output any GPS coordinates, location names, or personal greetings. Focus 100% on the agronomic advice.
5. Crop Specifics: If the user query is about a specific crop (e.g., rice, tomato, wheat, maize, etc.), you MUST include:
   - Scientific name
   - Climate
   - Soil
   - Seed rate
   - Irrigation
   - Fertilizers
   - Diseases
   - Pests
   - Harvesting
   - Yield
   - Practical farmer tips
6. Topics: Cover cultivation, irrigation requirements, fertilizer needs, crop rotation, sowing/harvesting, and soil fertility.

Context details:
{crop_context_str}

Conversation history:
{history_str}

Current Farmer Query:
{user_query}

AgriCore AI Crop Recommendation:
"""

    try:
        response = generate_text(prompt)
        if not response:
            raise CropAgentException("Received empty response from LLM service.")
        return response.strip()
    except Exception as e:
        logger.error(f"Crop Agent LLM query failed: {e}", exc_info=True)
        raise CropAgentException(f"Failed to generate crop recommendation: {str(e)}") from e

