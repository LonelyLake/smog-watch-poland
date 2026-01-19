import argparse
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://api.openaq.org/v3"
API_KEY = os.getenv("OPENAQ_API_KEY")
HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}
TIMEOUT_SECONDS = 20
DAYS_BACK = 7
DEFAULT_OUTPUT = "data/raw/katowice_zawodzie_history.parquet"

# Our target sensors in Katowice, Zawodzie
SENSORS = {"pm25": 14152505, "temp": 14152507, "humidity": 14152506}


def _get_session() -> requests.Session:
    retries = Retry(
        total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", adapter)
    return session


def fetch_sensor_history(
    session: requests.Session, sensor_id: int, label: str, days_back: int
) -> List[Dict]:
    logger.info("Fetching RECENT history for %s (ID: %s)...", label, sensor_id)
    if not API_KEY:
        raise RuntimeError("OPENAQ_API_KEY is not set")

    start_date = (datetime.now() - timedelta(days=days_back)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    params = {
        "datetime_from": start_date,
        "limit": 1000,
        "order_by": "datetime",
        "sort_order": "desc",
    }

    url = f"{BASE_URL}/sensors/{sensor_id}/measurements"
    response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    results = response.json().get("results", [])

    return [
        {
            "timestamp": r["period"]["datetimeTo"]["local"],
            "value": r["value"],
            "parameter": label,
        }
        for r in results
    ]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch recent OpenAQ sensor history")
    parser.add_argument(
        "--days-back", type=int, default=DAYS_BACK, help="Days of history"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT, help="Output parquet"
    )
    parser.add_argument(
        "--timeout", type=int, default=TIMEOUT_SECONDS, help="HTTP timeout (s)"
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    global TIMEOUT_SECONDS
    TIMEOUT_SECONDS = args.timeout

    session = _get_session()
    all_measurements: List[Dict] = []

    for label, s_id in SENSORS.items():
        try:
            all_measurements.extend(
                fetch_sensor_history(session, s_id, label, args.days_back)
            )
        except Exception as exc:
            logger.error("Error for %s: %s", label, exc)

    if not all_measurements:
        print("❌ No data collected.")
        return

    df = pd.DataFrame(all_measurements)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print("\n✅ DATA COLLECTED!")
    print(f"Total records: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    main()
