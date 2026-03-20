"""Unit tests for src/map_builder.py."""

import folium
import pandas as pd
from unittest.mock import patch

from src.map_builder import (
    GROUP_COLORS,
    build_kingdom_map,
    build_territory_map, build_advanced_territory_map,
    build_heatmap_layer, build_heatmap_map,
    generate_territory_kml,
    _compute_map_bounds, _apply_fixed_bounds,
    _convex_hull, _cross, _compute_voronoi_boundaries,
    _load_ward_data,
    TERRITORY_PALETTE, STRENGTH_TERRITORY,
)


class TestGroupColors:
    """Tests for GROUP_COLORS constant."""

    def test_group_colors_length(self):
        """GROUP_COLORS should have exactly 32 entries."""
        assert len(GROUP_COLORS) == 32


# ---------------------------------------------------------------------------
# Map bounds tests
# ---------------------------------------------------------------------------


class TestComputeMapBounds:
    """Tests for _compute_map_bounds."""

    def test_returns_center_and_bounds(self):
        """Should return a center point and bounds list."""
        center, bounds = _compute_map_bounds()
        assert len(center) == 2
        assert bounds is not None
        assert len(bounds) == 2  # [[south, west], [north, east]]
        assert bounds[0][0] < bounds[1][0]  # south < north
        assert bounds[0][1] < bounds[1][1]  # west < east

    def test_center_within_bounds(self):
        """Center should be within the bounds."""
        center, bounds = _compute_map_bounds()
        assert bounds[0][0] <= center[0] <= bounds[1][0]
        assert bounds[0][1] <= center[1] <= bounds[1][1]


class TestApplyFixedBounds:
    """Tests for _apply_fixed_bounds."""

    def test_sets_max_bounds(self):
        """Should set maxBounds on the map."""
        m = folium.Map()
        bounds = [[17.42, 78.26], [17.54, 78.51]]
        _apply_fixed_bounds(m, bounds)
        assert m.options["maxBounds"] == bounds
        assert m.options["minZoom"] == 12

    def test_none_bounds_does_nothing(self):
        """None bounds should not crash."""
        m = folium.Map()
        _apply_fixed_bounds(m, None)
        assert "maxBounds" not in m.options


# ---------------------------------------------------------------------------
# Kingdom map tests
# ---------------------------------------------------------------------------


class TestBuildKingdomMap:
    """Tests for build_kingdom_map."""

    def _make_summary(self, df):
        from src.data_loader import get_area_summary
        return get_area_summary(df)

    def test_returns_folium_map(self, sample_df):
        """Should return a folium.Map."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        m = build_kingdom_map(sample_df, summary)
        assert isinstance(m, folium.Map)

    def test_empty_df(self):
        """Empty DataFrame should return valid map."""
        df = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families",
            "individuals", "members", "meeting_day",
            "latitude", "longitude", "strength",
        ])
        summary = pd.DataFrame(columns=[
            "area", "total_groups", "total_members",
            "total_families", "avg_members", "latitude",
            "longitude", "strength",
        ])
        m = build_kingdom_map(df, summary)
        assert isinstance(m, folium.Map)

    def test_kingdom_legend_in_html(self, sample_df):
        """Kingdom map should contain kingdom legend."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Strong"
        summary = self._make_summary(sample_df)
        m = build_kingdom_map(sample_df, summary)
        html = m.get_root().render()
        assert "King's Kingdom" in html

    def test_kingdom_markers_present(self, sample_df):
        """Kingdom map should have markers for data rows."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        m = build_kingdom_map(sample_df, summary)
        children = list(m._children.values())
        markers = [c for c in children
                   if isinstance(c, folium.CircleMarker)]
        assert len(markers) > 0


# ---------------------------------------------------------------------------
# Voronoi / convex hull tests
# ---------------------------------------------------------------------------


class TestConvexHull:
    """Tests for _convex_hull and _cross."""

    def test_cross_product(self):
        """Cross product should compute correctly."""
        assert _cross((0, 0), (1, 0), (0, 1)) == 1
        assert _cross((0, 0), (0, 1), (1, 0)) == -1
        assert _cross((0, 0), (1, 1), (2, 2)) == 0

    def test_convex_hull_triangle(self):
        """Three non-collinear points should return all three."""
        pts = [(0, 0), (1, 0), (0, 1)]
        hull = _convex_hull(pts)
        assert len(hull) == 3

    def test_convex_hull_square(self):
        """Square with interior point should return 4 corners."""
        pts = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]
        hull = _convex_hull(pts)
        assert len(hull) == 4

    def test_convex_hull_single_point(self):
        """Single point returns single point."""
        hull = _convex_hull([(5, 5)])
        assert len(hull) == 1

    def test_convex_hull_empty(self):
        """Empty input returns empty."""
        hull = _convex_hull([])
        assert len(hull) == 0


class TestComputeVoronoiBoundaries:
    """Tests for _compute_voronoi_boundaries."""

    def test_two_centers(self):
        """Two centers should produce two boundary regions."""
        centers = [(17.49, 78.39), (17.50, 78.40)]
        bbox = (17.48, 17.51, 78.38, 78.41)
        boundaries = _compute_voronoi_boundaries(
            centers, bbox, grid_size=10)
        assert len(boundaries) == 2
        for idx, bnd in boundaries.items():
            assert len(bnd) >= 3  # each region is a polygon

    def test_single_center(self):
        """Single center should get all cells."""
        centers = [(17.49, 78.39)]
        bbox = (17.48, 17.50, 78.38, 78.40)
        boundaries = _compute_voronoi_boundaries(
            centers, bbox, grid_size=5)
        assert len(boundaries) == 1
        assert len(boundaries[0]) >= 3


# ---------------------------------------------------------------------------
# Territory map tests
# ---------------------------------------------------------------------------


class TestBuildTerritoryMap:
    """Tests for build_territory_map."""

    def _make_summary(self, df):
        from src.data_loader import get_area_summary
        return get_area_summary(df)

    def test_returns_folium_map(self, sample_df):
        """Should return a folium.Map."""
        summary = self._make_summary(sample_df)
        m = build_territory_map(sample_df, summary)
        assert isinstance(m, folium.Map)

    def test_empty_df(self):
        """Empty DataFrame should return valid map."""
        df = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families",
            "individuals", "members", "meeting_day",
            "latitude", "longitude",
        ])
        summary = pd.DataFrame(columns=[
            "area", "total_groups", "total_members",
            "total_families", "avg_members", "latitude",
            "longitude", "strength",
        ])
        m = build_territory_map(df, summary)
        assert isinstance(m, folium.Map)

    def test_custom_center_area(self, sample_df):
        """Should accept custom center area."""
        summary = self._make_summary(sample_df)
        m = build_territory_map(
            sample_df, summary, center_area="KPHB")
        assert isinstance(m, folium.Map)


# ---------------------------------------------------------------------------
# Advanced territory map tests
# ---------------------------------------------------------------------------


class TestBuildAdvancedTerritoryMap:
    """Tests for build_advanced_territory_map."""

    def _make_summary(self, df):
        from src.data_loader import get_area_summary
        return get_area_summary(df)

    def test_returns_folium_map(self, sample_df):
        """Should return a folium.Map."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        m = build_advanced_territory_map(sample_df, summary)
        assert isinstance(m, folium.Map)

    def test_color_by_strength(self, sample_df):
        """Color by strength should work."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Strong"
        summary = self._make_summary(sample_df)
        m = build_advanced_territory_map(
            sample_df, summary, color_by="strength")
        assert isinstance(m, folium.Map)

    def test_color_by_density(self, sample_df):
        """Color by density should work."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Weak"
        summary = self._make_summary(sample_df)
        m = build_advanced_territory_map(
            sample_df, summary, color_by="density")
        assert isinstance(m, folium.Map)

    def test_layers_parameter(self, sample_df):
        """Map should accept layers config."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        layers = {"boundaries": True, "markers": False,
                  "gaps": True, "strength": False, "density": False,
                  "heatmap": False}
        m = build_advanced_territory_map(
            sample_df, summary, layers=layers)
        assert isinstance(m, folium.Map)

    def test_heatmap_layer(self, sample_df):
        """Heatmap layer should work when enabled."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        layers = {"boundaries": True, "markers": True,
                  "gaps": False, "strength": False, "density": False,
                  "heatmap": True}
        m = build_advanced_territory_map(
            sample_df, summary, layers=layers)
        assert isinstance(m, folium.Map)

    def test_empty_df(self):
        """Empty DataFrame should return valid map."""
        df = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families",
            "individuals", "members", "meeting_day",
            "latitude", "longitude", "strength",
        ])
        summary = pd.DataFrame(columns=[
            "area", "total_groups", "total_members",
            "total_families", "avg_members", "latitude",
            "longitude", "strength",
        ])
        m = build_advanced_territory_map(df, summary)
        assert isinstance(m, folium.Map)


# ---------------------------------------------------------------------------
# Heatmap tests
# ---------------------------------------------------------------------------


class TestBuildHeatmapLayer:
    """Tests for build_heatmap_layer."""

    def test_returns_correct_format(self, sample_df):
        """Should return list of [lat, lng, weight] lists."""
        result = build_heatmap_layer(sample_df)
        assert isinstance(result, list)
        assert len(result) == len(sample_df)
        for item in result:
            assert len(item) == 3
            assert isinstance(item[0], float)
            assert isinstance(item[1], float)
            assert isinstance(item[2], int)

    def test_weights_match_members(self, sample_df):
        """Weights should match member counts."""
        result = build_heatmap_layer(sample_df)
        for i, (_, row) in enumerate(sample_df.iterrows()):
            assert result[i][2] == int(row["members"])

    def test_empty_dataframe(self):
        """Empty DataFrame should return empty list."""
        df = pd.DataFrame(columns=[
            "latitude", "longitude", "members",
        ])
        result = build_heatmap_layer(df)
        assert result == []


class TestBuildHeatmapMap:
    """Tests for build_heatmap_map."""

    def test_returns_folium_map(self, sample_df):
        """Should return a folium.Map."""
        m = build_heatmap_map(sample_df)
        assert isinstance(m, folium.Map)

    def test_empty_df_returns_map(self):
        """Empty DataFrame should return valid map without heatmap."""
        df = pd.DataFrame(columns=[
            "area", "lg_group", "leader_name", "families",
            "individuals", "members", "meeting_day",
            "latitude", "longitude",
        ])
        m = build_heatmap_map(df)
        assert isinstance(m, folium.Map)

    def test_map_has_bounds(self, sample_df):
        """Heatmap map should have maxBounds set."""
        m = build_heatmap_map(sample_df)
        assert "maxBounds" in m.options


# ---------------------------------------------------------------------------
# Ward data loading tests
# ---------------------------------------------------------------------------


class TestLoadWardData:
    """Tests for _load_ward_data."""

    def test_loads_successfully(self):
        """Should load ward boundaries and mapping."""
        boundaries, mapping = _load_ward_data()
        # May or may not have data depending on files
        assert isinstance(boundaries, dict)
        assert isinstance(mapping, dict)

    def test_returns_empty_on_missing_file(self):
        """Should return empty dicts if files are missing."""
        with patch("builtins.open",
                   side_effect=FileNotFoundError("missing")):
            boundaries, mapping = _load_ward_data()
            assert boundaries == {}
            assert mapping == {}


# ---------------------------------------------------------------------------
# KML export tests
# ---------------------------------------------------------------------------


class TestGenerateKML:
    """Tests for generate_territory_kml."""

    def test_generates_valid_kml(self, sample_df):
        """Should generate KML with correct structure."""
        from src.data_loader import get_area_summary
        summary = get_area_summary(sample_df)
        kml = generate_territory_kml(sample_df, summary)

        assert kml.startswith('<?xml version="1.0"')
        assert "<kml" in kml
        assert "</kml>" in kml
        assert "<Document>" in kml
        assert "<Placemark>" in kml
        assert "LG GeoView Territories" in kml

    def test_contains_area_names(self, sample_df):
        """KML should contain area names from data."""
        from src.data_loader import get_area_summary
        summary = get_area_summary(sample_df)
        kml = generate_territory_kml(sample_df, summary)

        for area in sample_df["area"].unique():
            assert area in kml

    def test_contains_leader_names(self, sample_df):
        """KML should contain leader names."""
        from src.data_loader import get_area_summary
        summary = get_area_summary(sample_df)
        kml = generate_territory_kml(sample_df, summary)

        for leader in sample_df["leader_name"].unique():
            assert leader in kml

    def test_contains_coordinates(self, sample_df):
        """KML should contain coordinate elements."""
        from src.data_loader import get_area_summary
        summary = get_area_summary(sample_df)
        kml = generate_territory_kml(sample_df, summary)
        assert "<coordinates>" in kml


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------


class TestTerritoryConstants:
    """Tests for territory-related constants."""

    def test_territory_palette_length(self):
        """Palette should have at least 18 colors."""
        assert len(TERRITORY_PALETTE) >= 18

    def test_territory_palette_structure(self):
        """Each palette entry should have fill and border."""
        for entry in TERRITORY_PALETTE:
            assert "fill" in entry
            assert "border" in entry

    def test_strength_territory_keys(self):
        """Strength territory should have Strong/Medium/Weak."""
        assert "Strong" in STRENGTH_TERRITORY
        assert "Medium" in STRENGTH_TERRITORY
        assert "Weak" in STRENGTH_TERRITORY
