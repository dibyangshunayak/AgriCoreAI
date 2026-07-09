# =====================================================================
# FILE: backend/app/services/response_validator.py
# DESCRIPTION: Validator service that scans synthesized responses for
#              banned terms based on active agents/intents.
# =====================================================================

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def validate_response(response: str, agents: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks the response against negative constraints defined in Rule 8.
    - Weather responses must not contain: fertilizer, crop rotation, soil management.
    - Crop responses must not contain: latitude, longitude, coordinates.
    - Location responses must not contain: fertilizer recommendations (or fertilizer recommendation), disease treatment.
    Returns (is_valid, list_of_failed_rules).
    """
    if not response:
        return True, []
        
    response_lower = response.lower()
    failed = []
    
    # Standardize agent names (can be 'weather', 'weather_agent', etc.)
    normalized_agents = [a.replace("_agent", "").lower() for a in agents]
    
    if "weather" in normalized_agents:
        banned_weather = ["fertilizer", "crop rotation", "soil management"]
        for term in banned_weather:
            if term in response_lower:
                failed.append(f"Weather response contains banned term: '{term}'")
                
    if "crop" in normalized_agents:
        banned_crop = ["latitude", "longitude", "coordinates"]
        for term in banned_crop:
            if term in response_lower:
                failed.append(f"Crop response contains banned term: '{term}'")
                
    if "location" in normalized_agents:
        banned_location = ["fertilizer recommendation", "disease treatment"]
        for term in banned_location:
            if term in response_lower:
                failed.append(f"Location response contains banned term: '{term}'")
                
    is_valid = len(failed) == 0
    return is_valid, failed
