import sys
import os
import sqlite3
import json
import unittest
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.services.memory_service import get_user_memory, SessionMemory, DB_PATH

class TestMemoryPersistence(unittest.TestCase):
    def setUp(self):
        # Generate a unique session ID for this run
        self.session_id = "test-session-12345"
        # Ensure database is initialized
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id,))
        conn.commit()
        conn.close()

    def tearDown(self):
        # Clean up database entry
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (self.session_id,))
        conn.commit()
        conn.close()

    def test_database_persistence(self):
        # 1. Retrieve blank memory and check defaults
        memory = get_user_memory(self.session_id)
        self.assertEqual(memory.session_id, self.session_id)
        self.assertIsNone(memory.latitude)
        self.assertIsNone(memory.longitude)
        self.assertIsNone(memory.location_name)
        self.assertIsNone(memory.previous_crop)
        self.assertIsNone(memory.previous_weather)

        # 2. Update properties
        memory.update_location(20.9517, 85.0985, "Odisha, India")
        memory.update_crop("mango")
        weather_data = {"temperature": 32.5, "humidity": 78, "weather_condition": "Humid"}
        memory.update_weather(weather_data)
        memory.update_file("uploads/mango_leaf.jpg", "Mango leaf spots analysis")

        # 3. Verify SQLite DB has the updated rows
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude, location_name, previous_crop, previous_weather, file_path FROM sessions WHERE session_id = ?", (self.session_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], 20.9517)
        self.assertEqual(row[1], 85.0985)
        self.assertEqual(row[2], "Odisha, India")
        self.assertEqual(row[3], "mango")
        self.assertEqual(json.loads(row[4]), weather_data)
        self.assertEqual(row[5], "uploads/mango_leaf.jpg")

        # 4. Check if re-instantiation of memory retrieves values from DB correctly
        # Clear SESSION_MEMORY cache to force reloading from DB
        from app.services.memory_service import SESSION_MEMORY
        if self.session_id in SESSION_MEMORY:
            del SESSION_MEMORY[self.session_id]

        new_memory = get_user_memory(self.session_id)
        self.assertEqual(new_memory.session_id, self.session_id)
        self.assertEqual(new_memory.latitude, 20.9517)
        self.assertEqual(new_memory.longitude, 85.0985)
        self.assertEqual(new_memory.location_name, "Odisha, India")
        self.assertEqual(new_memory.previous_crop, "mango")
        self.assertEqual(new_memory.previous_weather, weather_data)
        self.assertEqual(new_memory.file_path, "uploads/mango_leaf.jpg")
        print("[+] SQLite DB persistence unit test passed successfully!")

if __name__ == "__main__":
    unittest.main()
