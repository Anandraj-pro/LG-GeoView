"""Unit tests for src/charts.py."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.charts import (
    area_detail_table,
    groups_by_area_chart,
    leader_members_chart,
    meeting_day_chart,
    members_by_area_chart,
    strength_pie_chart,
    top_bottom_groups_chart,
    get_layout,
    DARK_LAYOUT,
    LIGHT_LAYOUT,
)
from src.data_loader import assign_strength


@pytest.fixture
def sample_df_with_strength(sample_df):
    """Return sample_df with the strength column added."""
    return assign_strength(sample_df)


class TestGetLayout:
    """Tests for get_layout helper."""

    def test_dark_returns_dark_layout(self):
        """get_layout(dark=True) should return DARK_LAYOUT."""
        assert get_layout(dark=True) is DARK_LAYOUT

    def test_light_returns_light_layout(self):
        """get_layout(dark=False) should return LIGHT_LAYOUT."""
        assert get_layout(dark=False) is LIGHT_LAYOUT

    def test_default_is_dark(self):
        """Default call should return DARK_LAYOUT."""
        assert get_layout() is DARK_LAYOUT


class TestMembersByAreaChart:
    """Tests for members_by_area_chart."""

    def test_members_by_area_chart_returns_figure(self, sample_df):
        """Should return a plotly go.Figure."""
        fig = members_by_area_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_members_by_area_chart_light_mode(self, sample_df):
        """Should return a valid figure in light mode."""
        fig = members_by_area_chart(sample_df, dark=False)
        assert isinstance(fig, go.Figure)


class TestGroupsByAreaChart:
    """Tests for groups_by_area_chart."""

    def test_groups_by_area_chart_returns_figure(self, sample_df):
        """Should return a plotly go.Figure."""
        fig = groups_by_area_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_groups_by_area_chart_light_mode(self, sample_df):
        """Should return a valid figure in light mode."""
        fig = groups_by_area_chart(sample_df, dark=False)
        assert isinstance(fig, go.Figure)


class TestStrengthPieChart:
    """Tests for strength_pie_chart."""

    def test_strength_pie_chart_returns_figure(self, sample_df_with_strength):
        """Should return a plotly go.Figure when strength column is present."""
        fig = strength_pie_chart(sample_df_with_strength)
        assert isinstance(fig, go.Figure)

    def test_strength_pie_chart_light_mode(self, sample_df_with_strength):
        """Should return a valid figure in light mode."""
        fig = strength_pie_chart(sample_df_with_strength, dark=False)
        assert isinstance(fig, go.Figure)


class TestMeetingDayChart:
    """Tests for meeting_day_chart."""

    def test_meeting_day_chart_returns_figure(self, sample_df):
        """Should return a plotly go.Figure."""
        fig = meeting_day_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_meeting_day_chart_light_mode(self, sample_df):
        """Should return a valid figure in light mode."""
        fig = meeting_day_chart(sample_df, dark=False)
        assert isinstance(fig, go.Figure)


class TestTopBottomGroupsChart:
    """Tests for top_bottom_groups_chart."""

    def test_top_bottom_groups_chart_returns_figure(self, sample_df):
        """Should return a plotly go.Figure."""
        fig = top_bottom_groups_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_top_bottom_groups_chart_light_mode(self, sample_df):
        """Should return a valid figure in light mode."""
        fig = top_bottom_groups_chart(sample_df, dark=False)
        assert isinstance(fig, go.Figure)


class TestLeaderMembersChart:
    """Tests for leader_members_chart."""

    def test_leader_members_chart_returns_figure(self, sample_df):
        """Should return a plotly go.Figure."""
        fig = leader_members_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_leader_members_chart_light_mode(self, sample_df):
        """Should return a valid figure in light mode."""
        fig = leader_members_chart(sample_df, dark=False)
        assert isinstance(fig, go.Figure)


class TestAreaDetailTable:
    """Tests for area_detail_table."""

    def test_area_detail_table_columns(self, sample_df_with_strength):
        """Returned DataFrame should have the expected display columns."""
        result = area_detail_table(sample_df_with_strength, "Kukatpally")
        expected_cols = ["Care Group", "Leader", "Families", "Individuals", "Total", "Meeting Day", "Strength"]
        assert list(result.columns) == expected_cols

    def test_area_detail_table_filters_area(self, sample_df_with_strength):
        """Should only return rows for the specified area."""
        result = area_detail_table(sample_df_with_strength, "Kukatpally")
        assert len(result) == 2  # sample_df has 2 Kukatpally rows

        result_kondapur = area_detail_table(sample_df_with_strength, "Kondapur")
        assert len(result_kondapur) == 2


class TestChartsEdgeCases:
    """Edge case tests for all chart functions."""

    def test_members_by_area_chart_single_row(self):
        """Single row DataFrame should produce a valid chart."""
        df = pd.DataFrame({
            "area": ["Kukatpally"], "families": [5], "individuals": [7], "members": [12],
        })
        fig = members_by_area_chart(df)
        assert isinstance(fig, go.Figure)

    def test_groups_by_area_chart_single_area(self):
        """Single area should produce a valid chart."""
        df = pd.DataFrame({
            "area": ["Kukatpally", "Kukatpally"],
            "lg_group": ["LG1", "LG2"],
        })
        fig = groups_by_area_chart(df)
        assert isinstance(fig, go.Figure)

    def test_strength_pie_chart_single_category(self):
        """Only one strength category should produce a valid chart."""
        df = pd.DataFrame({"strength": ["Strong", "Strong", "Strong"]})
        fig = strength_pie_chart(df)
        assert isinstance(fig, go.Figure)

    def test_strength_pie_chart_two_categories(self):
        """Two strength categories should produce a valid chart."""
        df = pd.DataFrame({"strength": ["Strong", "Weak"]})
        fig = strength_pie_chart(df)
        assert isinstance(fig, go.Figure)

    def test_meeting_day_chart_all_blank(self):
        """All blank meeting days should produce a valid chart (may be empty)."""
        df = pd.DataFrame({"meeting_day": ["", "", "  "]})
        fig = meeting_day_chart(df)
        assert isinstance(fig, go.Figure)

    def test_top_bottom_groups_chart_fewer_than_10(self):
        """Fewer than 10 groups should still produce a valid chart."""
        df = pd.DataFrame({
            "leader_name": ["L1", "L2", "L3"],
            "area": ["A1", "A2", "A3"],
            "members": [5, 15, 25],
        })
        fig = top_bottom_groups_chart(df)
        assert isinstance(fig, go.Figure)

    def test_leader_members_chart_duplicate_leaders(self):
        """Leaders with same name in different areas should aggregate correctly."""
        df = pd.DataFrame({
            "leader_name": ["Ravi", "Ravi", "Suresh"],
            "lg_group": ["LG1", "LG2", "LG3"],
            "members": [10, 15, 20],
        })
        fig = leader_members_chart(df)
        assert isinstance(fig, go.Figure)

    def test_area_detail_table_nonexistent_area(self, sample_df_with_strength):
        """Non-existent area should return empty DataFrame."""
        result = area_detail_table(sample_df_with_strength, "NonExistentArea")
        assert len(result) == 0

    def test_area_detail_table_special_characters(self, sample_df_with_strength):
        """Areas with special characters should not cause errors."""
        df = sample_df_with_strength.copy()
        df.loc[df.index[0], "area"] = "Area (Test) & <Special>"
        result = area_detail_table(df, "Area (Test) & <Special>")
        assert len(result) == 1


class TestChartsEmptyDataFrame:
    """Test all chart functions with empty DataFrames."""

    def test_members_by_area_chart_empty(self):
        """Empty DataFrame should produce a valid chart."""
        df = pd.DataFrame(columns=["area", "families", "individuals", "members"])
        fig = members_by_area_chart(df)
        assert isinstance(fig, go.Figure)

    def test_groups_by_area_chart_empty(self):
        """Empty DataFrame should produce a valid chart."""
        df = pd.DataFrame(columns=["area", "lg_group"])
        fig = groups_by_area_chart(df)
        assert isinstance(fig, go.Figure)

    def test_strength_pie_chart_empty(self):
        """Empty DataFrame with strength column should produce a valid chart."""
        df = pd.DataFrame(columns=["strength"])
        fig = strength_pie_chart(df)
        assert isinstance(fig, go.Figure)

    def test_meeting_day_chart_empty(self):
        """Empty DataFrame should produce a valid chart."""
        df = pd.DataFrame(columns=["meeting_day"])
        fig = meeting_day_chart(df)
        assert isinstance(fig, go.Figure)

    def test_top_bottom_groups_chart_empty(self):
        """Empty DataFrame should produce a valid chart."""
        df = pd.DataFrame(columns=["leader_name", "area", "members"])
        fig = top_bottom_groups_chart(df)
        assert isinstance(fig, go.Figure)

    def test_leader_members_chart_empty(self):
        """Empty DataFrame should produce a valid chart."""
        df = pd.DataFrame(columns=["leader_name", "lg_group", "members"])
        fig = leader_members_chart(df)
        assert isinstance(fig, go.Figure)

    def test_top_bottom_fewer_than_5(self):
        """Fewer than 5 groups (2) should still produce a valid chart."""
        df = pd.DataFrame({
            "leader_name": ["L1", "L2"],
            "area": ["A1", "A2"],
            "members": [5, 25],
        })
        fig = top_bottom_groups_chart(df)
        assert isinstance(fig, go.Figure)
