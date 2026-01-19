# --- Global Settings ---
# Important: Global settings must be defined at the very beginning of the file
set shell := ["zsh", "-c"]

# --- Infrastructure ---

# Sync dependencies and build environment using uv
setup:
    uv sync

# --- Development & Quality ---

# Run Ruff linter with autofix
lint:
    uv tool run ruff check . --fix

# Run unit tests with pytest
test:
    uv run pytest tests/ -v

# Run tests with coverage report
test-cov:
    uv run pytest tests/ --cov=src -v

# --- Data Pipeline ---

# Full pipeline: Fetch -> Validate
pipeline: fetch validate

# 1. Fetch data
fetch:
    uv run src/data/fetch_data.py --output data/raw/katowice.parquet

# 2. Validate data
validate:
    uv run src/data/check_quality.py --input data/raw/katowice.parquet