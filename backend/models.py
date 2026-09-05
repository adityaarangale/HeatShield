from typing import List, Optional
from pydantic import BaseModel, Field


class ForecastDay(BaseModel):
    day: str = Field(..., description="Forecast day identifier (e.g., Day 1, Day 2, Day 3, Day 4, Day 5)")
    temp_c: float = Field(..., description="Forecasted maximum temperature in Celsius (°C)", examples=[45.5])
    humidity_pct: float = Field(..., description="Forecasted relative humidity percentage (%)", examples=[35.0])
    solar_radiation_wm2: float = Field(850.0, description="Forecasted solar radiation in W/m²", examples=[850.0])


class ForecastRiskTrendItem(BaseModel):
    day: str = Field(..., description="Forecast day identifier")
    temp_c: float = Field(..., description="Temperature in °C")
    humidity_pct: float = Field(..., description="Humidity percentage")
    heat_index: float = Field(..., description="NWS Heat Index in °C")
    wbgt: float = Field(..., description="Outdoor WBGT in °C")
    solar_adjusted_wbgt: float = Field(..., description="Solar-adjusted WBGT in °C")
    apparent_temperature_c: float = Field(..., description="Australian BOM Apparent Temperature in °C")
    human_thermal_stress_index: float = Field(..., description="Blended Human Thermal Stress Index (°C)")
    risk_score: float = Field(..., description="Computed risk score (0-100)")
    risk_band: str = Field(..., description="Risk level classification band (Safe, Caution, Danger, Extreme)")


class Ward(BaseModel):
    ward_id: str = Field(..., description="Unique ward/taluka identifier", examples=["CHA_001"])
    ward_name: str = Field(..., description="Name of the ward or taluka in Chandrapur", examples=["Chandrapur City"])
    lat: float = Field(..., description="Latitude coordinate", examples=[23.0478])
    lon: float = Field(..., description="Longitude coordinate", examples=[72.5975])
    population: int = Field(..., description="Total estimated ward population", examples=[142000])
    elderly_pct: float = Field(..., description="Percentage of elderly population (60+ yrs)", examples=[11.5])
    outdoor_worker_pct: float = Field(..., description="Percentage of outdoor/informal workers", examples=[34.0])
    green_cover_pct: float = Field(..., description="Percentage of urban canopy / green cover", examples=[6.2])
    current_temp_c: float = Field(..., description="Current observed ambient temperature (°C)", examples=[44.2])
    humidity_pct: float = Field(..., description="Current relative humidity percentage (%)", examples=[38.0])
    wind_speed_kmh: float = Field(..., description="Current wind speed in km/h", examples=[12.5])
    solar_radiation_wm2: float = Field(..., description="Solar radiation intensity in W/m²", examples=[850.0])
    forecast_3day: List[ForecastDay] = Field(..., description="3 to 5-day temperature, humidity, and solar radiation forecast list")


class WardResponse(BaseModel):
    ward_id: str
    ward_name: str
    lat: float
    lon: float
    population: int
    elderly_pct: float
    outdoor_worker_pct: float
    green_cover_pct: float
    current_temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    solar_radiation_wm2: float
    heat_index: float
    wbgt: float
    solar_adjusted_wbgt: float
    apparent_temperature_c: float
    human_thermal_stress_index: float
    risk_score: float
    risk_band: str
    forecast_3day: List[ForecastDay]
    forecast_risk_trend: Optional[List[ForecastRiskTrendItem]] = None
    advisories: List[str]


class CalculationInput(BaseModel):
    temp_c: float = Field(..., description="Temperature in °C", examples=[43.5])
    humidity_pct: float = Field(..., description="Relative humidity %", examples=[40.0])
    wind_speed_kmh: Optional[float] = Field(10.0, description="Wind speed in km/h", examples=[12.0])
    solar_radiation_wm2: Optional[float] = Field(850.0, description="Solar radiation in W/m²", examples=[850.0])
    elderly_pct: Optional[float] = Field(10.0, description="Elderly population %", examples=[12.0])
    outdoor_worker_pct: Optional[float] = Field(30.0, description="Outdoor worker population %", examples=[35.0])
    green_cover_pct: Optional[float] = Field(5.0, description="Green cover %", examples=[4.5])


class CalculationResponse(BaseModel):
    heat_index_c: float = Field(..., description="Calculated NWS Heat Index in °C")
    wbgt_c: float = Field(..., description="Calculated Wet-Bulb Globe Temperature in °C")
    solar_adjusted_wbgt: float = Field(..., description="Solar-adjusted WBGT in °C")
    apparent_temperature_c: float = Field(..., description="Australian BOM Apparent Temperature in °C")
    human_thermal_stress_index: float = Field(..., description="Blended Human Thermal Stress Index (°C)")
    vulnerability_score: float = Field(..., description="Socio-environmental vulnerability index (0-100)")
    heatwave_category: str = Field(..., description="IMD Heatwave classification")
    risk_level: str = Field(..., description="Overall combined risk alert level")
    health_advisory: List[str] = Field(..., description="Recommended actions for citizens and municipal authorities")


class AlertTriggerRequest(BaseModel):
    ward_id: str = Field(..., description="Target Ward ID (e.g. CHA_001)", examples=["CHA_001"])
    risk_band: str = Field(..., description="Risk level band (e.g. Extreme, Danger)", examples=["Extreme"])
    recipient_phone: Optional[str] = Field(None, description="Optional recipient phone number for SMS delivery", examples=["+919876543210"])
    custom_message: Optional[str] = Field(None, description="Customized official advisory message text")


class AlertTriggerResponse(BaseModel):
    status: str = Field(..., description="Alert status (sent or simulated)")
    ward_id: str
    ward_name: str
    risk_band: str
    wbgt: float
    message: str
    provider: str = Field(..., description="Delivery mechanism (Twilio SMS or Console Log Fallback)")
    recipient_phone: Optional[str] = None


# Backward compatibility alias
WardRiskResponse = WardResponse
