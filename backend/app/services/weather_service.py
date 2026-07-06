import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather(latitude: float, longitude: float):
    """Fetch weather data for a location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": "celsius",
        "windspeed_unit": "kmh",
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m,soil_temperature_0_to_7cm,soil_moisture_0_to_7cm",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 7  # Get 7-day forecast
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=3.0)
        response.raise_for_status()  # Raise exception for bad responses
        data = response.json()
        
        return {
            "current": data.get("current", {}),
            "daily": data.get("daily", {}),
            "timezone": data.get("timezone")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None

def interpret_weather(weather_data):
    """Interpret weather data into actionable advice."""
    if not weather_data or not weather_data.get("current"):  # pragma: no cover
        return None

    current = weather_data["current"]
    daily = weather_data["daily"]
    
    temp = current.get("temperature_2m", 0.0)
    humidity = current.get("relative_humidity_2m", 0.0)
    precipitation = current.get("precipitation", 0.0)
    wind_speed = current.get("wind_speed_10m", 0.0)
    weather_code = current.get("weather_code", -1)
    soil_temp = current.get("soil_temperature_0_to_7cm")
    soil_moisture = current.get("soil_moisture_0_to_7cm")
    
    # Basic interpretation
    advice = []
    
    # Temperature advice
    if temp < 10:
        advice.append("Temperatures are cold. Ensure proper irrigation scheduling to avoid water stress.")
    elif temp > 30:
        advice.append("High temperatures detected. Consider shading and increase irrigation frequency.")
    
    # Humidity advice
    if humidity > 80:
        advice.append("High humidity may increase disease risk. Monitor crops for fungal infections.")
    
    # Precipitation advice
    if precipitation > 5:  # 5mm or more
        advice.append("Heavy rain expected. Ensure good drainage and avoid pesticide application.")
    elif precipitation > 0:
        advice.append("Light rain expected. Irrigation may not be needed.")
    
    # Wind advice
    if wind_speed > 30:
        advice.append("Strong winds expected. Protect crops from wind damage if necessary.")
    
    # Weather code interpretation (simplified)
    weather_descriptions = {
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
    
    code = weather_code
    if code in weather_descriptions:
        advice.append(f"Current weather: {weather_descriptions[code]}")
    
    # 7-day forecast summary
    if daily and daily.get("temperature_2m_max") and daily.get("temperature_2m_min"):
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        total_temps = len(max_temps) + len(min_temps)
        if total_temps > 0:
            avg_temp = (sum(max_temps) + sum(min_temps)) / total_temps
            advice.append(f"7-day average temperature: {avg_temp:.1f}°C")
            
    # Soil metrics interpretation
    if soil_temp is not None:
        if soil_temp < 15:
            advice.append("Low soil temperature detected. Root activity is slow; avoid warm-season crop planting.")
        elif soil_temp > 35:
            advice.append("High soil temperature detected. Root zone evaporation is high; consider mulching to keep soil cool.")
            
    if soil_moisture is not None:
        if soil_moisture < 0.15:
            advice.append("Low soil moisture. Crop roots are dry; immediate irrigation is recommended.")
        elif soil_moisture > 0.40:
            advice.append("High soil moisture (waterlogged conditions). Halt irrigation and check drainage to prevent root rot.")
        else:
            advice.append("Soil moisture is at an optimal level for crop growth.")
            
    return {
        "summary": "Based on the weather forecast:",
        "advice": advice,
        "metrics": {
            "temperature": temp,
            "humidity": humidity,
            "precipitation": precipitation,
            "wind_speed": wind_speed,
            "soil_temperature": soil_temp,
            "soil_moisture": soil_moisture
        }
    }
