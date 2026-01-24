# --- Global Settings ---
set shell := ["zsh", "-c"]

# Default station to Kossutha
station := "kossutha"

# --- Infrastructure ---

# Sync dependencies and build environment using uv
setup:
    uv sync

# --- Development & Quality ---

# Run Ruff linter with autofix
lint:
    uv tool run ruff check . --fix
    uv tool run ruff format .

# Run unit tests with pytest
test:
    uv run pytest tests/ -v

# --- Data Pipeline ---

# Full pipeline: Fetch -> Validate
pipeline: fetch validate

# 1. Fetch data for a specific station from config/stations.yaml
fetch:
    uv run src/data/fetch_data.py --station {{station}}

# 2. Validate data quality for the specific station
validate:
    uv run src/data/check_quality.py --input data/raw/katowice_{{station}}.parquet

# --- Sensor Discovery ---

# Find IDs by Location Name (Fuzzy search)
# Usage: just discover "Katowice-Kossutha"
discover name="Katowice-Kossutha":
    uv run python scripts/discover_sensors.py --name "{{name}}"

# Find Sensors by specific Location ID (Precise lookup from map)
# Usage: just discover-id 70644
discover-id id:
    uv run python scripts/discover_sensors.py --id {{id}}

# --- Notebooks ---

# Start Jupyter Lab for EDA
eda:
    uv run jupyter lab