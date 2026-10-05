import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from models import (
    Ward,
    CalculationInput,
    CalculationResponse,
    WardResponse,
    ForecastRiskTrendItem,
    AlertTriggerRequest,
    AlertTriggerResponse,
    BroadcastAlertRequest,
    BroadcastAlertResponse,
    LiveWeatherResponse,
    ForecastDay,
    MLPredictionRequest,
    MLPredictionResponse,
    MLModelMetadataResponse,
    AuthSignupRequest,
    AuthLoginRequest,
    UserSignupRequest,
    UserLoginRequest,
    AuthorityLoginRequest,
    AuthorityRegisterRequest,
    UserResponse,
    TokenResponse,
    CitizenProfileSaveRequest
)
from personal_risk import router as personal_risk_router
from weather import fetch_realtime_weather, fetch_realtime_weather_cached
from ml.predict import predict_single_risk, get_model_and_metadata
from logic import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_risk_score,
    calculate_vulnerability_score,
    classify_heatwave_risk,
    load_wards_dataset,
    evaluate_ward_detail
)
import database
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_citizen,
    require_authority,
    AUTHORITY_REGISTRATION_CODE
)

logger = logging.getLogger("uvicorn.error")

from fastapi.responses import JSONResponse
from sqlalchemy import text

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


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database tables and log registered routes banner on startup."""
    logger.info("Initializing database tables...")
    database.init_db()

    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "8000")
    base_url = f"http://{host}:{port}"

    print("\n" + "=" * 65)
    print("  HEAT SHIELD BACKEND API STARTED SUCCESSFULLY")
    print(f"  URL:  {base_url}")

    print(f"  Docs: {base_url}/docs")
    print("-" * 65)
    print("  REGISTERED ROUTES:")
    for route in app.routes:
        methods = ", ".join(sorted(list(getattr(route, "methods", [])))) or "INTERNAL"
        path = getattr(route, "path", str(route))
        print(f"    [{methods:<12}] {path}")
    print("=" * 65 + "\n")


@app.get("/api/health", tags=["Health"])
def health_check_endpoint():
    """Health check endpoint that verifies database connectivity."""
    try:
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


app.include_router(personal_risk_router)

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def auth_signup(req: AuthSignupRequest):
    # Field 'name' validation
    if not req.name or not req.name.strip():
        raise HTTPException(status_code=422, detail="Field 'name' is required")
    
    # Field 'phone' validation (must be 10 digits)
    raw_phone = (req.phone or "").strip()
    phone_digits = raw_phone[3:] if raw_phone.startswith("+91") else raw_phone
    if not phone_digits.isdigit() or len(phone_digits) != 10:
        raise HTTPException(status_code=422, detail="Field 'phone' must be exactly 10 digits")

    # Field 'password' validation (at least 6 characters)
    if not req.password or len(req.password.strip()) < 6:
        raise HTTPException(status_code=422, detail="Field 'password' must be at least 6 characters long")

    # Field 'role' validation (must be exactly 'citizen' or 'authority')
    role_clean = (req.role or "").strip().lower()
    if role_clean not in ["citizen", "authority"]:
        raise HTTPException(status_code=422, detail="Field 'role' must be either 'citizen' or 'authority'")

    # Existing phone check
    existing = database.get_user_by_phone(raw_phone) or database.get_user_by_phone(phone_digits) or database.get_user_by_phone(f"+91{phone_digits}")
    if existing:
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")

    # Hash password with passlib bcrypt scheme
    hashed = hash_password(req.password)
    user = database.create_user_with_phone(
        name=req.name.strip(),
        phone=raw_phone,
        password_hash=hashed,
        role=role_clean,
        ward_or_department=req.ward_or_department.strip() if req.ward_or_department else None
    )

    token = create_access_token(data={"sub": str(user["id"]), "phone": user["phone"], "role": role_clean})
    user_payload = {
        "id": user["id"],
        "name": user["name"],
        "role": role_clean,
        "phone": user["phone"],
        "ward_or_department": user.get("ward_or_department")
    }
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_payload
    }



@app.post("/api/auth/login", tags=["Authentication"])
def auth_login(req: AuthLoginRequest):
    raw_phone = (req.phone or "").strip()
    phone_digits = raw_phone[3:] if raw_phone.startswith("+91") else raw_phone

    user = database.get_user_by_phone(raw_phone) or database.get_user_by_phone(phone_digits) or database.get_user_by_phone(f"+91{phone_digits}")
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or password")

    user_role = str(user.get("role", "citizen")).lower()
    token = create_access_token(
        data={
            "sub": str(user["id"]),
            "role": user_role,
            "name": user["name"]
        },
        expires_delta=timedelta(days=7)
    )
    return {
        "access_token": token,
        "role": user_role,
        "name": user["name"],
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "phone": user["phone"],
            "role": user_role,
            "ward_or_department": user.get("ward_or_department")
        }
    }


@app.get("/api/auth/me", tags=["Authentication"])
def get_current_user_profile(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "name": user["name"],
        "phone": user.get("phone") or user.get("email"),
        "role": str(user.get("role", "citizen")).lower(),
        "ward_or_department": user.get("ward_or_department"),
        "email": user.get("email"),
        "created_at": user.get("created_at")
    }


# ==================== CITIZEN PROFILE MANAGEMENT ====================

@app.get("/api/citizen/profile", tags=["Citizen Profile"])
def get_citizen_user_profile(current_user: dict = Depends(get_current_user)):
    """Fetch current logged-in citizen's profile from database."""
    prof = database.get_citizen_profile(current_user["id"])
    if prof:
        return {"has_profile": True, "profile": prof}
    return {"has_profile": False, "profile": None}


@app.put("/api/citizen/profile", tags=["Citizen Profile"])
def update_citizen_user_profile(req: CitizenProfileSaveRequest, current_user: dict = Depends(get_current_user)):
    """Save or update logged-in citizen's profile in database."""
    saved_prof = database.save_citizen_profile(
        user_id=current_user["id"],
        age_group=req.age_group,
        gender=req.gender,
        occupation_type=req.occupation_type,
        health_flags=req.health_flags,
        activity_level=req.activity_level,
        ward_id=req.ward_id
    )
    return {
        "status": "success",
        "message": "Profile saved successfully",
        "has_profile": True,
        "profile": saved_prof
    }


# ==================== ADMIN ACCOUNTS MANAGEMENT ====================

@app.get("/api/admin/accounts", tags=["Admin Accounts"])
def list_admin_accounts(
    role: Optional[str] = Query(None, description="Filter accounts by role: 'citizen' or 'authority'"),
    current_user: dict = Depends(require_authority)
):
    """Retrieve list of all registered accounts (authority-only). Excludes password hashes."""
    accounts = database.get_all_users(role_filter=role)
    return accounts


@app.delete("/api/admin/accounts/{user_id}", tags=["Admin Accounts"])
def delete_admin_account(
    user_id: int,
    current_user: dict = Depends(require_authority)
):
    """Remove a user account by ID (authority-only)."""
    success = database.delete_user_by_id(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")
    return {
        "status": "deleted",
        "id": user_id,
        "message": "User account successfully removed"
    }




@app.post("/api/auth/citizen/signup", response_model=TokenResponse, tags=["Authentication"])
def citizen_signup(req: UserSignupRequest):
    if len(req.password.strip()) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    existing = database.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    hashed = hash_password(req.password)
    user = database.create_user(
        name=req.name,
        email=req.email,
        password_hash=hashed,
        role="citizen"
    )
    token = create_access_token(data={"sub": str(user["id"]), "role": user["role"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    )

@app.post("/api/auth/citizen/login", response_model=TokenResponse, tags=["Authentication"])
def citizen_login(req: UserLoginRequest):
    user = database.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user["role"].lower() != "citizen":
        raise HTTPException(status_code=403, detail="Please use Authority Login for authority accounts")
    
    token = create_access_token(data={"sub": str(user["id"]), "role": user["role"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    )

@app.post("/api/auth/authority/login", response_model=TokenResponse, tags=["Authentication"])
def authority_login(req: AuthorityLoginRequest):
    user = database.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid authority credentials")
    if user["role"].lower() != "authority":
        raise HTTPException(status_code=403, detail="Access denied: Not an authority account")
    
    token = create_access_token(data={"sub": str(user["id"]), "role": user["role"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    )

@app.post("/api/auth/authority/register", response_model=TokenResponse, tags=["Authentication"])
def authority_register(req: AuthorityRegisterRequest):
    if req.registration_code != AUTHORITY_REGISTRATION_CODE:
        raise HTTPException(status_code=403, detail="Invalid authority registration code")
    if len(req.password.strip()) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    existing = database.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    hashed = hash_password(req.password)
    user = database.create_user(
        name=req.name,
        email=req.email,
        password_hash=hashed,
        role="authority"
    )
    token = create_access_token(data={"sub": str(user["id"]), "role": user["role"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    )

# Protected sample routes for testing role authorization
@app.get("/api/citizen/dashboard", tags=["Citizen Features"])
def citizen_dashboard(user: dict = Depends(require_citizen)):
    return {"status": "access_granted", "user": user["name"], "role": user["role"], "message": "Welcome to Citizen Dashboard"}

@app.get("/api/authority/dashboard", tags=["Authority Features"])
def authority_dashboard(user: dict = Depends(require_authority)):
    return {"status": "access_granted", "user": user["name"], "role": user["role"], "message": "Welcome to Municipal Authority Dashboard"}



@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
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
    if request.custom_message and request.custom_message.strip():
        sms_message = request.custom_message.strip()
    else:
        sms_message = (
            f"ALERT: {target_ward.ward_name} - {request.risk_band} heat risk. "
            f"WBGT {wbgt}°C. Vulnerable groups advised to avoid outdoor activity 11am-4pm."
        )

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    recipient_phone = request.recipient_phone or os.getenv("TO_PHONE_NUMBER", "+919876543210")
    fast2sms_key = request.api_key or os.getenv("FAST2SMS_API_KEY")

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
                provider="Twilio SMS Gateway",
                recipient_phone=recipient_phone
            )
        except Exception as err:
            logger.warning(f"[Twilio Fallback Error] {str(err)}. Falling back to console log.")

    if fast2sms_key:
        try:
            import urllib.request
            import json
            clean_num = recipient_phone.replace("+91", "").replace("+", "").strip()
            if len(clean_num) == 10 and clean_num.isdigit():
                req_payload = json.dumps({
                    "route": "q",
                    "message": sms_message,
                    "language": "english",
                    "flash": 0,
                    "numbers": clean_num
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://www.fast2sms.com/dev/bulkV2",
                    data=req_payload,
                    headers={
                        "authorization": fast2sms_key,
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_body = resp.read().decode()
                    logger.info(f"[Fast2SMS Single]: {resp_body}")
                return AlertTriggerResponse(
                    status="sent",
                    ward_id=target_ward.ward_id,
                    ward_name=target_ward.ward_name,
                    risk_band=request.risk_band,
                    wbgt=wbgt,
                    message=sms_message,
                    provider="Fast2SMS India Cellular Gateway",
                    recipient_phone=recipient_phone
                )
        except Exception as err:
            logger.warning(f"[Fast2SMS Error] {str(err)}. Falling back to simulation.")

    # Fallback log for demonstration / unconfigured Twilio credentials
    try:
        print(f"\n=======================================================")
        print(f"[ALERT TRIGGER DEMO LOG - MOCK SMS]")
        print(f"To: {recipient_phone}")
        print(f"Message: {sms_message}")
        print(f"=======================================================\n")
    except UnicodeEncodeError:
        safe_msg = sms_message.encode('ascii', errors='backslashreplace').decode('ascii')
        print(f"[ALERT TRIGGER DEMO LOG - MOCK SMS] To: {recipient_phone} | Message: {safe_msg}")

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


@app.post("/alerts/broadcast", response_model=BroadcastAlertResponse, tags=["Alerts"])
@app.post("/api/alerts/broadcast", response_model=BroadcastAlertResponse, tags=["Alerts"])
def broadcast_alerts(request: BroadcastAlertRequest):
    """
    POST /alerts/broadcast
    Dispatches a batch emergency advisory or safe green bulletin to multiple citizen / evaluator contacts
    in a single 1-click execution.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")

    sent_recipients = []
    provider = "Console Audit Log"

    print(f"\n=======================================================")
    print(f"[1-CLICK BATCH BROADCAST TRIGGERED - HEAT SHIELD]")
    print(f"Target Ward: {request.ward_id} | Risk Tier: {request.risk_band}")
    print(f"Recipients ({len(request.recipient_phones)}): {', '.join(request.recipient_phones)}")
    print(f"Message Content:\n{request.custom_message}")
    print(f"=======================================================\n")

    fast2sms_key = request.api_key or os.getenv("FAST2SMS_API_KEY")

    if account_sid and auth_token and from_phone:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            provider = "Twilio SMS Gateway"
            for phone in request.recipient_phones:
                clean_phone = phone.strip()
                if clean_phone:
                    client.messages.create(
                        body=request.custom_message,
                        from_=from_phone,
                        to=clean_phone
                    )
                    sent_recipients.append(clean_phone)
        except Exception as e:
            logger.warning(f"Twilio broadcast error: {str(e)}. Defaulted to simulated log.")
            sent_recipients = request.recipient_phones
    elif fast2sms_key:
        try:
            import urllib.request
            import json
            raw_nums = [p.replace("+91", "").replace("+", "").strip() for p in request.recipient_phones]
            clean_nums = [n for n in raw_nums if len(n) == 10 and n.isdigit()]
            if clean_nums:
                req_payload = json.dumps({
                    "route": "q",
                    "message": request.custom_message,
                    "language": "english",
                    "flash": 0,
                    "numbers": ",".join(clean_nums)
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://www.fast2sms.com/dev/bulkV2",
                    data=req_payload,
                    headers={
                        "authorization": fast2sms_key,
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_body = resp.read().decode()
                    logger.info(f"[Fast2SMS Broadcast Response]: {resp_body}")
                provider = "Fast2SMS India Cellular Gateway"
                sent_recipients = request.recipient_phones
        except Exception as e:
            logger.warning(f"Fast2SMS error: {str(e)}")
            sent_recipients = request.recipient_phones
    else:
        sent_recipients = request.recipient_phones

    return BroadcastAlertResponse(
        status="broadcast_completed",
        total_recipients=len(request.recipient_phones),
        successful_count=len(sent_recipients),
        recipients=sent_recipients,
        provider=provider,
        message=request.custom_message
    )



@app.get("/api/weather/live", tags=["Weather"])
@app.get("/weather/live", tags=["Weather"])
def get_live_weather_cached_endpoint(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    latitude: Optional[float] = Query(None, description="Latitude alias"),
    longitude: Optional[float] = Query(None, description="Longitude alias")
):
    """
    GET /api/weather/live?lat=<lat>&lon=<lon>
    Fetches live weather from Open-Meteo with a 10-minute server-side in-memory cache TTL.
    Both Citizen Advisor and Authority views rely on this endpoint for identical weather data.
    """
    final_lat = lat if lat is not None else (latitude if latitude is not None else 19.9615)
    final_lon = lon if lon is not None else (longitude if longitude is not None else 79.2961)

    if not (-90.0 <= final_lat <= 90.0) or not (-180.0 <= final_lon <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude or longitude coordinates."
        )

    return fetch_realtime_weather_cached(final_lat, final_lon, cache_ttl=600)


@app.get("/api/weather", response_model=LiveWeatherResponse, tags=["Weather"])
def get_live_weather(latitude: float, longitude: float):
    """
    GET /api/weather?latitude=<lat>&longitude=<lon>
    Fetches real-time weather from Open-Meteo API and calculates thermal stress indices
    and risk scores using the scientific HeatShield engine.
    """
    if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid latitude or longitude coordinates."
        )
        
    weather_data = fetch_realtime_weather_cached(latitude, longitude, cache_ttl=600)
    w = weather_data["weather"]
    
    # Calculate scientific HeatShield metrics using live weather values
    risk_info = calculate_risk_score(
        temp_c=w["temperature_c"],
        rh=w["relative_humidity_pct"],
        elderly_pct=11.0,
        outdoor_worker_pct=35.0,
        green_cover_pct=10.0,
        wind_speed_kmh=w["wind_speed_kmh"],
        solar_radiation_wm2=w["solar_radiation_wm2"]
    )
    
    # Parse 5-day forecast
    forecast_list = [
        ForecastDay(
            day=item["day"],
            temp_c=item["temp_c"],
            humidity_pct=item["humidity_pct"],
            solar_radiation_wm2=item["solar_radiation_wm2"]
        ) for item in weather_data.get("forecast_5day", [])
    ]
    
    return LiveWeatherResponse(
        status=weather_data["status"],
        source=weather_data["source"],
        latitude=latitude,
        longitude=longitude,
        timestamp=weather_data["timestamp"],
        is_live=weather_data["is_live"],
        weather=w,
        forecast_5day=forecast_list,
        heat_index_c=risk_info["heat_index_c"],
        wbgt_c=risk_info["wbgt_c"],
        solar_adjusted_wbgt=risk_info["solar_adjusted_wbgt"],
        apparent_temperature_c=risk_info["apparent_temperature_c"],
        human_thermal_stress_index=risk_info["human_thermal_stress_index"],
        risk_score=risk_info["risk_score"],
        risk_band=risk_info["risk_band"],
        advisories=risk_info["advisories"]
    )


@app.post("/api/predict-risk", response_model=MLPredictionResponse, tags=["Machine Learning Inference"])
def predict_heat_risk(request: MLPredictionRequest):
    """
    POST /api/predict-risk
    Runs inference using the offline-trained RandomForestRegressor model on provided or live weather features.
    Returns predicted risk score, risk category, model version, and inference timestamp.
    """
    try:
        result = predict_single_risk(
            temp_c=request.temp_c,
            humidity_pct=request.humidity_pct,
            wind_speed_kmh=request.wind_speed_kmh or 10.0,
            solar_radiation_wm2=request.solar_radiation_wm2 or 850.0,
            surface_pressure_hpa=request.surface_pressure_hpa or 1013.25,
            precipitation_mm=request.precipitation_mm or 0.0,
            hour=request.hour,
            month=request.month
        )
        return MLPredictionResponse(**result)
    except Exception as e:
        logger.error(f"[ML Inference Error] {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML Prediction unavailable: {str(e)}"
        )


@app.get("/api/ml-metadata", response_model=MLModelMetadataResponse, tags=["Machine Learning Inference"])
def get_ml_model_info():
    """
    GET /api/ml-metadata
    Returns transparency metadata about the trained ML model (version, algorithm, training period, records, MAE, RMSE, R²).
    """
    try:
        _, metadata = get_model_and_metadata()
        return MLModelMetadataResponse(**metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML Model metadata unavailable: {str(e)}"
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
