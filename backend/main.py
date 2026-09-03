import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import (
    Ward,
    CalculationInput,
    CalculationResponse,
    WardResponse,
    ForecastRiskTrendItem,
    AlertTriggerRequest,
    AlertTriggerResponse
)
from logic import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_risk_score,
    calculate_vulnerability_score,
    classify_heatwave_risk,
    load_wards_dataset,
    evaluate_ward_detail
)

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Heat Shield - Extreme Heatwave Early Warning & Human Thermal Stress Index System",
    description=(
        "Heat Shield: A city-agnostic Extreme Heatwave Early Warning and Human Thermal Stress Index System "
        "built for SIH26083 (Ministry of Earth Sciences). Pilot region: Chandrapur District, Maharashtra. "
        "Provides real-time ward/taluka-level risk assessments, Heat Index, Australian BOM WBGT, "
        "Apparent Temperature, blended Human Thermal Stress Index, combined Risk Score (0-100), "
        "multi-day forecasted risk trends, and automated SMS alerts via Twilio."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration on localhost and all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": "Extreme Heatwave Early Warning & Human Thermal Stress Index System",
        "sih_problem_code": "SIH26083",
        "ministry": "Ministry of Earth Sciences (MoES)",
        "pilot_city": "Chandrapur, Maharashtra",
        "endpoints": {
            "all_wards": "/wards",
            "ward_detail_with_trend": "/wards/{ward_id}",
            "trigger_alert": "POST /alerts/trigger",
            "docs": "/docs"
        }
    }


@app.get("/wards", response_model=List[WardResponse], tags=["Wards"])
@app.get("/api/wards", response_model=List[WardResponse], tags=["Wards"])
def get_all_wards():
    """
    GET /wards
    Returns all 8 Chandrapur talukas/wards with their computed heat_index, wbgt, risk_score, and risk_band.
    """
    try:
        wards = load_wards_dataset()
        return [evaluate_ward_detail(w, include_trend=False) for w in wards]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load wards data: {str(e)}"
        )


@app.get("/wards/{ward_id}", response_model=WardResponse, tags=["Wards"])
@app.get("/api/wards/{ward_id}", response_model=WardResponse, tags=["Wards"])
def get_ward_by_id(ward_id: str):
    """
    GET /wards/{ward_id}
    Returns full details for a ward plus a 3-day forecasted risk trend using the same formulas on forecast_3day data.
    """
    wards = load_wards_dataset()
    for w in wards:
        if w.ward_id.upper() == ward_id.upper() or w.ward_name.lower() == ward_id.lower():
            return evaluate_ward_detail(w, include_trend=True)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ward with ID or name '{ward_id}' not found."
    )


@app.get("/api/alerts", response_model=List[WardResponse], tags=["Alerts"])
def get_active_heatwave_alerts():
    """
    Get wards currently under active Caution, Danger, or Extreme heatwave risk bands.
    """
    wards = load_wards_dataset()
    evaluated = [evaluate_ward_detail(w, include_trend=False) for w in wards]
    return [e for e in evaluated if e.risk_band in ["Caution", "Danger", "Extreme"]]


@app.post("/alerts/trigger", response_model=AlertTriggerResponse, tags=["Alerts"])
@app.post("/api/alerts/trigger", response_model=AlertTriggerResponse, tags=["Alerts"])
def trigger_alert(request: AlertTriggerRequest):
    """
    POST /alerts/trigger
    Takes ward_id and risk_band, and sends a real SMS via Twilio using environment variables:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_PHONE_NUMBER
    If Twilio is not configured or fails, falls back to a console log for demo purposes.
    """
    wards = load_wards_dataset()
    target_ward = None
    for w in wards:
        if w.ward_id.upper() == request.ward_id.upper() or w.ward_name.lower() == request.ward_id.lower():
            target_ward = w
            break

    if not target_ward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ward with ID or name '{request.ward_id}' not found."
        )

    wbgt = calculate_wbgt(target_ward.current_temp_c, target_ward.humidity_pct)
    sms_message = (
        f"ALERT: {target_ward.ward_name} - {request.risk_band} heat risk. "
        f"WBGT {wbgt}°C. Vulnerable groups advised to avoid outdoor activity 11am-4pm."
    )

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    recipient_phone = request.recipient_phone or os.getenv("TO_PHONE_NUMBER", "+919876543210")

    if account_sid and auth_token and from_phone:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            message_instance = client.messages.create(
                body=sms_message,
                from_=from_phone,
                to=recipient_phone
            )
            logger.info(f"[Twilio SMS Sent] SID: {message_instance.sid} to {recipient_phone}")
            return AlertTriggerResponse(
                status="sent",
                ward_id=target_ward.ward_id,
                ward_name=target_ward.ward_name,
                risk_band=request.risk_band,
                wbgt=wbgt,
                message=sms_message,
                provider="Twilio SMS",
                recipient_phone=recipient_phone
            )
        except Exception as err:
            logger.warning(f"[Twilio Fallback Error] {str(err)}. Falling back to console log.")

    # Fallback log for demonstration / unconfigured Twilio credentials
    print(f"\n=======================================================")
    print(f"[ALERT TRIGGER DEMO LOG - MOCK SMS]")
    print(f"To: {recipient_phone}")
    print(f"Message: {sms_message}")
    print(f"=======================================================\n")

    return AlertTriggerResponse(
        status="simulated",
        ward_id=target_ward.ward_id,
        ward_name=target_ward.ward_name,
        risk_band=request.risk_band,
        wbgt=wbgt,
        message=sms_message,
        provider="Console Log (Fallback)",
        recipient_phone=recipient_phone
    )


@app.post("/api/calculate", response_model=CalculationResponse, tags=["Calculations"])
def calculate_custom_risk(input_data: CalculationInput):
    """
    Calculate custom thermal stress indices, vulnerability score, and health advisory
    given arbitrary meteorological and demographic inputs.
    """
    risk_info = calculate_risk_score(
        temp_c=input_data.temp_c,
        rh=input_data.humidity_pct,
        elderly_pct=input_data.elderly_pct or 10.0,
        outdoor_worker_pct=input_data.outdoor_worker_pct or 30.0,
        green_cover_pct=input_data.green_cover_pct or 5.0,
        wind_speed_kmh=input_data.wind_speed_kmh or 10.0,
        solar_radiation_wm2=input_data.solar_radiation_wm2 or 850.0
    )

    return CalculationResponse(
        heat_index_c=risk_info["heat_index_c"],
        wbgt_c=risk_info["wbgt_c"],
        solar_adjusted_wbgt=risk_info["solar_adjusted_wbgt"],
        apparent_temperature_c=risk_info["apparent_temperature_c"],
        human_thermal_stress_index=risk_info["human_thermal_stress_index"],
        vulnerability_score=risk_info["demographic_component"],
        heatwave_category=f"{risk_info['risk_band']} Heatwave Risk",
        risk_level=f"{risk_info['risk_band']} Band ({risk_info['risk_score']})",
        health_advisory=risk_info["advisories"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
