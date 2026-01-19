# SmogWatch Poland: ML Air Quality Predictor

Minimal data pipeline to fetch recent OpenAQ measurements for Katowice (Zawodzie),
store them in Parquet, and run a basic data quality check.

## Features

- OpenAQ v3 sensor history fetch with retries and timeouts
- CLI with configurable time range and output path
- Data quality report (nulls, time range, negatives)

## Quick start

1) Create .env with your API key:

	OPENAQ_API_KEY=your_key_here

2) Fetch data (CLI):

	uv run fetch-data --days-back 7 --output data/raw/katowice.parquet --timeout 20

3) Check data quality:

	uv run check-quality

## Convenience commands (Justfile)

	just setup
	just fetch 14
    just quality
	just lint
