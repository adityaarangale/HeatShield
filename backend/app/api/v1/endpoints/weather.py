from typing import List
from fastapi import APIRouter
from app.schemas.thermal import WeatherInput

router = APIRouter()


@router.get("/forecast", response_model=List[WeatherInput])
def get_mock_weather_data():
    """
    Simulate Automatic Weather Station (AWS) live observation feed
    across key regions in India (MoES grid).
    """
    return [
        WeatherInput(
            temperature=43.5,
            relative_humidity=40.0,
            wind_speed=3.0,
            solar_radiation=900.0,
            dew_point=25.0,
            latitude=28.6139,
            longitude=77.2090,
            location_name="New Delhi AWS"
        ),
        WeatherInput(
            temperature=46.2,
            relative_humidity=28.0,
            wind_speed=4.2,
            solar_radiation=950.0,
            dew_point=21.0,
            latitude=26.9124,
            longitude=75.7873,
            location_name="Jaipur AWS"
        ),
        WeatherInput(
            temperature=38.0,
            relative_humidity=65.0,
            wind_speed=2.5,
            solar_radiation=820.0,
            dew_point=27.0,
            latitude=19.0760,
            longitude=72.8777,
            location_name="Mumbai Coastal AWS"
        ),
        WeatherInput(
            temperature=44.8,
            relative_humidity=35.0,
            wind_speed=3.8,
            solar_radiation=910.0,
            dew_point=23.5,
            latitude=21.1458,
            longitude=79.0882,
            location_name="Nagpur AWS"
        )
    ]
