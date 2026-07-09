from app.services.weather_service import (
    get_weather,
    interpret_weather
)

weather = get_weather(
    latitude=20.2961,
    longitude=85.8245
)

print("Weather Data:")
print(weather)

advice = interpret_weather(weather)

print("\nRecommendations:")
print(advice)