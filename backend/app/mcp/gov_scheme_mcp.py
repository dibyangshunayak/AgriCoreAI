# =====================================================================
# FILE: backend/app/mcp/gov_scheme_mcp.py
# DESCRIPTION: Government Schemes MCP Server providing matching subsidies.
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
logger = logging.getLogger("gov_scheme_mcp")

mcp = FastMCP("Gov Scheme Server")

@mcp.tool()
def query_schemes(state: str, crop: str) -> str:
    """
    Retrieve eligible government schemes and credit support matched to the given state and crop.

    Parameters:
        state (str): State of the farmer.
        crop (str): Target cultivation crop.

    Returns:
        str: JSON-serialized string of schemes.
    """
    logger.info(f"Gov Schemes MCP received query for state={state}, crop={crop}")
    schemes = [
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Insurance coverage and financial support to farmers in the event of failure of crops.",
            "premium_rate": "2.0% for Kharif crops, 1.5% for Rabi crops"
        },
        {
            "name": "PM-Kisan Samman Nidhi",
            "description": "Direct income support benefit of INR 6,000 per year for landholding families.",
            "benefit": "INR 2,000 transferred in three equal installments"
        }
    ]
    if state.lower() == "odisha":
        schemes.append({
            "name": "KALIA Scheme (Odisha)",
            "description": "Krushak Assistance for Livelihood and Income Augmentation providing financial aid to small farmers and landless laborers."
        })
    return json.dumps(schemes)

if __name__ == "__main__":
    mcp.run()
