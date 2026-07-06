# =====================================================================
# FILE: backend/app/mcp/search_mcp.py
# DESCRIPTION: Search MCP Server providing agricultural web search queries.
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
logger = logging.getLogger("search_mcp")

mcp = FastMCP("Search Server")

@mcp.tool()
def search_web(query: str) -> str:
    """
    Search the web for up-to-date crop alerts, market prices, and agricultural guidelines.

    Parameters:
        query (str): The search query.

    Returns:
        str: JSON-serialized string containing mock/live search results.
    """
    logger.info(f"Search MCP received query: {query}")
    q_lower = query.lower()
    if "tomato" in q_lower:
        results = "Latest advisory: Early blight in tomato can be treated with chlorothalonil or copper-based fungicides. Keep foliage dry."
    elif "price" in q_lower:
        results = "Market rates: Paddy crop prices have risen by 3% in regional mandis. Average rate: INR 2,183/quintal."
    else:
        results = "Search results: Agricultural extension services recommend regular crop rotation and biological pest controls."
    return json.dumps({"results": results})

if __name__ == "__main__":
    mcp.run()
