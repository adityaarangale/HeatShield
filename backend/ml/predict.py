import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from ml.preprocessing import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_apparent_temperature,
    calculate_solar_adjusted_wbgt
)

MODEL_CACHE = {}

def get_model_and_metadata():
    """
    Load saved model artifact and metadata config once (singleton pattern).
    """
    if "model" in MODEL_CACHE and "metadata" in MODEL_CACHE:
        return MODEL_CACHE["model"], MODEL_CACHE["metadata"]

    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "model", "heat_risk_rf_v1.joblib")
    meta_path = os.path.join(base_dir, "model", "model_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(
            f"ML model artifact or metadata file not found at {model_path}. "
            "Please run 'python ml/train_model.py' to train and save the model first."
        )

    model = joblib.load(model_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    MODEL_CACHE["model"] = model
    MODEL_CACHE["metadata"] = metadata
    return model, metadata

def predict_single_risk(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float = 10.0,
    solar_radiation_wm2: float = 850.0,
    surface_pressure_hpa: float = 1013.25,
    precipitation_mm: float = 0.0,
    hour: Optional[int] = None,
    month: Optional[int] = None
) -> Dict[str, Any]:
    """
    Perform ML inference using the trained RandomForestRegressor model.
    Builds the required feature vector on live input parameters.
    """
    model, metadata = get_model_and_metadata()

    now = datetime.now()
    if hour is None:
        hour = now.hour
    if month is None:
        month = now.month
    day_of_year = now.timetuple().tm_yday

    # Engineer scientific features
    hi = calculate_heat_index(temp_c, humidity_pct)
    wbgt = calculate_wbgt(temp_c, humidity_pct)
    at = calculate_apparent_temperature(temp_c, humidity_pct, wind_speed_kmh)
    solar_wbgt = calculate_solar_adjusted_wbgt(wbgt, solar_radiation_wm2)

    # Feature vector matching FEATURE_COLUMNS order exactly
    feature_dict = {
        "temp_c": [temp_c],
        "humidity_pct": [humidity_pct],
        "wind_speed_kmh": [wind_speed_kmh],
        "surface_pressure_hpa": [surface_pressure_hpa],
        "solar_radiation_wm2": [solar_radiation_wm2],
        "precipitation_mm": [precipitation_mm],
        "wbgt_c": [wbgt],
        "heat_index_c": [hi],
        "apparent_temp_c": [at],
        "solar_adj_wbgt_c": [solar_wbgt],
        "hour": [hour],
        "month": [month],
        "day_of_year": [day_of_year],
        "temp_roll3": [temp_c],
        "temp_roll6": [temp_c],
        "humidity_roll3": [humidity_pct]
    }
    input_df = pd.DataFrame(feature_dict)

    pred_score = float(np.round(model.predict(input_df)[0], 1))
    pred_score = max(0.0, min(100.0, pred_score))

    # Determine risk category
    if pred_score >= 70.0:
        category = "Extreme"
    elif pred_score >= 50.0:
        category = "Danger"
    elif pred_score >= 30.0:
        category = "Caution"
    else:
        category = "Safe"

    return {
        "predicted_risk_score": pred_score,
        "predicted_risk_category": category,
        "model_version": metadata.get("model_version", "rf-v1"),
        "prediction_time": datetime.now().isoformat(),
        "prediction_type": "ML (Random Forest Regressor Inference)",
        "features_input": {
            "temp_c": temp_c,
            "humidity_pct": humidity_pct,
            "wbgt_c": wbgt,
            "heat_index_c": hi,
            "solar_adjusted_wbgt_c": solar_wbgt,
            "apparent_temperature_c": at
        }
    }
