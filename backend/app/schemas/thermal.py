from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    temperature: float = Field(..., description="Air temperature in Celsius (°C)", examples=[42.5])
    relative_humidity: float = Field(..., description="Relative humidity percentage (%)", ge=0, le=100, examples=[45.0])
    wind_speed: Optional[float] = Field(2.0, description="Wind speed in m/s (at 10m height)", ge=0, examples=[3.5])
    solar_radiation: Optional[float] = Field(800.0, description="Solar radiation in W/m²", ge=0, examples=[850.0])
    dew_point: Optional[float] = Field(None, description="Dew point temperature in Celsius (°C)", examples=[24.0])
    latitude: Optional[float] = Field(28.6139, description="Latitude of location", examples=[28.6139])
    longitude: Optional[float] = Field(77.2090, description="Longitude of location", examples=[77.2090])
    location_name: Optional[str] = Field("New Delhi", description="Location name or station identifier", examples=["New Delhi AWS"])


class ThermalIndexResponse(BaseModel):
    temperature: float
    relative_humidity: float
    heat_index: float = Field(..., description="NWS Heat Index in °C")
    wbgt: float = Field(..., description="Estimated Wet-Bulb Globe Temperature in °C")
    utci: float = Field(..., description="Estimated Universal Thermal Climate Index in °C")
    humidex: float = Field(..., description="Humidex rating in °C")
    stress_category: str = Field(..., description="Human thermal stress level category")
    heatwave_alert: str = Field(..., description="Heatwave alert status (Normal, Heatwave, Severe Heatwave)")
    precautions: List[str] = Field(..., description="Recommended safety & advisory guidelines")


class RegionAlertRequest(BaseModel):
    region_name: str
    stations: List[WeatherInput]


class RegionAlertResponse(BaseModel):
    region_name: str
    total_stations: int
    heatwave_count: int
    severe_heatwave_count: int
    highest_wbgt: float
    overall_alert_level: str
    station_results: List[ThermalIndexResponse]
