import argparse
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Constants
BASE_URL = "https://api.openaq.org/v3"
CONFIG_PATH = Path("config/stations.yaml")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAQClient:
    """Client for interacting with the OpenAQ v3 API with robust error handling."""

    def __init__(self, api_key: Optional[str], timeout: int = 20):
        if not api_key:
            raise ValueError("OPENAQ_API_KEY not found in .env")

        self.api_key = api_key
        self.timeout = timeout
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """Initialize session with exponential backoff retry mechanism."""
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update(
            {"X-API-Key": self.api_key, "Accept": "application/json"}
        )
        return session

    def fetch_history(self, sensor_id: int, label: str, days: int) -> List[Dict]:
        """Fetch history for a specific sensor ID."""
        logger.info(f"Requesting {label} (ID: {sensor_id})...")

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
        except Exception as e:
            logger.error(f"Error fetching {label}: {e}")
            return []


def load_stations_config() -> Dict:
    """
    Loads station metadata from YAML configuration.
    Professional approach: Decouples data/IDs from code logic.
    """
    if not CONFIG_PATH.exists():
        logger.error(f"Configuration file not found at {CONFIG_PATH}")
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
        return config.get("stations", {})


def main():
    # 1. Load configuration from YAML
    try:
        stations_registry = load_stations_config()
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        return

    parser = argparse.ArgumentParser(description="OpenAQ Multi-Station Data Pipeline")
    parser.add_argument("--days", type=int, default=7, help="History depth in days")
    parser.add_argument(
        "--station",
        type=str,
        default="kossutha",
        choices=stations_registry.keys(),
        help="Target station from config/stations.yaml",
    )
    parser.add_argument(
        "--output", type=str, help="Custom path (defaults to data/raw/...)"
    )

    args = parser.parse_args()

    # Dynamic Output Path based on station name
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"data/raw/katowice_{args.station}.parquet")
    )

    try:
        client = OpenAQClient(api_key=os.getenv("OPENAQ_API_KEY"))
    except ValueError as e:
        logger.error(e)
        return

    # 2. Select sensors based on the requested station from the YAML registry
    selected_sensors = stations_registry[args.station].get("sensors", {})
    all_data = []

    # 3. Iterate through the sensors defined in the config
    for label, s_id in selected_sensors.items():
        measurements = client.fetch_history(s_id, label, args.days)
        all_data.extend(measurements)

    if not all_data:
        logger.warning(f"No data collected for station: {args.station}")
        return

    # Data Processing
    df = pd.DataFrame(all_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, compression="snappy")

    logger.info(f"Success! Station: {args.station} | Records: {len(df)}")
    logger.info(f"File saved: {output_path}")


if __name__ == "__main__":
    main()
