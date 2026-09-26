import re

import pandas as pd
import pytest
from requests import Session

from data.fetch_data import fetch_sensor_measurements, fetch_station


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


def test_fetch_sensor_measurements_pagination(requests_mock):
    """Verify that all API pages are fetched and combined."""
    session = Session()

    url = "https://api.openaq.org/v3/sensors/35221/measurements"

    page_1 = {
        "results": [
            {"value": 10},
            {"value": 11},
        ]
    }

    page_2 = {
        "results": [
            {"value": 12},
            {"value": 13},
        ]
    }

    page_3 = {
        "results": [
            {"value": 14},
        ]
    }

    requests_mock.get(
        f"{url}?limit=2&page=1",
        json=page_1,
    )

    requests_mock.get(
        f"{url}?limit=2&page=2",
        json=page_2,
    )

    requests_mock.get(
        f"{url}?limit=2&page=3",
        json=page_3,
    )

    results = fetch_sensor_measurements(
        session=session,
        sensor_id=35221,
        headers={"X-API-Key": "fake_test_key"},
        params={
            "datetime_from": "2026-06-01T00:00:00+00:00",
            "limit": 2,
        },
    )

    assert len(results) == 5
    assert [item["value"] for item in results] == [10, 11, 12, 13, 14]
    assert requests_mock.call_count == 3
