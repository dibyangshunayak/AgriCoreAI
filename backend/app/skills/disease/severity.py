# =====================================================================
# FILE: backend/app/skills/disease/severity.py
# DESCRIPTION: Disease Severity Skill.
# =====================================================================

from typing import Dict, Any

def analyze_severity(disease_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates symptoms text and diagnosis confidence to estimate severity.
    """
    symptoms = disease_info.get("symptoms", "").lower()
    disease_name = disease_info.get("disease", "").lower()
    
    # Base heuristics
    severity_level = "Medium"
    score = 0.5
    
    critical_keywords = ["severe", "blight", "rot", "critical", "wilting", "dieback", "death", "widespread", "loss"]
    mild_keywords = ["mild", "early", "light", "slight", "healthy", "few", "minor"]
    
    for kw in critical_keywords:
        if kw in symptoms or kw in disease_name:
            severity_level = "High"
            score = 0.85
            break
            
    for kw in mild_keywords:
        if kw in symptoms or kw in disease_name:
            if severity_level != "High": # Critical takes priority
                severity_level = "Low"
                score = 0.20
            break
            
    # Add descriptions
    descriptions = {
        "Low": "Early stage infection. Crop damage is minimal. Easily manageable with cultural controls.",
        "Medium": "Active infection spreading. Moderate threat to crop yields. Requires localized treatment.",
        "High": "Advanced infection stage! Severe threat to harvest. Immediate intervention with systemic treatments necessary."
    }
    
    return {
        "level": severity_level,
        "score": score,
        "description": descriptions.get(severity_level, "")
    }
