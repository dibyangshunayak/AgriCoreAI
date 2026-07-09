# =====================================================================
# FILE: backend/app/skills/government/schemes.py
# DESCRIPTION: Subsidies mapping skill.
# =====================================================================

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def match_schemes(state: str, crop: str) -> List[Dict[str, str]]:
    """Determine eligible farm benefits based on crop and state."""
    logger.info("Executing government schemes mapping skill")
    schemes = [
        {
            "name": "PM-Kisan",
            "benefit": "INR 6,000 yearly income support paid in 3 instalments of INR 2,000."
        },
        {
            "name": "Pradhan Mantri Fasal Bima Yojana",
            "benefit": "Low premium crop damage coverage (2% Kharif / 1.5% Rabi premium rate)."
        }
    ]
    if state and state.lower() == "odisha":
        schemes.append({
            "name": "KALIA Scheme (Odisha)",
            "benefit": "Financial grant assistance of INR 25,000 for small farming families."
        })
    return schemes
