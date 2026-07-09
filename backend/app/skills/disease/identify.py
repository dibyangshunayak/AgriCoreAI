# =====================================================================
# FILE: backend/app/skills/disease/identify.py
# DESCRIPTION: Disease Identification Skill.
# =====================================================================

import re
from typing import Dict, Any
from app.agents.disease_agent import detect_crop_disease

def parse_report(report_text: str) -> Dict[str, Any]:
    """Helper to parse raw NVIDIA Disease Agent report text into structured dict."""
    name_match = re.search(r"🌿\s*Disease\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    cause_match = re.search(r"🦠\s*Cause\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    symptoms_match = re.search(r"🔍\s*Symptoms\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    treatment_match = re.search(r"💊\s*Treatment\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    prevention_match = re.search(r"🛡\s*Prevention\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    confidence_match = re.search(r"📊\s*Confidence\s*:\s*\n?\s*(.*)", report_text, re.IGNORECASE)
    
    name = name_match.group(1).strip() if name_match else "Unknown"
    cause = cause_match.group(1).strip() if cause_match else "Unknown"
    symptoms = symptoms_match.group(1).strip() if symptoms_match else ""
    treatment = treatment_match.group(1).strip() if treatment_match else ""
    prevention = prevention_match.group(1).strip() if prevention_match else ""
    confidence = confidence_match.group(1).strip() if confidence_match else "High"
    
    # Simple validation check matching standard failure signature
    is_failed = "Image Validation Failed" in report_text or "❌" in report_text and "Validation" in report_text
    
    return {
        "success": not is_failed,
        "disease": name,
        "cause": cause,
        "symptoms": symptoms,
        "treatment": treatment,
        "prevention": prevention,
        "confidence": confidence,
        "raw_report": report_text
    }

def identify_disease(image_path: str) -> Dict[str, Any]:
    """Analyze crop leaves image for disease diagnosis and return structured results."""
    raw_report = detect_crop_disease(image_path)
    return parse_report(raw_report)

