# SmogWatch Poland: Air Quality Monitoring & Analysis

A data engineering portfolio project analyzing air quality sensor data in Katowice, Poland using the OpenAQ API. This project demonstrates end-to-end data pipeline development, from data collection to exploratory analysis, with plans to expand into predictive modeling.

## Overview

This project currently focuses on collecting and analyzing air quality measurements from **private/citizen science sensors** (e.g., AirGradient devices) and **government reference stations** in the Silesia region. The pipeline is designed for scalability and follows MLOps best practices.

### Current Implementation (Phase 1)

- ✅ Multi-station data collection from OpenAQ v3 API
- ✅ Support for both citizen sensors (Zawodzie) and government reference stations (Kossutha)
- ✅ Configurable sensor registry using YAML
- ✅ Robust error handling with exponential backoff retries
- ✅ Data quality validation pipeline
- ✅ Exploratory data analysis with Jupyter notebooks
- ✅ Parquet-based storage for efficient analytics

### Future Roadmap

- 🔄 **Phase 2**: Expand to more government monitoring stations across Poland
- 🔮 **Phase 3**: Develop ML models for air quality prediction and anomaly detection
- 📊 **Phase 4**: Build real-time dashboard and alerting system

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

- ✅ Null value detection and reporting
- ✅ Negative value checks (physically impossible readings)
- ✅ Timestamp range validation
- ✅ Record count tracking
- ✅ Parameter coverage analysis

**Note**: Citizen science sensors may have calibration limitations compared to reference-grade equipment. Analysis focuses on pattern identification rather than absolute accuracy validation.

## Technical Stack

- **Language**: Python 3.12+
- **Data**: Pandas, PyArrow (Parquet)
- **API Client**: Requests with retry logic
- **Visualization**: Matplotlib, Seaborn
- **Development**: Ruff (linting), pytest (testing), uv (package management)
- **Task Runner**: Just

## Why This Project?

This portfolio project demonstrates:

1. **Data Engineering**: Building robust ETL pipelines with error handling
2. **API Integration**: Working with real-world REST APIs (OpenAQ v3)
3. **Configuration Management**: YAML-based sensor registry for maintainability  
4. **Data Quality**: Implementing validation checks for data integrity
5. **Best Practices**: Testing, linting, reproducible environments
6. **Domain Knowledge**: Understanding air quality metrics and sensor limitations

## Contributing

This is a personal portfolio project, but suggestions are welcome! Feel free to open an issue for feedback.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Air quality data provided by [OpenAQ](https://openaq.org)
- Citizen science sensors via AirGradient network
- Government reference data from Polish Chief Inspectorate for Environmental Protection
