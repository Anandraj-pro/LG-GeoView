"""Unit tests for src/analytics.py."""

import pandas as pd

from src.analytics import (
    compute_kpi_metrics,
    compute_territory_coverage,
    generate_html_report,
    haversine_km,
)


class TestHaversineKm:
    """Tests for haversine_km distance calculation."""

    def test_same_point_returns_zero(self):
        """Distance from a point to itself should be 0."""
        assert haversine_km(17.4948, 78.3996, 17.4948, 78.3996) == 0.0

    def test_kukatpally_to_patancheru(self):
        """Kukatpally to Patancheru should be roughly 14-15 km."""
        # Kukatpally: 17.4948, 78.3996
        # Patancheru: 17.5322, 78.2640
        dist = haversine_km(17.4948, 78.3996, 17.5322, 78.2640)
        assert 14 <= dist <= 15

    def test_one_degree_at_equator(self):
        """Two points 1 degree apart at equator should be ~111 km."""
        dist = haversine_km(0.0, 0.0, 0.0, 1.0)
        assert 110 <= dist <= 112


class TestComputeTerritoryCoverage:
    """Tests for compute_territory_coverage."""

    def test_basic_coverage(self):
        """Should identify nearby areas and separate occupied from uncovered."""
        coords = {
            "kukatpally": (17.4948, 78.3996),
            "kphb": (17.4835, 78.3878),
            "kondapur": (17.4600, 78.3700),
            "faraway": (18.0000, 79.0000),
        }
        occupied = {"kukatpally", "kphb"}
        result = compute_territory_coverage("Kukatpally", 15, coords, occupied)
        # faraway should be excluded (too far)
        assert "faraway" not in result["nearby_set"]
        assert result["occupied_count"] == 2
        assert "Kondapur" in result["uncovered"]

    def test_all_covered(self):
        """When all nearby areas are occupied, uncovered should be empty."""
        coords = {
            "kukatpally": (17.4948, 78.3996),
            "kphb": (17.4835, 78.3878),
        }
        occupied = {"kukatpally", "kphb"}
        result = compute_territory_coverage("Kukatpally", 15, coords, occupied)
        assert result["uncovered"] == []
        assert result["occupied_count"] == result["total_nearby"]

    def test_unknown_focus_area_uses_default(self):
        """Unknown focus area should fall back to default center."""
        coords = {
            "kukatpally": (17.4948, 78.3996),
        }
        result = compute_territory_coverage("NonExistent", 15, coords, set())
        # Default center is (17.4948, 78.3996) — kukatpally should be nearby
        assert result["total_nearby"] >= 1

    def test_zero_radius(self):
        """Zero radius should return only the exact center area if it exists."""
        coords = {
            "kukatpally": (17.4948, 78.3996),
            "kphb": (17.4835, 78.3878),
        }
        result = compute_territory_coverage("Kukatpally", 0, coords, set())
        # Only kukatpally itself (distance = 0) should match
        assert result["total_nearby"] == 1
        assert "kukatpally" in result["nearby_set"]

    def test_empty_coordinates(self):
        """Empty coordinates dict should return empty results."""
        result = compute_territory_coverage("Kukatpally", 15, {}, set())
        assert result["total_nearby"] == 0
        assert result["occupied_count"] == 0
        assert result["uncovered"] == []


class TestComputeKpiMetrics:
    """Tests for compute_kpi_metrics."""

    def test_basic_kpis(self, sample_df):
        """Should compute correct KPI values from sample data."""
        from src.data_loader import assign_strength
        df = assign_strength(sample_df)
        metrics = compute_kpi_metrics(df)
        assert metrics["total_groups"] == 6
        assert metrics["num_areas"] == 3
        assert metrics["total_members"] == 12 + 30 + 8 + 21 + 14 + 19
        assert metrics["total_families"] == 5 + 8 + 3 + 6 + 4 + 2
        assert metrics["avg_per_group"] == metrics["total_members"] / 6

    def test_empty_df(self):
        """Empty DataFrame should return zero metrics."""
        df = pd.DataFrame(columns=[
            "families", "individuals", "members", "area", "strength",
        ])
        metrics = compute_kpi_metrics(df)
        assert metrics["total_groups"] == 0
        assert metrics["total_members"] == 0
        assert metrics["avg_per_group"] == 0

    def test_single_row(self):
        """Single row should produce correct metrics."""
        df = pd.DataFrame({
            "families": [5],
            "individuals": [7],
            "members": [12],
            "area": ["Kukatpally"],
            "strength": ["Weak"],
        })
        metrics = compute_kpi_metrics(df)
        assert metrics["total_groups"] == 1
        assert metrics["total_members"] == 12
        assert metrics["strong_count"] == 0
        assert metrics["weak_count"] == 1

    def test_strength_counts(self):
        """Should correctly count Strong and Weak groups."""
        df = pd.DataFrame({
            "families": [5, 8, 3],
            "individuals": [7, 22, 5],
            "members": [12, 30, 8],
            "area": ["A", "B", "C"],
            "strength": ["Weak", "Strong", "Weak"],
        })
        metrics = compute_kpi_metrics(df)
        assert metrics["strong_count"] == 1
        assert metrics["weak_count"] == 2


class TestGenerateHtmlReport:
    """Tests for generate_html_report."""

    def test_returns_string(self):
        """Should return a string."""
        df = pd.DataFrame({
            "area": ["A"], "lg_group": ["LG1"], "leader_name": ["L1"],
            "families": [5], "individuals": [7], "members": [12],
            "meeting_day": ["Sunday"],
        })
        summary = pd.DataFrame({
            "area": ["A"], "total_groups": [1], "total_families": [5],
            "total_members": [12], "avg_members": [12.0], "strength": ["Weak"],
        })
        kpi = {"num_areas": 1, "total_groups": 1, "total_members": 12,
               "total_families": 5, "strong_count": 0}
        result = generate_html_report(df, summary, kpi)
        assert isinstance(result, str)

    def test_contains_html_structure(self):
        """Should contain basic HTML structure."""
        df = pd.DataFrame({
            "area": ["A"], "lg_group": ["LG1"], "leader_name": ["L1"],
            "families": [5], "individuals": [7], "members": [12],
            "meeting_day": ["Sunday"],
        })
        summary = pd.DataFrame({
            "area": ["A"], "total_groups": [1], "total_families": [5],
            "total_members": [12], "avg_members": [12.0], "strength": ["Weak"],
        })
        kpi = {"num_areas": 1, "total_groups": 1, "total_members": 12,
               "total_families": 5, "strong_count": 0}
        result = generate_html_report(df, summary, kpi)
        assert "<!DOCTYPE html>" in result
        assert "TKT Kingdom" in result
        assert "</html>" in result

    def test_includes_kpi_values(self):
        """Should include KPI values in the report."""
        df = pd.DataFrame({
            "area": ["A"], "lg_group": ["LG1"], "leader_name": ["L1"],
            "families": [5], "individuals": [7], "members": [12],
            "meeting_day": ["Sunday"],
        })
        summary = pd.DataFrame({
            "area": ["A"], "total_groups": [1], "total_families": [5],
            "total_members": [12], "avg_members": [12.0], "strength": ["Weak"],
        })
        kpi = {"num_areas": 3, "total_groups": 10, "total_members": 99,
               "total_families": 42, "strong_count": 5}
        result = generate_html_report(df, summary, kpi)
        assert "99" in result
        assert "42" in result

    def test_empty_dataframes(self):
        """Should handle empty DataFrames without errors."""
        df = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families",
            "individuals", "members", "meeting_day",
        ])
        summary = pd.DataFrame(columns=[
            "area", "total_groups", "total_families",
            "total_members", "avg_members", "strength",
        ])
        kpi = {"num_areas": 0, "total_groups": 0, "total_members": 0,
               "total_families": 0, "strong_count": 0}
        result = generate_html_report(df, summary, kpi)
        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result
