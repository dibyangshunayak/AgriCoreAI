# =====================================================================
# FILE: backend/app/agents/weather_agent.py
# DESCRIPTION: Orchestrates fetching agricultural weather/soil data,
#              extracting current metrics and daily forecasts, and querying
#              NVIDIA Nemotron to generate advisories.
# =====================================================================

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from app.services.weather_service import get_weather
from app.services.nvidia_service import generate_text

logger = logging.getLogger(__name__)

WEATHER_CODE_DESCRIPTIONS: Dict[int, str] = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail"
}

class WeatherAgentException(Exception):
    """Custom exception raised when the Weather Agent fails to perform its workflow."""
    pass

def get_weather_recommendation(
    latitude: float,
    longitude: float,
    user_query: Optional[str] = None
) -> dict:
    """
    Fetches weather/soil metrics and forecasts, formats them, and calls NVIDIA Nemotron.
    """
    logger.info(f"Weather Agent starting recommendation workflow for Lat: {latitude}, Lon: {longitude}")

    try:
        weather_data = get_weather(latitude=latitude, longitude=longitude)
    except Exception as e:
        logger.error(f"Weather Service call failed: {e}", exc_info=True)
        raise WeatherAgentException(f"Failed to retrieve weather data from service: {e}") from e

    if not weather_data or "current" not in weather_data:
        logger.error("Weather Service returned invalid payload.")
        raise WeatherAgentException("Weather data is currently unavailable.")

    # 1. Extract current metrics
    current_data = weather_data["current"]
    temperature = current_data.get("temperature_2m")
    humidity = current_data.get("relative_humidity_2m")
    precipitation = current_data.get("precipitation")
    wind_speed = current_data.get("wind_speed_10m")
    weather_code = current_data.get("weather_code")
    soil_temperature = current_data.get("soil_temperature_0_to_7cm")
    soil_moisture = current_data.get("soil_moisture_0_to_7cm")

    weather_condition = "Unknown"
    if weather_code is not None:
        weather_condition = WEATHER_CODE_DESCRIPTIONS.get(weather_code, f"Code {weather_code}")

    weather_metrics = {
        "temperature": temperature,
        "humidity": humidity,
        "precipitation": precipitation,
        "wind_speed": wind_speed,
        "weather_condition": weather_condition,
        "soil_temperature": soil_temperature,
        "soil_moisture": soil_moisture
    }

    # 2. Extract daily forecast metrics
    daily_data = weather_data.get("daily", {})
    forecast_lines = []
    if daily_data and "time" in daily_data:
        times = daily_data.get("time", [])
        max_temps = daily_data.get("temperature_2m_max", [])
        min_temps = daily_data.get("temperature_2m_min", [])
        precip_sums = daily_data.get("precipitation_sum", [])
        codes = daily_data.get("weather_code", [])

        for i in range(min(7, len(times))):
            date_str = times[i]
            max_t = max_temps[i] if i < len(max_temps) else "N/A"
            min_t = min_temps[i] if i < len(min_temps) else "N/A"
            prec = precip_sums[i] if i < len(precip_sums) else 0.0
            w_code = codes[i] if i < len(codes) else -1
            desc = WEATHER_CODE_DESCRIPTIONS.get(w_code, "Unknown")
            forecast_lines.append(f"- {date_str}: Max {max_t}°C, Min {min_t}°C, Rain {prec}mm, Condition: {desc}")

    forecast_str = "\n".join(forecast_lines) if forecast_lines else "No forecast data."

    # 3. Compile prompt
    prompt = f"""
You are a helpful agricultural assistant speaking directly to a farmer. Write a simple, direct farm advisory under 120 words.
Query from farmer: "{user_query or 'What is the weather report?'}"

Use these current metrics:
- Temperature: {temperature if temperature is not None else 'N/A'}°C
- Humidity: {humidity if humidity is not None else 'N/A'}%
- Rain: {precipitation if precipitation is not None else 'N/A'} mm
- Wind: {wind_speed if wind_speed is not None else 'N/A'} km/h
- Weather Condition: {weather_condition}
- Soil Temperature: {soil_temperature if soil_temperature is not None else 'N/A'}°C
- Soil Moisture: {soil_moisture if soil_moisture is not None else 'N/A'}

Use this 7-day forecast data:
{forecast_str}

Strict rules to follow:
1. NEVER assume or mention crop type, planting stage, soil type, or specific farming practices. Keep the advice generalized.
2. Give ONLY recommendations directly supported by the weather and forecast data. Do not invent information.
3. If the farmer asks about tomorrow, next week, or any forecast, make sure the advisory focuses on the daily forecast rather than just the current weather.
4. Do NOT mention any scientific units, formulas, or raw measurements for soil moisture or wind in the advisory text.
5. Keep the language extremely simple. Use emojis.
6. Every single section must be EXACTLY one sentence long.
7. The entire response must be under 120 words.

Output format must be EXACTLY as follows (no other text):

🌡 Temperature:
One short sentence.

☁ Weather:
One short sentence.

🌾 Irrigation:
One recommendation.

🦠 Disease Risk:
One recommendation.

🌱 Fertilizer:
One recommendation.

🚜 Field Activity:
One recommendation.

⚠ Precaution:
One recommendation.
"""

    logger.info("Submitting parameters to NVIDIA Nemotron service...")
    try:
        ai_recommendation = generate_text(prompt)
    except Exception as e:
        logger.error(f"NVIDIA Nemotron service call failed: {e}", exc_info=True)
        raise WeatherAgentException(f"Failed to generate AI recommendations: {e}") from e

    if not ai_recommendation:
        logger.error("NVIDIA Nemotron service returned empty response.")
        raise WeatherAgentException("AI recommendations could not be generated.")

    timestamp_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "weather_metrics": weather_metrics,
        "daily_forecast": daily_data,
        "ai_recommendation": ai_recommendation,
        "timestamp": timestamp_str
    }

