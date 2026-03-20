"""Unit tests for src/analytics.py."""

import pandas as pd

from src.analytics import (
    compute_coverage_scores,
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


class TestComputeCoverageScores:
    """Tests for compute_coverage_scores."""

    def _make_summary(self, rows):
        """Helper to create a summary DataFrame from list of dicts."""
        return pd.DataFrame(rows)

    def test_basic_score_calculation(self):
        """Verify score calculation with known values."""
        summary = self._make_summary([{
            "area": "TestArea",
            "total_members": 30,
            "total_groups": 2,
            "avg_members": 15.0,
        }])
        result = compute_coverage_scores(summary)
        # members_score = min(100, 30/30*100) = 100
        # groups_score = min(100, 2/2*100) = 100
        # avg_score = min(100, 15/20*100) = 75
        # final = 100*0.4 + 100*0.4 + 75*0.2 = 40 + 40 + 15 = 95
        assert result["coverage_score"].iloc[0] == 95.0
        assert result["coverage_level"].iloc[0] == "Well Served"
        assert result["coverage_color"].iloc[0] == "#2E7D32"

    def test_high_members_scores_high(self):
        """Area with 30+ members, 2+ groups should score >= 70 (green)."""
        summary = self._make_summary([{
            "area": "HighArea",
            "total_members": 50,
            "total_groups": 3,
            "avg_members": 25.0,
        }])
        result = compute_coverage_scores(summary)
        assert result["coverage_score"].iloc[0] >= 70
        assert result["coverage_level"].iloc[0] == "Well Served"

    def test_zero_members_scores_zero(self):
        """Area with 0 members should score 0."""
        summary = self._make_summary([{
            "area": "EmptyArea",
            "total_members": 0,
            "total_groups": 0,
            "avg_members": 0.0,
        }])
        result = compute_coverage_scores(summary)
        assert result["coverage_score"].iloc[0] == 0.0
        assert result["coverage_level"].iloc[0] == "Underserved"
        assert result["coverage_color"].iloc[0] == "#C62828"

    def test_green_boundary_at_70(self):
        """Score exactly 70 should be classified as Well Served (green)."""
        # We need: members_score*0.4 + groups_score*0.4 + avg_score*0.2 = 70
        # If members=21 -> members_score=min(100,21/30*100)=70
        # groups=1.4 -> groups_score=min(100,1.4/2*100)=70 (but groups is int)
        # Let's pick values that give exactly 70:
        # members=21 -> 70, groups=2 -> 100, avg=0 -> 0
        # final = 70*0.4 + 100*0.4 + 0*0.2 = 28+40+0 = 68 -- not 70
        # members=21 -> 70, groups=2 -> 100, avg=2 -> 10
        # final = 70*0.4 + 100*0.4 + 10*0.2 = 28+40+2 = 70
        summary = self._make_summary([{
            "area": "BoundaryGreen",
            "total_members": 21,
            "total_groups": 2,
            "avg_members": 2.0,
        }])
        result = compute_coverage_scores(summary)
        assert result["coverage_score"].iloc[0] == 70.0
        assert result["coverage_level"].iloc[0] == "Well Served"

    def test_yellow_boundary_at_40(self):
        """Score exactly 40 should be classified as Partial (yellow)."""
        # members=12 -> 12/30*100 = 40, groups=0 -> 0, avg=0 -> 0
        # final = 40*0.4 + 0*0.4 + 0*0.2 = 16 -- too low
        # members=12 -> 40, groups=1 -> 50, avg=12 -> 60
        # final = 40*0.4 + 50*0.4 + 60*0.2 = 16+20+12 = 48 -- too high
        # Need exactly 40: try members=12(40), groups=1(50), avg=0(0)
        # final = 40*0.4 + 50*0.4 + 0*0.2 = 16+20+0 = 36 -- too low
        # members=15(50), groups=1(50), avg=0(0)
        # final = 50*0.4 + 50*0.4 + 0*0.2 = 20+20+0 = 40
        summary = self._make_summary([{
            "area": "BoundaryYellow",
            "total_members": 15,
            "total_groups": 1,
            "avg_members": 0.0,
        }])
        result = compute_coverage_scores(summary)
        assert result["coverage_score"].iloc[0] == 40.0
        assert result["coverage_level"].iloc[0] == "Partial"
        assert result["coverage_color"].iloc[0] == "#F9A825"

    def test_red_below_40(self):
        """Score below 40 should be Underserved (red)."""
        summary = self._make_summary([{
            "area": "LowArea",
            "total_members": 5,
            "total_groups": 1,
            "avg_members": 5.0,
        }])
        result = compute_coverage_scores(summary)
        # members_score = 5/30*100 = 16.67
        # groups_score = 1/2*100 = 50
        # avg_score = 5/20*100 = 25
        # final = 16.67*0.4 + 50*0.4 + 25*0.2 = 6.67+20+5 = 31.67
        assert result["coverage_score"].iloc[0] < 40
        assert result["coverage_level"].iloc[0] == "Underserved"
        assert result["coverage_color"].iloc[0] == "#C62828"

    def test_empty_dataframe(self):
        """Empty DataFrame should return empty with added columns."""
        summary = pd.DataFrame(columns=[
            "area", "total_members", "total_groups", "avg_members",
        ])
        result = compute_coverage_scores(summary)
        assert len(result) == 0
        assert "coverage_score" in result.columns
        assert "coverage_level" in result.columns
        assert "coverage_color" in result.columns

    def test_multiple_areas_mixed_levels(self):
        """Multiple areas should be independently classified."""
        summary = self._make_summary([
            {"area": "Strong", "total_members": 60,
             "total_groups": 4, "avg_members": 25.0},
            {"area": "Medium", "total_members": 15,
             "total_groups": 1, "avg_members": 15.0},
            {"area": "Weak", "total_members": 3,
             "total_groups": 1, "avg_members": 3.0},
        ])
        result = compute_coverage_scores(summary)
        levels = result.set_index("area")["coverage_level"]
        assert levels["Strong"] == "Well Served"
        assert levels["Weak"] == "Underserved"

    def test_score_caps_at_100_per_component(self):
        """Scores should not exceed 100 per component even with large values."""
        summary = self._make_summary([{
            "area": "Huge",
            "total_members": 200,
            "total_groups": 10,
            "avg_members": 50.0,
        }])
        result = compute_coverage_scores(summary)
        # All components capped at 100
        # final = 100*0.4 + 100*0.4 + 100*0.2 = 100
        assert result["coverage_score"].iloc[0] == 100.0


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
