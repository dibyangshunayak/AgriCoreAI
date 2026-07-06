# =====================================================================
# FILE: backend/test_weather_agent.py
# DESCRIPTION: A simple test script to verify that the Weather Agent
#              can fetch weather/soil data and generate AI recommendations.
# =====================================================================

import sys
from pathlib import Path

# Add the parent directory (backend/) to the system path so Python can resolve imports from 'app.'
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Import the Weather Agent function.
from app.agents.weather_agent import get_weather_recommendation

def run_test():
    """
    Executes a test query to verify that the Weather Agent workflow is working.
    """
    # Fix Windows terminal encoding for emojis (UTF-8)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # If no API key is set, mock generate_text so the test runs successfully
    from app.config import settings
    from unittest.mock import patch
    if not settings.NVIDIA_API_KEY:
        print("[Note] NVIDIA_API_KEY not configured. Mocking Nemotron generate_text response.")
        patcher = patch("app.agents.weather_agent.generate_text", return_value=(
            "🌡 Temperature:\nWarm temperature is good.\n\n"
            "☁ Weather:\nClear sky.\n\n"
            "🌾 Irrigation:\nIrrigation is not required today.\n\n"
            "🦠 Disease Risk:\nLow risk.\n\n"
            "🌱 Fertilizer:\nNo fertilizer needed.\n\n"
            "🚜 Field Activity:\nNormal activity.\n\n"
            "⚠ Precaution:\nWear a hat."
        ))
        patcher.start()

    print("\n" + "="*50)
    print("AGRICORE AI: TESTING WEATHER AGENT")
    print("="*50)

    # Bhubaneswar, Odisha coordinates as used in test_weather.py
    latitude = 20.2961
    longitude = 85.8245
    
    print(f"\n[1] Querying Weather Agent for Lat: {latitude}, Lon: {longitude}...\n")
    
    try:
        # Call the weather agent
        result = get_weather_recommendation(latitude=latitude, longitude=longitude)
        
        # Print weather metrics
        print("="*50)
        print("WEATHER METRICS:")
        print("="*50)
        for key, val in result["weather_metrics"].items():
            print(f" - {key}: {val}")
            
        # Print AI recommendations
        print("\n" + "="*50)
        print("AI AGRI RECOMMENDATION:")
        print("="*50)
        print(result["ai_recommendation"])
        
        print("\n" + "="*50)
        print(f"Timestamp (UTC): {result['timestamp']}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\nTest failed with exception: {e}")

if __name__ == "__main__":
    run_test()
