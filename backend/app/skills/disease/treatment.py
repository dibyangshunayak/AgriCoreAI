# =====================================================================
# FILE: backend/app/skills/disease/treatment.py
# DESCRIPTION: Disease Treatment Skill.
# =====================================================================

from typing import Dict, Any, List

def get_treatment_advisory(disease_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and structures treatment options from disease info.
    """
    treatment_raw = disease_info.get("treatment", "")
    prevention_raw = disease_info.get("prevention", "")
    
    # Parse items if they are list-like
    def clean_advisory(text: str) -> List[str]:
        if not text:
            return []
        items = []
        # Split by typical list indicators
        lines = text.split("\n")
        for line in lines:
            line_clean = line.strip().lstrip("-*•123456789. ")
            if line_clean:
                items.append(line_clean)
        return items if items else [text]

    return {
        "treatment_steps": clean_advisory(treatment_raw),
        "preventative_measures": clean_advisory(prevention_raw)
    }
