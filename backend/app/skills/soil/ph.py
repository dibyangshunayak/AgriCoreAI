# =====================================================================
# FILE: backend/app/skills/soil/ph.py
# DESCRIPTION: Soil pH Skill.
# =====================================================================

from typing import Dict, Any

def evaluate_soil_ph(ph: float) -> Dict[str, Any]:
    """
    Evaluates soil pH and provides conditioning advice.
    """
    if ph is None:
        return {"status": "Unknown", "advice": "Soil pH details not provided."}
        
    if ph < 5.5:
        status = "Strongly Acidic"
        advice = "Soil is strongly acidic. Apply agricultural lime (calcium carbonate) to raise pH and prevent aluminum toxicity."
    elif ph < 6.0:
        status = "Moderately Acidic"
        advice = "Soil is moderately acidic. Suitable for acid-tolerant crops (e.g. potatoes). Consider light liming for other crops."
    elif ph <= 7.0:
        status = "Neutral/Optimal"
        advice = "Soil pH is in the optimal neutral range (6.0 - 7.0). Ideal for nutrient uptake across most crops."
    elif ph <= 7.5:
        status = "Slightly Alkaline"
        advice = "Soil is slightly alkaline. Ideal for legumes and alfalfa. No amendments needed for standard crops."
    else:
        status = "Strongly Alkaline"
        advice = "Soil is strongly alkaline. Apply elemental sulfur or organic compost to lower pH and release locked-in micronutrients."
        
    return {
        "ph_value": ph,
        "status": status,
        "advice": advice
    }
