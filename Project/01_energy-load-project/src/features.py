from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

project_root = Path.cwd().parent
DATA_DIR = project_root / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = project_root / "db" / "energy_load.db"


def load_data(db_path=DB_PATH, table_name="weekly_load"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    df["interval_start"] = pd.to_datetime(df["interval_start"])
    df["interval_end"] = pd.to_datetime(df["interval_end"])
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df


def add_basic_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["year"] = df["interval_end"].dt.year
    df["month"] = df["interval_end"].dt.month
    df["quarter"] = df["interval_end"].dt.quarter
    df["week_of_year"] = df["week_number"]

    return df


def add_season_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def map_season(month):
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    df["season"] = df["month"].apply(map_season)

    df["is_winter"] = (df["season"] == "winter").astype(int)
    df["is_spring"] = (df["season"] == "spring").astype(int)
    df["is_summer"] = (df["season"] == "summer").astype(int)
    df["is_autumn"] = (df["season"] == "autumn").astype(int)

    df["week_sin"] = np.sin(2 * np.pi * df["week_number"] / 52)
    df["week_cos"] = np.cos(2 * np.pi * df["week_number"] / 52)

    return df


def add_lag_features(df: pd.DataFrame, group_col="area_code", lags=[1, 2, 3, 4]) -> pd.DataFrame:
    df = df.copy()

    target_cols = [
        "actual_min_mw",
        "actual_max_mw",
        "forecast_min_mw",
        "forecast_max_mw",
    ]

    df = df.sort_values([group_col, "interval_end"])

    for col in target_cols:
        for lag in lags:
            df[f"{col}_lag_{lag}"] = df.groupby(group_col)[col].shift(lag)

    return df


def add_rolling_features(df: pd.DataFrame, group_col="area_code", windows=[3, 4, 8]) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values([group_col, "interval_end"])

    base_cols = [
        "actual_min_mw",
        "actual_max_mw",
        "forecast_min_mw",
        "forecast_max_mw",
    ]

    for col in base_cols:
        for window in windows:
            df[f"{col}_roll_mean_{window}"] = (
                df.groupby(group_col)[col]
                .transform(lambda x: x.shift(1).rolling(window=window).mean())
            )

            df[f"{col}_roll_std_{window}"] = (
                df.groupby(group_col)[col]
                .transform(lambda x: x.shift(1).rolling(window=window).std())
            )

    return df


def add_difference_features(df: pd.DataFrame, group_col="area_code") -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values([group_col, "interval_end"])

    base_cols = [
        "actual_min_mw",
        "actual_max_mw",
        "forecast_min_mw",
        "forecast_max_mw",
    ]

    for col in base_cols:
        df[f"{col}_diff_1"] = df.groupby(group_col)[col].diff(1)
        df[f"{col}_pct_change_1"] = df.groupby(group_col)[col].pct_change(1)

    df["range_actual_mw"] = df["actual_max_mw"] - df["actual_min_mw"]
    df["range_forecast_mw"] = df["forecast_max_mw"] - df["forecast_min_mw"]

    df["range_actual_diff_1"] = df.groupby(group_col)["range_actual_mw"].diff(1)
    df["range_forecast_diff_1"] = df.groupby(group_col)["range_forecast_mw"].diff(1)

    return df


def add_error_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["error_min_mw"] = df["actual_min_mw"] - df["forecast_min_mw"]
    df["error_max_mw"] = df["actual_max_mw"] - df["forecast_max_mw"]

    df["abs_error_min_mw"] = df["error_min_mw"].abs()
    df["abs_error_max_mw"] = df["error_max_mw"].abs()

    return df


def build_feature_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = add_basic_time_features(df)
    df = add_season_features(df)
    df = add_error_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_difference_features(df)

    df = df.sort_values(["area_code", "interval_end"]).reset_index(drop=True)

    return df


def save_feature_dataset(df: pd.DataFrame,
                         csv_path=PROCESSED_DIR / "weekly_load_features.csv",
                         db_path=DB_PATH,
                         table_name="weekly_load_features"):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)

    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    return csv_path, db_path, table_name


def main():
    df = load_data()
    feature_df = build_feature_dataset(df)
    csv_path, db_path, table_name = save_feature_dataset(feature_df)

    print("Feature engineering completed.")
    print(f"CSV saved to: {csv_path}")
    print(f"SQLite table saved to: {table_name} in {db_path}")


if __name__ == "__main__":
    main()
