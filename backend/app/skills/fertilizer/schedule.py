# =====================================================================
# FILE: backend/app/skills/fertilizer/schedule.py
# DESCRIPTION: Fertilizer Schedule Skill.
# =====================================================================

from typing import Dict, Any, List

def get_fertilizer_schedule(crop_name: str) -> Dict[str, Any]:
    """
    Returns a split application timeline for fertilizing the selected crop.
    """
    crop_clean = crop_name.lower().strip()
    
    schedules = {
        "paddy": [
            {"stage": "Sowing/Transplanting", "timing": "Day 0", "advice": "Apply full dose of P (DAP) and half dose of K (MOP) as basal application."},
            {"stage": "Active Tillering", "timing": "Day 25-30", "advice": "Apply first top-dressing of nitrogen (Urea) to encourage tillering."},
            {"stage": "Panicle Initiation", "timing": "Day 50-55", "advice": "Apply second top-dressing of nitrogen (Urea) and remaining half of K (MOP)."}
        ],
        "rice": [
            {"stage": "Sowing/Transplanting", "timing": "Day 0", "advice": "Apply full dose of P (DAP) and half dose of K (MOP) as basal application."},
            {"stage": "Active Tillering", "timing": "Day 25-30", "advice": "Apply first top-dressing of nitrogen (Urea) to encourage tillering."},
            {"stage": "Panicle Initiation", "timing": "Day 50-55", "advice": "Apply second top-dressing of nitrogen (Urea) and remaining half of K (MOP)."}
        ],
        "tomato": [
            {"stage": "Transplanting", "timing": "Day 0", "advice": "Incorporate compost/compost manure and a small basal dose of phosphorus/nitrogen."},
            {"stage": "Early Vegetative", "timing": "Day 20", "advice": "Top dress with nitrogen fertilizer to boost leaf and vine canopy growth."},
            {"stage": "Flowering & Fruit Set", "timing": "Day 45-50", "advice": "Apply potassium-rich fertilizer to support fruit sizing and calcium nitrate to prevent rot."}
        ]
    }
    
    fallback = [
        {"stage": "Basal Dressing", "timing": "At sowing", "advice": "Apply complete organic compost/manure and half of chemical NPK inputs."},
        {"stage": "Top Dressing", "timing": "3-4 weeks post-germination", "advice": "Apply remaining nitrogen/urea fertilizer to support vegetative growth."}
    ]
    
    selected_schedule = schedules.get(crop_clean, fallback)
    return {
        "crop": crop_name,
        "schedule": selected_schedule
    }
