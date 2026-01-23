import argparse
import logging
import sys

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def check_raw_data(input_path: str) -> None:
    try:
        df = pd.read_parquet(input_path)
    except Exception as e:
        logging.error(f"Failed to read file: {e}")
        sys.exit(1)

    logging.info("--- Data Quality Report ---")
    logging.info(f"Total rows: {len(df)}")

    # 1. Check for Missing Values
    if df.isnull().any().any():
        logging.warning("Found missing values!")
        logging.warning(df.isnull().sum())
    else:
        logging.info("No missing values found.")

    # 2. Check Time Coverage
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    start = df["timestamp"].min()
    end = df["timestamp"].max()
    logging.info(f"Time coverage: from {start} to {end}")

    # 3. Smart Negative Value Check
    # Temperature can be negative, but PM2.5 and Humidity cannot.

    # Check PM2.5 and Humidity (must be >= 0)
    physical_params = ["pm25", "humidity"]
    neg_physical = df[(df["parameter"].isin(physical_params)) & (df["value"] < 0)]

    # Check Temperature (let's say we only alert if it's below -50C, which is likely a sensor error)
    unrealistic_temp = df[(df["parameter"] == "temp") & (df["value"] < -50)]

    if not neg_physical.empty:
        logging.error(
            "CRITICAL ERROR: Found negative values in physical parameters (PM2.5/Humidity)!"
        )
        logging.error(neg_physical)
        sys.exit(1)

    if not unrealistic_temp.empty:
        logging.error(
            "CRITICAL ERROR: Found unrealistic temperature values (below -50C)!"
        )
        logging.error(unrealistic_temp)
        sys.exit(1)

    logging.info("Quality check passed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=str)
    args = parser.parse_args()
    check_raw_data(args.input)
