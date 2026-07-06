# =====================================================================
# FILE: backend/app/api/router.py
# DESCRIPTION: Blueprint routes for the Flask backend, handling uploads
#              and SSE streaming chat interactions.
# =====================================================================

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# Create the API blueprint
api_blueprint = Blueprint("api", __name__)



# Configure upload folder inside the backend root folder
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Map extensions to specific context descriptions requested by the user
EXTENSION_CONTEXTS = {
    # Images
    ".jpg": ("The user uploaded an image.", "image"),
    ".jpeg": ("The user uploaded an image.", "image"),
    ".png": ("The user uploaded an image.", "image"),
    ".webp": ("The user uploaded an image.", "image"),
    # PDFs
    ".pdf": ("The user uploaded a document.", "pdf"),
    # Documents
    ".docx": ("The user uploaded a document.", "document"),
    ".txt": ("The user uploaded a document.", "document"),
    # Spreadsheets
    ".csv": ("The user uploaded tabular data.", "spreadsheet"),
    ".xlsx": ("The user uploaded tabular data.", "spreadsheet")
}

def validate_mime_and_extension(file_stream, filename: str) -> tuple:
    """
    Reads the file header from the stream to verify that the actual file content
    matches its extension to prevent extension spoofing.
    Returns (context, file_type) if valid, or raises a ValueError.
    """
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in EXTENSION_CONTEXTS:
        raise ValueError(f"Unsupported file extension '{file_ext}'.")

    # Read up to 2048 bytes of file header to verify signature
    header = file_stream.read(2048)
    file_stream.seek(0)  # Rewind the file stream position so it can be saved in full

    if not header:
        raise ValueError("The uploaded file is empty.")

    detected_type = None

    # Detect file type based on signature magic bytes
    if header.startswith(b"\xff\xd8\xff"):
        detected_type = "image/jpeg"
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_type = "image/png"
    elif header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
        detected_type = "image/webp"
    elif header.startswith(b"%PDF-"):
        detected_type = "application/pdf"
    elif header.startswith(b"PK\x03\x04"):
        detected_type = "application/zip"  # DOCX/XLSX are ZIP-compressed documents
    else:
        # Fallback check for plain text / CSV files
        try:
            # If it's valid UTF-8/ASCII without null bytes, treat as text
            if b"\x00" not in header:
                header.decode("utf-8")
                detected_type = "text/plain"
            else:
                detected_type = "application/octet-stream"
        except UnicodeDecodeError:
            detected_type = "application/octet-stream"

    # Cross-verify detected MIME signature with file extension
    if file_ext in {".jpg", ".jpeg"}:
        if detected_type != "image/jpeg":
            raise ValueError(f"Spoofing detected: File signature does not match expected JPEG format for extension '{file_ext}'.")
    elif file_ext == ".png":
        if detected_type != "image/png":
            raise ValueError("Spoofing detected: File signature does not match expected PNG format.")
    elif file_ext == ".webp":
        if detected_type != "image/webp":
            raise ValueError("Spoofing detected: File signature does not match expected WEBP format.")
    elif file_ext == ".pdf":
        if detected_type != "application/pdf":
            raise ValueError("Spoofing detected: File signature does not match expected PDF format.")
    elif file_ext in {".docx", ".xlsx"}:
        if detected_type != "application/zip":
            raise ValueError(f"Spoofing detected: File signature does not match expected Office document format for extension '{file_ext}'.")
    elif file_ext in {".txt", ".csv"}:
        if detected_type != "text/plain":
            raise ValueError(f"Spoofing detected: File signature does not match expected text format for extension '{file_ext}'.")

    return EXTENSION_CONTEXTS[file_ext]


@api_blueprint.route("/upload", methods=["POST"])
def upload_file():


    """
    Receives an uploaded file, validates the content MIME type, automatically detects
    the context description, saves it to disk, and returns metadata.
    """
    if "file" not in request.files:
        logger.error("No file part in upload request.")
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        logger.error("Empty filename in upload request.")
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Perform strict content-based validation
    try:
        context, file_type = validate_mime_and_extension(file, filename)
    except ValueError as val_err:
        logger.warning(f"File validation failed for upload request: {val_err}")
        return jsonify({"error": str(val_err)}), 400
    
    # Save the file
    save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    try:
        file.save(save_path)
        logger.info(f"File saved successfully to {save_path}. Type: {file_type}. Context: '{context}'")
        
        # Return the relative path from the backend folder for reference
        relative_path = os.path.join("uploads", unique_filename)
        
        return jsonify({
            "file_path": relative_path,
            "file_name": unique_filename,
            "context": context,
            "type": file_type
        })
    except Exception as e:
        logger.error(f"Failed to save file: {e}", exc_info=True)
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500



@api_blueprint.route("/health", methods=["GET"])
def health_check():
    """Return application and database health for smoke tests and load balancers."""
    db_ok = False
    try:
        from sqlalchemy import text
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_ok = True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health database check failed: {e}", exc_info=True)

    status_code = 200 if db_ok else 503
    return jsonify({"status": "ok" if db_ok else "degraded", "database": db_ok}), status_code


@api_blueprint.route("/geocode", methods=["POST"])
def reverse_geocode():
    """Reverse geocode coordinates using the existing location tool."""
    data = request.json or {}
    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid latitude and longitude are required"}), 400

    try:
        from app.tools.implementations import ReverseGeocodeTool
        return jsonify(ReverseGeocodeTool().run(latitude=latitude, longitude=longitude))
    except Exception as e:
        logger.error(f"Reverse geocode failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to reverse geocode coordinates"}), 500


@api_blueprint.route("/weather", methods=["GET", "POST"])
def weather():
    """Fetch weather metrics for coordinates using the existing weather tool."""
    data = request.json or {}
    latitude = data.get("latitude", request.args.get("latitude"))
    longitude = data.get("longitude", request.args.get("longitude"))
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return jsonify({"error": "Valid latitude and longitude are required"}), 400

    try:
        from app.tools.implementations import WeatherApiTool
        result = WeatherApiTool().run(latitude=latitude, longitude=longitude)
        result["source"] = "open-meteo"
        return jsonify(result)
    except Exception as e:
        logger.error(f"Weather lookup failed: {e}. Returning offline fallback weather.", exc_info=True)
        return jsonify({
            "temperature": 28.0,
            "humidity": 70,
            "precipitation": 0.0,
            "wind_speed": 8.0,
            "soil_temperature": 27.0,
            "soil_moisture": 0.25,
            "weather_condition": "Unavailable - offline estimate",
            "source": "offline-fallback",
            "warning": "Live weather provider is unavailable; returned safe mock-mode weather data."
        }), 200


@api_blueprint.route("/schemes", methods=["POST"])
def government_schemes():
    """Return government scheme matches using the existing scheme tool."""
    data = request.json or {}
    state = str(data.get("state", "")).strip()
    crop = str(data.get("crop", "")).strip()
    if not state or not crop:
        return jsonify({"error": "State and crop are required"}), 400

    try:
        from app.tools.implementations import GovSchemesTool
        return jsonify(GovSchemesTool().run(state=state, crop=crop))
    except Exception as e:
        logger.error(f"Government schemes lookup failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch government schemes"}), 500


@api_blueprint.route("/translation", methods=["POST"])
def translate_text():
    """Translate text using the existing translation tool."""
    data = request.json or {}
    text = str(data.get("text", "")).strip()
    target_language = str(data.get("target_language", data.get("language", ""))).strip()
    if not text or not target_language:
        return jsonify({"error": "Text and target_language are required"}), 400

    try:
        from app.tools.implementations import TranslationTool
        return jsonify(TranslationTool().run(text=text, target_language=target_language))
    except Exception as e:
        logger.error(f"Translation failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to translate text"}), 500

@api_blueprint.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename):
    """Serves uploaded files from the UPLOAD_FOLDER."""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404




