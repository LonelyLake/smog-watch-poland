import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fetch_station(
    station_name: str = "kossutha", api_key: Optional[str] = None
) -> pd.DataFrame:
    all_measurements = []

    with open("config/stations.yaml", "r") as f:
        config = yaml.safe_load(f)

    sensors = config["stations"][station_name]["sensors"]

    headers = {"X-API-Key": api_key}

    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    params = {"datetime_from": start_date, "limit": 1000}

    for name, id in sensors.items():
        response = requests.get(
            f"https://api.openaq.org/v3/sensors/{id}/measurements",
            headers=headers,
            params=params,
        )

        data = response.json()

        measurements = []
        for result in data["results"]:
            measurements.append(
                {
                    "timestamp": result["period"]["datetimeTo"]["local"],
                    "value": result["value"],
                    "parameter": result["parameter"]["name"],
                }
            )

        all_measurements.extend(measurements)
        logging.info(f"Fetched {len(measurements)} records for {name}")

    return pd.DataFrame(all_measurements)


if __name__ == "__main__":
    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError("OPENAQ_API_KEY not found in .env")

    station_name = "kossutha"
    df = fetch_station(station_name, api_key=api_key)
    df.to_parquet(
        f"data/raw/katowice_{station_name}.parquet", index=False, compression="snappy"
    )
    logging.info(f"Saved {len(df)} total rows")
