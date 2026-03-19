"""Map visualization module using Folium (Google Maps-style background)."""

import os
import time

import folium
import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)

# Hyderabad West center
HYDERABAD_CENTER = [17.480, 78.385]
DEFAULT_ZOOM = 12

# Padding added around the outermost area coordinates
BOUNDS_PADDING = 0.015


def _compute_map_bounds():
    """Compute map bounds dynamically from area coordinates.

    Auto-expands when new areas are added to area_coordinates.json.
    Returns (center, bounds) where bounds = [[south, west], [north, east]].
    """
    from src.data_loader import AREA_COORDINATES
    if not AREA_COORDINATES:
        return HYDERABAD_CENTER, None

    lats = [c[0] for c in AREA_COORDINATES.values()]
    lngs = [c[1] for c in AREA_COORDINATES.values()]

    south = min(lats) - BOUNDS_PADDING
    north = max(lats) + BOUNDS_PADDING
    west = min(lngs) - BOUNDS_PADDING
    east = max(lngs) + BOUNDS_PADDING

    center = [(south + north) / 2, (west + east) / 2]
    bounds = [[south, west], [north, east]]
    return center, bounds


def _apply_fixed_bounds(m, bounds):
    """Lock map to fixed bounds — users can't pan outside the region."""
    if bounds:
        m.fit_bounds(bounds)
        m.options["maxBounds"] = bounds
        m.options["minZoom"] = 11


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

    center, bounds = _compute_map_bounds()

    # Create base map
    if style["tiles"] == "OpenStreetMap":
        m = folium.Map(
            location=center,
            zoom_start=DEFAULT_ZOOM,
            tiles="OpenStreetMap",
        )
    else:
        m = folium.Map(
            location=center,
            zoom_start=DEFAULT_ZOOM,
            tiles=style["tiles"],
            attr=style["attr"],
        )

    _apply_fixed_bounds(m, bounds)

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

    center, bounds = _compute_map_bounds()

    if style["tiles"] == "OpenStreetMap":
        m = folium.Map(
            location=center,
            zoom_start=DEFAULT_ZOOM,
            tiles="OpenStreetMap",
        )
    else:
        m = folium.Map(
            location=center,
            zoom_start=DEFAULT_ZOOM,
            tiles=style["tiles"],
            attr=style["attr"],
        )

    _apply_fixed_bounds(m, bounds)

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


# --- Strength colors for Kingdom map ---
STRENGTH_GLOW = {
    "Strong": {"fill": "#D4AF37", "border": "#FFD700", "glow": "rgba(212,175,55,0.45)"},
    "Medium": {"fill": "#C0A060", "border": "#DAA520", "glow": "rgba(192,160,96,0.30)"},
    "Weak":   {"fill": "#8B6914", "border": "#A0822A", "glow": "rgba(139,105,20,0.20)"},
}


def build_kingdom_map(df: pd.DataFrame, summary_df: pd.DataFrame,
                      map_style: str = None) -> folium.Map:
    """Build the King's Kingdom map — dark terrain with golden territory markers."""
    t0 = time.perf_counter()
    logger.info("Building King's Kingdom map with %d markers", len(df))

    center, bounds = _compute_map_bounds()

    # Dark tile layer for kingdom aesthetic
    m = folium.Map(
        location=center,
        zoom_start=DEFAULT_ZOOM,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Dark Matter",
    )

    _apply_fixed_bounds(m, bounds)

    if df.empty:
        return m

    # --- Territory reach circles (area-level) ---
    for _, area_row in summary_df.iterrows():
        strength = area_row.get("strength", "Weak")
        colors = STRENGTH_GLOW.get(strength, STRENGTH_GLOW["Weak"])
        total_members = int(area_row["total_members"])
        total_groups = int(area_row["total_groups"])

        # Outer glow — territory reach
        reach_radius = max(600, total_members * 25)
        folium.Circle(
            location=[area_row["latitude"], area_row["longitude"]],
            radius=reach_radius,
            color=colors["border"],
            fill=True,
            fill_color=colors["glow"],
            fill_opacity=0.15,
            weight=1,
            dash_array="6 4",
        ).add_to(m)

        # Inner territory circle
        folium.Circle(
            location=[area_row["latitude"], area_row["longitude"]],
            radius=reach_radius * 0.5,
            color=colors["fill"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=0.08,
            weight=1,
        ).add_to(m)

        # Area territory label
        territory_html = f"""
        <div style="
            font-family: 'Cinzel', 'Palatino Linotype', 'Book Antiqua', serif;
            color: {colors['border']};
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 0 8px rgba(0,0,0,0.9), 0 0 20px {colors['glow']};
            text-align: center;
            white-space: nowrap;
            pointer-events: none;
        ">{area_row['area']}</div>
        """
        folium.Marker(
            location=[area_row["latitude"] + 0.006, area_row["longitude"]],
            icon=folium.DivIcon(
                html=territory_html,
                icon_size=(200, 20),
                icon_anchor=(100, 10),
            ),
        ).add_to(m)

        # Territory stats below area name
        stats_html = f"""
        <div style="
            font-family: 'Cinzel', 'Palatino Linotype', serif;
            color: #BFA76A;
            font-size: 10px;
            letter-spacing: 1px;
            text-shadow: 0 0 6px rgba(0,0,0,0.9);
            text-align: center;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0.8;
        ">{total_groups} shepherds &middot; {total_members} souls</div>
        """
        folium.Marker(
            location=[area_row["latitude"] + 0.004, area_row["longitude"]],
            icon=folium.DivIcon(
                html=stats_html,
                icon_size=(200, 16),
                icon_anchor=(100, 8),
            ),
        ).add_to(m)

    # --- Individual group markers ---
    for _, row in df.iterrows():
        members = int(row["members"])
        strength = row.get("strength", "Weak")
        colors = STRENGTH_GLOW.get(strength, STRENGTH_GLOW["Weak"])

        # Golden marker circle
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(7, members * 0.5),
            color=colors["border"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=0.85,
            weight=2,
        ).add_to(m)

        # Center bright dot
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            color="#FFFFFF",
            fill=True,
            fill_color="#FFD700",
            fill_opacity=1.0,
            weight=0,
        ).add_to(m)

        # Popup
        popup_html = f"""
        <div style="font-family: 'Palatino Linotype', 'Book Antiqua', serif;
             min-width: 180px; background: #1a1a2e; color: #d4af37;
             padding: 12px 14px; border-radius: 8px;
             border: 1px solid #d4af3744;">
            <div style="font-size: 14px; font-weight: bold;
                 letter-spacing: 1px; margin-bottom: 6px;
                 border-bottom: 1px solid #d4af3733; padding-bottom: 6px;">
                {row['area']}
            </div>
            <table style="font-size: 12px; border-collapse: collapse; width: 100%;">
                <tr><td style="color: #BFA76A; padding: 2px 0;">Shepherd</td>
                    <td style="color: #E8D5A3; text-align: right;">{row['leader_name']}</td></tr>
                <tr><td style="color: #BFA76A; padding: 2px 0;">Families</td>
                    <td style="color: #E8D5A3; text-align: right;">{int(row.get('families', 0))}</td></tr>
                <tr><td style="color: #BFA76A; padding: 2px 0;">Individuals</td>
                    <td style="color: #E8D5A3; text-align: right;">{int(row.get('individuals', 0))}</td></tr>
                <tr><td style="color: #BFA76A; padding: 2px 0;">Total Souls</td>
                    <td style="color: #FFD700; font-weight: bold; text-align: right;">{members}</td></tr>
                <tr><td style="color: #BFA76A; padding: 2px 0;">Gathering</td>
                    <td style="color: #E8D5A3; text-align: right;">{row.get('meeting_day', '')}</td></tr>
            </table>
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(7, members * 0.5),
            color="transparent",
            fill=False,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{row['leader_name']} \u2014 {members} souls",
        ).add_to(m)

    # --- Kingdom legend ---
    _add_kingdom_legend(m, summary_df)

    elapsed = time.perf_counter() - t0
    logger.info("Kingdom map built: %d markers in %.3fs", len(df), elapsed)
    return m


def _add_kingdom_legend(m: folium.Map, summary_df: pd.DataFrame):
    """Add a regal legend to the Kingdom map."""
    total_areas = len(summary_df)
    total_groups = int(summary_df["total_groups"].sum())
    total_members = int(summary_df["total_members"].sum())

    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 20px;
        right: 10px;
        z-index: 1000;
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        color: #d4af37;
        padding: 16px 20px;
        border-radius: 10px;
        border: 1px solid #d4af3744;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6), inset 0 1px 0 rgba(212,175,55,0.1);
        font-family: 'Palatino Linotype', 'Book Antiqua', 'Cinzel', serif;
        font-size: 12px;
        min-width: 200px;
        max-width: 240px;
    ">
        <div style="font-size: 14px; font-weight: bold; letter-spacing: 2px;
             text-transform: uppercase; margin-bottom: 10px;
             border-bottom: 1px solid #d4af3733; padding-bottom: 8px;
             text-align: center;">
            &#9768; King's Kingdom
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #FFD700;">&#9679;</span>
            <span style="color: #BFA76A; font-size: 11px;">
                Strong (30+ souls)</span>
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #DAA520;">&#9679;</span>
            <span style="color: #BFA76A; font-size: 11px;">
                Growing (20-29 souls)</span>
        </div>
        <div style="margin-bottom: 12px;">
            <span style="color: #8B6914;">&#9679;</span>
            <span style="color: #BFA76A; font-size: 11px;">
                Emerging (&lt;20 souls)</span>
        </div>
        <div style="border-top: 1px solid #d4af3733; padding-top: 8px;
             font-size: 11px; color: #BFA76A; line-height: 1.6;">
            {total_areas} Territories &middot;
            {total_groups} Shepherds<br>
            {total_members} Souls Gathered
        </div>
        <div style="font-size: 9px; color: #8B7340; margin-top: 6px;
             text-align: center; letter-spacing: 1px;">
            DASHED CIRCLE = TERRITORY REACH
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


# --- Territory Fill Colors (Google Maps style) ---
TERRITORY_PALETTE = [
    {"fill": "#4CAF50", "border": "#2E7D32"},    # green
    {"fill": "#2196F3", "border": "#1565C0"},     # blue
    {"fill": "#F44336", "border": "#C62828"},     # red
    {"fill": "#9C27B0", "border": "#6A1B9A"},     # purple
    {"fill": "#FF9800", "border": "#EF6C00"},     # orange
    {"fill": "#009688", "border": "#00695C"},     # teal
    {"fill": "#E91E63", "border": "#AD1457"},     # pink
    {"fill": "#3F51B5", "border": "#283593"},     # indigo
    {"fill": "#8BC34A", "border": "#558B2F"},     # lime
    {"fill": "#FF5722", "border": "#D84315"},     # deep orange
    {"fill": "#00BCD4", "border": "#00838F"},     # cyan
    {"fill": "#673AB7", "border": "#4527A0"},     # deep purple
    {"fill": "#CDDC39", "border": "#9E9D24"},     # yellow-green
    {"fill": "#03A9F4", "border": "#0277BD"},     # light blue
    {"fill": "#FFC107", "border": "#F9A825"},     # amber
    {"fill": "#795548", "border": "#4E342E"},     # brown
    {"fill": "#607D8B", "border": "#37474F"},     # blue-grey
    {"fill": "#FFEB3B", "border": "#F57F17"},     # yellow
]

UNOCCUPIED_COLOR = {"fill": "#9E9E9E", "border": "#757575"}

KUKATPALLY_CENTER = [17.4948, 78.3996]
KUKATPALLY_RADIUS = 0.03


def _convex_hull(points):
    """Compute convex hull using Andrew's monotone chain algorithm."""
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    # Build lower hull
    lower = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _cross(o, a, b):
    """2D cross product of vectors OA and OB."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _compute_voronoi_boundaries(centers, bbox, grid_size=60):
    """Compute Voronoi-like polygon boundaries for each center point.

    Returns dict: center_index -> list of (lat, lng) boundary points.
    """
    lat_min, lat_max, lng_min, lng_max = bbox
    lat_step = (lat_max - lat_min) / grid_size
    lng_step = (lng_max - lng_min) / grid_size

    # Build assignment grid
    grid = []
    for row in range(grid_size):
        grid_row = []
        for col in range(grid_size):
            mid_lat = lat_min + (row + 0.5) * lat_step
            mid_lng = lng_min + (col + 0.5) * lng_step
            min_dist = float("inf")
            nearest = 0
            for i, (clat, clng) in enumerate(centers):
                d = ((mid_lat - clat) ** 2 +
                     (mid_lng - clng) ** 2)
                if d < min_dist:
                    min_dist = d
                    nearest = i
            grid_row.append(nearest)
        grid.append(grid_row)

    # For each center, collect all grid cell corner points
    cell_points = {i: [] for i in range(len(centers))}
    for row in range(grid_size):
        for col in range(grid_size):
            idx = grid[row][col]
            lat0 = lat_min + row * lat_step
            lng0 = lng_min + col * lng_step
            # Add all 4 corners of this cell
            cell_points[idx].append((lat0, lng0))
            cell_points[idx].append((lat0 + lat_step, lng0))
            cell_points[idx].append((lat0 + lat_step, lng0 + lng_step))
            cell_points[idx].append((lat0, lng0 + lng_step))

    # Compute convex hull for each center's region
    boundaries = {}
    for idx, pts in cell_points.items():
        if pts:
            hull = _convex_hull(pts)
            boundaries[idx] = [[p[0], p[1]] for p in hull]

    return boundaries


def build_territory_map(df: pd.DataFrame, summary_df: pd.DataFrame,
                        center_area: str = "Kukatpally",
                        radius: float = KUKATPALLY_RADIUS) -> folium.Map:
    """Build a Google Maps-style territory map with colored polygon
    boundaries for each area — filled regions with bold borders."""
    t0 = time.perf_counter()
    logger.info("Building territory map centered on %s", center_area)

    from src.data_loader import AREA_COORDINATES

    center_key = center_area.lower().strip()
    center_coords = AREA_COORDINATES.get(center_key, KUKATPALLY_CENTER)

    # Find nearby area coordinates
    nearby = {}
    for area_name, coords in AREA_COORDINATES.items():
        dist = ((coords[0] - center_coords[0]) ** 2 +
                (coords[1] - center_coords[1]) ** 2) ** 0.5
        if dist <= radius:
            nearby[area_name] = coords

    _, map_bounds = _compute_map_bounds()

    # Google Maps style — standard road map
    m = folium.Map(
        location=center_coords,
        zoom_start=14,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps",
    )

    _apply_fixed_bounds(m, map_bounds)

    if not nearby:
        return m

    # Bounding box with padding
    lats = [c[0] for c in nearby.values()]
    lngs = [c[1] for c in nearby.values()]
    pad = 0.008
    bbox = (min(lats) - pad, max(lats) + pad,
            min(lngs) - pad, max(lngs) + pad)

    area_names = list(nearby.keys())
    centers = [nearby[a] for a in area_names]

    # Which areas have LG groups?
    occupied_areas = set(
        df["area"].str.lower().str.strip().unique()
    )

    # Assign colors
    area_color_map = {}
    color_idx = 0
    for name in area_names:
        if name in occupied_areas:
            area_color_map[name] = TERRITORY_PALETTE[
                color_idx % len(TERRITORY_PALETTE)
            ]
            color_idx += 1
        else:
            area_color_map[name] = UNOCCUPIED_COLOR

    # Compute polygon boundaries
    boundaries = _compute_voronoi_boundaries(centers, bbox)

    # Summary lookup
    summary_lookup = {}
    for _, srow in summary_df.iterrows():
        summary_lookup[srow["area"].lower().strip()] = srow

    # Draw territory polygons — like Google Maps colored regions
    for idx, boundary in boundaries.items():
        if len(boundary) < 3:
            continue
        name = area_names[idx]
        colors = area_color_map[name]
        is_occupied = name in occupied_areas
        display = name.title()
        srow = summary_lookup.get(name)

        # Build popup
        if srow is not None:
            groups = int(srow["total_groups"])
            members = int(srow["total_members"])
            strength = srow.get("strength", "")
            popup_text = (
                f'<div style="font-family: Arial, sans-serif;'
                f' padding: 8px; min-width: 150px;">'
                f'<b style="font-size: 14px; color:'
                f' {colors["border"]};">{display}</b>'
                f'<hr style="margin: 6px 0; border-color: #ddd;">'
                f'<div style="font-size: 12px; line-height: 1.8;">'
                f'Groups: <b>{groups}</b><br>'
                f'Members: <b>{members}</b><br>'
                f'Strength: <b>{strength}</b></div></div>'
            )
        else:
            popup_text = (
                f'<div style="font-family: Arial, sans-serif;'
                f' padding: 8px;">'
                f'<b style="font-size: 14px;">{display}</b>'
                f'<br><span style="color: #999;">No groups yet'
                f' — expansion opportunity</span></div>'
            )

        # The territory polygon — colored fill + bold border
        folium.Polygon(
            locations=boundary,
            color=colors["border"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=0.35 if is_occupied else 0.12,
            weight=3,
            popup=folium.Popup(popup_text, max_width=220),
            tooltip=f"{display}",
        ).add_to(m)

        # Area name label centered in polygon
        center_lat = nearby[name][0]
        center_lng = nearby[name][1]

        label_html = (
            f'<div style="font-family: Arial, Helvetica, sans-serif;'
            f' font-size: 12px; font-weight: bold;'
            f' color: {colors["border"]};'
            f' text-shadow: 1px 1px 2px white, -1px -1px 2px white,'
            f' 1px -1px 2px white, -1px 1px 2px white;'
            f' text-align: center; white-space: nowrap;'
            f' pointer-events: none;">{display}</div>'
        )
        folium.Marker(
            location=[center_lat, center_lng],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(160, 18),
                icon_anchor=(80, 9),
            ),
        ).add_to(m)

    # Draw group markers on top
    nearby_df = df[
        df["area"].str.lower().str.strip().isin(set(area_names))
    ]
    for _, row in nearby_df.iterrows():
        members = int(row["members"])
        akey = row["area"].lower().strip()
        colors = area_color_map.get(akey, TERRITORY_PALETTE[0])
        families = int(row.get("families", 0))
        individuals = int(row.get("individuals", 0))
        meeting_day = row.get("meeting_day", "")

        popup_html = (
            f'<div style="font-family: Arial, sans-serif;'
            f' padding: 8px; min-width: 160px;">'
            f'<b>{row["leader_name"]}</b>'
            f' — {row["area"]}<hr style="margin: 4px 0;">'
            f'<div style="font-size: 12px;">'
            f'Families: {families}<br>'
            f'Individuals: {individuals}<br>'
            f'Total: <b>{members}</b><br>'
            f'Meeting: {meeting_day}</div></div>'
        )

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(6, members * 0.4),
            color=colors["border"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=(
                f"{row['leader_name']} \u2014 {members} members"
            ),
        ).add_to(m)

    # Legend
    _add_territory_legend(m, area_color_map, area_names,
                          summary_lookup, occupied_areas, center_area)

    elapsed = time.perf_counter() - t0
    logger.info("Territory map built in %.3fs", elapsed)
    return m


def _add_territory_legend(m, area_color_map, area_names,
                          summary_lookup, occupied_areas, center_area):
    """Add Google Maps-style territory legend."""
    items_html = ""
    for name in sorted(area_names):
        colors = area_color_map[name]
        is_occ = name in occupied_areas
        display = name.title()
        srow = summary_lookup.get(name)
        if srow is not None:
            members = int(srow["total_members"])
            groups = int(srow["total_groups"])
            detail = f"{groups} groups &middot; {members} members"
        else:
            detail = "no groups yet"
        label_color = "#333" if is_occ else "#999"
        items_html += (
            f'<div style="margin-bottom: 6px; display: flex;'
            f' align-items: center;">'
            f'<div style="width: 16px; height: 16px;'
            f' border-radius: 3px;'
            f' background: {colors["fill"]};'
            f' border: 2px solid {colors["border"]};'
            f' margin-right: 8px; flex-shrink: 0;'
            f' opacity: {"0.8" if is_occ else "0.3"};"></div>'
            f'<div><div style="color: {label_color};'
            f' font-size: 12px; font-weight: 600;">'
            f'{display}</div>'
            f'<div style="color: #888; font-size: 10px;">'
            f'{detail}</div></div></div>'
        )

    occ_count = sum(1 for n in area_names if n in occupied_areas)
    total_count = len(area_names)

    legend_html = f"""
    <div style="
        position: fixed; bottom: 20px; right: 10px; z-index: 1000;
        background: white; color: #333;
        padding: 14px 16px; border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        font-family: Arial, Helvetica, sans-serif;
        font-size: 12px; min-width: 200px; max-width: 280px;
        max-height: 420px; overflow-y: auto;
    ">
        <div style="font-size: 14px; font-weight: bold;
             margin-bottom: 10px; border-bottom: 1px solid #eee;
             padding-bottom: 8px;">
            {center_area.title()} Region
        </div>
        {items_html}
        <div style="border-top: 1px solid #eee; padding-top: 8px;
             margin-top: 8px; font-size: 11px; color: #888;
             text-align: center;">
            {occ_count} of {total_count} territories occupied
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


# --- Strength-based coloring for density view ---
STRENGTH_TERRITORY = {
    "Strong": {"fill": "#2E7D32", "border": "#1B5E20"},
    "Medium": {"fill": "#F9A825", "border": "#F57F17"},
    "Weak":   {"fill": "#C62828", "border": "#B71C1C"},
}


def _load_ward_data():
    """Load ward boundary polygons and area-to-ward mapping."""
    import json as _json
    base = os.path.dirname(os.path.dirname(__file__))
    bnd_path = os.path.join(base, "data", "ward_boundaries.json")
    map_path = os.path.join(base, "data", "area_ward_mapping.json")
    try:
        with open(bnd_path) as f:
            boundaries = _json.load(f)
        with open(map_path) as f:
            mapping = _json.load(f)
        return boundaries, mapping
    except (FileNotFoundError, ValueError) as e:
        logger.warning("Ward boundary data not found: %s", e)
        return {}, {}


def build_advanced_territory_map(
    df, summary_df,
    center_area="Kukatpally",
    radius=KUKATPALLY_RADIUS,
    color_by="area",
):
    """Build advanced territory map with real GHMC ward boundaries.

    Uses actual administrative polygon shapes from ward_boundaries.json.
    Layers: Ward Boundaries, Group Markers, Gap Analysis,
    Strength Indicators, and Member Density Stats.
    """
    t0 = time.perf_counter()
    logger.info("Building advanced territory map, color_by=%s", color_by)

    from src.data_loader import AREA_COORDINATES

    center_key = center_area.lower().strip()
    center_coords = AREA_COORDINATES.get(center_key, KUKATPALLY_CENTER)

    # Find nearby areas
    nearby = {}
    for area_name, coords in AREA_COORDINATES.items():
        dist = ((coords[0] - center_coords[0]) ** 2 +
                (coords[1] - center_coords[1]) ** 2) ** 0.5
        if dist <= radius:
            nearby[area_name] = coords

    _, map_bounds = _compute_map_bounds()

    m = folium.Map(
        location=center_coords, zoom_start=13,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps",
    )

    _apply_fixed_bounds(m, map_bounds)

    if not nearby:
        return m

    # Load real ward boundary data
    ward_boundaries, area_ward_map = _load_ward_data()

    area_names = list(nearby.keys())
    occupied = set(df["area"].str.lower().str.strip().unique())

    slookup = {}
    for _, srow in summary_df.iterrows():
        slookup[srow["area"].lower().strip()] = srow

    # Find which wards are relevant (used by nearby areas)
    ward_to_areas = {}
    for area_name in area_names:
        ward = area_ward_map.get(area_name)
        if ward:
            if ward not in ward_to_areas:
                ward_to_areas[ward] = []
            ward_to_areas[ward].append(area_name)

    # Assign colors per ward
    ward_color_map = {}
    cidx = 0
    for ward_name in ward_to_areas:
        areas_in_ward = ward_to_areas[ward_name]
        has_groups = any(a in occupied for a in areas_in_ward)

        if not has_groups:
            ward_color_map[ward_name] = UNOCCUPIED_COLOR
            continue

        if color_by == "strength":
            # Use the dominant strength of areas in this ward
            strengths = []
            for a in areas_in_ward:
                sr = slookup.get(a)
                if sr is not None:
                    strengths.append(sr.get("strength", "Weak"))
            if "Strong" in strengths:
                ward_color_map[ward_name] = STRENGTH_TERRITORY["Strong"]
            elif "Medium" in strengths:
                ward_color_map[ward_name] = STRENGTH_TERRITORY["Medium"]
            else:
                ward_color_map[ward_name] = STRENGTH_TERRITORY["Weak"]
        elif color_by == "density":
            total_mem = sum(
                int(slookup[a]["total_members"])
                for a in areas_in_ward if a in slookup
            )
            if total_mem >= 80:
                ward_color_map[ward_name] = {
                    "fill": "#1B5E20", "border": "#2E7D32"}
            elif total_mem >= 50:
                ward_color_map[ward_name] = {
                    "fill": "#4CAF50", "border": "#388E3C"}
            elif total_mem >= 25:
                ward_color_map[ward_name] = {
                    "fill": "#FFC107", "border": "#F9A825"}
            else:
                ward_color_map[ward_name] = {
                    "fill": "#FF5722", "border": "#D84315"}
        else:
            ward_color_map[ward_name] = TERRITORY_PALETTE[
                cidx % len(TERRITORY_PALETTE)]
            cidx += 1

    # --- Layer 1: Real Ward Boundary Polygons ---
    t_layer = folium.FeatureGroup(
        name="Ward Boundaries", show=True)

    for ward_name, ward_areas in ward_to_areas.items():
        bnd = ward_boundaries.get(ward_name)
        if not bnd or len(bnd) < 3:
            continue
        colors = ward_color_map.get(ward_name, UNOCCUPIED_COLOR)
        has_groups = any(a in occupied for a in ward_areas)

        # Aggregate stats for this ward
        total_grp = 0
        total_mem = 0
        area_list = []
        for a in ward_areas:
            sr = slookup.get(a)
            if sr is not None:
                total_grp += int(sr["total_groups"])
                total_mem += int(sr["total_members"])
                area_list.append(a.title())

        avg = total_mem / total_grp if total_grp > 0 else 0
        display = ward_name.replace("Ward ", "")

        if has_groups:
            areas_str = ", ".join(area_list) if area_list else "—"
            popup_t = (
                f'<div style="font-family:Arial;padding:10px;'
                f'min-width:200px;">'
                f'<b style="font-size:14px;color:'
                f'{colors["border"]};">{ward_name}</b>'
                f'<hr style="margin:6px 0;">'
                f'<div style="font-size:11px;color:#666;'
                f'margin-bottom:6px;">Areas: {areas_str}</div>'
                f'<table style="font-size:12px;width:100%;">'
                f'<tr><td>Groups:</td>'
                f'<td align="right"><b>{total_grp}</b></td></tr>'
                f'<tr><td>Members:</td>'
                f'<td align="right"><b>{total_mem}</b></td></tr>'
                f'<tr><td>Avg/Group:</td>'
                f'<td align="right"><b>{avg:.1f}</b></td></tr>'
                f'</table></div>')
        else:
            popup_t = (
                f'<div style="font-family:Arial;padding:10px;">'
                f'<b style="font-size:14px;">{ward_name}</b><br>'
                f'<span style="color:#e74c3c;font-weight:bold;">'
                f'No groups \u2014 expansion zone</span></div>')

        # Draw the real irregular ward polygon
        folium.Polygon(
            locations=bnd, color=colors["border"],
            fill=True, fill_color=colors["fill"],
            fill_opacity=0.40 if has_groups else 0.10,
            weight=3,
            popup=folium.Popup(popup_t, max_width=280),
            tooltip=ward_name,
        ).add_to(t_layer)

        # Ward label at centroid
        avg_lat = sum(p[0] for p in bnd) / len(bnd)
        avg_lng = sum(p[1] for p in bnd) / len(bnd)
        folium.Marker(
            location=[avg_lat, avg_lng],
            icon=folium.DivIcon(html=(
                f'<div style="font-family:Arial;font-size:11px;'
                f'font-weight:bold;color:{colors["border"]};'
                f'text-shadow:1px 1px 2px white,-1px -1px 2px white,'
                f'1px -1px 2px white,-1px 1px 2px white;'
                f'text-align:center;pointer-events:none;'
                f'white-space:nowrap;">{display}</div>'),
                icon_size=(180, 18), icon_anchor=(90, 9)),
        ).add_to(t_layer)

    t_layer.add_to(m)

    # Build area -> color lookup from ward colors
    area_color_map = {}
    for area_name in area_names:
        ward = area_ward_map.get(area_name)
        if ward and ward in ward_color_map:
            area_color_map[area_name] = ward_color_map[ward]
        elif area_name in occupied:
            area_color_map[area_name] = TERRITORY_PALETTE[0]
        else:
            area_color_map[area_name] = UNOCCUPIED_COLOR

    # --- Layer 2: Group Markers ---
    m_layer = folium.FeatureGroup(
        name="Group Markers", show=True)
    nearby_df = df[
        df["area"].str.lower().str.strip().isin(set(area_names))]
    for _, row in nearby_df.iterrows():
        mem = int(row["members"])
        akey = row["area"].lower().strip()
        colors = area_color_map.get(akey, TERRITORY_PALETTE[0])
        popup_html = (
            f'<div style="font-family:Arial;padding:8px;'
            f'min-width:150px;">'
            f'<b style="color:{colors["border"]};">'
            f'{row["leader_name"]}</b>'
            f' ({row["area"]})<hr style="margin:4px 0;">'
            f'<div style="font-size:12px;">'
            f'Families: {int(row.get("families", 0))}<br>'
            f'Individuals: {int(row.get("individuals", 0))}<br>'
            f'Total: <b>{mem}</b><br>'
            f'Meeting: {row.get("meeting_day", "")}<br>'
            f'Strength: {row.get("strength", "")}</div></div>')
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(6, mem * 0.4),
            color=colors["border"], fill=True,
            fill_color=colors["fill"], fill_opacity=0.9, weight=2,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{row['leader_name']} \u2014 {mem} members",
        ).add_to(m_layer)
    m_layer.add_to(m)

    # --- Layer 3: Gap Analysis ---
    g_layer = folium.FeatureGroup(
        name="Gap Analysis (Expansion)", show=False)
    for name in area_names:
        if name in occupied:
            continue
        coords = nearby[name]
        display = name.title()
        folium.CircleMarker(
            location=coords, radius=20, color="#e74c3c",
            fill=True, fill_color="#e74c3c",
            fill_opacity=0.15, weight=2, dash_array="5 5",
        ).add_to(g_layer)
        folium.CircleMarker(
            location=coords, radius=8, color="#e74c3c",
            fill=True, fill_color="#e74c3c",
            fill_opacity=0.4, weight=0,
        ).add_to(g_layer)
        folium.Marker(
            location=[coords[0] - 0.002, coords[1]],
            icon=folium.DivIcon(html=(
                f'<div style="font-family:Arial;font-size:10px;'
                f'color:#c0392b;font-weight:bold;'
                f'text-shadow:1px 1px 2px white,-1px -1px 2px white;'
                f'text-align:center;pointer-events:none;">'
                f'{display}<br>'
                f'<span style="font-size:9px;color:#e74c3c;">'
                f'NO COVERAGE</span></div>'),
                icon_size=(140, 28), icon_anchor=(70, 14)),
        ).add_to(g_layer)
    g_layer.add_to(m)

    # --- Layer 4: Strength Indicators ---
    s_layer = folium.FeatureGroup(
        name="Strength Indicators", show=False)
    for _, row in nearby_df.iterrows():
        st = row.get("strength", "Weak")
        mem = int(row["members"])
        sc = STRENGTH_TERRITORY.get(st, STRENGTH_TERRITORY["Weak"])
        sym = {"Strong": "+", "Medium": "~", "Weak": "-"}.get(
            st, "?")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(10, mem * 0.5),
            color=sc["border"], fill=True,
            fill_color=sc["fill"], fill_opacity=0.3, weight=2,
        ).add_to(s_layer)
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(html=(
                f'<div style="font-family:Arial;font-size:11px;'
                f'font-weight:bold;color:{sc["border"]};'
                f'text-shadow:1px 1px 1px white;'
                f'text-align:center;pointer-events:none;">'
                f'{sym}{mem}</div>'),
                icon_size=(40, 16), icon_anchor=(20, 8)),
        ).add_to(s_layer)
    s_layer.add_to(m)

    # --- Layer 5: Member Density Stats ---
    d_layer = folium.FeatureGroup(
        name="Member Density Stats", show=False)
    for name in area_names:
        srow = slookup.get(name)
        if srow is None:
            continue
        coords = nearby[name]
        mem = int(srow["total_members"])
        grp = int(srow["total_groups"])
        avg = mem / grp if grp > 0 else 0
        folium.Marker(
            location=[coords[0] - 0.001, coords[1]],
            icon=folium.DivIcon(html=(
                f'<div style="font-family:Arial;background:white;'
                f'border:1px solid #ddd;border-radius:6px;'
                f'padding:6px 8px;box-shadow:0 1px 4px '
                f'rgba(0,0,0,0.2);text-align:center;'
                f'pointer-events:none;">'
                f'<div style="font-size:11px;font-weight:bold;'
                f'color:#333;">{name.title()}</div>'
                f'<div style="font-size:18px;font-weight:bold;'
                f'color:#2E7D32;">{mem}</div>'
                f'<div style="font-size:9px;color:#888;">'
                f'{grp} groups &middot; avg {avg:.0f}</div>'
                f'</div>'),
                icon_size=(130, 60), icon_anchor=(65, 30)),
        ).add_to(d_layer)
    d_layer.add_to(m)

    # Layer control toggle (top-right checkbox panel)
    folium.LayerControl(collapsed=False).add_to(m)

    # Color mode legend (bottom-left)
    _add_advanced_legend(m, color_by, area_names, occupied, center_area)

    elapsed = time.perf_counter() - t0
    logger.info("Advanced territory map built in %.3fs", elapsed)
    return m


def _add_advanced_legend(m, color_by, area_names, occupied, center_area):
    """Legend for advanced territory map."""
    occ = sum(1 for n in area_names if n in occupied)
    total = len(area_names)
    gap = total - occ

    if color_by == "strength":
        mode_items = (
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#2E7D32;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Strong (30+)</span></div>'
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#F9A825;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Medium (20-29)</span></div>'
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#C62828;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Weak (&lt;20)</span></div>'
        )
    elif color_by == "density":
        mode_items = (
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#1B5E20;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">High (50+)</span></div>'
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#4CAF50;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Good (30-49)</span></div>'
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#FFC107;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Low (15-29)</span></div>'
            '<div style="margin-bottom:4px;">'
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:#FF5722;border-radius:2px;"></span>'
            ' <span style="font-size:11px;">Critical (&lt;15)'
            '</span></div>'
        )
    else:
        mode_items = (
            '<div style="font-size:11px;color:#888;'
            'margin-bottom:4px;">Each area = unique color</div>'
        )

    legend_html = f"""
    <div style="
        position:fixed;bottom:20px;left:10px;z-index:1000;
        background:white;color:#333;padding:12px 14px;
        border-radius:8px;border:1px solid #ddd;
        box-shadow:0 2px 10px rgba(0,0,0,0.15);
        font-family:Arial,sans-serif;font-size:12px;
        min-width:160px;max-width:200px;">
        <div style="font-size:13px;font-weight:bold;
             margin-bottom:8px;border-bottom:1px solid #eee;
             padding-bottom:6px;">{center_area.title()} Region</div>
        {mode_items}
        <div style="margin-top:6px;padding-top:6px;
             border-top:1px solid #eee;">
            <div style="margin-bottom:2px;">
                <span style="display:inline-block;width:12px;
                      height:12px;background:#9E9E9E;
                      border-radius:2px;"></span>
                <span style="font-size:11px;">
                    Unoccupied ({gap})</span></div></div>
        <div style="font-size:10px;color:#888;margin-top:6px;
             text-align:center;">
            {occ}/{total} territories occupied</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


def generate_territory_kml(df, summary_df):
    """Generate KML string for territory data export."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '<name>LG GeoView Territories</name>',
    ]
    for _, row in summary_df.iterrows():
        area = row["area"]
        mem = int(row["total_members"])
        grp = int(row["total_groups"])
        st = row.get("strength", "")
        lines.append('<Placemark>')
        lines.append(f'<name>{area}</name>')
        lines.append(
            f'<description>{grp} groups, {mem} members,'
            f' {st}</description>')
        lines.append(
            f'<Point><coordinates>{row["longitude"]},'
            f'{row["latitude"]},0</coordinates></Point>')
        lines.append('</Placemark>')
    for _, row in df.iterrows():
        lines.append('<Placemark>')
        lines.append(
            f'<name>{row["leader_name"]} - {row["area"]}</name>')
        lines.append(
            f'<description>{int(row["members"])}'
            f' members</description>')
        lines.append(
            f'<Point><coordinates>{row["longitude"]},'
            f'{row["latitude"]},0</coordinates></Point>')
        lines.append('</Placemark>')
    lines.append('</Document>')
    lines.append('</kml>')
    return '\n'.join(lines)
