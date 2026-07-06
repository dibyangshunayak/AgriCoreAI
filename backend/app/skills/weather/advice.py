# =====================================================================
# FILE: backend/app/skills/weather/advice.py
# DESCRIPTION: Weather Advice Skill.
# =====================================================================

from typing import Dict, Any, List
from app.services.weather_service import interpret_weather

def generate_weather_advice(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate agricultural recommendations based on weather forecast."""
    # Leverage the existing interpretation engine
    result = interpret_weather(weather_data)
    if not result:
        return {
            "summary": "No specific advisory available.",
            "advice": [],
            "metrics": {}
        }
    return result
