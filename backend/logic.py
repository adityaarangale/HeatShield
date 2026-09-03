import json
import math
import os
from typing import List, Dict, Any
from models import (
    Ward,
    CalculationInput,
    CalculationResponse,
    WardResponse,
    WardRiskResponse,
    ForecastRiskTrendItem
)


def calculate_heat_index(temp_c: float, rh: float) -> float:
    """
    Calculate NWS Heat Index (°C) using the Rothfusz regression equation.
    Converts C to F for calculation and back to C.
    """
    T = (temp_c * 9.0 / 5.0) + 32.0
    R = rh

    # Simple formula threshold check
    hi_f = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

    if hi_f >= 80.0:
        # Full Rothfusz regression
        hi_f = (-42.379 +
                (2.04901523 * T) +
                (10.14333127 * R) -
                (0.22475541 * T * R) -
                (6.83783e-3 * T * T) -
                (5.481717e-2 * R * R) +
                (1.22874e-3 * T * T * R) +
                (8.5282e-4 * T * R * R) -
                (1.99e-6 * T * T * R * R))

        # Adjustments for low and high humidity
        if R < 13.0 and 80.0 <= T <= 112.0:
            adj = ((13.0 - R) / 4.0) * math.sqrt((17.0 - abs(T - 95.0)) / 17.0)
            hi_f -= adj
        elif R > 85.0 and 80.0 <= T <= 87.0:
            adj = ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0)
            hi_f += adj

    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(hi_c, 2)


def calculate_wbgt(temp_c: float, rh: float) -> float:
    """
    Calculate Wet-Bulb Globe Temperature (WBGT) in °C using the Australian Bureau of Meteorology (BOM)
    simplified outdoor formula:
    WBGT = 0.567 * T + 0.393 * e + 3.94
    where e = (RH / 100) * 6.105 * exp(17.27 * T / (237.7 + T))
    """
    e = (rh / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    wbgt = 0.567 * temp_c + 0.393 * e + 3.94
    return round(wbgt, 2)


def calculate_apparent_temperature(temp_c: float, rh: float, wind_speed_kmh: float) -> float:
    """
    Calculate Apparent Temperature (AT) in °C using Australian BOM formula:
    Convert wind to m/s: wind_ms = wind_speed_kmh / 3.6
    Compute vapor pressure e = (rh/100) * 6.105 * exp(17.27 * temp_c / (237.7 + temp_c))
    AT = temp_c + 0.33 * e - 0.70 * wind_ms - 4.00
    Rounds to 2 decimals.
    """
    wind_ms = wind_speed_kmh / 3.6
    e = (rh / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    at = temp_c + 0.33 * e - 0.70 * wind_ms - 4.00
    return round(at, 2)


def calculate_solar_adjusted_wbgt(wbgt_c: float, solar_radiation_wm2: float) -> float:
    """
    Calculate solar radiation adjusted WBGT in °C:
    adjusted = wbgt_c + (0.0037 * solar_radiation_wm2)
    Rounds to 2 decimals.
    """
    adjusted = wbgt_c + (0.0037 * solar_radiation_wm2)
    return round(adjusted, 2)


def calculate_risk_score(
    temp_c: float,
    rh: float,
    elderly_pct: float,
    outdoor_worker_pct: float,
    green_cover_pct: float,
    wind_speed_kmh: float = 10.0,
    solar_radiation_wm2: float = 850.0
) -> Dict[str, Any]:
    """
    Calculates overall Heatwave Risk Score (0-100) combining:
      1) Normalized Blended Human Thermal Stress Index (60% weight):
         raw_htsi = 0.5 * solar_adjusted_wbgt + 0.3 * apparent_temperature + 0.2 * heat_index_c
         normalized from [25, 50] to [0, 100], clamped.
      2) Demographic vulnerability component (40% weight):
         0.4 * elderly_pct + 0.4 * outdoor_worker_pct + 0.2 * (100 - green_cover_pct)
    Classifies the final score into Safe / Caution / Danger / Extreme risk bands.
    """
    # Base metrics
    heat_index_c = calculate_heat_index(temp_c, rh)
    wbgt_c = calculate_wbgt(temp_c, rh)
    apparent_temp_c = calculate_apparent_temperature(temp_c, rh, wind_speed_kmh)
    solar_adj_wbgt = calculate_solar_adjusted_wbgt(wbgt_c, solar_radiation_wm2)

    # 1. Blended Human Thermal Stress Index (HTSI)
    raw_htsi = (0.5 * solar_adj_wbgt) + (0.3 * apparent_temp_c) + (0.2 * heat_index_c)
    raw_htsi = round(raw_htsi, 2)

    # Normalize HTSI range [25°C, 50°C] linearly to [0, 100]
    raw_htsi_norm = ((raw_htsi - 25.0) / (50.0 - 25.0)) * 100.0
    heat_component = max(0.0, min(100.0, raw_htsi_norm))

    # 2. Demographic Vulnerability Component (0 - 100)
    demo_component = (0.4 * elderly_pct) + (0.4 * outdoor_worker_pct) + (0.2 * (100.0 - green_cover_pct))
    demo_component = max(0.0, min(100.0, demo_component))

    # 3. Total Weighted Risk Score (0 - 100)
    total_score = (0.60 * heat_component) + (0.40 * demo_component)
    total_score = round(max(0.0, min(100.0, total_score)), 1)

    # 4. Classification into Bands: Safe / Caution / Danger / Extreme
    if total_score >= 70.0:
        band = "Extreme"
        advisories = [
            "Mandatory suspension of outdoor manual labor during peak sunlight hours (11am-4pm).",
            "Emergency activation of municipal hydration stations and cooling hubs.",
            "Immediate alert to hospital emergency departments for heat stroke cases."
        ]
    elif total_score >= 50.0:
        band = "Danger"
        advisories = [
            "High risk of heat exhaustion and cramps; stay indoors or in shade.",
            "Ensure regular intake of water and electrolyte solutions.",
            "Frequent rest breaks required for outdoor workers."
        ]
    elif total_score >= 30.0:
        band = "Caution"
        advisories = [
            "Moderate heat stress; avoid prolonged strenuous activities outdoors.",
            "Wear light, loose cotton clothing and protect heads from direct sun."
        ]
    else:
        band = "Safe"
        advisories = [
            "Normal weather conditions.",
            "Maintain baseline hydration throughout daytime hours."
        ]

    return {
        "risk_score": total_score,
        "risk_band": band,
        "apparent_temperature_c": apparent_temp_c,
        "solar_adjusted_wbgt": solar_adj_wbgt,
        "human_thermal_stress_index": raw_htsi,
        "heat_index_c": heat_index_c,
        "wbgt_c": wbgt_c,
        "heat_component": round(heat_component, 1),
        "demographic_component": round(demo_component, 1),
        "advisories": advisories
    }


def calculate_vulnerability_score(elderly_pct: float, outdoor_worker_pct: float, green_cover_pct: float) -> float:
    """
    Helper vulnerability score formula.
    """
    demo = (0.4 * elderly_pct) + (0.4 * outdoor_worker_pct) + (0.2 * (100.0 - green_cover_pct))
    return round(max(0.0, min(100.0, demo)), 1)


def classify_heatwave_risk(temp_c: float, wbgt_c: float, vuln_score: float) -> Dict[str, Any]:
    """
    Helper for category mapping.
    """
    if temp_c >= 45.0 or wbgt_c >= 33.0 or (temp_c >= 44.0 and vuln_score > 65.0):
        return {
            "category": "Severe Heatwave Warning",
            "risk_level": "Red Alert",
            "advisories": [
                "Mandatory suspension of heavy outdoor physical work during peak hours.",
                "Activate emergency cooling shelters and hydration vans."
            ]
        }
    elif temp_c >= 43.0 or wbgt_c >= 30.0 or (temp_c >= 42.0 and vuln_score > 50.0):
        return {
            "category": "Heatwave Warning",
            "risk_level": "Orange Alert",
            "advisories": [
                "Avoid direct sunlight exposure between 12:00 PM and 3:30 PM.",
                "Distribute ORS and drinking water at labor hubs."
            ]
        }
    elif temp_c >= 40.0 or wbgt_c >= 28.0:
        return {
            "category": "Heatwave Watch",
            "risk_level": "Yellow Alert",
            "advisories": ["Stay hydrated; drink water regularly."]
        }
    else:
        return {
            "category": "Normal Weather",
            "risk_level": "Green Status",
            "advisories": ["Standard weather conditions."]
        }


def load_wards_dataset() -> List[Ward]:
    """
    Load ward dataset from data/wards.json file.
    """
    json_path = os.path.join(os.path.dirname(__file__), "data", "wards.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Ward dataset not found at {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [Ward(**item) for item in data]


def evaluate_ward_detail(ward: Ward, include_trend: bool = False) -> WardResponse:
    """
    Evaluate full heat risk metrics for a single ward.
    If include_trend is True, computes 3-5 day forecasted risk trend using forecast_3day data.
    """
    risk_info = calculate_risk_score(
        temp_c=ward.current_temp_c,
        rh=ward.humidity_pct,
        elderly_pct=ward.elderly_pct,
        outdoor_worker_pct=ward.outdoor_worker_pct,
        green_cover_pct=ward.green_cover_pct,
        wind_speed_kmh=ward.wind_speed_kmh,
        solar_radiation_wm2=ward.solar_radiation_wm2
    )

    forecast_trend = None
    if include_trend:
        forecast_trend = []
        for fc in ward.forecast_3day:
            fc_solar = getattr(fc, "solar_radiation_wm2", 850.0)
            f_risk = calculate_risk_score(
                temp_c=fc.temp_c,
                rh=fc.humidity_pct,
                elderly_pct=ward.elderly_pct,
                outdoor_worker_pct=ward.outdoor_worker_pct,
                green_cover_pct=ward.green_cover_pct,
                wind_speed_kmh=ward.wind_speed_kmh,
                solar_radiation_wm2=fc_solar
            )
            forecast_trend.append(ForecastRiskTrendItem(
                day=fc.day,
                temp_c=fc.temp_c,
                humidity_pct=fc.humidity_pct,
                heat_index=f_risk["heat_index_c"],
                wbgt=f_risk["wbgt_c"],
                solar_adjusted_wbgt=f_risk["solar_adjusted_wbgt"],
                apparent_temperature_c=f_risk["apparent_temperature_c"],
                human_thermal_stress_index=f_risk["human_thermal_stress_index"],
                risk_score=f_risk["risk_score"],
                risk_band=f_risk["risk_band"]
            ))

    return WardResponse(
        ward_id=ward.ward_id,
        ward_name=ward.ward_name,
        lat=ward.lat,
        lon=ward.lon,
        population=ward.population,
        elderly_pct=ward.elderly_pct,
        outdoor_worker_pct=ward.outdoor_worker_pct,
        green_cover_pct=ward.green_cover_pct,
        current_temp_c=ward.current_temp_c,
        humidity_pct=ward.humidity_pct,
        wind_speed_kmh=ward.wind_speed_kmh,
        solar_radiation_wm2=ward.solar_radiation_wm2,
        heat_index=risk_info["heat_index_c"],
        wbgt=risk_info["wbgt_c"],
        solar_adjusted_wbgt=risk_info["solar_adjusted_wbgt"],
        apparent_temperature_c=risk_info["apparent_temperature_c"],
        human_thermal_stress_index=risk_info["human_thermal_stress_index"],
        risk_score=risk_info["risk_score"],
        risk_band=risk_info["risk_band"],
        forecast_3day=ward.forecast_3day,
        forecast_risk_trend=forecast_trend,
        advisories=risk_info["advisories"]
    )


# Backward compatibility alias
evaluate_ward_risk = evaluate_ward_detail
