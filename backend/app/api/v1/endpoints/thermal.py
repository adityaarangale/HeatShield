from fastapi import APIRouter, HTTPException, status
from app.schemas.thermal import WeatherInput, ThermalIndexResponse, RegionAlertRequest, RegionAlertResponse
from app.services.thermal_index import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_utci,
    calculate_humidex,
    classify_thermal_stress,
    classify_heatwave_alert,
)

router = APIRouter()


@router.post("/calculate", response_model=ThermalIndexResponse, status_code=status.HTTP_200_OK)
def calculate_thermal_indices(data: WeatherInput):
    """
    Calculate Human Thermal Stress Indices (Heat Index, WBGT, UTCI, Humidex)
    and output early warning alerts & health recommendations.
    """
    try:
        hi = calculate_heat_index(data.temperature, data.relative_humidity)
        wbgt = calculate_wbgt(
            temp_c=data.temperature,
            rh=data.relative_humidity,
            wind_speed=data.wind_speed or 2.0,
            solar_rad=data.solar_radiation or 800.0
        )
        utci = calculate_utci(
            temp_c=data.temperature,
            rh=data.relative_humidity,
            wind_speed=data.wind_speed or 2.0,
            solar_rad=data.solar_radiation or 800.0
        )
        humidex = calculate_humidex(data.temperature, data.relative_humidity)

        stress_info = classify_thermal_stress(wbgt, hi)
        heatwave_alert = classify_heatwave_alert(data.temperature)

        return ThermalIndexResponse(
            temperature=data.temperature,
            relative_humidity=data.relative_humidity,
            heat_index=hi,
            wbgt=wbgt,
            utci=utci,
            humidex=humidex,
            stress_category=stress_info["category"],
            heatwave_alert=heatwave_alert,
            precautions=stress_info["precautions"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing thermal index calculation: {str(e)}"
        )


@router.post("/heatwave-alert", response_model=RegionAlertResponse, status_code=status.HTTP_200_OK)
def evaluate_regional_heatwave(request: RegionAlertRequest):
    """
    Evaluate multiple Automatic Weather Stations across a geographical region
    and issue consolidated heatwave warning alert level.
    """
    station_results = []
    heatwave_count = 0
    severe_heatwave_count = 0
    highest_wbgt = 0.0

    for station in request.stations:
        res = calculate_thermal_indices(station)
        station_results.append(res)

        if "Severe Heatwave" in res.heatwave_alert:
            severe_heatwave_count += 1
        elif "Heatwave" in res.heatwave_alert:
            heatwave_count += 1

        if res.wbgt > highest_wbgt:
            highest_wbgt = res.wbgt

    if severe_heatwave_count > 0:
        overall_alert = "RED ALERT - SEVERE HEATWAVE EMERGENCY"
    elif heatwave_count > 0:
        overall_alert = "ORANGE ALERT - HEATWAVE WARNING"
    elif highest_wbgt >= 31.0:
        overall_alert = "YELLOW ALERT - HIGH THERMAL STRESS WATCH"
    else:
        overall_alert = "GREEN STATUS - NORMAL METEOROLOGICAL CONDITIONS"

    return RegionAlertResponse(
        region_name=request.region_name,
        total_stations=len(request.stations),
        heatwave_count=heatwave_count,
        severe_heatwave_count=severe_heatwave_count,
        highest_wbgt=highest_wbgt,
        overall_alert_level=overall_alert,
        station_results=station_results
    )
