# =====================================================================
# FILE: backend/app/skills/location/gps.py
# DESCRIPTION: GPS coordinates validation skill.
# =====================================================================

import logging

logger = logging.getLogger(__name__)

def is_valid_gps(latitude: float, longitude: float) -> bool:
    """Validate if the latitude and longitude coordinates are physically valid."""
    logger.info(f"Validating coordinates: {latitude}, {longitude}")
    if latitude is None or longitude is None:
        return False
    return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0
