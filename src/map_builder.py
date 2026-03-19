"""Map visualization module using Folium (Google Maps-style background)."""

import time

import folium
import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)

# Hyderabad West center
HYDERABAD_CENTER = [17.470, 78.410]
DEFAULT_ZOOM = 12

# 32 distinct colors — one per care group, no repeats
GROUP_COLORS = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#fffac8", "#800000", "#aaffc3",
    "#808000", "#ffd8b1", "#000075", "#a9a9a9", "#e6beff",
    "#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e",
    "#16a085", "#27ae60", "#2980b9", "#8e44ad", "#2c3e50",
    "#f39c12", "#d35400",
]

# Map tile options
MAP_STYLES = {
    "Google Maps": {
        "tiles": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "attr": "Google Maps",
    },
    "Google Satellite": {
        "tiles": "https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}",
        "attr": "Google Satellite",
    },
    "Google Terrain": {
        "tiles": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "attr": "Google Terrain",
    },
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None,
    },
}


def build_map(df: pd.DataFrame, map_style: str = None) -> folium.Map:
    """Build a Folium map with Google Maps background and colored markers."""
    t0 = time.perf_counter()
    style_key = map_style or "Google Maps"
    style = MAP_STYLES.get(style_key, MAP_STYLES["Google Maps"])

    logger.info("Building overview map with %d markers, style=%s", len(df), style_key)

    # Create base map
    if style["tiles"] == "OpenStreetMap":
        m = folium.Map(
            location=HYDERABAD_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles="OpenStreetMap",
        )
    else:
        m = folium.Map(
            location=HYDERABAD_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles=style["tiles"],
            attr=style["attr"],
        )

    if df.empty:
        return m

    # Assign a unique color to each care group
    group_color_map = {}
    for idx, (_, row) in enumerate(df.iterrows()):
        group_key = f"{row['leader_name']}_{row['area']}"
        if group_key not in group_color_map:
            group_color_map[group_key] = GROUP_COLORS[len(group_color_map) % len(GROUP_COLORS)]

    # Add markers for each LG group
    for idx, (_, row) in enumerate(df.iterrows()):
        members = int(row["members"])
        families = int(row.get("families", 0))
        individuals = int(row.get("individuals", 0))
        meeting_day = row.get("meeting_day", "")
        group_key = f"{row['leader_name']}_{row['area']}"
        marker_color = group_color_map[group_key]

        # Popup with detailed info
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;
             background: white; color: #333; padding: 10px; border-radius: 6px;">
            <h4 style="margin: 0 0 8px 0; color: #2c3e50;">{row['area']}</h4>
            <table style="font-size: 13px; border-collapse: collapse; color: #333;">
                <tr><td style="padding: 3px 8px 3px 0; color: #7f8c8d;"><b>Leader</b></td>
                    <td style="padding: 3px 0; color: #333;">{row['leader_name']}</td></tr>
                <tr><td style="padding: 3px 8px 3px 0; color: #7f8c8d;"><b>Families</b></td>
                    <td style="padding: 3px 0; color: #333;">{families}</td></tr>
                <tr><td style="padding: 3px 8px 3px 0; color: #7f8c8d;"><b>Individuals</b></td>
                    <td style="padding: 3px 0; color: #333;">{individuals}</td></tr>
                <tr><td style="padding: 3px 8px 3px 0; color: #7f8c8d;"><b>Total</b></td>
                    <td style="padding: 3px 0; color: #333;"><b>{members}</b></td></tr>
                <tr><td style="padding: 3px 8px 3px 0; color: #7f8c8d;"><b>Meeting</b></td>
                    <td style="padding: 3px 0; color: #333;">{meeting_day}</td></tr>
            </table>
        </div>
        """

        # Tooltip on hover
        tooltip_text = f"{row['area']} | {row['leader_name']} | {members} members"

        # Circle marker with unique color per group
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(10, members * 0.6),
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=tooltip_text,
        ).add_to(m)

        # Add member count as text label on the marker
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-size: 11px;
                    font-weight: bold;
                    color: white;
                    text-align: center;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    width: 30px;
                    margin-left: -15px;
                    margin-top: -8px;
                ">{members}</div>
                """,
                icon_size=(30, 16),
            ),
        ).add_to(m)

    # Add legend with group colors
    _add_legend(m, group_color_map, df)

    elapsed = time.perf_counter() - t0
    logger.info("Overview map built: %d markers in %.3fs", len(df), elapsed)
    return m


def build_detailed_map(df: pd.DataFrame, map_style: str = None) -> folium.Map:
    """Build a detailed map with always-visible labels — no hover needed."""
    t0 = time.perf_counter()
    style_key = map_style or "Google Maps"
    style = MAP_STYLES.get(style_key, MAP_STYLES["Google Maps"])

    logger.info("Building detailed map with %d markers", len(df))

    if style["tiles"] == "OpenStreetMap":
        m = folium.Map(
            location=HYDERABAD_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles="OpenStreetMap",
        )
    else:
        m = folium.Map(
            location=HYDERABAD_CENTER,
            zoom_start=DEFAULT_ZOOM,
            tiles=style["tiles"],
            attr=style["attr"],
        )

    if df.empty:
        return m

    # Assign unique colors
    group_color_map = {}
    for _, row in df.iterrows():
        group_key = f"{row['leader_name']}_{row['area']}"
        if group_key not in group_color_map:
            group_color_map[group_key] = GROUP_COLORS[len(group_color_map) % len(GROUP_COLORS)]

    # Stagger positions: alternate label direction to reduce overlap
    # 4 positions: right, left, bottom-right, top-right
    offsets = [
        {"margin_left": "12px", "margin_top": "-28px", "anchor": (0, 30)},     # right
        {"margin_left": "-210px", "margin_top": "-28px", "anchor": (200, 30)},  # left
        {"margin_left": "12px", "margin_top": "10px", "anchor": (0, 0)},       # bottom-right
        {"margin_left": "-210px", "margin_top": "10px", "anchor": (200, 0)},   # top-left
    ]

    for idx, (_, row) in enumerate(df.iterrows()):
        members = int(row["members"])
        families = int(row.get("families", 0))
        individuals = int(row.get("individuals", 0))
        meeting_day = row.get("meeting_day", "")
        group_key = f"{row['leader_name']}_{row['area']}"
        marker_color = group_color_map[group_key]
        offset = offsets[idx % len(offsets)]

        # Circle marker (background)
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(12, members * 0.7),
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.25,
            weight=3,
        ).add_to(m)

        # Small dot at center for precise location
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=1,
            weight=0,
        ).add_to(m)

        # Always-visible label card
        label_html = f"""
        <div style="
            font-family: Arial, sans-serif;
            background: white;
            border-left: 4px solid {marker_color};
            border-radius: 4px;
            padding: 4px 7px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            white-space: nowrap;
            min-width: 120px;
            max-width: 195px;
            margin-left: {offset['margin_left']};
            margin-top: {offset['margin_top']};
        ">
            <div style="font-size: 11px; font-weight: bold; color: #222;
                 margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis;">
                {row['leader_name']}
            </div>
            <div style="font-size: 10px; color: #666; margin-bottom: 2px;">
                {row['area']}
            </div>
            <div style="font-size: 10px; color: #333;">
                <span style="color: {marker_color}; font-weight: bold;">{members}</span> mbrs
                &nbsp;| {families} fam
                &nbsp;| {individuals} ind
            </div>
            <div style="font-size: 9px; color: #999; margin-top: 1px;">
                {meeting_day}
            </div>
        </div>
        """

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(210, 70),
                icon_anchor=offset["anchor"],
            ),
        ).add_to(m)

    elapsed = time.perf_counter() - t0
    logger.info("Detailed map built: %d markers in %.3fs", len(df), elapsed)
    return m


def _add_legend(m: folium.Map, group_color_map: dict, df: pd.DataFrame):
    """Add a color legend to the map showing each care group with its unique color."""
    # Build legend entries from the dataframe to show leader + area
    legend_items = ""
    seen = set()
    for _, row in df.iterrows():
        group_key = f"{row['leader_name']}_{row['area']}"
        if group_key in seen:
            continue
        seen.add(group_key)
        color = group_color_map[group_key]
        label = f"{row['leader_name']} — {row['area']}"
        legend_items += (
            f'<span style="color: {color}; font-size: 16px;">&#9679;</span> '
            f'<span style="color: #333; font-size: 11px;">{label}</span><br>\n'
        )

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 30px;
        right: 10px;
        z-index: 1000;
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-family: Arial, sans-serif;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
        min-width: 200px;
    ">
        <b style="font-size: 13px; color: #333;">Care Groups</b><br><br>
        {legend_items}
        <br><small style="color: #666;">Circle size = member count</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
