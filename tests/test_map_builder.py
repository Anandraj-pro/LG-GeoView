"""Unit tests for src/map_builder.py."""

import folium

from src.map_builder import GROUP_COLORS, MAP_STYLES, build_detailed_map, build_map


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
