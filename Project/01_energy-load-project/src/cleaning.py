from pathlib import Path
import re
import sqlite3
import pandas as pd


project_root = Path.cwd().parent
DATA_DIR = project_root / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = project_root / "db" / "energy_load.db"



def parse_time_interval(value: str):
    parts = [p.strip() for p in str(value).split(" - ")]
    if len(parts) != 2:
        return pd.Series([pd.NaT, pd.NaT])
    start_date = pd.to_datetime(parts[0], format="%d/%m/%Y", errors="coerce")
    end_date = pd.to_datetime(parts[1], format="%d/%m/%Y", errors="coerce")
    return pd.Series([start_date, end_date])


def parse_week_number(value: str):
    match = re.search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return pd.NA


def parse_area(value: str):
    text = str(value).strip()
    match = re.match(r"^(.*)\s+\(([^)]+)\)$", text)
    if match:
        return pd.Series([match.group(1).strip(), match.group(2).strip()])
    return pd.Series([text, pd.NA])


def clean_single_file(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    expected_columns = [
        "Time Interval",
        "Week",
        "Area",
        "Forecast min [MW]",
        "Actual min [MW]",
        "Actual max [MW]",
        "Forecast max [MW]",
    ]

    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in {file_path.name}: {missing_cols}")

    df = df[expected_columns].copy()

    df[["interval_start", "interval_end"]] = df["Time Interval"].apply(parse_time_interval)
    df["week_number"] = df["Week"].apply(parse_week_number)
    df[["area_name", "area_code"]] = df["Area"].apply(parse_area)

    rename_map = {
        "Week": "week_label",
        "Forecast min [MW]": "forecast_min_mw",
        "Actual min [MW]": "actual_min_mw",
        "Actual max [MW]": "actual_max_mw",
        "Forecast max [MW]": "forecast_max_mw",
    }

    df = df.rename(columns=rename_map)

    numeric_cols = [
        "forecast_min_mw",
        "actual_min_mw",
        "actual_max_mw",
        "forecast_max_mw",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["data_year"] = df["interval_end"].dt.year
    df["source_file"] = file_path.name
    df["created_at"] = pd.Timestamp.now().floor("s")

    final_cols = [
        "source_file",
        "interval_start",
        "interval_end",
        "week_label",
        "week_number",
        "area_name",
        "area_code",
        "forecast_min_mw",
        "actual_min_mw",
        "actual_max_mw",
        "forecast_max_mw",
        "data_year",
        "created_at",
    ]

    return df[final_cols]


def combine_all_files(raw_dir: Path) -> pd.DataFrame:
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in data/raw")

    frames = []
    for file_path in csv_files:
        cleaned = clean_single_file(file_path)
        frames.append(cleaned)

    combined_df = pd.concat(frames, ignore_index=True)
    return combined_df


def run_quality_checks(df: pd.DataFrame) -> dict:
    report = {}

    report["row_count"] = len(df)
    report["missing_values"] = df.isna().sum().to_dict()
    report["duplicate_rows"] = int(df.duplicated().sum())

    if {"area_code", "week_number", "data_year"}.issubset(df.columns):
        report["duplicate_business_keys"] = int(
            df.duplicated(subset=["area_code", "week_number", "data_year"]).sum()
        )
    else:
        report["duplicate_business_keys"] = None

    report["invalid_week_numbers"] = int(
        df["week_number"].isna().sum() + (~df["week_number"].between(1, 53, inclusive="both")).sum()
    )

    report["invalid_date_ranges"] = int(
        (df["interval_start"].isna() | df["interval_end"].isna()).sum()
    )

    report["invalid_min_max_actual"] = int(
        (df["actual_min_mw"] > df["actual_max_mw"]).fillna(False).sum()
    )

    report["invalid_min_max_forecast"] = int(
        (df["forecast_min_mw"] > df["forecast_max_mw"]).fillna(False).sum()
    )

    return report


def save_outputs(df: pd.DataFrame):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    processed_csv_path = PROCESSED_DIR / "weekly_load_cleaned.csv"
    df.to_csv(processed_csv_path, index=False)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("weekly_load", conn, if_exists="replace", index=False)
    conn.close()

    return processed_csv_path, DB_PATH


def main():
    combined_df = combine_all_files(RAW_DIR)
    quality_report = run_quality_checks(combined_df)
    processed_csv_path, db_path = save_outputs(combined_df)

    print("Data cleaning completed.")
    print(f"Processed CSV: {processed_csv_path}")
    print(f"SQLite DB: {db_path}")
    print("Quality report:")
    for key, value in quality_report.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
