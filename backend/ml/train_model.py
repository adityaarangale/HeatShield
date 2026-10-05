import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from ml.preprocessing import (
    calculate_heat_index,
    calculate_wbgt,
    calculate_apparent_temperature,
    calculate_solar_adjusted_wbgt,
    calculate_target_risk_score
)
from ml.fetch_data import fetch_and_save_historical_data

FEATURE_COLUMNS = [
    "temp_c",
    "humidity_pct",
    "wind_speed_kmh",
    "surface_pressure_hpa",
    "solar_radiation_wm2",
    "precipitation_mm",
    "wbgt_c",
    "heat_index_c",
    "apparent_temp_c",
    "solar_adj_wbgt_c",
    "hour",
    "month",
    "day_of_year",
    "temp_roll3",
    "temp_roll6",
    "humidity_roll3"
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build time-series and scientific biometeorological features from raw weather observations.
    Calculates WBGT, Heat Index, Apparent Temp, rolling averages, and hour/month temporal components.
    """
    df = df.copy()
    df["dt"] = pd.to_datetime(df["time"])
    df["hour"] = df["dt"].dt.hour
    df["month"] = df["dt"].dt.month
    df["day_of_year"] = df["dt"].dt.dayofyear

    # Vectorized / apply scientific calculations
    df["heat_index_c"] = [calculate_heat_index(t, r) for t, r in zip(df["temp_c"], df["humidity_pct"])]
    df["wbgt_c"] = [calculate_wbgt(t, r) for t, r in zip(df["temp_c"], df["humidity_pct"])]
    df["apparent_temp_c"] = [calculate_apparent_temperature(t, r, w) for t, r, w in zip(df["temp_c"], df["humidity_pct"], df["wind_speed_kmh"])]
    df["solar_adj_wbgt_c"] = [calculate_solar_adjusted_wbgt(w, s) for w, s in zip(df["wbgt_c"], df["solar_radiation_wm2"])]

    # Time-series rolling features (avoiding leakage by using closed='left' or past values)
    df["temp_roll3"] = df["temp_c"].shift(1).rolling(window=3, min_periods=1).mean()
    df["temp_roll6"] = df["temp_c"].shift(1).rolling(window=6, min_periods=1).mean()
    df["humidity_roll3"] = df["humidity_pct"].shift(1).rolling(window=3, min_periods=1).mean()

    # Fill initial rolling NAs
    df["temp_roll3"] = df["temp_roll3"].fillna(df["temp_c"])
    df["temp_roll6"] = df["temp_roll6"].fillna(df["temp_c"])
    df["humidity_roll3"] = df["humidity_roll3"].fillna(df["humidity_pct"])

    # Target variable generation (Transparent scientific derived heat risk target)
    df["target_risk_score"] = [
        calculate_target_risk_score(
            temp_c=t,
            rh=r,
            wind_speed_kmh=w,
            solar_radiation_wm2=s
        ) for t, r, w, s in zip(df["temp_c"], df["humidity_pct"], df["wind_speed_kmh"], df["solar_radiation_wm2"])
    ]

    return df

def train_heatshield_model():
    """
    Train RandomForestRegressor on historical weather dataset using a time-aware train/test split.
    Evaluates MAE, RMSE, R² and saves model artifact + metadata config.
    """
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "data", "historical_weather_chandrapur.csv")
    model_dir = os.path.join(base_dir, "model")
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(data_path):
        fetch_and_save_historical_data(output_path=data_path)

    df_raw = pd.read_csv(data_path)
    df = engineer_features(df_raw)

    # Time-aware split: Train on 80% earlier date data, Test on latest 20%
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target_risk_score"]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target_risk_score"]

    print(f"Training dataset: {len(X_train)} samples (Train), {len(X_test)} samples (Test)")

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = float(np.round(mean_absolute_error(y_test, y_pred), 3))
    rmse = float(np.round(root_mean_squared_error(y_test, y_pred), 3))
    r2 = float(np.round(r2_score(y_test, y_pred), 4))

    print("==================================================")
    print("MODEL EVALUATION METRICS (RandomForestRegressor v1)")
    print("==================================================")
    print(f"• Mean Absolute Error (MAE) : {mae}")
    print(f"• Root Mean Sq Error (RMSE) : {rmse}")
    print(f"• Coefficient of Det (R²)   : {r2}")
    print("==================================================")

    # Save model binary
    model_file = os.path.join(model_dir, "heat_risk_rf_v1.joblib")
    joblib.dump(model, model_file)

    # Save metadata JSON
    metadata = {
        "model_version": "rf-v1",
        "algorithm": "RandomForestRegressor",
        "training_period": "2023-01-01 to 2024-12-31",
        "dataset_records": len(df),
        "train_records": len(X_train),
        "test_records": len(X_test),
        "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features_used": FEATURE_COLUMNS,
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        },
        "target_definition": "Scientifically derived Human Thermal Stress & Demographic Vulnerability Index (0-100)"
    }
    meta_file = os.path.join(model_dir, "model_metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Successfully saved model artifact to {model_file}")
    print(f"Successfully saved model metadata to {meta_file}")
    return metadata

if __name__ == "__main__":
    train_heatshield_model()
