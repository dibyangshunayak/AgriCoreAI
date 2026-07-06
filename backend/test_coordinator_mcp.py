# =====================================================================
# FILE: backend/test_coordinator_mcp.py
# DESCRIPTION: Test suite for Coordinator Agent to verify MCP routing,
#              disease detection, and general inquiries with the new
#              NVIDIA Nemotron planner.
# =====================================================================

import sys
import os
import unittest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

from app.agents.coordinator_agent import process_request

def mock_generate_execution_plan(user_query, image_uploaded=False, gps_available=False, location_name=None, conversation_context=None):
    """Mocks the planner to return appropriate execution steps based on query content."""
    query_lower = user_query.lower()
    steps = []
    
    if "spot" in query_lower or "disease" in query_lower or "detect" in query_lower:
        steps.append({"step": len(steps) + 1, "agent": "disease", "action": "Diagnose leaf spots"})
    if "irrigate" in query_lower or "weather" in query_lower or "temperature" in query_lower:
        steps.append({"step": len(steps) + 1, "agent": "weather", "action": "Fetch weather advisory"})
    if "where am i" in query_lower or "coordinates" in query_lower or "area" in query_lower:
        steps.append({"step": len(steps) + 1, "agent": "location", "action": "Determine location"})
        
    if not steps:
        steps.append({"step": 1, "agent": "crop", "action": "Provide general crop advice"})
        
    return {
        "steps": steps,
        "required_data": [],
        "response_tone": "general"
    }

async def mock_call_weather_mcp_tool(latitude, longitude):
    return {
        "temperature": 33.6,
        "humidity": 66,
        "precipitation": 0.0,
        "wind_speed": 9.2,
        "soil_temperature": 33.7,
        "soil_moisture": 0.368,
        "weather_condition": "Thunderstorm"
    }

async def mock_call_location_mcp_tool(latitude, longitude):
    return {
        "city": "Baripada",
        "district": "Mayurbhanj",
        "state": "Odisha",
        "country": "India",
        "formatted_location": "Baripada, Odisha, India"
    }

def mock_get_weather(latitude, longitude):
    return {
        "current": {
            "temperature_2m": 33.6,
            "relative_humidity_2m": 66,
            "precipitation": 0.0,
            "wind_speed_10m": 9.2,
            "weather_code": 95,
            "soil_temperature_0_to_7cm": 33.7,
            "soil_moisture_0_to_7cm": 0.368
        },
        "daily": {
            "time": ["2026-06-24"],
            "temperature_2m_max": [35.0],
            "temperature_2m_min": [25.0],
            "precipitation_sum": [0.0],
            "weather_code": [95]
        },
        "timezone": "UTC"
    }

@patch("app.agents.coordinator_agent.call_weather_mcp_tool", new=mock_call_weather_mcp_tool)
@patch("app.agents.coordinator_agent.call_location_mcp_tool", new=mock_call_location_mcp_tool)
@patch("app.agents.weather_agent.get_weather", new=mock_get_weather)
@patch("app.agents.coordinator_agent.generate_execution_plan", side_effect=mock_generate_execution_plan)
@patch("app.agents.weather_agent.generate_text")
@patch("app.agents.crop_agent.generate_text")
@patch("app.agents.location_agent.generate_text")
@patch("app.agents.coordinator_agent.ResponseSynthesizer.synthesize_response")
class TestCoordinatorMCP(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        cls.mock_image_path = backend_dir / "uploads" / "temp_leaf_test.jpg"
        cls.mock_image_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (100, 100), color="green")
        img.save(cls.mock_image_path)
        
    @classmethod
    def tearDownClass(cls):
        if cls.mock_image_path.exists():
            try:
                cls.mock_image_path.unlink()
            except OSError:
                pass

    def test_1_weather_query_with_gps(self, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 1: Weather query with valid GPS coordinates."""
        print("\nRunning Test 1: Weather query with GPS...")
        mock_weather_llm.return_value = "No irrigation required today."
        mock_synthesize.return_value = "Synthesized weather report: No irrigation required today."
        res = process_request("Should I irrigate today?", latitude=21.9592, longitude=86.7430)
        
        self.assertNotIn("error", res)
        self.assertIn("weather_agent", res["agents_used"])
        self.assertNotEqual(res["weather"], {})
        self.assertEqual(res["recommendation"], "Synthesized weather report: No irrigation required today.")
        print("[OK] Test 1 passed.")
        
    def test_2_location_query(self, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 2: Location inquiry."""
        print("\nRunning Test 2: Location query...")
        mock_loc_llm.return_value = "Baripada is known for rice cultivation."
        mock_synthesize.return_value = "Synthesized location details: Baripada is known for rice cultivation."
        res = process_request("What crops suit my area?", latitude=21.9592, longitude=86.7430)
        
        self.assertNotIn("error", res)
        self.assertIn("location_agent", res["agents_used"])
        self.assertNotEqual(res["location"], {})
        self.assertEqual(res["location"]["city"], "Baripada")
        self.assertEqual(res["recommendation"], "Synthesized location details: Baripada is known for rice cultivation.")
        print("[OK] Test 2 passed.")
        
    @patch("app.agents.coordinator_agent.detect_crop_disease")
    def test_3_disease_query(self, mock_detect_disease, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 3: Disease analysis query with image."""
        print("\nRunning Test 3: Disease query...")
        mock_detect_disease.return_value = "🌿 Disease:\nAnthracnose\n\n🔍 Symptoms:\nspots\n\n📊 Confidence:\nHigh"
        mock_synthesize.return_value = "Cohesive advice"
        res = process_request("Detect the disease.", image_path=str(self.mock_image_path))
        
        self.assertNotIn("error", res)
        self.assertIn("disease_agent", res["agents_used"])
        self.assertNotEqual(res["disease"], {})
        self.assertEqual(res["disease"]["name"], "Anthracnose")
        print("[OK] Test 3 passed.")
        
    @patch("app.agents.coordinator_agent.detect_crop_disease")
    def test_4_combined_query(self, mock_detect_disease, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 4: Combined weather + disease query."""
        print("\nRunning Test 4: Combined query...")
        mock_detect_disease.return_value = "🌿 Disease:\nAnthracnose\n\n"
        mock_weather_llm.return_value = "No irrigation required today."
        mock_synthesize.return_value = "Apply fungicide and check irrigation."
        res = process_request(
            "My mango leaf has spots and should I irrigate today?",
            image_path=str(self.mock_image_path),
            latitude=21.9592,
            longitude=86.7430
        )
        
        self.assertNotIn("error", res)
        self.assertIn("weather_agent", res["agents_used"])
        self.assertIn("disease_agent", res["agents_used"])
        self.assertNotEqual(res["weather"], {})
        self.assertNotEqual(res["disease"], {})
        print("[OK] Test 4 passed.")
        
    def test_5_missing_gps_coordinates(self, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 5: Weather query but missing coordinates."""
        print("\nRunning Test 5: Missing GPS coordinates...")
        res = process_request("Should I irrigate today?", latitude=None, longitude=None)
        
        self.assertIn("error", res)
        self.assertEqual(res["error"], "🌾 AgriCore AI\n\n📍 Location access unavailable.\n\nPlease enable location permission or specify your location explicitly.")
        print("[OK] Test 5 passed.")
        
    def test_6_invalid_image(self, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 6: Disease query but missing image."""
        print("\nRunning Test 6: Missing image file for disease query...")
        res = process_request("Detect the disease.", image_path=None)
        
        self.assertIn("error", res)
        self.assertEqual(res["error"], "Please upload a crop leaf image.")
        print("[OK] Test 6 passed.")
        
    def test_7_general_farming_question(self, mock_synthesize, mock_loc_llm, mock_crop_llm, mock_weather_llm, mock_planner):
        """Test Case 7: General conversational inquiry."""
        print("\nRunning Test 7: General conversational query...")
        mock_crop_llm.return_value = "Hello farmer. I am here to help you."
        mock_synthesize.return_value = "Hello assistant."
        res = process_request("Hello assistant.")
        
        self.assertNotIn("error", res)
        self.assertIn("general_agent", res["agents_used"])
        print("[OK] Test 7 passed.")

if __name__ == "__main__":
    unittest.main()
