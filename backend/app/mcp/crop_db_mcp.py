# =====================================================================
# FILE: backend/app/mcp/crop_db_mcp.py
# DESCRIPTION: Crop Database MCP Server that provides the 'query_crop' tool.
# =====================================================================

import sys
import logging
import json
from typing import Dict, Any
from pathlib import Path

# Ensure parent directory is in sys.path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastmcp import FastMCP

# Redirect logs to stderr to avoid protocol corruption
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("crop_db_mcp")

mcp = FastMCP("Crop DB Server")

@mcp.tool()
def query_crop(crop_name: str) -> str:
    """
    Query localized crop details including planting spacing, ideal pH, NPK requirements, and soil type.

    Parameters:
        crop_name (str): The crop to query.

    Returns:
        str: JSON-serialized string of crop guidelines.
    """
    logger.info(f"Crop DB MCP received query for: {crop_name}")
    crop = crop_name.lower()
    db = {
        "tomato": {
            "spacing": "60cm x 45cm row spacing",
            "ph_range": "6.0 - 6.8",
            "npk_ratio": "N: 80kg/ha, P: 40kg/ha, K: 100kg/ha",
            "soil_type": "Well-drained sandy loamy soil"
        },
        "rice": {
            "spacing": "20cm x 15cm row spacing",
            "ph_range": "5.5 - 6.5",
            "npk_ratio": "N: 100kg/ha, P: 50kg/ha, K: 50kg/ha",
            "soil_type": "Clayey loamy soils which retain water"
        },
        "wheat": {
            "spacing": "22.5cm row spacing",
            "ph_range": "6.0 - 7.5",
            "npk_ratio": "N: 120kg/ha, P: 60kg/ha, K: 40kg/ha",
            "soil_type": "Well-drained loamy texture soils"
        }
    }
    result = db.get(crop, {
        "spacing": "Standard agricultural crop spacing",
        "ph_range": "6.0 - 7.0",
        "npk_ratio": "N: 80kg/ha, P: 40kg/ha, K: 40kg/ha",
        "soil_type": "Rich organic matter loamy soil"
    })
    return json.dumps(result)

if __name__ == "__main__":
    mcp.run()
