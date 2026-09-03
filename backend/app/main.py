from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        f"Backend REST API for **Heat Shield** ({settings.SIH_CODE}) developed for "
        f"the **{settings.MINISTRY}**.\n\n"
        "Provides real-time calculation of Human Thermal Stress Indices (WBGT, UTCI, Heat Index, Humidex) "
        "and Extreme Heatwave Early Warning alerts."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root_health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "sih_problem_code": settings.SIH_CODE,
        "ministry": settings.MINISTRY,
        "version": settings.VERSION,
        "docs": "/docs"
    }
