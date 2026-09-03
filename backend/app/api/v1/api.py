from fastapi import APIRouter
from app.api.v1.endpoints import thermal, weather

api_router = APIRouter()
api_router.include_router(thermal.router, prefix="/thermal", tags=["Thermal Stress & Heatwave Alert"])
api_router.include_router(weather.router, prefix="/weather", tags=["AWS Weather Stations"])
