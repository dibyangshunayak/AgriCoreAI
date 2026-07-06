# =====================================================================
# FILE: backend/app/mcp/weather_mcp.py
# DESCRIPTION: Weather MCP Server that provides the 'get_weather' tool
#              using the Open-Meteo API.
# =====================================================================

import os
import sys
import logging
from typing import Dict, Any

# Ensure parent directory is in sys.path so we can import from app
# Path of this file: backend/app/mcp/weather_mcp.py
# Parent: backend/app/mcp/
# Grandparent: backend/app/
# Great-grandparent: backend/
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastmcp import FastMCP
from app.services.weather_service import get_weather as fetch_weather
from app.agents.weather_agent import WEATHER_CODE_DESCRIPTIONS

# --- Logging Setup ---
# Crucial for MCP stdio servers: do not log to stdout (print),
# as that will corrupt the JSON-RPC message stream. Redirect logs to stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("weather_mcp")

# Initialize the Weather MCP server
mcp = FastMCP("Weather Server")

@mcp.tool()
def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Retrieve real-time weather and agricultural metrics for a given latitude and longitude.

    Parameters:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        Dict[str, Any]: A dictionary containing temperature, humidity, precipitation,
                        wind speed, soil metrics, and weather condition description.
    """
    logger.info(f"Weather MCP received request for Lat: {latitude}, Lon: {longitude}")
    
    try:
        # Call the existing weather service
        weather_data = fetch_weather(latitude=latitude, longitude=longitude)
        
        # Validate data returned by the service
        if not weather_data or "current" not in weather_data:
            logger.error("Weather service returned empty or invalid structure.")
            raise ValueError("Weather data is currently unavailable for this location.")
            
        current = weather_data["current"]
        
        # Safely extract target metrics
        temperature = float(current.get("temperature_2m", 0.0))
        humidity = int(current.get("relative_humidity_2m", 0))
        precipitation = float(current.get("precipitation", 0.0))
        wind_speed = float(current.get("wind_speed_10m", 0.0))
        weather_code = current.get("weather_code", 0)
        soil_temperature = float(current.get("soil_temperature_0_to_7cm", 0.0))
        soil_moisture = float(current.get("soil_moisture_0_to_7cm", 0.0))
        
        # Map the code to a description
        weather_condition = WEATHER_CODE_DESCRIPTIONS.get(weather_code, f"Code {weather_code}")
        
        # Package output as defined in Task 1/2 specifications
        result = {
            "temperature": temperature,
            "humidity": humidity,
            "precipitation": precipitation,
            "wind_speed": wind_speed,
            "soil_temperature": soil_temperature,
            "soil_moisture": soil_moisture,
            "weather_condition": weather_condition
        }
        
        logger.info(f"Weather MCP successfully processed request: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute get_weather tool: {e}", exc_info=True)
        raise RuntimeError(f"Weather MCP Error: {str(e)}")

if __name__ == "__main__":
    # Start the FastMCP server (default transport is stdio)
    mcp.run()
