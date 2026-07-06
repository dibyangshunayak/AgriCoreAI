# =====================================================================
# FILE: backend/app/main.py
# DESCRIPTION: Main entry point for the Flask backend. Initializes the
#              Flask app, configures CORS, and registers API routes.
#              No authentication required — direct access for all users.
# =====================================================================

import logging
from flask import Flask
from flask_cors import CORS
from app.config import settings
from app.api.router import api_blueprint
from app.routes.chat import chat_blueprint
from app.routes.auth import auth_blueprint, user_blueprint


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    
    # Configure CORS to allow React frontend with credentials support
    cors_origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176"
    ]
    if getattr(settings, "ALLOWED_ORIGINS", None):
        for o in settings.ALLOWED_ORIGINS.split(","):
            o_clean = o.strip()
            if o_clean and o_clean not in cors_origins:
                cors_origins.append(o_clean)

    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {
            "origins": cors_origins
        }}
    )
    
    # Register the API routes blueprints
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(chat_blueprint, url_prefix="/api")
    app.register_blueprint(auth_blueprint, url_prefix="/api")
    app.register_blueprint(user_blueprint, url_prefix="/api")

    # Startup logging of app.url_map
    logger.info(f"Registered URL Map: {app.url_map}")


    @app.route("/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "AgriCore AI",
            "version": "1.0"
        }, 200

    @app.before_request
    def enforce_security_guardrails():
        from flask import request
        # Allow OPTIONS request bypass (CORS preflight)
        if request.method == "OPTIONS":
            return
            
        # Rate Limiting Check
        from app.utils.security import check_rate_limit
        ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr) or "127.0.0.1"
        if not check_rate_limit(ip_addr):
            return {"error": "Too many requests. Rate limit exceeded."}, 429
    
    # Premium Startup Diagnostics Logging
    import os
    env = os.getenv("ENVIRONMENT", "Production")
    host = settings.HOST
    port_str = "Render Assigned" if os.getenv("PORT") else str(settings.PORT)
    
    print("\n=====================================")
    print("AgriCore AI Backend")
    print(f"Environment : {env}")
    print(f"Host        : {host}")
    print(f"Port        : {port_str}")
    print("AI Agents   : Loaded")
    print("MCP Servers : Loaded")
    print("=====================================\n")

    print("\n========== REGISTERED ROUTES ==========")
    for rule in app.url_map.iter_rules():
        print(rule)
    print("=======================================\n")

    logger.info("Flask application created and registered with security middleware.")
    return app



app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}...")
    app.run(host=settings.HOST, port=settings.PORT, debug=True, use_reloader=False)
