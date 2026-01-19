import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Raw data quality validation")
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/katowice.parquet",
        help="Path to the input parquet file",
    )
    parser.add_argument(
        "--output-clean",
        type=str,
        default="data/processed/katowice_clean.parquet",
        help="Path to save cleaned data",
    )
    return parser.parse_args()


def check_raw_data() -> int:
    """Check data for critical issues.
    Returns 0 if data is fine, 1 if critical issues are found.
    """
    args = _parse_args()
    file_path = Path(args.input)

    if not file_path.exists():
        logger.error(f"File {file_path} not found!")
        return 1

    # Load data
    df = pd.read_parquet(file_path)
    critical_error = False

    logger.info("--- Data Quality Report ---")

    # 1. Check structure
    logger.info(f"Total rows: {len(df)}")

    # 2. Check for missing values
    nulls = df.isnull().sum().sum()
    if nulls > 0:
        logger.warning(f"Found {nulls} missing values.")
        # Usually missing sensor data is normal and can be imputed
    else:
        logger.info("No missing values found.")

    # 3. Time range
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    start_date, end_date = df["timestamp"].min(), df["timestamp"].max()
    logger.info(f"Time coverage: from {start_date} to {end_date}")

    # 4. Physical consistency (PM2.5 and others cannot be < 0)
    neg_values = df[df["value"] < 0]
    if not neg_values.empty:
        logger.error(f"CRITICAL ERROR: Found {len(neg_values)} negative values!")
        logger.error(neg_values.head())
        critical_error = True
    else:
        logger.info("No negative values found (physically consistent).")

    # 5. Save cleaned data (remove noise if not critical)
    if not critical_error:
        df_clean = df[df["value"] >= 0].dropna()
        output_path = Path(args.output_clean)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_parquet(output_path, index=False)
        logger.info(f"Cleaned data saved to {output_path}")
        return 0
    else:
        logger.error("Validation failed. Please fix the data source.")
        return 1


if __name__ == "__main__":
    # Exit code is important for automation (just/ci-cd)
    sys.exit(check_raw_data())
