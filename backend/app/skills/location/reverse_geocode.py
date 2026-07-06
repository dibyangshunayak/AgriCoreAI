# =====================================================================
# FILE: backend/app/skills/location/reverse_geocode.py
# DESCRIPTION: Reverse geocoding location skill.
# =====================================================================

import logging

logger = logging.getLogger(__name__)

def skill_reverse_geocode(latitude: float, longitude: float) -> str:
    """Provide quick localized description for specific key farming coordinates."""
    logger.info("Executing reverse geocode location skill")
    if abs(latitude - 21.9592) < 0.001 and abs(longitude - 86.7430) < 0.001:
        return "Baripada, Mayurbhanj, Odisha, India"
    if abs(latitude - 20.2961) < 0.001 and abs(longitude - 85.8245) < 0.001:
        return "Bhubaneswar, Khordha, Odisha, India"
    return "India"
