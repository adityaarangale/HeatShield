import pytest
import math
from fastapi.testclient import TestClient
from main import app
from logic import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_apparent_temperature,
    calculate_solar_adjusted_wbgt,
    calculate_risk_score,
    load_wards_dataset
)

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"



def test_calculate_apparent_temperature():
    temp_c = 42.0
    rh = 35.0
    wind_kmh = 10.0
    
    wind_ms = wind_kmh / 3.6
    e = (rh / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    expected_at = round(temp_c + 0.33 * e - 0.70 * wind_ms - 4.00, 2)
    
    at = calculate_apparent_temperature(temp_c, rh, wind_kmh)
    assert at == expected_at


def test_calculate_solar_adjusted_wbgt():
    wbgt_c = 32.5
    solar_wm2 = 850.0
    expected_adj = round(32.5 + (0.0037 * 850.0), 2)
    
    adj_wbgt = calculate_solar_adjusted_wbgt(wbgt_c, solar_wm2)
    assert adj_wbgt == expected_adj


def test_calculate_risk_score_htsi_blend():
    temp_c = 45.0
    rh = 35.0
    elderly = 12.0
    outdoor = 40.0
    green = 5.0
    wind = 12.0
    solar = 880.0

    res = calculate_risk_score(
        temp_c, rh, elderly, outdoor, green, wind, solar
    )
    assert "apparent_temperature_c" in res
    assert "solar_adjusted_wbgt" in res
    assert "human_thermal_stress_index" in res
    assert "risk_score" in res
    assert "risk_band" in res
    assert res["risk_band"] in ["Safe", "Caution", "Danger", "Extreme"]


def test_load_wards_dataset_5day_forecast():
    wards = load_wards_dataset()
    assert len(wards) == 8
    first_ward = wards[0]
    assert hasattr(first_ward, "solar_radiation_wm2")
    assert first_ward.solar_radiation_wm2 >= 0.0
    assert len(first_ward.forecast_3day) == 5


def test_get_ward_by_id_5day_risk_trend():
    response = client.get("/wards/CHA_001")
    assert response.status_code == 200
    data = response.json()
    assert data["ward_id"] == "CHA_001"
    assert "solar_radiation_wm2" in data
    assert "apparent_temperature_c" in data
    assert "human_thermal_stress_index" in data
    assert "solar_adjusted_wbgt" in data
    assert len(data["forecast_risk_trend"]) == 5
    
    item = data["forecast_risk_trend"][0]
    assert "apparent_temperature_c" in item
    assert "solar_adjusted_wbgt" in item
    assert "human_thermal_stress_index" in item
    assert "ml_predicted_risk_score" in item


def test_ml_predict_risk_endpoint():
    payload = {
        "temp_c": 44.5,
        "humidity_pct": 38.0,
        "wind_speed_kmh": 12.0,
        "solar_radiation_wm2": 890.0,
        "surface_pressure_hpa": 1008.5,
        "precipitation_mm": 0.0
    }
    response = client.post("/api/predict-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_risk_score" in data
    assert "predicted_risk_category" in data
    assert data["model_version"] == "rf-v1"
    assert 0.0 <= data["predicted_risk_score"] <= 100.0


def test_ml_metadata_endpoint():
    response = client.get("/api/ml-metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "loaded"
    assert data["algorithm"] == "RandomForestRegressor"
    assert data["dataset_records"] == 17544
    assert "metrics" in data
    assert "mae" in data["metrics"]
    assert "rmse" in data["metrics"]
    assert "r2" in data["metrics"]


# ==================== AUTHENTICATION & RBAC TESTS ====================

def test_citizen_signup_login_flow():
    import uuid
    email = f"citizen_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "CitizenPass123!"
    
    # 1. Signup
    signup_res = client.post("/api/auth/citizen/signup", json={
        "name": "Test Citizen",
        "email": email,
        "password": pwd
    })
    assert signup_res.status_code == 200
    signup_data = signup_res.json()
    assert "access_token" in signup_data
    assert signup_data["user"]["role"] == "CITIZEN"
    token = signup_data["access_token"]
    
    # 2. Access Citizen Dashboard
    dash_res = client.get("/api/citizen/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    assert dash_res.json()["role"] == "CITIZEN"

    # 3. Reject Citizen accessing Authority Dashboard
    auth_dash_res = client.get("/api/authority/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert auth_dash_res.status_code == 403

    # 4. Duplicate Email Signup fails
    dup_res = client.post("/api/auth/citizen/signup", json={
        "name": "Duplicate User",
        "email": email,
        "password": pwd
    })
    assert dup_res.status_code == 400

    # 5. Wrong Login Password fails
    wrong_login = client.post("/api/auth/citizen/login", json={
        "email": email,
        "password": "WrongPassword!"
    })
    assert wrong_login.status_code == 401

    # 6. Correct Login succeeds
    login_res = client.post("/api/auth/citizen/login", json={
        "email": email,
        "password": pwd
    })
    assert login_res.status_code == 200
    assert login_res.json()["user"]["role"] == "CITIZEN"


def test_authority_login_flow():
    # Test default pre-seeded Authority Account
    login_res = client.post("/api/auth/authority/login", json={
        "email": "authority@heatshield.gov.in",
        "password": "HeatShield2026!"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["user"]["role"] == "AUTHORITY"
    token = data["access_token"]

    # Authority can access authority dashboard
    auth_dash = client.get("/api/authority/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert auth_dash.status_code == 200
    assert auth_dash.json()["role"] == "AUTHORITY"


def test_authority_register_with_secret_code():
    import uuid
    email = f"officer_{uuid.uuid4().hex[:8]}@heatshield.gov.in"
    reg_res = client.post("/api/auth/authority/register", json={
        "name": "New Officer",
        "email": email,
        "password": "OfficerPass2026!",
        "registration_code": "HEATSHIELD_AUTH_SECRET_2026"
    })
    assert reg_res.status_code == 200
    assert reg_res.json()["user"]["role"] == "AUTHORITY"

    # Wrong secret code fails
    fail_res = client.post("/api/auth/authority/register", json={
        "name": "Intruder Officer",
        "email": f"hacker_{uuid.uuid4().hex[:8]}@heatshield.gov.in",
        "password": "HackerPass2026!",
        "registration_code": "WRONG_SECRET_CODE"
    })
    assert fail_res.status_code == 403


def test_unauthorized_direct_access_rejected():
    res = client.get("/api/authority/dashboard")
    assert res.status_code == 401


def test_get_live_weather_cached_endpoint():
    res1 = client.get("/api/weather/live?lat=19.9615&lon=79.2961")
    assert res1.status_code == 200
    data1 = res1.json()
    assert "status" in data1
    assert "cached" in data1

    # Second call should hit the 10-minute server cache
    res2 = client.get("/api/weather/live?lat=19.9615&lon=79.2961")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2.get("cached") is True


def test_phone_auth_signup_login_me_flow():
    import random
    unique_phone = "".join([str(random.randint(0, 9)) for _ in range(10)])


    # Validation failure: phone not 10 digits
    bad_phone_res = client.post("/api/auth/signup", json={
        "name": "Test Citizen",
        "phone": "123",
        "password": "Password123!",
        "role": "citizen"
    })
    assert bad_phone_res.status_code == 422
    assert "phone" in bad_phone_res.json()["detail"].lower()

    # 1. Signup citizen
    signup_res = client.post("/api/auth/signup", json={
        "name": "Test Citizen",
        "phone": unique_phone,
        "password": "Password123!",
        "role": "citizen",
        "ward_or_department": "Ward 5"
    })
    assert signup_res.status_code == 201
    s_data = signup_res.json()
    assert "id" in s_data
    assert "password_hash" not in s_data
    assert s_data["name"] == "Test Citizen"
    assert s_data["phone"] == unique_phone
    assert s_data["role"] == "citizen"

    # Duplicate phone signup fails with 409
    dup_res = client.post("/api/auth/signup", json={
        "name": "Duplicate Citizen",
        "phone": unique_phone,
        "password": "Password123!",
        "role": "citizen"
    })
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"] == "An account with this phone number already exists."

    # 2. Invalid Login fails with 401 "Invalid phone number or password"
    invalid_login = client.post("/api/auth/login", json={
        "phone": unique_phone,
        "password": "WrongPassword123!"
    })
    assert invalid_login.status_code == 401
    assert invalid_login.json()["detail"] == "Invalid phone number or password"

    # Valid Login
    login_res = client.post("/api/auth/login", json={
        "phone": unique_phone,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    l_data = login_res.json()
    assert "access_token" in l_data
    assert l_data["role"] == "citizen"
    assert l_data["name"] == "Test Citizen"
    token = l_data["access_token"]

    # 3. GET /api/auth/me with invalid token fails with 401
    invalid_me = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert invalid_me.status_code == 401

    # GET /api/auth/me with valid token succeeds
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["phone"] == unique_phone
    assert me_data["name"] == "Test Citizen"
    assert me_data["role"] == "citizen"


def test_admin_accounts_rbac_and_crud():
    import random
    phone1 = "".join([str(random.randint(0, 9)) for _ in range(10)])
    phone2 = "".join([str(random.randint(0, 9)) for _ in range(10)])

    # Create citizen account
    cit_res = client.post("/api/auth/signup", json={
        "name": "Citizen User",
        "phone": phone1,
        "password": "Password123!",
        "role": "citizen"
    })
    assert cit_res.status_code == 201
    cit_token = cit_res.json()["access_token"]
    cit_id = cit_res.json()["id"]

    # Create authority account
    auth_res = client.post("/api/auth/signup", json={
        "name": "Authority Officer",
        "phone": phone2,
        "password": "Password123!",
        "role": "authority",
        "ward_or_department": "Disaster Cell"
    })
    assert auth_res.status_code == 201
    auth_token = auth_res.json()["access_token"]

    # 1. Citizen cannot access /api/admin/accounts (403)
    forbidden_res = client.get("/api/admin/accounts", headers={"Authorization": f"Bearer {cit_token}"})
    assert forbidden_res.status_code == 403

    # 2. Authority can list all accounts
    list_res = client.get("/api/admin/accounts", headers={"Authorization": f"Bearer {auth_token}"})
    assert list_res.status_code == 200
    accounts = list_res.json()
    assert isinstance(accounts, list)
    assert len(accounts) > 0
    # Ensure password_hash is excluded
    for acc in accounts:
        assert "password_hash" not in acc

    # 3. Query with ?role=citizen filter
    cit_list_res = client.get("/api/admin/accounts?role=citizen", headers={"Authorization": f"Bearer {auth_token}"})
    assert cit_list_res.status_code == 200
    cit_accounts = cit_list_res.json()
    for acc in cit_accounts:
        assert acc["role"] == "citizen"

    # 4. Authority deletes citizen account
    del_res = client.delete(f"/api/admin/accounts/{cit_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # 5. Deleting non-existent account returns 404
    del_404 = client.delete("/api/admin/accounts/999999", headers={"Authorization": f"Bearer {auth_token}"})
    assert del_404.status_code == 404






