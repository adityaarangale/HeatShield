import time
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("uvicorn.error")

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Server-side 10-minute (600 seconds) in-memory TTL cache for live weather
_WEATHER_CACHE: Dict[tuple, tuple] = {}
CACHE_TTL_SECONDS = 600

def fetch_realtime_weather_cached(lat: float, lon: float, cache_ttl: int = CACHE_TTL_SECONDS) -> Dict[str, Any]:
    """
    Fetches real-time weather from Open-Meteo, caching results for 10 minutes (600s).
    Ensures citizen and authority views utilize the identical backend data pipeline.
    """
    now = time.time()
    cache_key = (round(lat, 3), round(lon, 3))

    if cache_key in _WEATHER_CACHE:
        cached_time, cached_data = _WEATHER_CACHE[cache_key]
        if now - cached_time < cache_ttl:
            logger.info(f"[Weather Cache Hit] Serving cached weather for ({lat}, {lon}) - Age: {int(now - cached_time)}s")
            data_copy = dict(cached_data)
            data_copy["cached"] = True
            data_copy["cache_age_seconds"] = int(now - cached_time)
            data_copy["cache_ttl_seconds"] = cache_ttl
            data_copy["source"] = f"FastAPI Server Cache (Open-Meteo API, {int(now - cached_time)}s old)"
            return data_copy

    fresh_data = fetch_realtime_weather(lat, lon)
    if fresh_data.get("status") == "success":
        fresh_data["cached"] = False
        fresh_data["cache_age_seconds"] = 0
        fresh_data["cache_ttl_seconds"] = cache_ttl
        _WEATHER_CACHE[cache_key] = (now, fresh_data)

    return fresh_data

def fetch_realtime_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch real-time weather and 5-day forecast from Open-Meteo API for given coordinates.
    Includes proper error handling and timeout handling.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,direct_normal_irradiance,precipitation",
        "daily": "temperature_2m_max,relative_humidity_2m_mean,wind_speed_10m_max,shortwave_radiation_sum,precipitation_sum",
        "forecast_days": 5,
        "timezone": "auto"
    }
    
    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.get(OPEN_METEO_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            # Extract current variables
            temp_c = current.get("temperature_2m", 35.0)
            rh = current.get("relative_humidity_2m", 40.0)
            wind_speed = current.get("wind_speed_10m", 10.0)
            pressure = current.get("surface_pressure", 1013.25)
            # Direct normal irradiance or shortwave proxy
            solar_rad = current.get("direct_normal_irradiance", 850.0)
            if solar_rad is None or solar_rad < 0:
                solar_rad = 850.0
            precipitation = current.get("precipitation", 0.0)
            time_str = current.get("time", datetime.now().isoformat())
            
            # Format 5-day forecast
            forecast_5day = []
            daily_times = daily.get("time", [])
            daily_temps = daily.get("temperature_2m_max", [])
            daily_rhs = daily.get("relative_humidity_2m_mean", [])
            daily_solars = daily.get("shortwave_radiation_sum", [])
            
            for i in range(len(daily_times)):
                # Shortwave radiation sum is in MJ/m², convert ~ to average peak W/m² (1 MJ/m² ≈ 25 W/m² peak equivalent estimation or fallback to 800)
                solar_val = 850.0
                if i < len(daily_solars) and daily_solars[i] is not None:
                    # e.g., 18 MJ/m² -> approx 800 W/m² peak solar irradiance
                    solar_val = round(min(1200.0, max(200.0, daily_solars[i] * 45.0)), 1)
                
                day_temp = daily_temps[i] if i < len(daily_temps) and daily_temps[i] is not None else temp_c
                day_rh = daily_rhs[i] if i < len(daily_rhs) and daily_rhs[i] is not None else rh
                
                forecast_5day.append({
                    "day": f"Day {i+1} ({daily_times[i]})" if i < len(daily_times) else f"Day {i+1}",
                    "date": daily_times[i] if i < len(daily_times) else "",
                    "temp_c": day_temp,
                    "humidity_pct": day_rh,
                    "solar_radiation_wm2": solar_val
                })
                
            return {
                "status": "success",
                "source": "Open-Meteo Live API",
                "latitude": lat,
                "longitude": lon,
                "timestamp": time_str,
                "is_live": True,
                "weather": {
                    "temperature_c": temp_c,
                    "relative_humidity_pct": rh,
                    "wind_speed_kmh": wind_speed,
                    "surface_pressure_hpa": pressure,
                    "solar_radiation_wm2": solar_rad,
                    "precipitation_mm": precipitation,
                    "time": time_str
                },
                "forecast_5day": forecast_5day
            }
            
    except Exception as e:
        logger.error(f"[Weather API Error] Failed to fetch live weather from Open-Meteo for ({lat}, {lon}): {str(e)}")
        return {
            "status": "error",
            "source": "Open-Meteo Live API (FAILED)",
            "error_detail": str(e),
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.now().isoformat(),
            "is_live": False,
            "weather": None,
            "forecast_5day": []
        }
