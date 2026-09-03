from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Heat Shield - Extreme Heatwave Early Warning & Thermal Stress System"
    SIH_CODE: str = "SIH26083"
    MINISTRY: str = "Ministry of Earth Sciences (MoES)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Heatwave threshold defaults (in °C) according to IMD / MoES standards
    HEATWAVE_TEMP_THRESHOLD: float = 40.0
    SEVERE_HEATWAVE_TEMP_THRESHOLD: float = 45.0
    HEATWAVE_DEPARTURE_THRESHOLD: float = 4.5
    SEVERE_HEATWAVE_DEPARTURE_THRESHOLD: float = 6.4

    # Thermal Stress Index Warnings (WBGT in °C)
    WBGT_CAUTION: float = 28.0
    WBGT_EXTREME_CAUTION: float = 31.0
    WBGT_DANGER: float = 33.0

settings = Settings()
