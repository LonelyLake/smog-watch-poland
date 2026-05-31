import argparse
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fetch_station(
    station_name: str = "kossutha", api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch air quality measurements for a station from OpenAQ API.

    Args:
        station_name: Station key from config/stations.yaml
        api_key: OpenAQ API key

    Returns:
        DataFrame with columns: timestamp, value, parameter
    """

    all_measurements = []

    # Read sensors from stations.yaml
    with open("config/stations.yaml", "r") as f:
        config = yaml.safe_load(f)

    sensors = config["stations"][station_name]["sensors"]

    # Set up session
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    headers = {"X-API-Key": api_key}

    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    params = {"datetime_from": start_date, "limit": 1000}

    # Get sensors measurements (timestamp, value, parameter)
    for name, id in sensors.items():
        response = session.get(
            f"https://api.openaq.org/v3/sensors/{id}/measurements",
            headers=headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()

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

        # Save measurements to list
        all_measurements.extend(measurements)
        logging.info(f"Fetched {len(measurements)} records for {name}")

    return pd.DataFrame(all_measurements)


if __name__ == "__main__":
    # Read arguments from terminal
    parser = argparse.ArgumentParser()
    parser.add_argument("--station", type=str, default="kossutha")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    # Check if api_key exists
    api_key = os.getenv("OPENAQ_API_KEY")
    if not api_key:
        raise ValueError("OPENAQ_API_KEY not found in .env")

    # Fetch station data and save it to .parquet file
    station_name = args.station
    df = fetch_station(station_name, api_key=api_key)
    df.to_parquet(
        f"data/raw/katowice_{station_name}.parquet", index=False, compression="snappy"
    )
    logging.info(f"Saved {len(df)} total rows")
