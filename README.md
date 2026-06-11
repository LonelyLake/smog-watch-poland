# SmogWatch Poland: Air Quality Data Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Database: PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

ETL pipeline collecting and analyzing air quality measurements from government and citizen sensors in Katowice, Poland using the OpenAQ v3 API.

## Architecture

OpenAQ API → Parquet (Bronze Layer) → Parquet (Silver Layer) → PostgreSQL (Storage) → SQL Analytics (Gold Layer)

## What this project does

- **Robust Ingestion**: Fetches PM2.5, PM10, NO₂, SO₂, O₃ data from OpenAQ v3 API with automated exponential backoff and network retry logic.
- **Structured Bronze**: Stores immutable raw snapshots in compressed Parquet format to optimize local disk usage and memory efficiency under WSL2.
- **Physical Silver Layer**: Validates data against nulls, physical anomalies (e.g., negative values), and timestamp alignment, outputting sanitized Parquet states.
- **Idempotent DB Storage**: Loads cleaned data into PostgreSQL using transactional bulk upserts (`ON CONFLICT DO NOTHING`) via a composite primary key.

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
│   ├── raw/                    # Immutable raw data snapshots (Bronze Layer)
│   └── clean/                  # Sanitized, type-safe data (Silver Layer)
├── sql/
│   ├── schema/
│   │   └── init.sql            # PostgreSQL schema, constraints + composite indexes
│   └── analysis/
│       ├── 01_daily_avg_pm25.sql    # Daily PM2.5 averages
│       ├── 02_who_limits.sql        # WHO guideline exceedances
│       └── 03_parameter_stats.sql  # Advanced statistics (including medians)
├── src/data/
│   ├── fetch_data.py           # API client with retry budgets & empty data guards
│   ├── check_quality.py        # Data validation and physical constraint filtering
│   └── load_to_postgres.py     # Batch loader with idempotent upsert logic
├── scripts/
│   └── discover_sensors.py     # Sensor discovery tool (fuzzy lookup)
└── tests/                      # Unit tests with pytest
```

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your OpenAQ API key and PostgreSQL credentials
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
just pipeline        # Run full E-t-L-T chain: fetch → validate → load
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

SQL queries in `sql/analysis/` answer:

- **Daily PM2.5 averages** — which days had highest pollution?
- **WHO exceedances** — days exceeding 15 µg/m³ guideline (2021)
- **Parameter statistics** — min, max, avg, median per parameter

## Data Quality

- Null value detection
- Negative value checks (physically impossible readings)
- Timestamp range validation
- Upsert deduplication in PostgreSQL (composite primary key)

**Note**: Citizen sensors may have calibration limitations 
vs reference-grade equipment.

## Technical Stack

- **Language**: Python 3.12+
- **Data**: Pandas, PyArrow, Parquet
- **Database**: PostgreSQL (Docker), psycopg2
- **API**: Requests with exponential backoff retry
- **Development**: Ruff, pytest, uv, Just
- **Infrastructure**: Docker, docker-compose

## License

MIT License

## Acknowledgments

- Air quality data: [OpenAQ](https://openaq.org)
- Citizen sensors: AirGradient network
- Government data: Polish Chief Inspectorate for Environmental Protection
