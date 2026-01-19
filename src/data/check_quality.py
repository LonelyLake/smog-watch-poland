import argparse
from pathlib import Path

import pandas as pd


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check raw data quality")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/katowice.parquet",
        help="Input parquet path",
    )
    return parser.parse_args()


def check_raw_data() -> None:
    args = _parse_args()
    file_path = Path(args.input)

    if not file_path.exists():
        print(f"❌ File {file_path} not found!")
        return

    # Load data
    df = pd.read_parquet(file_path)

    print("--- Data Quality Report ---")

    # 1. Check structure
    print(f"✅ Total rows: {len(df)}")
    print(f"✅ Columns: {list(df.columns)}")

    # 2. Check for missing values
    nulls = df.isnull().sum().sum()
    if nulls == 0:
        print("✅ No missing values found.")
    else:
        print(f"⚠️ Found {nulls} missing values.")

    # 3. Check time range
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    start_date = df["timestamp"].min()
    end_date = df["timestamp"].max()
    print(f"✅ Time range: from {start_date} to {end_date}")

    # 4. Check values (e.g., PM2.5 cannot be negative)
    neg_values = len(df[df["value"] < 0])
    if neg_values == 0:
        print("✅ No negative values (Physically consistent).")
    else:
        print(f"❌ Found {neg_values} negative values!")

    # Look at distribution by parameter
    print("\nCounts by parameter:")
    print(df["parameter"].value_counts())


if __name__ == "__main__":
    check_raw_data()
