import argparse
import logging
import os
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def validate_and_clean_data(input_path: str, output_path: str) -> None:
    try:
        df = pd.read_parquet(input_path)
    except Exception as e:
        logging.error(f"CRITICAL: Failed to read file: {e}")
        sys.exit(1)

    initial_rows = len(df)
    logging.info("--- Data Quality Check ---")
    logging.info(f"Loaded {initial_rows} rows from Bronze.")

    # 1. Convert timestamp to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # 2. Check schema
    if df["timestamp"].isnull().any():
        logging.error("CRITICAL: Found unparseable timestamps! Pipeline stopped.")
        sys.exit(1)

    # 3. Data cleaning
    physical_params = ["pm25", "pm10", "humidity"]

    invalid_physical = (df["parameter"].isin(physical_params)) & (df["value"] < 0)
    invalid_temp = (df["parameter"] == "temp") & (
        (df["value"] < -50) | (df["value"] > 60)
    )

    mask_to_keep = ~(invalid_physical | invalid_temp)
    df_clean = df[mask_to_keep]

    removed_rows = initial_rows - len(df_clean)
    if removed_rows > 0:
        logging.warning(
            f"Filtered out {removed_rows} anomalous rows (negative PM or crazy temp)."
        )

    # 4. Staging
    if df_clean.empty:
        logging.error("CRITICAL: Dataframe is empty after cleaning. Nothing to load!")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df_clean.to_parquet(output_path, index=False, compression="snappy")
    logging.info(f"Successfully saved {len(df_clean)} cleaned rows to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=str, default="data/raw/katowice_kossutha.parquet"
    )
    parser.add_argument(
        "--output", type=str, default="data/clean/katowice_kossutha_clean.parquet"
    )
    args = parser.parse_args()

    validate_and_clean_data(args.input, args.output)
