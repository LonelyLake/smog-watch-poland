import re

import pandas as pd
import pytest

from data.fetch_data import fetch_station


def test_fetch_station_value_error_without_api_key():
    """Ensure ValueError is raised if api_key is missing."""
    with pytest.raises(ValueError, match="api_key is required"):
        fetch_station(station_name="kossutha", api_key=None)


def test_fetch_station_mock_success(requests_mock):
    """Verify successful OpenAQ API response parsing into a DataFrame."""
    api_key = "fake_test_key"

    mock_response = {
        "results": [
            {
                "period": {"datetimeTo": {"local": "2026-06-06T12:00:00+02:00"}},
                "value": 15.5,
                "parameter": {"name": "pm25"},
            }
        ]
    }

    requests_mock.get(
        re.compile(r"https://api.openaq.org/v3/sensors/\d+/measurements"),
        json=mock_response,
    )

    df = fetch_station(station_name="kossutha", api_key=api_key, days=1)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "timestamp" in df.columns
    assert df.iloc[0]["value"] == 15.5
    assert df.iloc[0]["parameter"] == "pm25"
    assert df.iloc[0]["station"] == "kossutha"
