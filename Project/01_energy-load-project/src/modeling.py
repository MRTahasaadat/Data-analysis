from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from statsmodels.tsa.arima.model import ARIMA

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from src.metrics import evaluate_regression



project_root = Path.cwd().parent
DATA_DIR = project_root / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = project_root / "db" / "energy_load.db"




def load_feature_data(db_path=DB_PATH, table_name="weekly_load_features"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    df["interval_end"] = pd.to_datetime(df["interval_end"])
    return df


def prepare_model_data(df, target_col="actual_max_mw", drop_cols=None):
    df = df.copy()
    df = df.sort_values(["area_code", "interval_end"]).reset_index(drop=True)

    if drop_cols is None:
        drop_cols = [
            "id", "source_file", "interval_start", "interval_end", "week_label",
            "area_name", "season", "created_at"
        ]

    y = df[target_col]

    X = df.drop(columns=[target_col] + [c for c in drop_cols if c in df.columns], errors="ignore")

    non_numeric_cols = X.select_dtypes(include=["object"]).columns.tolist()
    X = X.drop(columns=non_numeric_cols, errors="ignore")

    return X, y, df


def time_train_test_split(df, test_size=0.2):
    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    return train_df, test_df


def baseline_forecast(train_df, test_df, target_col="actual_max_mw"):
    last_value = train_df[target_col].iloc[-1]
    preds = np.repeat(last_value, len(test_df))
    return preds


def train_random_forest(X_train, y_train):
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        ))
    ])
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train):
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed.")

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        ))
    ])
    model.fit(X_train, y_train)
    return model


def train_arima(train_series, order=(2, 1, 2)):
    model = ARIMA(train_series, order=order)
    fitted = model.fit()
    return fitted


def compare_models(df, target_col="actual_max_mw", test_size=0.2):
    df = df.sort_values("interval_end").reset_index(drop=True)

    train_df, test_df = time_train_test_split(df, test_size=test_size)

    X, y, full_df = prepare_model_data(df, target_col=target_col)
    X_train, X_test = X.iloc[:len(train_df)], X.iloc[len(train_df):]
    y_train, y_test = y.iloc[:len(train_df)], y.iloc[len(train_df):]

    results = []

    # Baseline
    baseline_preds = baseline_forecast(train_df, test_df, target_col=target_col)
    baseline_metrics = evaluate_regression(y_test, baseline_preds)
    baseline_metrics["Model"] = "Baseline (Last Value)"
    results.append(baseline_metrics)

    # Random Forest
    rf_model = train_random_forest(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_metrics = evaluate_regression(y_test, rf_preds)
    rf_metrics["Model"] = "Random Forest"
    results.append(rf_metrics)

    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_model = train_xgboost(X_train, y_train)
        xgb_preds = xgb_model.predict(X_test)
        xgb_metrics = evaluate_regression(y_test, xgb_preds)
        xgb_metrics["Model"] = "XGBoost"
        results.append(xgb_metrics)

    # ARIMA
    arima_model = train_arima(train_df[target_col], order=(2, 1, 2))
    arima_preds = arima_model.forecast(steps=len(test_df))
    arima_metrics = evaluate_regression(y_test, arima_preds)
    arima_metrics["Model"] = "ARIMA(2,1,2)"
    results.append(arima_metrics)

    results_df = pd.DataFrame(results)[["Model", "MAE", "RMSE", "MAPE", "R2"]]
    return results_df
