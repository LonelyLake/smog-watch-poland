import pandas as pd

from data.check_quality import validate_and_clean_data


def test_invalid_values_are_removed(tmp_path):
    df = pd.DataFrame(
        {
            "timestamp": ["2026-06-06T12:00:00+02:00"] * 8,
            "value": [10.0, -1.0, 20.0, 99.0, 50.0, 120.0, -1.0, 5.0],
            "parameter": [
                "pm25",
                "pm25",
                "temperature",
                "temperature",
                "relativehumidity",
                "relativehumidity",
                "so2",
                "so2",
            ],
            "station": ["zawodzie"] * 8,
        }
    )

    input_path = tmp_path / "in.parquet"
    output_path = tmp_path / "out.parquet"
    df.to_parquet(input_path, index=False)

    validate_and_clean_data(str(input_path), str(output_path))

    result = pd.read_parquet(output_path)
    assert sorted(result["value"]) == [5.0, 10.0, 20.0, 50.0]
    assert (result["value"] >= 0).all()
