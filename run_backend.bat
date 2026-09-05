@echo off
title HEAT SHIELD - FastAPI Backend Service (MoES SIH26083)
echo =====================================================================
echo    HEAT SHIELD - EXTREME HEAT EARLY WARNING SYSTEM (SIH26083)
echo    Ministry of Earth Sciences (MoES) - Pilot: Chandrapur District
echo =====================================================================
echo.
echo [1/2] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    pause
    exit /b 1
)

echo [2/2] Starting FastAPI backend on http://127.0.0.1:8000...
echo Swagger Interactive API Docs available at: http://127.0.0.1:8000/docs
echo Press CTRL+C to stop the server anytime.
echo.

cd /d "%~dp0backend"
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Backend encountered an issue. Installing requirements...
    pip install -r requirements.txt
    python main.py
)

pause
