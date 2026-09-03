import math
from typing import Dict, Any, List
from app.core.config import settings


def calculate_vapor_pressure(temp_c: float, rh: float) -> float:
    """
    Calculate actual vapor pressure (e) in hPa (mbar) using Tetens equation.
    """
    sat_vp = 6.1078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    actual_vp = sat_vp * (rh / 100.0)
    return actual_vp


def calculate_heat_index(temp_c: float, rh: float) -> float:
    """
    Calculate NWS Heat Index (°C) using Rothfusz regression equation.
    Converted to Celsius.
    """
    # Convert C to F
    T = (temp_c * 9.0 / 5.0) + 32.0
    R = rh

    # Simple formula check first
    hi_f = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

    if hi_f >= 80.0:
        # Rothfusz regression formula
        hi_f = (-42.379 +
                (2.04901523 * T) +
                (10.14333127 * R) -
                (0.22475541 * T * R) -
                (6.83783e-3 * T * T) -
                (5.481717e-2 * R * R) +
                (1.22874e-3 * T * T * R) +
                (8.5282e-4 * T * R * R) -
                (1.99e-6 * T * T * R * R))

        # Adjustment for low humidity
        if R < 13.0 and 80.0 <= T <= 112.0:
            adj = ((13.0 - R) / 4.0) * math.sqrt((17.0 - abs(T - 95.0)) / 17.0)
            hi_f -= adj
        # Adjustment for high humidity
        elif R > 85.0 and 80.0 <= T <= 87.0:
            adj = ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0)
            hi_f += adj

    # Convert F back to C
    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(hi_c, 2)


def calculate_wbgt(temp_c: float, rh: float, wind_speed: float = 2.0, solar_rad: float = 800.0) -> float:
    """
    Estimate Wet Bulb Globe Temperature (WBGT) in °C outdoors.
    Uses Australian Bureau of Meteorology (BOM) & Liljegren outdoor model approximation:
    WBGT = 0.567 * T + 0.393 * e + 3.94
    Adjusted slightly for wind speed and solar radiation damping.
    """
    e = calculate_vapor_pressure(temp_c, rh)
    
    # Base BOM empirical WBGT approximation
    wbgt_base = 0.567 * temp_c + 0.393 * e + 3.94

    # Radiation & Wind adjustment factor
    rad_effect = (solar_rad / 1000.0) * 2.5
    wind_cooling = math.sqrt(max(wind_speed, 0.1)) * 1.2
    
    wbgt = wbgt_base + rad_effect - wind_cooling
    return round(wbgt, 2)


def calculate_utci(temp_c: float, rh: float, wind_speed: float = 2.0, solar_rad: float = 800.0) -> float:
    """
    Calculate Universal Thermal Climate Index (UTCI) in °C.
    Polynomial approximation based on thermal sensation.
    """
    e = calculate_vapor_pressure(temp_c, rh)
    # UTCI offset derived from temperature, vapor pressure, wind speed, solar load
    wind_effect = math.pow(max(wind_speed, 0.5), 0.16)
    delta_utci = (temp_c - 20.0) * 0.1 + (e - 10.0) * 0.25 - (wind_effect - 1.0) * 3.0 + (solar_rad / 1000.0) * 3.5
    
    utci = temp_c + delta_utci
    return round(utci, 2)


def calculate_humidex(temp_c: float, rh: float) -> float:
    """
    Calculate Canadian Humidex (°C).
    Humidex = T + (5/9) * (e - 10)
    """
    e = calculate_vapor_pressure(temp_c, rh)
    humidex = temp_c + (5.0 / 9.0) * (e - 10.0)
    return round(humidex, 2)


def classify_thermal_stress(wbgt: float, hi: float) -> Dict[str, Any]:
    """
    Classify human thermal stress level and generate safety precautions.
    """
    if wbgt >= settings.WBGT_DANGER or hi >= 54.0:
        category = "EXTREME DANGER / VERY SEVERE STRESS"
        precautions = [
            "Avoid direct exposure to sunlight and all strenuous outdoor activity.",
            "High risk of heat stroke, heat exhaustion, and cardiovascular collapse.",
            "Ensure access to active cooling centers and emergency oral rehydration solutions.",
            "Mandatory rest breaks in shaded/air-conditioned zones for outdoor workers."
        ]
    elif wbgt >= settings.WBGT_EXTREME_CAUTION or hi >= 41.0:
        category = "DANGER / SEVERE STRESS"
        precautions = [
            "Limit physical activity, especially between 11:00 AM and 4:00 PM.",
            "Stay hydrated; drink water/electrolyte fluids regularly even if not thirsty.",
            "Wear light, light-colored, loose-fitting cotton clothing and protective hats/sunscreen.",
            "Check on vulnerable individuals (elderly, children, chronic illness patients)."
        ]
    elif wbgt >= settings.WBGT_CAUTION or hi >= 32.0:
        category = "EXTREME CAUTION / MODERATE STRESS"
        precautions = [
            "Take frequent rest periods in shade during prolonged outdoor exposure.",
            "Maintain continuous fluid intake.",
            "Monitor for signs of heat rash, cramps, or mild heat dizziness."
        ]
    else:
        category = "NORMAL / LOW STRESS"
        precautions = [
            "Normal thermal stress levels.",
            "Standard hydrational practices recommended during routine outdoor activities."
        ]

    return {
        "category": category,
        "precautions": precautions
    }


def classify_heatwave_alert(temp_c: float) -> str:
    """
    Categorize heatwave alert state according to Indian Meteorological Department (IMD) / MoES standards.
    """
    if temp_c >= settings.SEVERE_HEATWAVE_TEMP_THRESHOLD:
        return "Severe Heatwave Warning (Red Alert)"
    elif temp_c >= settings.HEATWAVE_TEMP_THRESHOLD:
        return "Heatwave Warning (Orange Alert)"
    elif temp_c >= 37.0:
        return "Heatwave Watch (Yellow Alert)"
    else:
        return "Normal Weather (Green Status)"
