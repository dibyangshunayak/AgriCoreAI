# =====================================================================
# FILE: backend/app/agents/location_agent.py
# DESCRIPTION: Location Agent that fetches regional geographic details,
#              coordinates, and queries NVIDIA Nemotron to determine
#              suitable crop varieties and optimal local farming methods.
# =====================================================================

import logging
from typing import Dict, Any, Optional
from app.services.nvidia_service import generate_text

logger = logging.getLogger(__name__)

class LocationAgentException(Exception):
    """Custom exception raised when the Location Agent fails to perform its workflow."""
    pass

def get_location_suitability(
    latitude: float,
    longitude: float,
    user_query: str,
    location_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Coordinates building geographic metadata and queries NVIDIA Nemotron
    to return a suitability advisory for farming in that region.
    """
    logger.info(f"Location Agent starting recommendation workflow for coordinates: {latitude}, {longitude}")

    location_name = location_data.get("formatted_location", "Your location")
    city = location_data.get("city", "Unknown City")
    district = location_data.get("district", "Unknown District")
    state = location_data.get("state", "Unknown State")
    country = location_data.get("country", "Unknown Country")

    prompt = f"""You are AgriCore AI's Location Agent, an expert agricultural geography consultant.
Given the farmer's geographic region, provide a concise advice summary detailing suitable crop varieties and regional farming practices.

Location context:
- Region Name: {location_name}
- City: {city}
- District: {district}
- State: {state}
- Country: {country}
- Coordinates: Latitude {latitude}, Longitude {longitude}

Farmer query: "{user_query}"

Rules:
1. Provide a professional, concise advice summary under 60 words.
2. Recommend suitable crop varieties (e.g. rice, pulses, millets, vegetables) and general agronomic practices typical of this region.
3. Use at most 2 emojis as visual markers. Do NOT print coordinates in the advice body text.

Region-specific agricultural recommendation:
"""

    try:
        recommendation = generate_text(prompt).strip()
        if not recommendation:
            raise LocationAgentException("Received empty response from LLM service.")

        return {
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "district": district,
            "state": state,
            "country": country,
            "formatted_location": location_name,
            "suitability_recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Location Agent LLM recommendation query failed: {e}", exc_info=True)
        raise LocationAgentException(f"Failed to generate location suitability: {str(e)}") from e

