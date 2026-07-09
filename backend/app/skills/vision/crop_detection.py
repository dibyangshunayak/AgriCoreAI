# =====================================================================
# FILE: backend/app/skills/vision/crop_detection.py
# DESCRIPTION: Crop classification skill.
# =====================================================================

import os
import logging

logger = logging.getLogger(__name__)

def identify_crop_by_name(image_path: str) -> str:
    """Classifies which crop is present in the image (based on file naming heuristics)."""
    logger.info("Executing crop detection skill")
    basename = os.path.basename(image_path).lower()
    for crop in ["tomato", "mango", "rice", "wheat", "potato", "apple", "cotton", "maize"]:
        if crop in basename:
            return crop
    return "crop"
