"""Shared pytest fixtures for LG-GeoView tests."""

import pandas as pd
import pytest


DASHBOARD_COLUMNS = [
    "area", "lg_group", "leader_name", "families", "individuals",
    "members", "meeting_day", "latitude", "longitude",
]


@pytest.fixture
def sample_df():
    """Return a DataFrame with all dashboard columns and realistic test data."""
    data = [
        {
            "area": "Kukatpally",
            "lg_group": "LG1",
            "leader_name": "Ravi Kumar",
            "families": 5,
            "individuals": 7,
            "members": 12,
            "meeting_day": "Sunday",
            "latitude": 17.4948,
            "longitude": 78.3996,
        },
        {
            "area": "Kukatpally",
            "lg_group": "LG2",
            "leader_name": "Suresh Reddy",
            "families": 8,
            "individuals": 22,
            "members": 30,
            "meeting_day": "Saturday",
            "latitude": 17.4955,
            "longitude": 78.4010,
        },
        {
            "area": "Kondapur",
            "lg_group": "LG3",
            "leader_name": "Priya Sharma",
            "families": 3,
            "individuals": 5,
            "members": 8,
            "meeting_day": "Sunday",
            "latitude": 17.4636,
            "longitude": 78.3635,
        },
        {
            "area": "Kondapur",
            "lg_group": "LG4",
            "leader_name": "Anil Reddy",
            "families": 6,
            "individuals": 15,
            "members": 21,
            "meeting_day": "Wednesday",
            "latitude": 17.4645,
            "longitude": 78.3650,
        },
        {
            "area": "KPHB",
            "lg_group": "LG5",
            "leader_name": "Rajesh Naidu",
            "families": 4,
            "individuals": 10,
            "members": 14,
            "meeting_day": "Sunday",
            "latitude": 17.4835,
            "longitude": 78.3878,
        },
        {
            "area": "KPHB",
            "lg_group": "LG6",
            "leader_name": "Sita Ram",
            "families": 2,
            "individuals": 17,
            "members": 19,
            "meeting_day": "Saturday",
            "latitude": 17.4842,
            "longitude": 78.3890,
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_path(tmp_path, sample_df):
    """Write sample data to a temporary CSV file and return its path."""
    csv_file = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def empty_df():
    """Return an empty DataFrame with the correct dashboard columns."""
    return pd.DataFrame(columns=DASHBOARD_COLUMNS)
