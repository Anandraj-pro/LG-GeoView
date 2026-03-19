"""Unit tests for src/map_builder.py."""

import folium
import pandas as pd
from unittest.mock import patch

from src.map_builder import (
    GROUP_COLORS, MAP_STYLES,
    build_map, build_detailed_map, build_kingdom_map,
    build_territory_map, build_advanced_territory_map,
    generate_territory_kml,
    _compute_map_bounds, _apply_fixed_bounds,
    _convex_hull, _cross, _compute_voronoi_boundaries,
    _load_ward_data,
    TERRITORY_PALETTE, STRENGTH_TERRITORY,
)


class TestBuildMap:
    """Tests for build_map."""

    def test_build_map_returns_folium_map(self, sample_df):
        """build_map should return a folium.Map object."""
        m = build_map(sample_df)
        assert isinstance(m, folium.Map)

    def test_build_map_empty_df(self, empty_df):
        """An empty DataFrame should still produce a valid folium.Map."""
        m = build_map(empty_df)
        assert isinstance(m, folium.Map)

    def test_build_map_marker_count(self, sample_df):
        """Map should contain children for each data row (CircleMarker + DivIcon Marker per row)."""
        m = build_map(sample_df)
        # Each row produces 2 children: a CircleMarker and a Marker (DivIcon label)
        # Plus the base tile layer. Count non-tile children.
        children = list(m._children.values())
        # Filter to only Marker and CircleMarker objects
        markers = [c for c in children if isinstance(c, (folium.CircleMarker, folium.Marker))]
        # 6 rows * 2 elements each = 12
        assert len(markers) == len(sample_df) * 2


class TestMapStyles:
    """Tests for MAP_STYLES."""

    def test_map_styles_all_valid(self, sample_df):
        """All MAP_STYLES keys should produce valid folium.Map objects."""
        for style_name in MAP_STYLES:
            m = build_map(sample_df, map_style=style_name)
            assert isinstance(m, folium.Map), f"Style '{style_name}' did not produce a valid map"


class TestBuildDetailedMap:
    """Tests for build_detailed_map."""

    def test_build_detailed_map_returns_map(self, sample_df):
        """build_detailed_map should return a folium.Map object."""
        m = build_detailed_map(sample_df)
        assert isinstance(m, folium.Map)


class TestGroupColors:
    """Tests for GROUP_COLORS constant."""

    def test_group_colors_length(self):
        """GROUP_COLORS should have exactly 32 entries."""
        assert len(GROUP_COLORS) == 32


class TestAddLegend:
    """Tests for _add_legend HTML content."""

    def test_legend_contains_all_groups(self, sample_df):
        """Legend HTML should contain entries for all unique groups."""
        m = build_map(sample_df)
        # Get the HTML of the map
        html = m.get_root().render()
        # Check that all leader names appear in the legend
        for _, row in sample_df.iterrows():
            assert row["leader_name"] in html

    def test_legend_contains_colors(self, sample_df):
        """Legend HTML should contain color codes."""
        m = build_map(sample_df)
        html = m.get_root().render()
        assert "&#9679;" in html  # bullet character in legend


class TestBuildDetailedMapEdgeCases:
    """Edge case tests for build_detailed_map."""

    def test_build_detailed_map_empty_df(self, empty_df):
        """Empty DataFrame should still return a valid map."""
        m = build_detailed_map(empty_df)
        assert isinstance(m, folium.Map)

    def test_build_detailed_map_marker_elements(self, sample_df):
        """Detailed map should have CircleMarker elements for each row."""
        m = build_detailed_map(sample_df)
        children = list(m._children.values())
        circle_markers = [c for c in children if isinstance(c, folium.CircleMarker)]
        # build_detailed_map creates 2 CircleMarkers per row (background + center dot)
        assert len(circle_markers) == len(sample_df) * 2

    def test_build_detailed_map_label_html(self, sample_df):
        """Detailed map labels should contain leader names."""
        m = build_detailed_map(sample_df)
        html = m.get_root().render()
        for _, row in sample_df.iterrows():
            assert row["leader_name"] in html

    def test_build_detailed_map_all_styles(self, sample_df):
        """All map styles should work with build_detailed_map."""
        for style_name in MAP_STYLES:
            m = build_detailed_map(sample_df, map_style=style_name)
            assert isinstance(m, folium.Map)


class TestColorCycling:
    """Test color assignment when groups exceed palette size."""

    def test_color_cycling_beyond_32(self):
        """When more than 32 groups exist, colors should cycle."""
        import pandas as pd
        # Create 35 unique groups
        data = []
        for i in range(35):
            data.append({
                "area": f"Area{i}",
                "lg_group": f"LG{i}",
                "leader_name": f"Leader{i}",
                "families": 5,
                "individuals": 5,
                "members": 10,
                "meeting_day": "Sunday",
                "latitude": 17.49 + i * 0.001,
                "longitude": 78.40 + i * 0.001,
            })
        df = pd.DataFrame(data)
        m = build_map(df)
        assert isinstance(m, folium.Map)
        # Should not crash — colors wrap around


class TestDetailedMapOffsets:
    """Test offset cycling in build_detailed_map."""

    def test_offset_cycling_wraps(self):
        """Offset cycling should wrap around after 4 entries."""
        import pandas as pd
        # Create 5 rows to test that offset index wraps (5 % 4 = 1)
        data = []
        for i in range(5):
            data.append({
                "area": f"Area{i}",
                "lg_group": f"LG{i}",
                "leader_name": f"Leader{i}",
                "families": 3,
                "individuals": 4,
                "members": 7,
                "meeting_day": "Sunday",
                "latitude": 17.49 + i * 0.002,
                "longitude": 78.40 + i * 0.002,
            })
        df = pd.DataFrame(data)
        m = build_detailed_map(df)
        assert isinstance(m, folium.Map)
        children = list(m._children.values())
        # 5 rows * 3 elements each (2 CircleMarkers + 1 Marker label) = 15
        markers = [c for c in children if isinstance(c, (folium.CircleMarker, folium.Marker))]
        assert len(markers) == 5 * 3


class TestLegendContent:
    """Test legend HTML content details."""

    def test_legend_contains_area_names(self, sample_df):
        """Legend should contain area names."""
        m = build_map(sample_df)
        html = m.get_root().render()
        for area in sample_df["area"].unique():
            assert area in html

    def test_legend_contains_care_groups_heading(self, sample_df):
        """Legend should contain 'Care Groups' heading."""
        m = build_map(sample_df)
        html = m.get_root().render()
        assert "Care Groups" in html

    def test_legend_contains_circle_size_note(self, sample_df):
        """Legend should contain the circle size explanation."""
        m = build_map(sample_df)
        html = m.get_root().render()
        assert "Circle size = member count" in html


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
        assert m.options["minZoom"] == 11

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

    def test_has_layer_control(self, sample_df):
        """Map should have LayerControl."""
        sample_df = sample_df.copy()
        sample_df["strength"] = "Medium"
        summary = self._make_summary(sample_df)
        m = build_advanced_territory_map(sample_df, summary)
        children = list(m._children.values())
        layer_controls = [c for c in children
                          if isinstance(c, folium.LayerControl)]
        assert len(layer_controls) == 1

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
