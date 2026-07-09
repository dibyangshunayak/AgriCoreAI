# =====================================================================
# FILE: backend/test_location_mcp.py
# DESCRIPTION: Direct python-level test for the Location MCP tool logic.
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
        # Direct import of the tool function from our Location MCP module
        from app.mcp.location_mcp import reverse_geocode
        
        # Target Coordinates for Baripada, Odisha, India
        latitude = 21.9592
        longitude = 86.7430

        print("==================================================")
        print("TESTING LOCATION MCP SERVER - DIRECT FUNCTION CALL")
        print("==================================================")
        print(f"Coordinates: Lat {latitude}, Lon {longitude}\n")

        # Invoke the reverse_geocode function directly
        address = reverse_geocode(latitude=latitude, longitude=longitude)

        # Print the geocoded address components returned by the tool (without emojis for encoding safety)
        print(f"City: {address.get('city')}")
        print(f"District: {address.get('district')}")
        print(f"State: {address.get('state')}")
        print(f"Country: {address.get('country')}")
        print(f"Formatted Location: {address.get('formatted_location')}")
        print("==================================================")

    except Exception as e:
        logger.error(f"Location MCP test failed with exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_test()

