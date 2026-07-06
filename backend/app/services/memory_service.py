from typing import Optional
import uuid
import logging
import requests
import re
import sqlite3
import json
from contextlib import closing
from pathlib import Path
from threading import Lock
from flask import session, request

logger = logging.getLogger(__name__)

# Resolve DB path
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "agri_session.db"

# Global session memory cache
SESSION_MEMORY = {}
memory_lock = Lock()

def init_db():
    try:
        with memory_lock:
            with closing(sqlite3.connect(str(DB_PATH), timeout=20.0)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        latitude REAL,
                        longitude REAL,
                        location_name TEXT,
                        file_path TEXT,
                        file_context TEXT,
                        previous_crop TEXT,
                        previous_weather TEXT,
                        uploaded_images TEXT,
                        crop_history TEXT,
                        disease_history TEXT,
                        weather_history TEXT,
                        preferred_language TEXT,
                        preferred_units TEXT,
                        previous_recommendations TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

                # Column migrations checker to support incremental updates
                cursor.execute("PRAGMA table_info(sessions)")
                columns = [col[1] for col in cursor.fetchall()]
                new_cols = {
                    "crop_history": "TEXT",
                    "disease_history": "TEXT",
                    "weather_history": "TEXT",
                    "preferred_language": "TEXT",
                    "preferred_units": "TEXT",
                    "previous_recommendations": "TEXT"
                }
                migrated = False
                for col_name, col_type in new_cols.items():
                    if col_name not in columns:
                        cursor.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_type};")
                        migrated = True
                if migrated:
                    conn.commit()

        logger.info(f"SQLite database initialized and checked for migrations at: {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}", exc_info=True)

# Run DB initialization
init_db()

OFFLINE_OVERRIDES = {
    "odisha": (20.9517, 85.0985, "Odisha, India"),
    "baripada": (21.9592, 86.7430, "Baripada, Odisha, India"),
    "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar, Odisha, India")
}

class SessionMemory:
    """
    SQLAlchemy database-backed data structure representing user session context including 
    location coordinates, resolved address, last uploaded crop leaf images, 
    previously discussed crops, and previous weather conditions.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.latitude = None
        self.longitude = None
        self.location_name = None
        self.file_path = None
        self.file_context = None
        self.previous_crop = None
        self.previous_weather = None
        self.uploaded_images = []
        
        # New Long-term memory history logs
        self.crop_history = []
        self.disease_history = []
        self.weather_history = []
        self.preferred_language = "en"
        self.preferred_units = "metric"
        self.previous_recommendations = []

        self.load()

    def sync_with_db_load(self):
        """Sync user profile parameters from central database when user id is present in session id."""
        if self.session_id.startswith("user_"):
            try:
                user_id = int(self.session_id.split("_")[1])
                from app.db.session import SessionLocal
                from app.db.models import User
                
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        if user.preferences:
                            self.preferred_language = user.preferences.preferred_language or self.preferred_language
                            self.preferred_units = user.preferences.units or self.preferred_units
                            if user.preferences.latitude is not None and user.preferences.longitude is not None:
                                self.latitude = user.preferences.latitude
                                self.longitude = user.preferences.longitude
                                self.location_name = user.preferences.farm_location or self.location_name
                        if user.farm_profiles:
                            for profile in user.farm_profiles:
                                if profile.primary_crop and profile.primary_crop not in self.crop_history:
                                    self.crop_history.append(profile.primary_crop)
                                if profile.secondary_crop and profile.secondary_crop not in self.crop_history:
                                    self.crop_history.append(profile.secondary_crop)
                            # Set default previous crop
                            if not self.previous_crop and self.crop_history:
                                self.previous_crop = self.crop_history[0]
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"[SessionMemory] Central DB load sync failed: {e}")

    def sync_with_db_save(self):
        """Sync session parameters back to user profile central database tables."""
        if self.session_id.startswith("user_"):
            try:
                user_id = int(self.session_id.split("_")[1])
                from app.db.session import SessionLocal
                from app.db.models import User, UserPreference
                
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        if not user.preferences:
                            user.preferences = UserPreference(user_id=user_id)
                            db.add(user.preferences)
                        
                        user.preferences.preferred_language = self.preferred_language
                        user.preferences.units = self.preferred_units
                        if self.latitude is not None:
                            user.preferences.latitude = self.latitude
                        if self.longitude is not None:
                            user.preferences.longitude = self.longitude
                        if self.location_name:
                            user.preferences.farm_location = self.location_name
                        
                        db.commit()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"[SessionMemory] Central DB save sync failed: {e}")

    def load(self):
        # Sync with main app database first
        self.sync_with_db_load()

        try:
            with memory_lock:
                with closing(sqlite3.connect(str(DB_PATH), timeout=20.0)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT latitude, longitude, location_name, file_path, file_context, previous_crop, previous_weather, uploaded_images,
                               crop_history, disease_history, weather_history, preferred_language, preferred_units, previous_recommendations
                        FROM sessions WHERE session_id = ?
                    """, (self.session_id,))
                    row = cursor.fetchone()
            
            if row:
                # Merge central db preferences with SQLite if values are missing
                self.latitude = row[0] if row[0] is not None else self.latitude
                self.longitude = row[1] if row[1] is not None else self.longitude
                self.location_name = row[2] if row[2] is not None else self.location_name
                self.file_path = row[3]
                self.file_context = row[4]
                self.previous_crop = row[5] if row[5] is not None else self.previous_crop
                
                try:
                    self.previous_weather = json.loads(row[6]) if row[6] else self.previous_weather
                except Exception as json_err:
                    logger.error(f"Error decoding previous_weather: {json_err}")
                try:
                    self.uploaded_images = json.loads(row[7]) if row[7] else []
                except Exception as json_err:
                    logger.error(f"Error decoding uploaded_images: {json_err}")
                try:
                    loaded_crops = json.loads(row[8]) if row[8] else []
                    for c in loaded_crops:
                        if c not in self.crop_history:
                            self.crop_history.append(c)
                except Exception as json_err:
                    logger.error(f"Error decoding crop_history: {json_err}")
                try:
                    self.disease_history = json.loads(row[9]) if row[9] else []
                except Exception as json_err:
                    logger.error(f"Error decoding disease_history: {json_err}")
                try:
                    self.weather_history = json.loads(row[10]) if row[10] else []
                except Exception as json_err:
                    logger.error(f"Error decoding weather_history: {json_err}")
                
                self.preferred_language = row[11] if row[11] else self.preferred_language
                self.preferred_units = row[12] if row[12] else self.preferred_units
                
                try:
                    self.previous_recommendations = json.loads(row[13]) if row[13] else []
                except Exception as json_err:
                    logger.error(f"Error decoding previous_recommendations: {json_err}")
                
                logger.info(f"Loaded memory for session '{self.session_id}' from SQLite database.")
            else:
                self.save()  # Insert new blank record
                logger.info(f"Initialized blank memory record for session '{self.session_id}' in SQLite database.")
        except Exception as e:
            logger.error(f"Error loading session '{self.session_id}' memory: {e}", exc_info=True)

    def save(self):
        # Sync with main app database first
        self.sync_with_db_save()

        try:
            try:
                weather_str = json.dumps(self.previous_weather) if self.previous_weather else None
            except Exception as json_err:
                logger.error(f"Error encoding previous_weather in save: {json_err}")
                weather_str = None
            try:
                images_str = json.dumps(self.uploaded_images) if self.uploaded_images else None
            except Exception as json_err:
                logger.error(f"Error encoding uploaded_images in save: {json_err}")
                images_str = None
            try:
                crop_hist_str = json.dumps(self.crop_history) if self.crop_history else None
            except Exception as json_err:
                logger.error(f"Error encoding crop_history in save: {json_err}")
                crop_hist_str = None
            try:
                disease_hist_str = json.dumps(self.disease_history) if self.disease_history else None
            except Exception as json_err:
                logger.error(f"Error encoding disease_history in save: {json_err}")
                disease_hist_str = None
            try:
                weather_hist_str = json.dumps(self.weather_history) if self.weather_history else None
            except Exception as json_err:
                logger.error(f"Error encoding weather_history in save: {json_err}")
                weather_hist_str = None
            try:
                prev_recs_str = json.dumps(self.previous_recommendations) if self.previous_recommendations else None
            except Exception as json_err:
                logger.error(f"Error encoding previous_recommendations in save: {json_err}")
                prev_recs_str = None

            with memory_lock:
                with closing(sqlite3.connect(str(DB_PATH), timeout=20.0)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO sessions (session_id, latitude, longitude, location_name, file_path, file_context, previous_crop, previous_weather, uploaded_images,
                                             crop_history, disease_history, weather_history, preferred_language, preferred_units, previous_recommendations, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(session_id) DO UPDATE SET
                            latitude=excluded.latitude,
                            longitude=excluded.longitude,
                            location_name=excluded.location_name,
                            file_path=excluded.file_path,
                            file_context=excluded.file_context,
                            previous_crop=excluded.previous_crop,
                            previous_weather=excluded.previous_weather,
                            uploaded_images=excluded.uploaded_images,
                            crop_history=excluded.crop_history,
                            disease_history=excluded.disease_history,
                            weather_history=excluded.weather_history,
                            preferred_language=excluded.preferred_language,
                            preferred_units=excluded.preferred_units,
                            previous_recommendations=excluded.previous_recommendations,
                            updated_at=CURRENT_TIMESTAMP
                    """, (
                        self.session_id,
                        self.latitude,
                        self.longitude,
                        self.location_name,
                        self.file_path,
                        self.file_context,
                        self.previous_crop,
                        weather_str,
                        images_str,
                        crop_hist_str,
                        disease_hist_str,
                        weather_hist_str,
                        self.preferred_language,
                        self.preferred_units,
                        prev_recs_str
                    ))
                    conn.commit()
            logger.info(f"Persisted memory for session '{self.session_id}' to SQLite database.")
        except Exception as e:
            logger.error(f"Error saving session '{self.session_id}' memory: {e}", exc_info=True)

    def update_location(self, lat: float, lon: float, name: str = None):
        self.latitude = lat
        self.longitude = lon
        if name:
            self.location_name = name
        logger.info(f"Memory location updated: lat={self.latitude}, lon={self.longitude}, name={self.location_name}")
        self.save()

    def update_file(self, path: str, context: str = None):
        self.file_path = path
        if context:
            self.file_context = context
        
        # Add to uploaded_images list to keep history
        image_entry = {"file_path": path, "context": context}
        if image_entry not in self.uploaded_images:
            self.uploaded_images.append(image_entry)
            
        logger.info(f"Memory file updated: path={self.file_path}")
        self.save()

    def update_crop(self, crop: str):
        self.previous_crop = crop
        if crop not in self.crop_history:
            self.crop_history.append(crop)
        logger.info(f"Memory crop updated: {self.previous_crop}. Crop history: {self.crop_history}")
        self.save()

    def update_weather(self, weather_data: dict):
        self.previous_weather = weather_data
        self.weather_history.append(weather_data)
        logger.info(f"Memory weather updated: {self.previous_weather}")
        self.save()

    def add_disease(self, disease_name: str):
        if disease_name not in self.disease_history:
            self.disease_history.append(disease_name)
        logger.info(f"Memory disease history updated: {self.disease_history}")
        self.save()

    def add_recommendation(self, recommendation: str):
        self.previous_recommendations.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recommendation": recommendation
        })
        self.save()

    def update_preferences(self, preferred_language: Optional[str] = None, preferred_units: Optional[str] = None):
        if preferred_language:
            self.preferred_language = preferred_language
        if preferred_units:
            self.preferred_units = preferred_units
        logger.info(f"Memory preferences updated: language={self.preferred_language}, units={self.preferred_units}")
        self.save()



def get_user_memory(session_id: str = None) -> SessionMemory:
    """
    Retrieves or initializes SQLite-backed session memory. Automatically inspects incoming 
    request payloads, headers, and Flask context cookies.
    """
    if not session_id:
        # 1. Try to get from request payload if in request context
        try:
            if request and request.is_json:
                # Use silent=True to avoid errors if request is not parsed or json format
                data = request.get_json(silent=True) or {}
                session_id = data.get("session_id")
        except RuntimeError:
            pass

    if not session_id:
        # 2. Try to get from custom HTTP headers
        try:
            if request:
                session_id = request.headers.get("X-Session-ID")
        except RuntimeError:
            pass

    if not session_id:
        # 3. Try to get from Flask session cookie
        try:
            session_id = session.get("session_id")
            if not session_id:
                session_id = str(uuid.uuid4())
                session["session_id"] = session_id
                logger.info(f"Initialized new session ID in Flask cookie session: {session_id}")
        except RuntimeError:
            # Fallback for testing environments outside Flask request context
            session_id = "test-session-id"

    # Return a new instance to bypass memory caching leaks
    return SessionMemory(session_id)



def forward_geocode(query: str):
    """
    Converts a location name string to GPS coordinates (lat, lon, display_name)
    using OpenStreetMap Nominatim. Includes offline overrides for common queries.
    """
    query_clean = query.strip().lower()
    
    # Check offline overrides first
    for key, coords in OFFLINE_OVERRIDES.items():
        if key in query_clean:
            logger.info(f"Applying geocoding override for location text: '{query_clean}' -> {coords}")
            return coords[0], coords[1], coords[2]

    try:
        # Request coordinates from Nominatim
        url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(query)}&format=json&limit=1"
        headers = {"User-Agent": "AgriCoreAI-Location-Server/1.0"}
        logger.info(f"Geocoding location text '{query}' via Nominatim: {url}")
        response = requests.get(url, headers=headers, timeout=2.0)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                display_name = data[0].get("display_name", query)
                return lat, lon, display_name
            else:
                logger.warning(f"No results returned from Nominatim for location text: '{query}'")
        else:
            logger.warning(f"Nominatim Search API returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Forward geocoding API error for '{query}': {e}", exc_info=True)
        
    return None

def cleanup_user_data(user_id: int):
    """Deletes all session memory and history for a given user from SQLite database."""
    import sqlite3
    from contextlib import closing
    session_key = f"user_{user_id}"
    try:
        with memory_lock:
            with closing(sqlite3.connect(str(DB_PATH), timeout=20.0)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_key,))
                conn.commit()
        logger.info(f"Successfully cleaned up SQLite session data for user key: {session_key}")
    except Exception as e:
        logger.error(f"Failed to cleanup user data for user ID {user_id}: {e}", exc_info=True)

