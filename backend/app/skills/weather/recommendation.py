# =====================================================================
# FILE: backend/app/skills/weather/recommendation.py
# DESCRIPTION: Weather recommendation skill.
# =====================================================================

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_weather_recommendation(metrics: Dict[str, Any]) -> str:
    """Analyze weather metrics and suggest irrigation/crop protection actions."""
    logger.info("Executing weather recommendation skill")
    temp = metrics.get("temperature", 25.0)
    humidity = metrics.get("humidity", 60)
    rain = metrics.get("precipitation", 0.0)
    
    if rain > 5.0:
        return "⚠️ Heavy rainfall detected. Suspend all irrigation activities and ensure proper field drainage."
    if temp > 35.0 and humidity < 40:
        return "💧 High temperature and low humidity detected. Increase irrigation frequency to prevent soil dryness."
    return "✅ Weather conditions are normal. Maintain the regular watering schedule."
