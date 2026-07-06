# =====================================================================
# FILE: backend/app/skills/fertilizer/recommend.py
# DESCRIPTION: Fertilizer Recommendation Skill.
# =====================================================================

from typing import Dict, Any, List

def recommend_fertilizer(crop_name: str) -> Dict[str, Any]:
    """
    Suggests fertilizer types and NPK application guidelines for a target crop.
    """
    crop_clean = crop_name.lower().strip()
    
    # Crop-specific recommendations
    recommendations = {
        "rice": {
            "primary": "NPK 120-60-60 kg/ha",
            "organic": "Apply Sesbania/green manure or Vermicompost before planting.",
            "chemical": "Urea (Nitrogen) in split doses, DAP (Diammonium Phosphate) at sowing, and MOP (Muriate of Potash)."
        },
        "paddy": {
            "primary": "NPK 120-60-60 kg/ha",
            "organic": "Apply green manure (Azolla) or compost before transplanting.",
            "chemical": "Urea in three split doses (basal, tillering, panicle initiation), DAP, and MOP."
        },
        "tomato": {
            "primary": "NPK 100-80-100 kg/ha",
            "organic": "Well-rotted farmyard manure (FYM) or compost at 20-25 tons/ha.",
            "chemical": "Calcium ammonium nitrate (CAN) to prevent blossom-end rot, along with balanced NPK compost."
        },
        "wheat": {
            "primary": "NPK 120-50-40 kg/ha",
            "organic": "Vermicompost at 5 tons/ha mixed into the soil during field preparation.",
            "chemical": "Urea (in two splits: at first irrigation and flowering stages) and Single Super Phosphate (SSP)."
        }
    }
    
    fallback = {
        "primary": "NPK 100-50-50 kg/ha (Standard fallback)",
        "organic": "Incorporate organic matter, farmyard manure (FYM), or compost at 10 tons/ha.",
        "chemical": "Apply balanced granular NPK (19-19-19) during early vegetative growth."
    }
    
    selected = recommendations.get(crop_clean, fallback)
    return {
        "crop": crop_name,
        "recommendations": selected
    }
