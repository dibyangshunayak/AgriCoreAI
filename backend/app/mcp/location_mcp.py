# =====================================================================
# FILE: backend/app/mcp/location_mcp.py
# DESCRIPTION: Location MCP Server that provides the 'reverse_geocode' tool
#              using the OpenStreetMap Nominatim API.
# =====================================================================

import sys
import logging
import requests
from typing import Dict, Any

# Ensure parent directory is in sys.path so we can import app modules if needed
from pathlib import Path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastmcp import FastMCP

# --- Logging Setup ---
# Crucial for MCP stdio servers: do not log to stdout (print),
# redirect to stderr to prevent protocol stream corruption.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("location_mcp")

# Initialize the Location MCP server
mcp = FastMCP("Location Server")

@mcp.tool()
def reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Convert coordinates (latitude and longitude) into a human-readable location address.

    Parameters:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        Dict[str, Any]: Geocoded address components: city, district, state, country, and formatted_location.
    """
    logger.info(f"Location MCP received request for Lat: {latitude}, Lon: {longitude}")
    
    # 1. Query OSM Nominatim Reverse Geocoding API
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&zoom=14"
        headers = {"User-Agent": "AgriCoreAI-Location-Server/1.0"}
        
        logger.info(f"Making reverse geocode API call to: {url}")
        response = requests.get(url, headers=headers, timeout=2.0)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            
            # Extract standard address keys
            city = address.get("city") or address.get("town") or address.get("village") or address.get("municipality") or ""
            district = address.get("county") or address.get("district") or address.get("state_district") or ""
            state = address.get("state") or address.get("region") or ""
            country = address.get("country") or ""
            
            # Construct a clean, commas-separated display string
            parts = []
            display_city = city or district
            if display_city:
                parts.append(display_city)
            if state:
                parts.append(state)
            if country:
                parts.append(country)
            formatted = ", ".join(parts) if parts else "Unknown Location"
            
            result = {
                "city": city,
                "district": district,
                "state": state,
                "country": country,
                "formatted_location": formatted
            }
            logger.info(f"Nominatim resolved location: {result}")
            return result

            
        else:
            logger.warning(f"Nominatim API returned status code {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error calling Nominatim reverse geocoding API: {e}", exc_info=True)
        
    # Fallback response in case of API issues or offline state
    fallback = {
        "city": "Unknown City",
        "district": "Unknown District",
        "state": "Unknown State",
        "country": "Unknown Country",
        "formatted_location": "Using your current location"
    }
    logger.warning(f"Returning geocoding fallback: {fallback}")
    return fallback

if __name__ == "__main__":
    # Start the FastMCP server (default transport is stdio)
    mcp.run()
