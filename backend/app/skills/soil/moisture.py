# =====================================================================
# FILE: backend/app/skills/soil/moisture.py
# DESCRIPTION: Soil Moisture Skill.
# =====================================================================

from typing import Dict, Any

def evaluate_soil_moisture(soil_moisture: float) -> Dict[str, Any]:
    """
    Evaluates soil moisture levels and provides irrigation advice.
    """
    if soil_moisture is None:
        return {"status": "Unknown", "advice": "Soil moisture data is not available."}
        
    if soil_moisture < 0.15:
        status = "Critical Dry"
        advice = "Low soil moisture. Crop roots are dry; immediate irrigation is recommended."
    elif soil_moisture > 0.40:
        status = "Waterlogged"
        advice = "High soil moisture (waterlogged conditions). Halt irrigation and check drainage to prevent root rot."
    else:
        status = "Optimal"
        advice = "Soil moisture is at an optimal level for crop growth."
        
    return {
        "status": status,
        "moisture_value": soil_moisture,
        "advice": advice
    }
