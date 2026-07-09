# =====================================================================
# FILE: backend/app/services/context_builder.py
# DESCRIPTION: Context Builder service that extracts and returns only relevant
#              context keys based on active agents/intents.
# =====================================================================

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Selectively compiles and filters coordinates, weather metrics, crop context, and
    uploaded leaf images depending on the current query's active intents (agents list).
    """
    @staticmethod
    def build(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives data:
        {
            "agents": ["crop", "weather", ...],
            "query": "...",
            "location": "...",
            "coordinates": "...",
            "weather": "...",
            "image": "...",
            "crop": "...",
            "history": "..."
        }
        Returns a filtered dictionary matching the relevant active intents:
        - general -> {}
        - weather -> {"location": "...", "weather": "..."}
        - crop -> {"location": "..."}
        - disease -> {"image": "...", "crop": "...", "location": "..."}
        - location -> {"location": "..."} (and coordinates if explicitly requested)
        """
        agents = data.get("agents") or []
        query = data.get("query") or ""

        logger.info(f"ContextBuilder building context selectively for agents: {agents} using English query: '{query}'")

        # General intent requires an empty context
        if "general" in agents:
            return {}

        context = {}

        # 1. Location (relevant for crop, weather, location, and disease agents)
        # Note: crop, weather, disease, and location agents all need user location name context.
        if any(agent in agents for agent in ["crop", "weather", "location", "disease"]):
            context["location"] = data.get("location") or "Unknown"

        # 2. Weather metrics (strictly for weather agent)
        if "weather" in agents:
            context["weather"] = data.get("weather") or "Unknown"

        # 3. Disease context (strictly for disease agent)
        if "disease" in agents:
            context["image"] = data.get("image") or "No image uploaded."
            context["crop"] = data.get("crop") or "Unknown"

        # 4. Coordinates (strictly for location agent, and only if explicitly requested)
        if "location" in agents:
            query_lower = query.lower()
            explicit_coords = any(word in query_lower for word in ["coordinate", "where am i", "my location", "what is my location", "tell me my location"])
            if explicit_coords:
                context["coordinates"] = data.get("coordinates") or "Unknown"

        return context
