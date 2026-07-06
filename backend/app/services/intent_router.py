# =====================================================================
# FILE: backend/app/services/intent_router.py
# DESCRIPTION: Rule/Keyword-based Intent Router for AgriCore AI.
#              Classifies user queries semantically using keywords to coordinate between
#              specialized agents (crop, weather, location, disease) with 0ms latency.
# =====================================================================

import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Keyword Lists from Rule 4
WEATHER_KWS = ["rain", "weather", "forecast", "temperature", "humidity", "storm", "wind", "temp", "precipitation", "climate", "cloudy", "sunny"]
DISEASE_KWS = ["leaf", "spots", "yellow", "disease", "pest", "fungus", "infection", "spot", "leaves", "blight", "rot", "mold", "mildew", "rust", "lesion", "dieback", "anthracnose", "canker"]
LOCATION_KWS = ["where am i", "my location", "district", "coordinates", "near me", "coordinate", "gps", "latitude", "longitude", "geocoding", "suitable crops"]
CROP_KWS = ["cultivation", "fertilizer", "irrigation", "soil", "harvest", "crop rotation", "seed", "yield", "farming", "cultivate", "fertilizers", "irrigate", "water", "sow", "sowing", "harvesting", "seeds", "yields", "farm", "crop", "crops", "paddy", "rice", "tomato", "wheat", "maize", "potato", "apple", "cotton", "urea", "dap", "npk", "vermicompost", "manure", "mulching", "azolla", "kharif", "rabi", "agriculture", "agricultural", "agronomy", "agronomic"]

# Crop-specific keywords to identify if crop agent should be activated
CROP_SPECIFIC_KWS = ["paddy", "rice", "tomato", "wheat", "maize", "potato", "apple", "cotton", "cultivation", "rotation", "soil", "fertilizer", "fertilizers", "harvest", "sow", "sowing", "yield", "urea", "dap", "npk", "vermicompost", "manure", "azolla", "kharif", "rabi", "agriculture", "agricultural", "agronomy", "agronomic"]

def count_word_matches(keywords: List[str], text: str) -> int:
    """Helper to count how many keywords appear in text as whole words/phrases."""
    count = 0
    for kw in keywords:
        if " " in kw:
            if kw in text:
                count += 1
        else:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                count += 1
    return count

def classify_intent(
    user_query: str,
    image_uploaded: bool = False,
    conversation_context: Optional[List[Dict[str, str]]] = None,
    gps_available: bool = False,
    location_name: Optional[str] = None,
    file_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deterministic rule-based intent routing with confidence scoring.
    """
    logger.info(f"Keyword intent routing for query: '{user_query}' | Image: {image_uploaded}")
    
    query_lower = user_query.lower().strip().rstrip(".?!,")
    
    # 1. Deterministic Greeting & General Intent Check (Rule 1)
    general_queries = {
        "hi", "hello", "hellow", "hey", "hola", "greetings", "good morning", "good evening",
        "who are you", "what can you do", "thanks", "thank you", "bye"
    }
    
    is_general = query_lower in general_queries
    if not is_general:
        words = query_lower.split()
        if words and words[0] in {"hi", "hello", "hellow", "hey", "hola", "greetings"} and len(words) <= 3:
            is_general = True
            
    if is_general:
        return {"agents": ["general"], "confidence": {"general": 1.0}}

    confidence = {}
    
    # 2. Match counts on whole word boundaries
    weather_matches = count_word_matches(WEATHER_KWS, query_lower)
    disease_matches = count_word_matches(DISEASE_KWS, query_lower)
    location_matches = count_word_matches(LOCATION_KWS, query_lower)
    crop_matches = count_word_matches(CROP_KWS, query_lower)
    
    # Special rules & overrides
    # "Should I irrigate today?" or "Should I irrigate tomorrow?" -> weather
    has_irrigation = "irrigate" in query_lower or "irrigation" in query_lower or "water" in query_lower
    has_time_or_weather = any(w in query_lower for w in ["today", "tomorrow", "weather", "rain", "forecast", "storm", "precipit", "temp"])
    if has_irrigation and has_time_or_weather:
        # Check if crop name or crop details are mentioned
        has_crop_spec = any(re.search(r'\b' + re.escape(ckw) + r'\b', query_lower) for ckw in CROP_SPECIFIC_KWS)
        if not has_crop_spec:
            weather_matches += 2
        else:
            weather_matches += 1
            
    if "suitable crops" in query_lower or "crops for" in query_lower or "crops suit" in query_lower:
        location_matches += 2
        
    if "where am i" in query_lower or "my location" in query_lower or "coordinates" in query_lower:
        location_matches += 2
        
    # Calculate confidence scores (Rule 5 formula)
    if weather_matches > 0:
        confidence["weather"] = round(min(0.70 + 0.12 * weather_matches, 0.98), 2)
    if disease_matches > 0 or image_uploaded:
        confidence["disease"] = round(min(0.70 + 0.12 * max(disease_matches, 1), 0.98), 2)
    if location_matches > 0:
        confidence["location"] = round(min(0.70 + 0.12 * location_matches, 0.98), 2)
        
    # Check Crop score suppression
    has_crop_spec = any(re.search(r'\b' + re.escape(ckw) + r'\b', query_lower) for ckw in CROP_SPECIFIC_KWS)
    # If crop keyword matches but query is weather-only or location-only or disease-only without crop specific keywords, suppress crop
    if crop_matches > 0 and not has_crop_spec and ("weather" in confidence or "location" in confidence or "disease" in confidence):
        crop_matches = 0
        
    if crop_matches > 0:
        confidence["crop"] = round(min(0.70 + 0.12 * crop_matches, 0.98), 2)
        
    # Collect agents with confidence >= 0.70
    agents = [a for a, score in confidence.items() if score >= 0.70]
    
    # If image is uploaded but disease was not added, add it (fallback protection)
    if image_uploaded and "disease" not in agents:
        agents.append("disease")
        confidence["disease"] = 0.94
        
    # Remove location or other agents if confidence is too low
    if not agents:
        return {"agents": ["crop"], "confidence": {"crop": 0.70}}
        
    return {"agents": agents, "confidence": {a: score for a, score in confidence.items() if a in agents}}
