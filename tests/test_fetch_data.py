import pytest

from data.fetch_data import OpenAQClient


def test_client_init_error():
    """Verify that ValueError is raised when API key is missing."""
    with pytest.raises(ValueError):
        OpenAQClient(api_key=None)


def test_fetch_history_mock(requests_mock):
    """Test successful API response parsing."""
    client = OpenAQClient(api_key="test_key")

    # Mock OpenAQ API response
    mock_response = {
        "results": [
            {"period": {"datetimeTo": {"local": "2024-01-20T12:00:00"}}, "value": 15.5}
        ]
    }

    requests_mock.get(
        "https://api.openaq.org/v3/sensors/14152505/measurements",
        json=mock_response,
    )

    result = client.fetch_history(14152505, "pm25", days=1)

    assert len(result) == 1
    assert result[0]["value"] == 15.5
    assert result[0]["parameter"] == "pm25"


def test_fetch_history_api_error(requests_mock):
    """Test handling of 404 API error."""
    client = OpenAQClient(api_key="test_key")

    requests_mock.get(
        "https://api.openaq.org/v3/sensors/14152505/measurements",
        status_code=404,
    )

    result = client.fetch_history(14152505, "pm25", days=1)
    assert result == []
