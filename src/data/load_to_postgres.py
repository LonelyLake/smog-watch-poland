import logging
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

df = pd.read_parquet("data/raw/katowice_kossutha.parquet")

with psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="smogwatch",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
) as conn:
    with conn.cursor() as cursor:
        rows = [
            (row["timestamp"], row["value"], row["parameter"], row["station"])
            for _, row in df.iterrows()
        ]

        execute_values(
            cursor,
            """
            INSERT INTO measurements (timestamp, value, parameter, station)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            rows,
        )

    conn.commit()

    inserted = cursor.rowcount
    skipped = len(rows) - inserted
    logging.info(f"Inserted: {inserted} | Skipped: {skipped}")
