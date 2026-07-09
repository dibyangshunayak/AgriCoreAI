# =====================================================================
# FILE: backend/app/skills/crop/knowledge.py
# DESCRIPTION: Cultivation guidelines skill.
# =====================================================================

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_crop_care_info(crop_name: str) -> Dict[str, Any]:
    """Retrieve cultivation instructions for standard farming crops."""
    logger.info("Executing crop care knowledge skill")
    db = {
        "tomato": {
            "spacing": "60cm x 45cm spacing",
            "ph": "6.0 - 6.8",
            "temp": "18 - 28 degrees Celsius",
            "npk": "N: 80, P: 40, K: 100"
        },
        "rice": {
            "spacing": "20cm x 15cm spacing",
            "ph": "5.5 - 6.5",
            "temp": "22 - 32 degrees Celsius",
            "npk": "N: 100, P: 50, K: 50"
        }
    }
    return db.get(crop_name.lower(), {
        "spacing": "Standard space guidelines",
        "ph": "6.0 - 7.0",
        "temp": "20 - 30 degrees Celsius",
        "npk": "N: 80, P: 40, K: 40"
    })
