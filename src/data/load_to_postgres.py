import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_to_postgres(parquet_path: str) -> None:
    """
    Load measurements from Parquet file into PostgreSQL database.

    Args:
        parquet_path: Path to the Parquet file to load

    Raises:
        ValueError: If PostgreSQL credentials are missing
        FileNotFoundError: If Parquet file does not exist
    """

    # Load and check credentials
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    if not pg_user or not pg_password:
        raise ValueError("POSTGRES_USER or POSTGRES_PASSWORD not found in .env")

    # Read data
    if not Path(parquet_path).exists():
        raise FileNotFoundError("Parquet file not found. Run 'just fetch' first.")

    df = pd.read_parquet(parquet_path)
    if df.empty:
        logging.warning("No data to load")
        return

    # Connect to database
    with psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="smogwatch",
        user=pg_user,
        password=pg_password,
    ) as conn:
        # Insert data to table measurements
        with conn.cursor() as cursor:
            rows = (
                df[["timestamp", "value", "parameter", "station"]]
                .to_records(index=False)
                .tolist()
            )

            execute_values(
                cursor,
                """
                INSERT INTO measurements (timestamp, value, parameter, station)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                rows,
            )

            inserted = cursor.rowcount
            skipped = len(rows) - inserted

        conn.commit()
        logging.info(f"Inserted: {inserted} | Skipped: {skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=str, default="data/clean/katowice_kossutha_clean.parquet"
    )
    args = parser.parse_args()
    load_to_postgres(args.input)
