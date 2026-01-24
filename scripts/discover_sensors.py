import argparse
import logging
import os
import sys

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.openaq.org/v3"


class SensorDiscovery:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAQ_API_KEY")
        if not self.api_key:
            logger.error("OPENAQ_API_KEY not found in .env file.")
            sys.exit(1)

        self.headers = {"X-API-Key": self.api_key, "Accept": "application/json"}

    def print_sensors(self, location_id: int, location_name: str):
        """Fetches and prints all sensors for a verified location ID."""
        url = f"{BASE_URL}/locations/{location_id}/sensors"
        try:
            res = requests.get(url, headers=self.headers, timeout=15)
            res.raise_for_status()
            sensors = res.json().get("results", [])

            print(f"\n{'=' * 60}")
            print(f"LOCATION: {location_name} (ID: {location_id})")
            print(f"{'=' * 60}")

            if not sensors:
                print("No active sensors found for this location.")
                return

            for s in sensors:
                param = s.get("parameter", {})
                print(f"- {param.get('displayName', param.get('name', 'Unknown'))}:")
                print(f"  ID:    {s['id']}")
                print(f"  Units: {param.get('units', 'n/a')}")
                print(f"  Last Value: {s.get('latest', {}).get('value', 'N/A')}")
                print("-" * 30)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch sensors for ID {location_id}: {e}")

    def discover_by_name(self, name: str):
        """Searches for a location ID by name first, then finds sensors."""
        logger.info(f"Searching for location matching: '{name}'")
        url = f"{BASE_URL}/locations"
        params = {"name": name}

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            res.raise_for_status()
            results = res.json().get("results", [])

            if not results:
                print(f"No locations found matching '{name}'.")
                return

            # Use the first match but warn if multiple found
            loc = results[0]
            if len(results) > 1:
                logger.warning(
                    f"Multiple matches found. Using first result: {loc['name']}"
                )

            self.print_sensors(loc["id"], loc["name"])

        except requests.exceptions.RequestException as e:
            logger.error(f"Discovery API error: {e}")


def main():
    parser = argparse.ArgumentParser(description="OpenAQ Sensor Discovery Tool (v2)")

    # Mutually exclusive group: search by name OR provide ID directly
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--name", type=str, help="Search by location name (e.g. 'Katowice-Kossutha')"
    )
    group.add_argument(
        "--id", type=int, help="Provide Location ID directly from map/registry"
    )

    args = parser.parse_args()
    discovery = SensorDiscovery()

    if args.id:
        # If we have the ID, skip the search and go straight to sensors
        discovery.print_sensors(args.id, "Direct ID Lookup")
    else:
        discovery.discover_by_name(args.name)


if __name__ == "__main__":
    main()
