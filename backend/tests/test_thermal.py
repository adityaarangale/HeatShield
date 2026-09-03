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
    assert first_ward.solar_radiation_wm2 >= 600.0
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
