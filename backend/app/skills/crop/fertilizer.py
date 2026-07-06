# =====================================================================
# FILE: backend/app/skills/crop/fertilizer.py
# DESCRIPTION: NPK fertilizer calculation skill.
# =====================================================================

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def calculate_npk_dose(crop_name: str, area_acres: float) -> Dict[str, float]:
    """Calculate the precise NPK weight in kg required for a given acreage."""
    logger.info("Executing NPK dose calculation skill")
    base_ratios = {
        "tomato": {"n": 80.0, "p": 40.0, "k": 100.0},
        "rice": {"n": 100.0, "p": 50.0, "k": 50.0},
        "wheat": {"n": 120.0, "p": 60.0, "k": 40.0}
    }
    ratio = base_ratios.get(crop_name.lower(), {"n": 80.0, "p": 40.0, "k": 40.0})
    return {
        "nitrogen_kg": ratio["n"] * area_acres,
        "phosphorus_kg": ratio["p"] * area_acres,
        "potash_kg": ratio["k"] * area_acres
    }
