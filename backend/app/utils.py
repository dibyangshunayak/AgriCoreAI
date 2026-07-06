# =====================================================================
# FILE: backend/app/utils.py
# DESCRIPTION: Utility wrapper functions for spell correction, translation,
#              intent routing, and external service calls used by the chat endpoint.
# =====================================================================

import os
import json
import logging
import threading
import flask

# Initialize logger
logger = logging.getLogger(__name__)

# Request-scoped local storage for backup if flask.g is not present/accessible
_local = threading.local()

def correct_spelling(query: str) -> str:
    """
    Corrects spelling errors in an English query while protecting agricultural vocabulary.
    """
    from app.services.spell_service import spell_service
    try:
        return spell_service.correct_query(query)
    except Exception as e:
        logger.error(f"Error correcting spelling: {e}")
        return query

def translate_to_english(text: str) -> str:
    """
    Detects the primary language of the text, stores the language code in the request context,
    and translates the query to English.
    """
    from app.services.language_service import language_service
    from app.services.translator_service import translator_service
    
    try:
        lang = language_service.detect_language(text)
        logger.info(f"[utils] Detected language: '{lang}' for text: '{text[:30]}...'")
        
        # Store language code for back-translation later in the request lifecycle
        if flask.has_request_context():
            flask.g.detected_lang = lang
        else:
            _local.detected_lang = lang
            
        return translator_service.translate_to_english(text, lang)
    except Exception as e:
        logger.error(f"Error translating to English: {e}")
        return text

def translate_from_english(text: str) -> str:
    """
    Translates synthesized response from English back to the stored original language.
    """
    from app.services.translator_service import translator_service
    
    try:
        if flask.has_request_context():
            lang = getattr(flask.g, "detected_lang", "en")
        else:
            lang = getattr(_local, "detected_lang", "en")
            
        logger.info(f"[utils] Translating back from English to target language: '{lang}'")
        return translator_service.translate_from_english(text, lang)
    except Exception as e:
        logger.error(f"Error translating from English: {e}")
        return text

def route_intent(query: str, latitude: float = None, longitude: float = None, file_path: str = None) -> list:
    """
    Routes query intents by classifying the query into a list of active agents (e.g. ['weather', 'crop']).
    """
    from app.services.intent_router import classify_intent
    from app.services.image_service import is_image_file
    
    try:
        image_uploaded = is_image_file(file_path) if file_path else False
        gps_available = latitude is not None and longitude is not None
        
        result = classify_intent(
            user_query=query,
            image_uploaded=image_uploaded,
            gps_available=gps_available
        )
        return result.get("agents", [])
    except Exception as e:
        logger.error(f"Error in intent routing: {e}")
        return ["crop"]

def call_weather_api(latitude: float, longitude: float) -> dict:
    """
    Retrieves weather data from the weather service for the given coordinates.
    """
    from app.services.weather_service import get_weather
    try:
        res = get_weather(latitude, longitude)
        return res if res else {}
    except Exception as e:
        logger.error(f"Error calling weather API: {e}")
        return {}

def call_location_api(latitude: float, longitude: float) -> dict:
    """
    Uses the location reverse geocoding API to resolve coordinates to region/city details.
    """
    from app.mcp.location_mcp import reverse_geocode
    try:
        return reverse_geocode(latitude, longitude)
    except Exception as e:
        logger.error(f"Error calling location API: {e}")
        return {}

def call_llm(context_json: str) -> str:
    """
    Loads context from JSON, queries specialized agents depending on intent, and synthesizes the response.
    """
    from app.services.response_generator import ResponseSynthesizer
    from app.services.rag_service import RAGService
    from app.services.image_service import is_image_file
    
    try:
        context = json.loads(context_json)
        query = context.get("query", "")
        intents = context.get("intents", [])
        latitude = context.get("latitude")
        longitude = context.get("longitude")
        file_path = context.get("file_path")
        
        crop_knowledge = None
        weather_advisory = None
        location_suitability = None
        disease_report = None
        rag_context = None
        
        # 1. Fetch Crop Knowledge if needed
        if "crop" in intents:
            from app.agents.crop_agent import get_crop_recommendation
            try:
                crop_knowledge = get_crop_recommendation(query)
            except Exception as e:
                logger.warning(f"Crop Agent failed: {e}")
                
        # 2. Fetch Weather Advisory if needed
        if "weather" in intents and latitude is not None and longitude is not None:
            from app.agents.weather_agent import get_weather_recommendation
            try:
                weather_res = get_weather_recommendation(latitude, longitude, query)
                if isinstance(weather_res, dict):
                    weather_advisory = weather_res.get("weather_advisory") or weather_res.get("advisory")
                else:
                    weather_advisory = str(weather_res)
            except Exception as e:
                logger.warning(f"Weather Agent failed: {e}")
                
        # 3. Fetch Location Suitability if needed
        if "location" in intents and latitude is not None and longitude is not None:
            from app.agents.location_agent import get_location_suitability
            try:
                location_data = context.get("location") or {}
                loc_res = get_location_suitability(latitude, longitude, query, location_data)
                if isinstance(loc_res, dict):
                    location_suitability = loc_res.get("suitability_recommendation")
                else:
                    location_suitability = str(loc_res)
            except Exception as e:
                logger.warning(f"Location Agent failed: {e}")
                
        # 4. Fetch Disease Report if needed
        if "disease" in intents and file_path and is_image_file(file_path):
            from app.agents.disease_agent import detect_crop_disease
            try:
                abs_image_path = file_path
                if not os.path.isabs(abs_image_path):
                    from app.api.router import UPLOAD_FOLDER
                    base_filename = os.path.basename(file_path)
                    abs_image_path = os.path.join(UPLOAD_FOLDER, base_filename)
                
                dis_res = detect_crop_disease(abs_image_path)
                if isinstance(dis_res, dict):
                    disease_report = dis_res.get("disease_report")
                else:
                    disease_report = str(dis_res)
            except Exception as e:
                logger.warning(f"Disease Agent failed: {e}")
                
        # 5. Retrieve RAG context
        try:
            rag_context = RAGService().retrieve_context(query)
        except Exception as e:
            logger.warning(f"RAG Service failed: {e}")
            
        # 6. Synthesize the final response
        return ResponseSynthesizer.synthesize_response(
            query=query,
            context=context,
            crop_knowledge=crop_knowledge,
            weather_advisory=weather_advisory,
            location_suitability=location_suitability,
            disease_report=disease_report,
            rag_context=rag_context
        )
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        # Fallback to nvidia_service directly
        try:
            from app.services.nvidia_service import generate_text
            return generate_text(query)
        except Exception as fallback_err:
            logger.error(f"Fallback generation failed: {fallback_err}")
            return "Sorry, I encountered an error while processing your request. Please try again."
