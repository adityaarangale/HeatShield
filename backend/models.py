from typing import List, Optional, Dict, Any
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
    ml_predicted_risk_score: Optional[float] = Field(None, description="ML Random Forest Predicted Risk Score")
    ml_predicted_risk_category: Optional[str] = Field(None, description="ML Random Forest Predicted Risk Category")



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
    api_key: Optional[str] = Field(None, description="Optional Fast2SMS or Twilio API key from frontend")


class AlertTriggerResponse(BaseModel):
    status: str = Field(..., description="Alert status (sent or simulated)")
    ward_id: str
    ward_name: str
    risk_band: str
    wbgt: float
    message: str
    provider: str = Field(..., description="Delivery mechanism (Twilio SMS, Fast2SMS, or Console Log Fallback)")
    recipient_phone: Optional[str] = None


class BroadcastAlertRequest(BaseModel):
    ward_id: str = Field(..., description="Target Ward ID or 'ALL'", examples=["CHA_001"])
    risk_band: str = Field(..., description="Risk tier classification", examples=["Extreme"])
    recipient_phones: List[str] = Field(..., description="List of recipient phone numbers", examples=[["+919876543210", "+919876543211"]])
    custom_message: str = Field(..., description="Broadcast message content", examples=["EMERGENCY HEAT ADVISORY: Stay indoors between 11 AM - 4 PM."])
    api_key: Optional[str] = Field(None, description="Optional Fast2SMS or Twilio API key from frontend")


class BroadcastAlertResponse(BaseModel):
    status: str = Field("broadcast_completed", description="Overall broadcast status")
    total_recipients: int
    successful_count: int
    recipients: List[str]
    provider: str
    message: str


class LiveWeatherDetails(BaseModel):
    temperature_c: float
    relative_humidity_pct: float
    wind_speed_kmh: float
    surface_pressure_hpa: float
    solar_radiation_wm2: float
    precipitation_mm: float
    time: str


class LiveWeatherResponse(BaseModel):
    status: str
    source: str
    latitude: float
    longitude: float
    timestamp: str
    is_live: bool
    weather: LiveWeatherDetails
    forecast_5day: List[ForecastDay]
    heat_index_c: float
    wbgt_c: float
    solar_adjusted_wbgt: float
    apparent_temperature_c: float
    human_thermal_stress_index: float
    risk_score: float
    risk_band: str
    advisories: List[str]


class MLPredictionRequest(BaseModel):
    temp_c: float = Field(..., description="Ambient temperature (°C)", examples=[44.5])
    humidity_pct: float = Field(..., description="Relative humidity (%)", examples=[38.0])
    wind_speed_kmh: Optional[float] = Field(10.0, description="Wind speed in km/h", examples=[12.0])
    solar_radiation_wm2: Optional[float] = Field(850.0, description="Solar radiation in W/m²", examples=[850.0])
    surface_pressure_hpa: Optional[float] = Field(1013.25, description="Surface pressure in hPa", examples=[1008.5])
    precipitation_mm: Optional[float] = Field(0.0, description="Precipitation in mm", examples=[0.0])
    hour: Optional[int] = Field(None, description="Hour of day (0-23)", examples=[14])
    month: Optional[int] = Field(None, description="Month of year (1-12)", examples=[5])


class MLPredictionResponse(BaseModel):
    predicted_risk_score: float = Field(..., description="ML predicted heat risk score (0-100)")
    predicted_risk_category: str = Field(..., description="Predicted risk level (Safe, Caution, Danger, Extreme)")
    model_version: str = Field(..., description="Version of the trained ML model")
    prediction_time: str = Field(..., description="ISO 8601 timestamp of prediction")
    prediction_type: str = Field("ML (Random Forest Regressor Inference)", description="Type of inference engine")
    features_input: Dict[str, Any] = Field(..., description="Inputs and engineered features passed to ML model")


class MLModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float


class MLModelMetadataResponse(BaseModel):
    status: str = "loaded"
    model_version: str
    algorithm: str
    training_period: str
    dataset_records: int
    train_records: int
    test_records: int
    training_date: str
    features_used: List[str]
    metrics: MLModelMetrics
    target_definition: str


class MLForecastItem(BaseModel):
    day: str
    temp_c: float
    humidity_pct: float
    solar_radiation_wm2: float
    formula_risk_score: float
    ml_predicted_risk_score: float
    ml_predicted_risk_category: str


# Backward compatibility alias
WardRiskResponse = WardResponse


# Authentication Models
class AuthSignupRequest(BaseModel):
    name: Optional[str] = Field(None, description="User's full name", examples=["Ramesh Kumar"])
    phone: Optional[str] = Field(None, description="Unique phone number", examples=["9876543210"])
    password: Optional[str] = Field(None, description="User password", examples=["Password123!"])
    role: Optional[str] = Field(None, description="Role: 'citizen' or 'authority'", examples=["citizen"])
    ward_or_department: Optional[str] = Field(None, description="Ward or department name", examples=["Ward 4"])



class AuthLoginRequest(BaseModel):
    phone: str = Field(..., description="Registered phone number", examples=["+919876543210"])
    password: str = Field(..., description="User password", examples=["Password123!"])


class UserSignupRequest(BaseModel):
    name: str = Field(..., description="User's full name", examples=["Ramesh Kumar"])
    email: str = Field(..., description="Unique email address", examples=["ramesh@example.com"])
    password: str = Field(..., description="Password (min 6 chars)", examples=["Password123!"])


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address", examples=["ramesh@example.com"])
    password: str = Field(..., description="User password", examples=["Password123!"])


class AuthorityLoginRequest(BaseModel):
    email: str = Field(..., description="Authority officer email", examples=["authority@heatshield.gov.in"])
    password: str = Field(..., description="Authority password", examples=["HeatShield2026!"])


class AuthorityRegisterRequest(BaseModel):
    name: str = Field(..., description="Officer name", examples=["Dr. A. Sharma"])
    email: str = Field(..., description="Officer email", examples=["sharma@heatshield.gov.in"])
    password: str = Field(..., description="Officer password", examples=["AuthorityPass2026!"])
    registration_code: str = Field(..., description="Secret authority registration code")


class UserResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class CitizenProfileSaveRequest(BaseModel):
    age_group: str = Field("adult", description="Age category: child, adult, elderly", examples=["adult"])
    gender: Optional[str] = Field("prefer_not_to_say", description="Gender: male, female, prefer_not_to_say", examples=["male"])
    occupation_type: str = Field("outdoor_manual", description="Occupation exposure type", examples=["outdoor_manual"])
    health_flags: List[str] = Field(default_factory=list, description="Health condition flags", examples=[["none"]])
    activity_level: Optional[str] = Field("heavy_exertion", description="Current activity level", examples=["heavy_exertion"])
    ward_id: str = Field("CHA_001", description="Location ward ID", examples=["CHA_001"])




