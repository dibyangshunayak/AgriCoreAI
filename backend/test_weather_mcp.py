# =====================================================================
# FILE: backend/test_weather_mcp.py
# DESCRIPTION: Direct python-level test for the Weather MCP tool logic.
#              Imports the server tool directly and calls it with coordinates.
# =====================================================================

import sys
import logging
from pathlib import Path

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Python Path Configuration ---
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

def run_test():
    try:
        # Direct import of the tool function from our Weather MCP module
        from app.mcp.weather_mcp import get_weather
        
        # Target Coordinates for Baripada, Odisha, India
        latitude = 21.9592
        longitude = 86.7430

        print("==================================================")
        print("TESTING WEATHER MCP SERVER - DIRECT FUNCTION CALL")
        print("==================================================")
        print(f"Coordinates: Lat {latitude}, Lon {longitude}\n")

        # Invoke the get_weather function directly
        metrics = get_weather(latitude=latitude, longitude=longitude)

        # Print the weather and agricultural metrics returned by the tool (without emojis for encoding safety)
        print(f"Temperature: {metrics.get('temperature')} C")
        print(f"Humidity: {metrics.get('humidity')}%")
        print(f"Rain: {metrics.get('precipitation')} mm")
        print(f"Wind Speed: {metrics.get('wind_speed')} km/h")
        print(f"Soil Temperature: {metrics.get('soil_temperature')} C")
        print(f"Soil Moisture: {metrics.get('soil_moisture')}")
        print(f"Weather Condition: {metrics.get('weather_condition')}")
        print("==================================================")

    except Exception as e:
        logger.error(f"Weather MCP test failed with exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_test()
