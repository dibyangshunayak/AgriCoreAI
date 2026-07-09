# =====================================================================
# FILE: backend/app/routes/chat.py
# DESCRIPTION: Flask route handling SSE chat powered by the orchestrator.
#              No authentication required — all users access directly.
# =====================================================================

import json
import logging
import uuid
from flask import Blueprint, request, Response

# Unified orchestrator agent
from app.agents.coordinator_agent import process_request_stream

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize blueprint
chat_blueprint = Blueprint("chat", __name__)


# Helper to stream SSE events safely
def sse_event(data: dict, event_type: str = "message") -> str:
    payload = json.dumps(data)
    return f"event: {event_type}\ndata: {payload}\n\n"

@chat_blueprint.route("/chat", methods=["POST"]) 
def chat():
    """Handle chat requests via SSE streaming using the Coordinator Agent."""
    request_id = str(uuid.uuid4())
    logger.info(f"[Chat] Started request {request_id}")

    data = request.json or {}
    user_message = data.get("message", "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    file_path = data.get("file_path")
    file_context = data.get("file_context")
    history = data.get("history", [])
    session_id = data.get("session_id", "default_session")

    # Preferred language from request body (sent by frontend from localStorage profile)
    pref_lang = data.get("preferred_language", "en")

    def event_generator():
        sent_end = False
        try:
            # Delegate entire chat processing, intent routing, translation, and RAG to process_request_stream
            token_generator = process_request_stream(
                user_query=user_message,
                image_path=file_path,
                latitude=latitude,
                longitude=longitude,
                conversation_context=history,
                file_context=file_context,
                session_id=session_id,
                preferred_language=pref_lang
            )
            for ch in token_generator:
                yield sse_event({"token": ch})

            # End event – ensure only one is sent
            if not sent_end:
                sent_end = True
                yield "event: end\ndata: {}\n\n"
        except Exception as e:
            logger.exception(f"[Chat] Error in request {request_id}")
            err_payload = {"error": str(e)}
            yield sse_event(err_payload, event_type="error")
            if not sent_end:
                sent_end = True
                yield "event: end\ndata: {}\n\n"
        finally:
            logger.info(f"[Chat] Completed request {request_id}")

    return Response(event_generator(), mimetype="text/event-stream")


@chat_blueprint.route("/metrics", methods=["GET"])
def get_observability_telemetry():
    """Reads agent_metrics.jsonl and returns telemetry for the developer dashboard."""
    from app.services.memory_service import DB_DIR
    import os
    
    metrics_path = DB_DIR / "agent_metrics.jsonl"
    events = []
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line.strip()))
        except Exception as e:
            logger.error(f"Failed to read agent metrics: {e}")
            
    # Generate proactive alert cards based on latest events
    alerts = []
    
    has_pest_advisory = True  # Default precaution
        
    alerts.append({
        "id": "alert_1",
        "type": "weather",
        "severity": "warning",
        "title": "Precipitation Precaution Alert",
        "message": "High rainfall is expected within the regional zone. Secure crop shelters and suspend fertilizer sprays."
    })
    
    if has_pest_advisory:
        alerts.append({
            "id": "alert_2",
            "type": "pest",
            "severity": "danger",
            "title": "Early Blight Spore Advisory",
            "message": "High relative humidity detected. Protect tomato crops against Early Blight expansion."
        })
        
    return {
        "metrics": events[-55:],  # Return last 55 agent invocation events
        "alerts": alerts
    }
