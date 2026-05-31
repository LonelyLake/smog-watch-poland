import logging
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

df = pd.read_parquet("data/raw/katowice_kossutha.parquet")

inserted = 0
skipped = 0

with psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="smogwatch",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
) as conn:
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO measurements (timestamp, value, parameter, station)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (row["timestamp"], row["value"], row["parameter"], row["station"]),
            )

            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
    conn.commit()

logging.info(f"Inserted: {inserted} | Skipped: {skipped}")
