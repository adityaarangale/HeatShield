import os
import json
import httpx
import pandas as pd
import numpy as np
from datetime import datetime

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_and_save_historical_data(
    lat: float = 19.9615,
    lon: float = 79.2961,
    start_date: str = "2023-01-01",
    end_date: str = "2024-12-31",
    output_path: str = None
) -> pd.DataFrame:
    """
    Fetch genuine historical weather observations from Open-Meteo Historical Weather Archive API
    for Chandrapur District (or specified lat/lon) and save to CSV.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data", "historical_weather_chandrapur.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,direct_normal_irradiance,precipitation",
        "timezone": "auto"
    }

    print(f"Fetching historical weather data from Open-Meteo API ({start_date} to {end_date})...")
    with httpx.Client(timeout=30.0) as client:
        response = client.get(OPEN_METEO_ARCHIVE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    hourly = data.get("hourly", {})
    df = pd.DataFrame({
        "time": hourly.get("time", []),
        "temp_c": hourly.get("temperature_2m", []),
        "humidity_pct": hourly.get("relative_humidity_2m", []),
        "wind_speed_kmh": hourly.get("wind_speed_10m", []),
        "surface_pressure_hpa": hourly.get("surface_pressure", []),
        "solar_radiation_wm2": hourly.get("direct_normal_irradiance", []),
        "precipitation_mm": hourly.get("precipitation", [])
    })

    # Fill any null values
    df["temp_c"] = df["temp_c"].ffill().bfill()
    df["humidity_pct"] = df["humidity_pct"].ffill().bfill()
    df["wind_speed_kmh"] = df["wind_speed_kmh"].fillna(10.0)
    df["surface_pressure_hpa"] = df["surface_pressure_hpa"].fillna(1013.25)
    df["solar_radiation_wm2"] = df["solar_radiation_wm2"].fillna(0.0)
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0.0)

    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} historical weather records to {output_path}")
    return df

if __name__ == "__main__":
    fetch_and_save_historical_data()
