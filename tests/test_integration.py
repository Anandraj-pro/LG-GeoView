"""Integration tests: end-to-end data flow from CSV -> charts -> map."""

import os
from unittest.mock import patch

import folium
import plotly.graph_objects as go

from src.data_loader import load_from_csv, assign_strength, get_area_summary
from src.map_builder import build_map, build_detailed_map
from src.charts import (
    members_by_area_chart,
    groups_by_area_chart,
    strength_pie_chart,
    meeting_day_chart,
    top_bottom_groups_chart,
    leader_members_chart,
    area_detail_table,
)


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(PROJECT_ROOT, "data", "sample_data.csv")


class TestEndToEndFlow:
    """Integration test: load CSV -> assign strength -> build maps -> charts."""

    @patch("src.data_loader.st")
    def test_full_pipeline(self, mock_st):
        """Load sample CSV, process data, build maps, generate all charts."""
        # Step 1: Load data
        df = load_from_csv(SAMPLE_CSV)
        assert not df.empty
        assert len(df) == 20

        # Step 2: Assign strength
        df = assign_strength(df)
        assert "strength" in df.columns

        # Step 3: Area summary
        summary = get_area_summary(df)
        assert not summary.empty
        assert "total_groups" in summary.columns

        # Step 4: Build maps
        overview_map = build_map(df)
        assert isinstance(overview_map, folium.Map)

        detailed_map = build_detailed_map(df)
        assert isinstance(detailed_map, folium.Map)

        # Step 5: Generate all charts
        assert isinstance(members_by_area_chart(df), go.Figure)
        assert isinstance(groups_by_area_chart(df), go.Figure)
        assert isinstance(strength_pie_chart(df), go.Figure)
        assert isinstance(meeting_day_chart(df), go.Figure)
        assert isinstance(top_bottom_groups_chart(df), go.Figure)
        assert isinstance(leader_members_chart(df), go.Figure)

        # Step 6: Drill-down table
        first_area = df["area"].iloc[0]
        detail = area_detail_table(df, first_area)
        assert not detail.empty
        assert "Leader" in detail.columns

    @patch("src.data_loader.st")
    def test_filtered_pipeline(self, mock_st):
        """Load data, filter to one area, verify pipeline works."""
        df = load_from_csv(SAMPLE_CSV)
        df = assign_strength(df)

        # Filter to single area
        areas = df["area"].unique()
        single_area = areas[0]
        filtered = df[df["area"] == single_area].copy()

        assert not filtered.empty
        assert filtered["area"].nunique() == 1

        # Maps and charts should work with filtered data
        m = build_map(filtered)
        assert isinstance(m, folium.Map)

        summary = get_area_summary(filtered)
        assert len(summary) == 1

        assert isinstance(members_by_area_chart(filtered), go.Figure)
        assert isinstance(strength_pie_chart(filtered), go.Figure)
