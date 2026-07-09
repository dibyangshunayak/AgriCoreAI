# =====================================================================
# FILE: backend/app/skills/weather/forecast.py
# DESCRIPTION: Weather Forecast Skill.
# =====================================================================

from typing import Dict, Any
from app.tools.registry import registry

def get_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """Retrieve weather forecast data using the registry tools."""
    # Try weather_mcp first, fallback to weather_api
    try:
        # Run async tool in sync wrapper if needed, or check if sync registry tool exists
        # In python, we can just run weather_api synchronously since it's defined with run()
        return registry.run_tool("weather_api", latitude=latitude, longitude=longitude)
    except Exception:
        # Fallback to run_tool
        return registry.run_tool("weather_api", latitude=latitude, longitude=longitude)
