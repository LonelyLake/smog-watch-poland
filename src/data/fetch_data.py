import argparse
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Constants in uppercase
BASE_URL = "https://api.openaq.org/v3"
DEFAULT_OUTPUT = Path("data/raw/katowice_zawodzie_history.parquet")

# Sensors in Katowice (Zawodzie)
SENSORS = {"pm25": 14152505, "temp": 14152507, "humidity": 14152506}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAQClient:
    """Client for interacting with the OpenAQ v3 API."""

    def __init__(self, api_key: Optional[str], timeout: int = 20):
        if not api_key:
            raise ValueError("OPENAQ_API_KEY not found in environment variables (.env)")

        self.api_key = api_key
        self.timeout = timeout
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """Initialize session with retry mechanism."""
        session = requests.Session()
        retries = Retry(
            total=5,  # Increase to 5 for reliability
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update(
            {"X-API-Key": self.api_key, "Accept": "application/json"}
        )
        return session

    def fetch_history(self, sensor_id: int, label: str, days: int) -> List[Dict]:
        """Fetch history for a specific sensor."""
        logger.info(f"Requesting data for {label} (ID: {sensor_id})...")

        # Use UTC for consistency (important for MLOps)
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        params = {
            "datetime_from": start_date,
            "limit": 1000,
            "order_by": "datetime",
            "sort_order": "desc",
        }

        url = f"{BASE_URL}/sensors/{sensor_id}/measurements"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            return [
                {
                    "timestamp": r["period"]["datetimeTo"]["local"],
                    "value": r["value"],
                    "parameter": label,
                    "sensor_id": sensor_id,
                }
                for r in results
            ]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sensor {label}: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(description="OpenAQ Data Pipeline")
    parser.add_argument("--days", type=int, default=7, help="History depth in days")
    parser.add_argument(
        "--output", type=str, default=str(DEFAULT_OUTPUT), help="File path"
    )
    args = parser.parse_args()

    # Initialize client
    try:
        client = OpenAQClient(api_key=os.getenv("OPENAQ_API_KEY"))
    except ValueError as e:
        logger.error(e)
        return

    all_data = []
    for label, s_id in SENSORS.items():
        measurements = client.fetch_history(s_id, label, args.days)
        all_data.extend(measurements)

    if not all_data:
        logger.warning("No data collected.")
        return

    # Processing with Pandas
    df = pd.DataFrame(all_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert to datetime immediately

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Saving to Parquet with compression
    df.to_parquet(output_path, index=False, compression="snappy")

    logger.info(f"Success! Records collected: {len(df)}")
    logger.info(f"File saved: {output_path}")


if __name__ == "__main__":
    main()
