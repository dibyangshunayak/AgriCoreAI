# =====================================================================
# FILE: backend/app/skills/weather/alerts.py
# DESCRIPTION: Weather Alerts Skill.
# =====================================================================

from typing import Dict, Any, List

def check_weather_alerts(weather_metrics: Dict[str, Any]) -> List[str]:
    """Analyze weather metrics to generate alerts for critical conditions."""
    alerts = []
    temp = weather_metrics.get("temperature", 0.0)
    wind_speed = weather_metrics.get("wind_speed", 0.0)
    precipitation = weather_metrics.get("precipitation", 0.0)
    
    if temp is not None and temp > 35:
        alerts.append("CRITICAL: Extreme high temperature detected! Risk of heat stress and excessive evaporation.")
    elif temp is not None and temp < 5:
        alerts.append("CRITICAL: Frost risk! Protect sensitive crops from cold stress.")
        
    if wind_speed is not None and wind_speed > 40:
        alerts.append("CRITICAL: High wind advisory! Risk of physical damage/lodging in tall or weak crops.")
        
    if precipitation is not None and precipitation > 20:
        alerts.append("CRITICAL: Severe precipitation warning! Risk of field waterlogging, nutrient leaching, and root rot.")
        
    return alerts
