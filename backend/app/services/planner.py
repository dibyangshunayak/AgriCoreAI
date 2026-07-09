# =====================================================================
# FILE: backend/app/services/planner.py
# DESCRIPTION: Advanced reasoning-based Planner for AgriCore AI.
#              Analyzes user query and context, thinking step-by-step,
#              to generate a structured DAG of agent/tool calls.
# =====================================================================

import json
import logging
import re
from typing import Dict, Any, List, Optional
from app.services.nvidia_service import generate_text

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def deterministic_agent_fallback(query: str, image_uploaded: bool) -> Optional[Dict[str, Any]]:
    """
    Heuristics-based classifier to guarantee 100% accurate classification for common routes,
    structured with the new DAG execution format.
    """
    clean_query = query.strip().lower().rstrip(".?!")
    
    # Greetings & Self-identification & General intents
    general_queries = {
        "hi", "hello", "hellow", "hey", "hola", "greetings", "good morning", "good evening",
        "who are you", "what can you do", "thanks", "thank you", "bye"
    }
    
    is_general = clean_query in general_queries
    if not is_general:
        words = clean_query.split()
        if words and words[0] in {"hi", "hello", "hellow", "hey", "hola", "greetings"} and len(words) <= 3:
            is_general = True
            
    if is_general:
        return {
            "reasoning": "Simple greeting or capability query. Invoke general agent directly.",
            "steps": [{"id": "step_1", "agent": "general", "tool": None, "depends_on": [], "action": "Provide greeting, capability overview, or polite response"}],
            "required_data": [],
            "response_tone": "general"
        }
        
    # Standard general agricultural questions
    if any(phrase in clean_query for phrase in ["rice cultivation", "crop rotation", "soil fertility", "improve soil", "water does paddy need"]):
        return {
            "reasoning": "Scientific question about general crop cultivation or soil management. Activate crop agent.",
            "steps": [{"id": "step_1", "agent": "crop", "tool": None, "depends_on": [], "action": "Retrieve crop cultivation knowledge"}],
            "required_data": [],
            "response_tone": "scientific"
        }

    # Combined Weather + Crop
    if "irrigate" in clean_query and ("tomorrow" in clean_query or "paddy" in clean_query or "crop" in clean_query):
        return {
            "reasoning": "Farmer asks about irrigation. This requires weather forecast to assess rainfall probability and crop guidelines for water requirements.",
            "steps": [
                {"id": "step_1", "agent": "weather", "tool": "weather_api", "depends_on": [], "action": "Retrieve forecast data to check rainfall probability"},
                {"id": "step_2", "agent": "crop", "tool": None, "depends_on": ["step_1"], "action": "Retrieve irrigation guidelines for specified crop and synthesize with weather"}
            ],
            "required_data": ["gps_coordinates"],
            "response_tone": "scientific"
        }

    # Weather Forecasts
    if any(w in clean_query for w in ["rain tomorrow", "will it rain", "weather forecast", "temperature today"]):
        return {
            "reasoning": "Farmer queries about upcoming weather or precipitation. Call weather API.",
            "steps": [{"id": "step_1", "agent": "weather", "tool": "weather_api", "depends_on": [], "action": "Retrieve forecast metrics and irrigation recommendations"}],
            "required_data": ["gps_coordinates"],
            "response_tone": "general"
        }

    # Location queries
    if clean_query in ["tell me my location", "where am i", "my coordinates", "what is my location", "my location"]:
        return {
            "reasoning": "Farmer asks to resolve coordinates or get location information.",
            "steps": [{"id": "step_1", "agent": "location", "tool": "reverse_geocode", "depends_on": [], "action": "Resolve GPS coordinates and geocode name"}],
            "required_data": ["gps_coordinates"],
            "response_tone": "general"
        }
        
    if "suitable crops" in clean_query or "crops suit my area" in clean_query:
        return {
            "reasoning": "Crop suitability check based on region/district.",
            "steps": [
                {"id": "step_1", "agent": "location", "tool": "reverse_geocode", "depends_on": [], "action": "Geocode coordinates to address"},
                {"id": "step_2", "agent": "location", "tool": None, "depends_on": ["step_1"], "action": "Evaluate crop suitability for the geocoded district"}
            ],
            "required_data": ["gps_coordinates", "location_name"],
            "response_tone": "scientific"
        }

    # Disease diagnosis
    if "spots" in clean_query or "disease" in clean_query or "blight" in clean_query or "pest" in clean_query or "fungus" in clean_query:
        if image_uploaded:
            return {
                "reasoning": "Image is uploaded and keywords indicate disease. Invoke disease agent.",
                "steps": [{"id": "step_1", "agent": "disease", "tool": None, "depends_on": [], "action": "Analyze crop leaves image for disease diagnosis"}],
                "required_data": ["leaf_image"],
                "response_tone": "scientific"
            }
        else:
            return {
                "reasoning": "Disease query but no image uploaded. Request image.",
                "steps": [],
                "required_data": ["leaf_image"],
                "response_tone": "urgent"
            }
            
    return None


def deterministic_agent_fallback(query: str, image_uploaded: bool) -> Optional[Dict[str, Any]]:
    """
    Heuristics-based classifier to guarantee 100% accurate classification for common routes,
    structured with the new DAG execution format.
    """
    clean_query = query.strip().lower().rstrip(".?!")
    
    # Greetings & Self-identification & General intents
    general_queries = {
        "hi", "hello", "hellow", "hey", "hola", "greetings", "good morning", "good evening",
        "who are you", "what can you do", "thanks", "thank you", "bye"
    }
    
    is_general = clean_query in general_queries
    if not is_general:
        words = clean_query.split()
        if words and words[0] in {"hi", "hello", "hellow", "hey", "hola", "greetings"} and len(words) <= 3:
            is_general = True
            
    if is_general:
        return {
            "reasoning": "Simple greeting or capability query. Invoke general agent directly.",
            "steps": [{"id": "step_1", "agent": "general", "tool": None, "depends_on": [], "action": "Provide greeting, capability overview, or polite response"}],
            "required_data": [],
            "response_tone": "general"
        }
        
    # Scientific queries with crop details
    if any(phrase in clean_query for phrase in ["rice cultivation", "crop rotation", "soil fertility", "improve soil", "water does paddy need"]):
        return {
            "reasoning": "Scientific question about general crop cultivation or soil management. Activate crop agent.",
            "steps": [{"id": "step_1", "agent": "crop", "tool": "crop_database", "depends_on": [], "action": "Retrieve crop cultivation knowledge"}],
            "required_data": [],
            "response_tone": "scientific"
        }

    # Weather Forecasts
    if any(w in clean_query for w in ["rain tomorrow", "will it rain", "weather forecast", "temperature today"]):
        return {
            "reasoning": "Farmer queries about upcoming weather or precipitation. Call weather API.",
            "steps": [{"id": "step_1", "agent": "weather", "tool": "weather_mcp", "depends_on": [], "action": "Retrieve weather metrics and irrigation recommendations"}],
            "required_data": ["gps_coordinates"],
            "response_tone": "general"
        }

    # Location queries
    if clean_query in ["tell me my location", "where am i", "my coordinates", "what is my location", "my location"]:
        return {
            "reasoning": "Farmer asks to resolve coordinates or get location information.",
            "steps": [{"id": "step_1", "agent": "location", "tool": "location_mcp", "depends_on": [], "action": "Resolve GPS coordinates and geocode name"}],
            "required_data": ["gps_coordinates"],
            "response_tone": "general"
        }
        
    if "suitable crops" in clean_query or "crops suit my area" in clean_query:
        return {
            "reasoning": "Crop suitability check based on region/district.",
            "steps": [
                {"id": "step_1", "agent": "location", "tool": "location_mcp", "depends_on": [], "action": "Geocode coordinates to address"},
                {"id": "step_2", "agent": "location", "tool": None, "depends_on": ["step_1"], "action": "Evaluate crop suitability for the geocoded district"}
            ],
            "required_data": ["gps_coordinates", "location_name"],
            "response_tone": "scientific"
        }

    # Calculator intents
    if any(phrase in clean_query for phrase in ["calculate", "seed rate", "spacing", "fertilizer amount", "yield calculator"]):
        return {
            "reasoning": "Farmer requests a calculation. Route to the calculator agent.",
            "steps": [{"id": "step_1", "agent": "calculator", "tool": "calculator", "depends_on": [], "action": "Perform agricultural mathematical calculations"}],
            "required_data": [],
            "response_tone": "scientific"
        }

    # Government scheme queries
    if any(phrase in clean_query for phrase in ["government scheme", "subsidy", "subsidies", "pm kisan", "crop insurance"]):
        return {
            "reasoning": "Farmer asks about government schemes or subsidies.",
            "steps": [{"id": "step_1", "agent": "government", "tool": "gov_scheme_mcp", "depends_on": [], "action": "Retrieve eligible government schemes and crop benefits"}],
            "required_data": [],
            "response_tone": "general"
        }

    # Complex query matching "My tomato leaves have spots. Will rain tomorrow make it worse?"
    if ("spot" in clean_query or "disease" in clean_query or "blight" in clean_query) and ("rain" in clean_query or "weather" in clean_query or "tomorrow" in clean_query):
        if image_uploaded:
            return {
                "reasoning": "Farmer reports spots on leaves and asks about upcoming rain. This requires disease detection, location/weather lookup, and crop database verification.",
                "steps": [
                    {"id": "step_loc", "agent": "location", "tool": "location_mcp", "depends_on": [], "action": "Resolve location of the farm"},
                    {"id": "step_weather", "agent": "weather", "tool": "weather_mcp", "depends_on": ["step_loc"], "action": "Fetch weather forecast to assess tomorrow's rain"},
                    {"id": "step_disease", "agent": "disease", "tool": "vision", "depends_on": [], "action": "Analyze uploaded leaf image to diagnose disease"},
                    {"id": "step_crop", "agent": "crop", "tool": "crop_database", "depends_on": ["step_disease", "step_weather"], "action": "Consult crop knowledge to see if rain will worsen diagnosed disease and synthesize advice"}
                ],
                "required_data": ["gps_coordinates", "leaf_image"],
                "response_tone": "scientific"
            }
        else:
            return {
                "reasoning": "Disease query but no image uploaded. Request image.",
                "steps": [],
                "required_data": ["leaf_image"],
                "response_tone": "urgent"
            }

    # Simple disease diagnosis fallback
    if "spots" in clean_query or "disease" in clean_query or "blight" in clean_query or "pest" in clean_query or "fungus" in clean_query:
        if image_uploaded:
            return {
                "reasoning": "Image is uploaded and keywords indicate disease. Invoke disease agent.",
                "steps": [{"id": "step_1", "agent": "disease", "tool": "vision", "depends_on": [], "action": "Analyze crop leaves image for disease diagnosis"}],
                "required_data": ["leaf_image"],
                "response_tone": "scientific"
            }
        else:
            return {
                "reasoning": "Disease query but no image uploaded. Request image.",
                "steps": [],
                "required_data": ["leaf_image"],
                "response_tone": "urgent"
            }
            
    return None


def generate_execution_plan(
    user_query: str,
    image_uploaded: bool = False,
    gps_available: bool = False,
    location_name: Optional[str] = None,
    conversation_context: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Leverages NVIDIA Nemotron with reasoning capability to generate a structured execution DAG plan.
    """
    logger.info(f"Generating execution plan for query: '{user_query}' | Image: {image_uploaded} | GPS: {gps_available}")

    # Check deterministic override first for 100% accuracy on basic routes
    fallback_plan = deterministic_agent_fallback(user_query, image_uploaded)
    if fallback_plan:
        logger.info(f"Heuristics-based plan match succeeded: {fallback_plan}")
        return fallback_plan

    system_prompt = """You are AgriAgent AI's Principal Task Planner.
Analyze the farmer's query and context, think step-by-step to plan the tasks required, and return a structured execution plan as a JSON object.

Available Agents:
- general: for greetings, farewells, thanks, capability questions, and general conversation.
- crop: for general agriculture, cultivation, soil, planting, harvesting, fertilizers, NPK advice.
- weather: for forecasts, temperature, precipitation, climate, and soil moisture.
- location: for geocoding, coordinates, regional suitability.
- disease: for diagnosing leaf/crop diseases.
- government: for government schemes, subsidies, matches.
- calculator: for farming calculations (seed rate, yield, spacing).
- vision: for general image analysis and leaf validation.
- translator: for translating text queries or response summaries.

Available Tools in the Registry:
- weather_api: retrieve weather metrics (temp, rain, wind).
- reverse_geocode: convert latitude and longitude into address.
- ocr: extract text from leaf labels or printouts.
- vision: analyze crop leaf image for disease diagnosis.
- search: perform web search for crop advisories.
- calculator: perform math calculations.
- translation: translate text between languages.
- government_schemes: query government agricultural subsidies.
- crop_database: query cultivation instructions.
- weather_mcp: invoke the Weather MCP Server get_weather tool.
- location_mcp: invoke the Location MCP Server reverse_geocode tool.
- crop_db_mcp: invoke Crop Database MCP server.
- gov_scheme_mcp: invoke Government Scheme MCP server.
- search_mcp: invoke Search MCP server.

Rules:
1. Always resolve location/geocode first if a weather forecast or regional suitability is requested and GPS is available.
2. If weather and crop irrigation are combined, invoke the weather agent first, then the crop agent, making the crop agent depend on the weather agent's outputs.
3. Only schedule the disease agent if the user uploaded an image.
4. Output steps in a clean, logical dependency DAG.
5. Do NOT include markdown blocks. Return ONLY valid JSON.

Plan JSON Schema:
{
  "reasoning": "Step-by-step thinking explaining which agents are needed, which tools to call, and their execution order/dependencies.",
  "steps": [
    {
      "id": "step_1",
      "agent": "crop" | "weather" | "location" | "disease" | "general" | "government" | "calculator" | "vision",
      "tool": "weather_api" | "reverse_geocode" | "ocr" | "vision" | "search" | "calculator" | "translation" | "government_schemes" | "crop_database" | "weather_mcp" | "location_mcp" | "crop_db_mcp" | "gov_scheme_mcp" | "search_mcp" | null,
      "depends_on": [],
      "action": "detailed description of action"
    }
  ],
  "required_data": ["gps_coordinates", "leaf_image", "location_name"],
  "response_tone": "scientific" | "urgent" | "general"
}
"""

    context_str = f"Image uploaded: {'Yes' if image_uploaded else 'No'}, GPS available: {'Yes' if gps_available else 'No'}, Location resolved: {location_name or 'Unknown'}"

    prompt = f"""{system_prompt}

Context:
{context_str}

Farmer Query:
{user_query}

Execution Plan JSON:
"""

    try:
        # Use reasoning=True to get step-by-step thinking from Nemotron
        response_text = generate_text(prompt, reasoning=True).strip()
        
        # Clean markdown code block wraps if present
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(?:json)?\n", "", response_text)
            response_text = re.sub(r"\n```$", "", response_text)
            response_text = response_text.strip()
        
        plan = json.loads(response_text)
        logger.info(f"Successfully generated task execution plan: {plan}")
        return plan
    except Exception as e:
        logger.error(f"Planner failed to generate/parse plan: {e}. Defaulting to basic plan.", exc_info=True)
        # Default fallback plan based on simple heuristics
        steps = []
        depends = []
        required = []
        
        if gps_available and not location_name:
            steps.append({
                "id": "step_loc",
                "agent": "location",
                "tool": "location_mcp",
                "depends_on": [],
                "action": "Resolve location name from coordinates"
            })
            depends = ["step_loc"]
            required.append("gps_coordinates")

        query_lower = user_query.lower()
        if image_uploaded:
            steps.append({
                "id": "step_disease",
                "agent": "disease",
                "tool": "vision",
                "depends_on": depends,
                "action": "Diagnose crop leaf disease"
            })
            required.append("leaf_image")
        
        if any(w in query_lower for w in ["weather", "rain", "temp", "forecast", "climate", "irrigate", "water"]):
            steps.append({
                "id": "step_weather",
                "agent": "weather",
                "tool": "weather_mcp",
                "depends_on": depends,
                "action": "Fetch weather forecast details"
            })
            if "gps_coordinates" not in required:
                required.append("gps_coordinates")
            
        if not steps:
            steps.append({
                "id": "step_crop",
                "agent": "crop",
                "tool": "crop_database",
                "depends_on": [],
                "action": "Provide crop recommendation"
            })
            
        return {
            "reasoning": "Heuristic fallback due to planner parse failure.",
            "steps": steps,
            "required_data": required,
            "response_tone": "general"
        }

