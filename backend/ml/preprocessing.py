import math
import numpy as np

def calculate_heat_index(temp_c: float, rh: float) -> float:
    """
    Calculate NWS Heat Index (°C) using the Rothfusz regression equation.
    """
    T = (temp_c * 9.0 / 5.0) + 32.0
    R = rh

    hi_f = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

    if hi_f >= 80.0:
        hi_f = (-42.379 +
                (2.04901523 * T) +
                (10.14333127 * R) -
                (0.22475541 * T * R) -
                (6.83783e-3 * T * T) -
                (5.481717e-2 * R * R) +
                (1.22874e-3 * T * T * R) +
                (8.5282e-4 * T * R * R) -
                (1.99e-6 * T * T * R * R))

        if R < 13.0 and 80.0 <= T <= 112.0:
            adj = ((13.0 - R) / 4.0) * math.sqrt((17.0 - abs(T - 95.0)) / 17.0)
            hi_f -= adj
        elif R > 85.0 and 80.0 <= T <= 87.0:
            adj = ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0)
            hi_f += adj

    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return float(np.round(hi_c, 2))


def calculate_wbgt(temp_c: float, rh: float) -> float:
    """
    Calculate Wet-Bulb Globe Temperature (WBGT) in °C using Australian BOM formula.
    """
    e = (rh / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    wbgt = 0.567 * temp_c + 0.393 * e + 3.94
    return float(np.round(wbgt, 2))


def calculate_apparent_temperature(temp_c: float, rh: float, wind_speed_kmh: float = 10.0) -> float:
    """
    Calculate Apparent Temperature (AT) in °C using Australian BOM formula.
    """
    wind_ms = wind_speed_kmh / 3.6
    e = (rh / 100.0) * 6.105 * math.exp((17.27 * temp_c) / (237.7 + temp_c))
    at = temp_c + 0.33 * e - 0.70 * wind_ms - 4.00
    return float(np.round(at, 2))


def calculate_solar_adjusted_wbgt(wbgt_c: float, solar_radiation_wm2: float = 850.0) -> float:
    """
    Calculate solar radiation adjusted WBGT in °C.
    """
    adjusted = wbgt_c + (0.0037 * solar_radiation_wm2)
    return float(np.round(adjusted, 2))


def calculate_target_risk_score(
    temp_c: float,
    rh: float,
    wind_speed_kmh: float = 10.0,
    solar_radiation_wm2: float = 850.0,
    elderly_pct: float = 11.0,
    outdoor_worker_pct: float = 35.0,
    green_cover_pct: float = 10.0
) -> float:
    """
    Derives scientific Heatwave Risk Score (0-100) target combining:
      1) Blended HTSI (60% weight): 0.5 * solar_adj_wbgt + 0.3 * apparent_temp + 0.2 * heat_index
         normalized from [25°C, 50°C] to [0, 100], clamped.
      2) Demographic component (40% weight): 0.4 * elderly_pct + 0.4 * outdoor_worker_pct + 0.2 * (100 - green_cover)
    """
    hi = calculate_heat_index(temp_c, rh)
    wbgt = calculate_wbgt(temp_c, rh)
    at = calculate_apparent_temperature(temp_c, rh, wind_speed_kmh)
    solar_wbgt = calculate_solar_adjusted_wbgt(wbgt, solar_radiation_wm2)

    raw_htsi = (0.5 * solar_wbgt) + (0.3 * at) + (0.2 * hi)
    norm_htsi = max(0.0, min(100.0, ((raw_htsi - 25.0) / (50.0 - 25.0)) * 100.0))

    demo_component = (0.4 * elderly_pct) + (0.4 * outdoor_worker_pct) + (0.2 * (100.0 - green_cover_pct))
    demo_component = max(0.0, min(100.0, demo_component))

    risk_score = (0.60 * norm_htsi) + (0.40 * demo_component)
    return float(np.round(max(0.0, min(100.0, risk_score)), 1))
