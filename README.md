# SmogWatch Poland: Air Quality Data Pipeline

Data engineering project for collecting and analyzing 
air quality measurements from sensors in Katowice, Poland 
using the OpenAQ v3 API.

## What this project does

- Fetches data from citizen sensors and government 
  reference stations via OpenAQ API
- Validates data quality (null checks, physical constraints, 
  timestamp validation)
- Stores data in Parquet format for efficient analytics
- Exploratory analysis of PM2.5, PM10, NO₂ and other 
  air quality parameters

## Current Status

Working pipeline with data collection, validation, 
and exploratory analysis for Katowice/Silesia region.

## Project Structure

```
smog-watch-poland/
├── config/
│   └── stations.yaml          # Sensor registry (IDs, parameters)
├── data/
│   ├── raw/                   # Parquet files from OpenAQ
│   └── processed/             # Cleaned datasets
├── notebooks/
│   └── eda_jan2026_*.ipynb    # Exploratory analysis
├── src/data/
│   ├── fetch_data.py          # OpenAQ API client
│   └── check_quality.py       # Data validation
├── scripts/
│   └── discover_sensors.py    # Sensor discovery tool
└── tests/                     # Unit tests with pytest
```

## Monitored Parameters

| Parameter | Source | Description |
|-----------|--------|-------------|
| PM2.5 | Citizen & Government | Fine particulate matter |
| PM10 | Government | Coarse particulate matter |
| NO₂ | Government | Nitrogen dioxide |
| SO₂ | Government | Sulfur dioxide |
| O₃ | Government | Ground-level ozone |
| Temperature | Citizen | Ambient temperature |
| Humidity | Citizen | Relative humidity |

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies using uv
just setup

# Or manually
uv sync
```

### 2. Configure API Access

Create a `.env` file with your OpenAQ API key:

```bash
OPENAQ_API_KEY=your_key_here
```

Get your free API key at: https://openaq.org

### 3. Fetch Data

```bash
# Fetch from government reference station (Kossutha)
just fetch

# Or specify a station from config/stations.yaml
uv run src/data/fetch_data.py --station kossutha --days 7

# Fetch from citizen sensor (Zawodzie)
uv run src/data/fetch_data.py --station zawodzie --days 7
```

### 4. Validate Data Quality

```bash
just validate

# Or manually
uv run src/data/check_quality.py --input data/raw/katowice_kossutha.parquet
```

### 5. Explore Data

```bash
just eda
```

This launches Jupyter Lab for interactive analysis.

## Available Commands (Justfile)

```bash
just setup          # Install dependencies
just fetch          # Fetch data (default: Kossutha station)
just validate       # Run data quality checks
just lint           # Format and lint code with Ruff
just test           # Run unit tests
just eda            # Start Jupyter Lab
just discover "Name"  # Find sensor IDs by location name
```

## Data Quality Approach

The project implements comprehensive data validation:

- Null value detection and reporting
- Negative value checks (physically impossible readings)
- Timestamp range validation
- Record count tracking
- Parameter coverage analysis

**Note**: Citizen science sensors may have calibration limitations compared to reference-grade equipment. Analysis focuses on pattern identification rather than absolute accuracy validation.

## Technical Stack

- **Language**: Python 3.12+
- **Data**: Pandas, PyArrow (Parquet)
- **API Client**: Requests with retry logic
- **Visualization**: Matplotlib, Seaborn
- **Development**: Ruff (linting), pytest (testing), uv (package management)
- **Task Runner**: Just

## Contributing

This is a personal portfolio project, but suggestions are welcome! Feel free to open an issue for feedback.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Air quality data provided by [OpenAQ](https://openaq.org)
- Citizen science sensors via AirGradient network
- Government reference data from Polish Chief Inspectorate for Environmental Protection
