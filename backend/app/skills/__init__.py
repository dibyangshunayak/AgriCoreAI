# =====================================================================
# FILE: backend/app/skills/__init__.py
# DESCRIPTION: Skills module initialization and dynamic loader.
# =====================================================================

import importlib
import logging

logger = logging.getLogger(__name__)

# Base static exports for backwards compatibility
from app.skills.weather.forecast import get_forecast
from app.skills.weather.alerts import check_weather_alerts
from app.skills.weather.advice import generate_weather_advice

from app.skills.disease.identify import identify_disease
from app.skills.disease.severity import analyze_severity
from app.skills.disease.treatment import get_treatment_advisory

from app.skills.soil.moisture import evaluate_soil_moisture
from app.skills.soil.ph import evaluate_soil_ph

from app.skills.fertilizer.recommend import recommend_fertilizer
from app.skills.fertilizer.schedule import get_fertilizer_schedule

# New skill exports
from app.skills.weather.recommendation import get_weather_recommendation
from app.skills.vision.leaf_detection import is_valid_leaf_image
from app.skills.vision.crop_detection import identify_crop_by_name
from app.skills.location.gps import is_valid_gps
from app.skills.location.reverse_geocode import skill_reverse_geocode
from app.skills.translator.translate import translate_query
from app.skills.government.schemes import match_schemes
from app.skills.crop.knowledge import get_crop_care_info
from app.skills.crop.fertilizer import calculate_npk_dose

def load_skill(category: str, name: str):
    """
    Dynamically loads and returns the module for a requested skill.
    Enables memory-efficient loading at runtime.
    """
    module_path = f"app.skills.{category}.{name}"
    try:
        logger.info(f"Dynamically loading skill: {module_path}")
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.error(f"Failed to dynamically import skill {module_path}: {e}")
        raise ValueError(f"Skill '{category}/{name}' could not be dynamically resolved.")

