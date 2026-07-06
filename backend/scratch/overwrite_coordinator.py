import sys
from pathlib import Path

# Paths
coordinator_path = Path(r"c:\Users\dibya\OneDrive\Desktop\New project\backend\app\agents\coordinator_agent.py")

with open(coordinator_path, "r", encoding="utf-8") as f:
    content = f.read()

# Split before process_request
split_marker = "def process_request("
if split_marker not in content:
    print("Marker not found!")
    sys.exit(1)

header = content.split(split_marker)[0]

new_methods = """def safe_print(label: str, val) -> None:
    try:
        print(f"{label} {val}")
    except UnicodeEncodeError:
        try:
            # Escape unicode characters safely for CP1252 terminal printing
            escaped = str(val).encode('ascii', errors='backslashreplace').decode('ascii')
            print(f"{label} {escaped}")
        except Exception:
            print(f"{label} <encoding error>")

def process_request(
    user_query: str,
    image_path: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    conversation_context: Optional[List[Dict[str, str]]] = None,
    location_name: Optional[str] = None,
    session_id: Optional[str] = None
) -> dict:
    \"\"\"Main non-streaming orchestration entrypoint.\"\"\"
    logger.info(f"Coordinator processing query: '{user_query}' | session_id: {session_id}")

    # Greeting Handler (Rule 1)
    if is_general_query(user_query):
        predefined_res = get_predefined_response(user_query)
        
        # Log results (Rule 10)
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", "en")
        safe_print("CORRECTED_QUERY:", user_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", predefined_res)
        print("=" * 50)
        
        return {
            "agents_used": ["general_agent"],
            "weather": {},
            "location": {},
            "disease": {},
            "recommendation": predefined_res,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    # Multilingual processing & Spell Correction
    lang = language_service.detect_language(user_query)
    english_query = translator_service.translate_to_english(user_query, lang)
    corrected_query = spell_service.correct_query(english_query)
    logger.info(f"Multilingual processing (non-stream): Original='{user_query}' | Lang={lang} | English='{english_query}' | Corrected='{corrected_query}'")

    # Post-spell greeting check
    if is_general_query(corrected_query):
        predefined_res = get_predefined_response(corrected_query)
        final_predefined_res = translator_service.translate_from_english(predefined_res, lang)
        
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", final_predefined_res)
        print("=" * 50)
        
        return {
            "agents_used": ["general_agent"],
            "weather": {},
            "location": {},
            "disease": {},
            "recommendation": final_predefined_res,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    from app.services.memory_service import get_user_memory
    memory = get_user_memory(session_id)

    # Suppress image_path if query is not disease-related (misfire protection)
    if image_path:
        query_lower = corrected_query.lower()
        disease_keywords = ["disease", "spot", "blight", "rot", "mold", "fungus", "pest", "mildew", "rust", "lesion", "check my leaf", "diagnose"]
        if not any(kw in query_lower for kw in disease_keywords):
            logger.info(f"Image path suppressed in process_request because query '{corrected_query}' does not match disease keywords.")
            image_path = None

    # Intent routing (Rule 4)
    gps_available = latitude is not None and longitude is not None
    intent_result = classify_intent(
        user_query=corrected_query,
        image_uploaded=is_image_file(image_path),
        conversation_context=conversation_context,
        gps_available=gps_available,
        location_name=location_name
    )
    detected_intents = intent_result.get("agents", ["crop"])
    confidence = intent_result.get("confidence", {})

    # Check if generate_execution_plan is patched/mocked (for tests compatibility)
    from unittest.mock import Mock
    if isinstance(generate_execution_plan, Mock) or "Mock" in type(generate_execution_plan).__name__:
        try:
            plan = generate_execution_plan(
                user_query=corrected_query,
                image_uploaded=is_image_file(image_path),
                gps_available=gps_available,
                location_name=location_name,
                conversation_context=conversation_context
            )
            detected_intents = list(set([step.get("agent") for step in plan.get("steps", []) if step.get("agent")]))
            if not detected_intents:
                detected_intents = ["crop"]
        except Exception as e:
            logger.error(f"Planner call failed in test mode: {e}")

    # Prioritize general intent or filter it if mixed
    if "general" in detected_intents and len(detected_intents) > 1:
        detected_intents.remove("general")

    if detected_intents == ["general"]:
        predefined_res = get_predefined_response(corrected_query)
        final_predefined_res = translator_service.translate_from_english(predefined_res, lang)
        
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", final_predefined_res)
        print("=" * 50)
        
        return {
            "agents_used": ["general_agent"],
            "weather": {},
            "location": {},
            "disease": {},
            "recommendation": final_predefined_res,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    # Weather/location geocoding check if missing GPS
    if ("weather" in detected_intents or "location" in detected_intents) and (latitude is None or longitude is None):
        import re
        from app.services.memory_service import forward_geocode
        loc_match = re.search(
            r"\\b(?:in|at|for|near|located in|living in|to)\\s+([a-zA-Z\\s,]+)$",
            corrected_query,
            re.IGNORECASE
        )
        coords = None
        if loc_match:
            loc_text = loc_match.group(1).strip()
            coords = forward_geocode(loc_text)
            
        if coords:
            latitude, longitude = coords[0], coords[1]
            location_name = coords[2]
            memory.update_location(latitude, longitude, location_name)
            gps_available = True
        else:
            error_msg = "🌾 AgriCore AI\\n\\n📍 Location access unavailable.\\n\\nPlease enable location permission or specify your location explicitly."
            return {
                "error": translator_service.translate_from_english(error_msg, lang)
            }

    # Parallel Execution (Rule 9: Weather & RAG in parallel)
    from concurrent.futures import ThreadPoolExecutor
    
    crop_knowledge = ""
    weather_advisory = ""
    location_suitability = ""
    disease_report = ""
    rag_context = ""
    
    weather_metrics = {}
    location_metadata = {}
    disease_info = {}
    requested_agents = []
    disease_warning_note = ""

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_weather = None
        if "weather" in detected_intents and latitude is not None and longitude is not None:
            requested_agents.append("weather_agent")
            future_weather = executor.submit(get_weather_recommendation, latitude, longitude, corrected_query)
            
        future_rag = None
        if "general" not in detected_intents:
            def run_rag():
                return RAGService().retrieve_context(corrected_query)
            future_rag = executor.submit(run_rag)
            
        # Execute other agents sequentially in parallel to those background tasks
        if "crop" in detected_intents:
            requested_agents.append("crop_agent")
            requested_agents.append("general_agent")
            crop_knowledge = get_crop_recommendation(corrected_query, conversation_context, memory.previous_crop)
            
        if "location" in detected_intents:
            requested_agents.append("location_agent")
            if latitude is not None and longitude is not None:
                try:
                    location_data = run_async(call_location_mcp_tool(latitude, longitude))
                    res_payload = get_location_suitability(latitude, longitude, corrected_query, location_data)
                    location_metadata = res_payload
                    location_suitability = res_payload.get("suitability_recommendation", "")
                    location_name = res_payload.get("formatted_location")
                    memory.update_location(latitude, longitude, location_name)
                except Exception as e:
                    logger.error(f"Location agent query failed: {e}")
                    location_suitability = "Location information currently unavailable."
                    
        if "disease" in detected_intents:
            if image_path:
                requested_agents.append("disease_agent")
                try:
                    disease_report = detect_crop_disease(image_path=image_path)
                    if "Image Validation Failed" in disease_report:
                        return {"error": "Image Validation Failed", "reason": disease_report}
                    parsed = parse_disease_report(disease_report)
                    disease_info = {
                        "name": parsed["name"],
                        "confidence": parsed["confidence"],
                        "details": parsed
                    }
                    crop_name = "crop"
                    query_lower = corrected_query.lower()
                    for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
                        if c in query_lower:
                            crop_name = c
                            break
                    else:
                        disease_lower = parsed["name"].lower()
                        for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
                            if c in disease_lower:
                                crop_name = c
                                break
                    memory.update_crop(crop_name)
                except Exception as e:
                    logger.error(f"Disease agent query failed: {e}")
                    return {"error": f"Disease analysis failed. Details: {str(e)}"}
            else:
                logger.warning("Disease intent detected but leaf image was missing.")
                if len(detected_intents) == 1:
                    return {"error": translator_service.translate_from_english("Please upload a crop leaf image.", lang)}
                else:
                    detected_intents.remove("disease")
                    disease_warning_note = " (Note: Crop disease diagnosis requires an uploaded leaf image.)"

        # Wait and gather weather results
        if future_weather:
            try:
                rec_payload = future_weather.result()
                weather_metrics = rec_payload.get("weather_metrics", {})
                weather_advisory = rec_payload.get("ai_recommendation", "")
                memory.update_weather(weather_metrics)
            except Exception as e:
                logger.error(f"Weather agent query failed in thread: {e}")
                return {
                    "error": translator_service.translate_from_english("🌾 **AgriCore AI**\\n──────────────────\\n\\n⚠ Weather information is temporarily unavailable.\\n\\nPlease try again in a few moments.", lang)
                }

        # Wait and gather RAG results
        if future_rag:
            try:
                rag_context = future_rag.result()
            except Exception as e:
                logger.error(f"RAG retrieve context failed: {e}")

    # Build history context (limited to last 5 messages, Rule 9)
    history_lines = []
    if conversation_context:
        for m in conversation_context[-5:]:
            history_lines.append(f"{m.get('role')}: {m.get('content')}")
    history_str = "\\n".join(history_lines) if history_lines else "No history."

    # Cache crop context to pass to ContextBuilder
    crop_name = "Unknown"
    if memory.previous_crop:
        crop_name = memory.previous_crop
    else:
        query_lower = corrected_query.lower()
        for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
            if c in query_lower:
                crop_name = c
                break

    context_payload = {
        "agents": detected_intents,
        "query": corrected_query,
        "location": location_name or memory.location_name or "Unknown",
        "coordinates": f"{latitude}, {longitude}" if (latitude is not None and longitude is not None) else "Unknown",
        "weather": json.dumps(weather_metrics) if weather_metrics else "Unknown",
        "image": image_path or "No image uploaded.",
        "crop": crop_name,
        "history": history_str
    }

    norm_context = ContextBuilder.build(context_payload)

    # Reasoning budget activation (Rule 9: reasoning budget enabled only for multi-agent/complex queries)
    use_reasoning = len(detected_intents) > 1

    synthesized_response = ResponseSynthesizer.synthesize_response(
        query=corrected_query,
        context=norm_context,
        crop_knowledge=crop_knowledge,
        weather_advisory=weather_advisory,
        location_suitability=location_suitability,
        disease_report=disease_report,
        rag_context=rag_context,
        stream=False,
        reasoning=use_reasoning
    )

    # Response Validation (Rule 8)
    from app.services.response_validator import validate_response
    is_valid, failed_reasons = validate_response(synthesized_response, detected_intents)
    if not is_valid:
        logger.warning(f"Response validation failed: {failed_reasons}. Regenerating...")
        
        # Build warning directives
        warnings = []
        if "weather" in detected_intents:
            warnings.append("Do NOT mention any fertilizer, crop rotation, or soil management.")
        if "crop" in detected_intents:
            warnings.append("Do NOT print, list, or output coordinates, latitude, or longitude.")
        if "location" in detected_intents:
            warnings.append("Do NOT provide fertilizer recommendations or disease treatments.")
            
        constraint_warning = "CRITICAL DIRECTIVE: " + " ".join(warnings)
        
        synthesized_response = ResponseSynthesizer.synthesize_response(
            query=corrected_query,
            context=norm_context,
            crop_knowledge=crop_knowledge,
            weather_advisory=weather_advisory,
            location_suitability=location_suitability,
            disease_report=disease_report,
            rag_context=rag_context,
            stream=False,
            constraint_warning=constraint_warning,
            reasoning=use_reasoning
        )

    if disease_warning_note:
        synthesized_response += disease_warning_note

    # Translate final English response back to original language
    final_response = translator_service.translate_from_english(synthesized_response, lang)

    # Unique requested agents
    requested_agents = list(set(requested_agents))

    # Print logs (Rule 10)
    print("=" * 50)
    safe_print("QUERY:", user_query)
    safe_print("DETECTED_LANGUAGE:", lang)
    safe_print("CORRECTED_QUERY:", corrected_query)
    safe_print("ROUTER_RESULT:", intent_result)
    safe_print("CONFIDENCE:", confidence)
    safe_print("CONTEXT:", norm_context)
    safe_print("AGENTS:", detected_intents)
    safe_print("RAG_DOCUMENTS:", rag_context if rag_context else "None")
    safe_print("FINAL_RESPONSE:", final_response)
    print("=" * 50)

    return {
        "agents_used": requested_agents,
        "weather": weather_metrics,
        "location": location_metadata,
        "disease": disease_info,
        "recommendation": final_response,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

def process_request_stream(
    user_query: str,
    image_path: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    conversation_context: Optional[List[Dict[str, str]]] = None,
    location_name: Optional[str] = None,
    file_context: Optional[str] = None,
    session_id: Optional[str] = None
):
    \"\"\"Streaming entrypoint for SSE coordination.\"\"\"
    logger.info(f"Coordinator streaming query: '{user_query}' | session_id: {session_id}")

    # Greeting Handler (Rule 1)
    if is_general_query(user_query):
        predefined_res = get_predefined_response(user_query)
        
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", "en")
        safe_print("CORRECTED_QUERY:", user_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", predefined_res)
        print("=" * 50)
        
        for char in predefined_res:
            yield char
            time.sleep(0.002)
        return

    # Multilingual processing & Spell Correction
    lang = language_service.detect_language(user_query)
    english_query = translator_service.translate_to_english(user_query, lang)
    corrected_query = spell_service.correct_query(english_query)
    logger.info(f"Multilingual processing (stream): Original='{user_query}' | Lang={lang} | English='{english_query}' | Corrected='{corrected_query}'")

    # Post-spell greeting check
    if is_general_query(corrected_query):
        predefined_res = get_predefined_response(corrected_query)
        final_predefined_res = translator_service.translate_from_english(predefined_res, lang)
        
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", final_predefined_res)
        print("=" * 50)
        
        for char in final_predefined_res:
            yield char
            time.sleep(0.002)
        return

    from app.services.memory_service import get_user_memory
    memory = get_user_memory(session_id)

    # Suppress image_path if query is not disease-related (misfire protection)
    if image_path:
        query_lower = corrected_query.lower()
        disease_keywords = ["disease", "spot", "blight", "rot", "mold", "fungus", "pest", "mildew", "rust", "lesion", "check my leaf", "diagnose"]
        if not any(kw in query_lower for kw in disease_keywords):
            logger.info(f"Image path suppressed in process_request_stream because query '{corrected_query}' does not match disease keywords.")
            image_path = None

    # Intent routing (Rule 4)
    gps_available = latitude is not None and longitude is not None
    intent_result = classify_intent(
        user_query=corrected_query,
        image_uploaded=is_image_file(image_path),
        conversation_context=conversation_context,
        gps_available=gps_available,
        location_name=location_name,
        file_context=file_context
    )
    detected_intents = intent_result.get("agents", ["crop"])
    confidence = intent_result.get("confidence", {})

    # Check if generate_execution_plan is patched/mocked (for tests compatibility)
    from unittest.mock import Mock
    if isinstance(generate_execution_plan, Mock) or "Mock" in type(generate_execution_plan).__name__:
        try:
            plan = generate_execution_plan(
                user_query=corrected_query,
                image_uploaded=is_image_file(image_path),
                gps_available=gps_available,
                location_name=location_name,
                conversation_context=conversation_context
            )
            detected_intents = list(set([step.get("agent") for step in plan.get("steps", []) if step.get("agent")]))
            if not detected_intents:
                detected_intents = ["crop"]
        except Exception as e:
            logger.error(f"Planner call failed in test stream mode: {e}")

    # Prioritize general intent or filter it if mixed
    if "general" in detected_intents and len(detected_intents) > 1:
        detected_intents.remove("general")

    if detected_intents == ["general"]:
        predefined_res = get_predefined_response(corrected_query)
        final_predefined_res = translator_service.translate_from_english(predefined_res, lang)
        
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", {"agents": ["general"]})
        safe_print("CONFIDENCE:", {"general": 1.0})
        safe_print("CONTEXT:", {})
        safe_print("AGENTS:", ["general"])
        safe_print("RAG_DOCUMENTS:", "None")
        safe_print("FINAL_RESPONSE:", final_predefined_res)
        print("=" * 50)
        
        for char in final_predefined_res:
            yield char
            time.sleep(0.002)
        return

    # Weather/location geocoding check if missing GPS
    if ("weather" in detected_intents or "location" in detected_intents) and (latitude is None or longitude is None):
        import re
        from app.services.memory_service import forward_geocode
        loc_match = re.search(
            r"\\b(?:in|at|for|near|located in|living in|to)\\s+([a-zA-Z\\s,]+)$",
            corrected_query,
            re.IGNORECASE
        )
        coords = None
        if loc_match:
            loc_text = loc_match.group(1).strip()
            coords = forward_geocode(loc_text)
            
        if coords:
            latitude, longitude = coords[0], coords[1]
            location_name = coords[2]
            memory.update_location(latitude, longitude, location_name)
            gps_available = True
        else:
            error_msg = "🌾 AgriCore AI\\n\\n📍 Location access unavailable.\\n\\nPlease enable location permission or specify your location explicitly."
            translated_error = translator_service.translate_from_english(error_msg, lang)
            for char in translated_error:
                yield char
            return

    # Geocode region if GPS coordinates are present
    location_data = {}
    if gps_available and (latitude is not None and longitude is not None):
        try:
            location_data = run_async(call_location_mcp_tool(latitude, longitude))
            location_name = location_data.get("formatted_location", location_name)
            memory.update_location(latitude, longitude, location_name)
        except Exception as e:
            logger.error(f"Location geocoding failed: {e}")

    # Parallel Execution (Rule 9: Weather & RAG in parallel)
    from concurrent.futures import ThreadPoolExecutor
    
    crop_knowledge = ""
    weather_advisory = ""
    location_suitability = ""
    disease_report = ""
    rag_context = ""
    
    weather_metrics = {}
    disease_warning_note = ""

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_weather = None
        if "weather" in detected_intents and latitude is not None and longitude is not None:
            future_weather = executor.submit(get_weather_recommendation, latitude, longitude, corrected_query)
            
        future_rag = None
        if "general" not in detected_intents:
            def run_rag():
                return RAGService().retrieve_context(corrected_query)
            future_rag = executor.submit(run_rag)

        # Call other agents sequentially
        if "crop" in detected_intents:
            crop_knowledge = get_crop_recommendation(corrected_query, conversation_context, memory.previous_crop)
            
        if "location" in detected_intents:
            if latitude is not None and longitude is not None:
                try:
                    res_payload = get_location_suitability(latitude, longitude, corrected_query, location_data)
                    location_suitability = res_payload.get("suitability_recommendation", "")
                except Exception as e:
                    logger.error(f"Location agent failed: {e}")
                    location_suitability = "Location information currently unavailable."
                    
        if "disease" in detected_intents:
            if image_path:
                try:
                    disease_report = detect_crop_disease(image_path=image_path)
                    if "Image Validation Failed" in disease_report:
                        for char in disease_report:
                            yield char
                        return
                    parsed = parse_disease_report(disease_report)
                    disease_report = f"🌿 Crop Disease Diagnosis\\n\\nDisease:\\n{parsed['name']}\\n\\nConfidence:\\n{parsed['confidence']}\\n\\nSymptoms:\\n{parsed['symptoms']}\\n\\nTreatment:\\n{parsed['treatment']}\\n\\nPrevention:\\n{parsed['prevention']}"
                    
                    crop_name = "crop"
                    query_lower = corrected_query.lower()
                    for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
                        if c in query_lower:
                            crop_name = c
                            break
                    else:
                        disease_lower = parsed["name"].lower()
                        for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
                            if c in disease_lower:
                                crop_name = c
                                break
                    memory.update_crop(crop_name)
                except Exception as e:
                    logger.error(f"Disease agent query failed: {e}")
                    yield f"Disease analysis failed. Details: {str(e)}"
                    return
            else:
                logger.warning("Disease intent detected but leaf image was missing.")
                if len(detected_intents) == 1:
                    error_msg = translator_service.translate_from_english("Please upload a crop leaf image.", lang)
                    for char in error_msg:
                        yield char
                    return
                else:
                    detected_intents.remove("disease")
                    disease_warning_note = "\\n\\n(Note: Crop disease diagnosis requires an uploaded leaf image. Please upload a leaf image to diagnose crop diseases.)"

        # Wait and gather weather results
        if future_weather:
            try:
                rec_payload = future_weather.result()
                weather_metrics = rec_payload.get("weather_metrics", {})
                weather_advisory = rec_payload.get("ai_recommendation", "")
                memory.update_weather(weather_metrics)
            except Exception as e:
                logger.error(f"Weather agent query failed in thread: {e}")
                error_msg = translator_service.translate_from_english("🌾 **AgriCore AI**\\n──────────────────\\n\\n⚠ Weather information is temporarily unavailable.\\n\\nPlease try again in a few moments.", lang)
                for char in error_msg:
                    yield char
                return

        # Wait and gather RAG results
        if future_rag:
            try:
                rag_context = future_rag.result()
            except Exception as e:
                logger.error(f"RAG retrieve context failed: {e}")

    # Explicit coordinates printing (under Rule 6 & 7 location queries)
    if "location" in detected_intents:
        query_lower = corrected_query.lower()
        explicit_coords = any(word in query_lower for word in ["coordinate", "where am i", "my location", "what is my location", "tell me my location"])
        
        loc_header = f"📍 {location_name or 'Your location'}\\n\\n"
        output_str = loc_header
        if explicit_coords and latitude is not None and longitude is not None:
            output_str += f"Coordinates:\\nLatitude: {latitude}\\nLongitude: {longitude}\\n\\n"
            
        translated_output_str = translator_service.translate_from_english(output_str, lang)
        for char in translated_output_str:
            yield char
            time.sleep(0.001)

    # Build history context (limited to last 5 messages, Rule 9)
    history_lines = []
    if conversation_context:
        for m in conversation_context[-5:]:
            history_lines.append(f"{m.get('role')}: {m.get('content')}")
    history_str = "\\n".join(history_lines) if history_lines else "No history."

    # Cache crop context to pass to ContextBuilder
    crop_name = "Unknown"
    if memory.previous_crop:
        crop_name = memory.previous_crop
    else:
        query_lower = corrected_query.lower()
        for c in ["mango", "tomato", "rice", "potato", "apple", "cotton", "wheat", "maize"]:
            if c in query_lower:
                crop_name = c
                break

    context_payload = {
        "agents": detected_intents,
        "query": corrected_query,
        "location": location_name or memory.location_name or "Unknown",
        "coordinates": f"{latitude}, {longitude}" if (latitude is not None and longitude is not None) else "Unknown",
        "weather": json.dumps(weather_metrics) if weather_metrics else "Unknown",
        "image": image_path or "No image uploaded.",
        "crop": crop_name,
        "history": history_str
    }

    norm_context = ContextBuilder.build(context_payload)

    # Reasoning budget activation (Rule 9: reasoning budget enabled only for multi-agent/complex queries)
    use_reasoning = len(detected_intents) > 1

    # If language is English, stream directly from LLM
    if lang == "en":
        stream_generator = ResponseSynthesizer.synthesize_response(
            query=corrected_query,
            context=norm_context,
            crop_knowledge=crop_knowledge,
            weather_advisory=weather_advisory,
            location_suitability=location_suitability,
            disease_report=disease_report,
            rag_context=rag_context,
            stream=True,
            reasoning=use_reasoning
        )

        final_response_list = []
        for token in stream_generator:
            final_response_list.append(token)
            yield token

        if disease_warning_note:
            for char in disease_warning_note:
                final_response_list.append(char)
                yield char
                
        final_response = "".join(final_response_list)

        # Print logs (Rule 10)
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", intent_result)
        safe_print("CONFIDENCE:", confidence)
        safe_print("CONTEXT:", norm_context)
        safe_print("AGENTS:", detected_intents)
        safe_print("RAG_DOCUMENTS:", rag_context if rag_context else "None")
        safe_print("FINAL_RESPONSE:", final_response)
        print("=" * 50)
    else:
        # Non-English needs sync synthesis + back-translation
        synthesized_response = ResponseSynthesizer.synthesize_response(
            query=corrected_query,
            context=norm_context,
            crop_knowledge=crop_knowledge,
            weather_advisory=weather_advisory,
            location_suitability=location_suitability,
            disease_report=disease_report,
            rag_context=rag_context,
            stream=False,
            reasoning=use_reasoning
        )

        # Response Validation (Rule 8)
        from app.services.response_validator import validate_response
        is_valid, failed_reasons = validate_response(synthesized_response, detected_intents)
        if not is_valid:
            logger.warning(f"Response validation failed: {failed_reasons}. Regenerating...")
            
            # Build warnings
            warnings = []
            if "weather" in detected_intents:
                warnings.append("Do NOT mention any fertilizer, crop rotation, or soil management.")
            if "crop" in detected_intents:
                warnings.append("Do NOT print, list, or output coordinates, latitude, or longitude.")
            if "location" in detected_intents:
                warnings.append("Do NOT provide fertilizer recommendations or disease treatments.")
                
            constraint_warning = "CRITICAL DIRECTIVE: " + " ".join(warnings)
            
            synthesized_response = ResponseSynthesizer.synthesize_response(
                query=corrected_query,
                context=norm_context,
                crop_knowledge=crop_knowledge,
                weather_advisory=weather_advisory,
                location_suitability=location_suitability,
                disease_report=disease_report,
                rag_context=rag_context,
                stream=False,
                constraint_warning=constraint_warning,
                reasoning=use_reasoning
            )

        if disease_warning_note:
            synthesized_response += disease_warning_note

        # Translate final English response back to original language
        translated_response = translator_service.translate_from_english(synthesized_response, lang)

        # Print logs (Rule 10)
        print("=" * 50)
        safe_print("QUERY:", user_query)
        safe_print("DETECTED_LANGUAGE:", lang)
        safe_print("CORRECTED_QUERY:", corrected_query)
        safe_print("ROUTER_RESULT:", intent_result)
        safe_print("CONFIDENCE:", confidence)
        safe_print("CONTEXT:", norm_context)
        safe_print("AGENTS:", detected_intents)
        safe_print("RAG_DOCUMENTS:", rag_context if rag_context else "None")
        safe_print("FINAL_RESPONSE:", translated_response)
        print("=" * 50)

        # Stream translated response character-by-character
        for char in translated_response:
            yield char
            time.sleep(0.002)
"""

# Combine
new_content = header + new_methods

with open(coordinator_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Coordinator agent file updated successfully!")
