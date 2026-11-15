# SmogWatch Poland: Air Quality Data Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Database: PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

ETL pipeline for collecting, validating, and loading air quality measurements from sensors in Katowice, Poland using the OpenAQ v3 API.

## Architecture

OpenAQ API → Parquet (Bronze) → Parquet (Silver) → PostgreSQL → SQL analytics

The Gold layer (dbt models on top of PostgreSQL) is planned.

## What this project does

- **Robust Ingestion**: Fetches PM2.5, PM10, NO₂, SO₂, O₃ measurements from the OpenAQ v3 API with retries and exponential backoff for transient failures (429, 5xx).
- **Bronze**: Stores extracted API fields (timestamp, value, parameter, station) as compressed Parquet. The file is overwritten on each run; immutable timestamped snapshots are planned (#13).
- **Silver Layer Validation**: Converts timestamps to UTC, stops on unparseable timestamps, and drops physically invalid readings: negative pollutant values (including sentinel −1 readings observed for SO₂ at Kossutha), humidity outside 0–100 %, and temperature outside −50…60 °C. Full schema validation is planned (#14).
- **Idempotent DB Storage**: Loads cleaned data into PostgreSQL with `INSERT ... ON CONFLICT DO NOTHING` on a composite primary key `(timestamp, parameter, station)`. Re-running does not create duplicates; existing rows are not updated.

## Pipeline

```
fetch_data.py → check_quality.py → load_to_postgres.py
```

Run the full pipeline:

```bash
just pipeline
```

## Project Structure

```
smog-watch-poland/
├── config/
│   └── stations.yaml           # Sensor registry (IDs, parameters)
├── data/
│   ├── raw/                    # Extracted API data (Bronze), overwritten on each run
│   └── clean/                  # Validated data (Silver Layer)
├── sql/
│   ├── schema/
│   │   └── init.sql            # PostgreSQL schema with composite primary key
│   └── analysis/
│       ├── 01_daily_avg_pm25.sql    # Daily PM2.5 averages
│       ├── 02_who_limits.sql        # WHO guideline exceedances
│       └── 03_parameter_stats.sql   # Per-parameter min/max/avg/median
├── src/data/
│   ├── fetch_data.py           # API client with retry handling
│   ├── check_quality.py        # Timestamp normalization and basic physical checks
│   └── load_to_postgres.py     # Batch loader with idempotent insert-ignore loading
├── scripts/
│   └── discover_sensors.py     # Sensor discovery tool (fuzzy lookup)
└── tests/                      # Unit tests with pytest
```

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Fill in your OpenAQ API key and PostgreSQL credentials
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Install dependencies

```bash
just setup
```

### 4. Run pipeline

```bash
just pipeline
```

## Available Commands

```bash
just pipeline        # Run full ETL chain: fetch → validate → load
just fetch           # Extract raw data from API to Bronze layer
just validate        # Run QA checks, filter anomalies, and output to Silver layer
just load            # Bulk load Silver Parquet data into PostgreSQL
just test            # Execute unit test suite with pytest
just lint            # Verify code quality and format using Ruff
just discover "Name" # Run fuzzy search for sensor IDs by city/location
```

## Monitored Parameters

| Parameter | Source | Description |
|-----------|--------|-------------|
| PM2.5 | Government | Fine particulate matter |
| PM10 | Government | Coarse particulate matter |
| NO₂ | Government | Nitrogen dioxide |
| SO₂ | Government | Sulfur dioxide |
| O₃ | Government | Ground-level ozone |
| Temperature | Citizen | Ambient temperature |
| Humidity | Citizen | Relative humidity |

## Analytical Questions

SQL queries in `sql/analysis/` cover:

- Daily PM2.5 averages for Kossutha
- Days exceeding the WHO PM2.5 guideline of 15 µg/m³
- Per-parameter statistics: count, min, max, average, median

## Data Quality

- Timestamp parsing and UTC normalization
- Negative-value checks for all pollutants (PM2.5, PM10, NO₂, SO₂, O₃)
- Range checks for relative humidity (0–100 %) and temperature (−50…60 °C)
- Deduplication in PostgreSQL via a composite primary key (insert-ignore)

**Note**: Citizen sensors may have calibration limitations compared with reference-grade equipment, so the pipeline treats them as a separate data source rather than the same quality tier.

## Portfolio Notes

This project is intentionally small and honest in scope. It shows that I can:

- build a repeatable data pipeline end to end;
- work with Parquet, PostgreSQL, and SQL-based analysis;
- write unit tests for ingestion and validation (loading tests are planned, #17) and run the project through a reproducible local setup;
- document limitations instead of overstating production readiness.

The current validation layer catches obvious bad values but does not attempt full statistical anomaly detection.

## Technical Stack

- **Language**: Python 3.12+
- **Data**: Pandas, Parquet
- **Database**: PostgreSQL (Docker), psycopg2
- **API**: Requests with exponential backoff retry
- **Development**: Ruff, pytest, uv, Just
- **Infrastructure**: Docker, docker-compose

## Known Limitations & Roadmap

- Bronze is not yet immutable (#13)
- Validation covers timestamps and basic value ranges only (#14)
- Tests cover ingestion and validation; the PostgreSQL loader is not tested yet (#12, #17)
- No CI yet (#22); PostgreSQL connection settings are partly hardcoded (#21)

## License

MIT License

## Acknowledgments

- Air quality data: [OpenAQ](https://openaq.org)

