# Sync dependencies and build scripts
setup:
    uv sync

# Fetch data for Katowice (Zawodzie)
# Usage: just fetch 14
fetch days="7":
    uv run fetch-data --days-back {{days}} --output data/raw/katowice.parquet

# Run Ruff linter with autofix
lint:
    uv tool run ruff check . --fix
