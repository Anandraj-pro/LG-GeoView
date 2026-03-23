"""Map visualization module using Folium with legal free tile providers."""

from __future__ import annotations

import os
import time
from html import escape as html_escape
from xml.sax.saxutils import escape as xml_escape

import math

import folium
import pandas as pd
from folium.plugins import HeatMap

from src.logger import get_logger


def _haversine_km(lat1: float, lon1: float,
                  lat2: float, lon2: float) -> float:
    """Great-circle distance in km (local copy to avoid circular import)."""
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


logger = get_logger(__name__)

# Map bounds based on Nehru ORR (Outer Ring Road) west sector
# Tighter bounds to prevent showing Dundigal on mobile
ORR_BOUNDS: list[list[float]] = [[17.4200, 78.2800], [17.5300, 78.4850]]
HYDERABAD_CENTER: list[float] = [17.4750, 78.3825]
DEFAULT_ZOOM: int = 12


def _compute_map_bounds() -> tuple[list[float], list[list[float]]]:
    """Return fixed ORR-based bounds for the ministry area.

    Uses hard-coded Nehru ORR bounds instead of auto-calculating
    from coordinates, ensuring consistent framing on all devices.
    New areas within ORR are automatically visible.
    """
    return HYDERABAD_CENTER, ORR_BOUNDS


def _apply_fixed_bounds(m: folium.Map, bounds: list[list[float]] | None) -> None:
    """Lock map strictly to ORR bounds.

    Uses fit_bounds with zero padding to frame exactly,
    plus maxBounds with viscosity=1.0 for hard pan lock.
    """
    if not bounds:
        return

    # Fit the view to bounds with zero padding
    m.fit_bounds(bounds, padding=(0, 0))
    # Hard-lock: can't pan outside
    m.options["maxBounds"] = bounds
    m.options["maxBoundsViscosity"] = 1.0
    m.options["minZoom"] = 12
    m.options["maxZoom"] = 18


# 32 distinct colors -- one per care group, no repeats
GROUP_COLORS: list[str] = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#fffac8", "#800000", "#aaffc3",
    "#808000", "#ffd8b1", "#000075", "#a9a9a9", "#e6beff",
    "#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e",
    "#16a085", "#27ae60", "#2980b9", "#8e44ad", "#2c3e50",
    "#f39c12", "#d35400",
]

# Map tile options -- legal free tile providers
MAP_STYLES: dict[str, dict[str, str | None]] = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None,
    },
    "ESRI Satellite": {
        "tiles": (
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        "attr": "ESRI",
    },
    "Stadia Terrain": {
        "tiles": (
            "https://tiles.stadiamaps.com/tiles/"
            "stamen_terrain/{z}/{x}/{y}{r}.png"
        ),
        "attr": "Stadia Maps",
    },
    "CartoDB Positron": {
        "tiles": (
            "https://{s}.basemaps.cartocdn.com/"
            "light_all/{z}/{x}/{y}{r}.png"
        ),
        "attr": "CartoDB",
    },
}


# --- Strength colors for Kingdom map ---
STRENGTH_GLOW: dict[str, dict[str, str]] = {
    "Strong": {"fill": "#D4AF37", "border": "#FFD700", "glow": "rgba(212,175,55,0.45)"},
    "Medium": {"fill": "#C0A060", "border": "#DAA520", "glow": "rgba(192,160,96,0.30)"},
    "Weak":   {"fill": "#8B6914", "border": "#A0822A", "glow": "rgba(139,105,20,0.20)"},
}


# --- Heatmap gradient ---
HEATMAP_GRADIENT: dict[float, str] = {
    0.2: '#2196F3',
    0.4: '#4CAF50',
    0.6: '#FFC107',
    0.8: '#FF9800',
    1.0: '#F44336',
}


def build_heatmap_layer(df: pd.DataFrame) -> list:
    """Generate heatmap data from group locations weighted by member count.

    Each group contributes its lat/lng weighted by member count.
    Returns list of [lat, lng, weight] for Folium HeatMap.
    """
    heat_data = []
    for _, row in df.iterrows():
        lat = row["latitude"]
        lng = row["longitude"]
        members = int(row["members"])
        heat_data.append([lat, lng, members])
    return heat_data


def build_heatmap_map(df: pd.DataFrame, map_style: str | None = None) -> folium.Map:
    """Build a map with heatmap overlay showing member density."""
    center, bounds = _compute_map_bounds()

    m = folium.Map(location=center, zoom_start=DEFAULT_ZOOM, tiles="OpenStreetMap")
    _apply_fixed_bounds(m, bounds)

    if df.empty:
        return m

    heat_data = build_heatmap_layer(df)
    if heat_data:
        HeatMap(
            heat_data,
            min_opacity=0.3,
            radius=25,
            blur=20,
            gradient=HEATMAP_GRADIENT,
        ).add_to(m)

    return m


def build_kingdom_map(
    df: pd.DataFrame,
    summary_df: pd.DataFrame,
    map_style: str | None = None,
) -> folium.Map:
    """Build the King's Kingdom map -- dark terrain with golden territory markers."""
    t0 = time.perf_counter()
    logger.info("Building King's Kingdom map with %d markers", len(df))

    center, bounds = _compute_map_bounds()

    # Light muted tile -- readable background with regal markers
    m = folium.Map(
        location=center,
        zoom_start=DEFAULT_ZOOM,
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Positron",
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

        # Outer glow -- territory reach
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

        esc_area_name = html_escape(str(area_row['area']))

        # Area territory label
        territory_html = f"""
        <div style="
            font-family: 'Cinzel', 'Palatino Linotype', 'Book Antiqua', serif;
            color: #5D4E37;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 1px 1px 2px white, -1px -1px 2px white;
            text-align: center;
            white-space: nowrap;
            pointer-events: none;
        ">{esc_area_name}</div>
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
            color: #7A6B50;
            font-size: 10px;
            letter-spacing: 1px;
            text-shadow: 1px 1px 1px white;
            text-align: center;
            white-space: nowrap;
            pointer-events: none;
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

        # Escaped user data
        esc_area = html_escape(str(row['area']))
        esc_leader = html_escape(str(row['leader_name']))
        esc_meeting = html_escape(str(row.get('meeting_day', '')))

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
            color=colors["border"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=1.0,
            weight=1,
        ).add_to(m)

        # Popup
        popup_html = f"""
        <div style="font-family: 'Palatino Linotype', 'Book Antiqua', serif;
             min-width: 180px; background: #FFFBF0; color: #5D4E37;
             padding: 12px 14px; border-radius: 8px;
             border: 1px solid #D4AF37; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
            <div style="font-size: 14px; font-weight: bold; color: #8B6914;
                 letter-spacing: 1px; margin-bottom: 6px;
                 border-bottom: 1px solid #D4AF3744; padding-bottom: 6px;">
                {esc_area}
            </div>
            <table style="font-size: 12px; border-collapse: collapse; width: 100%;">
                <tr><td style="color: #8B7355; padding: 2px 0;">Shepherd</td>
                    <td style="color: #5D4E37; text-align: right;">{esc_leader}</td></tr>
                <tr><td style="color: #8B7355; padding: 2px 0;">Families</td>
                    <td style="color: #5D4E37; text-align: right;">{int(row.get('families', 0))}</td></tr>
                <tr><td style="color: #8B7355; padding: 2px 0;">Individuals</td>
                    <td style="color: #5D4E37; text-align: right;">{int(row.get('individuals', 0))}</td></tr>
                <tr><td style="color: #8B7355; padding: 2px 0;">Total Souls</td>
                    <td style="color: #8B6914; font-weight: bold; text-align: right;">{members}</td></tr>
                <tr><td style="color: #8B7355; padding: 2px 0;">Gathering</td>
                    <td style="color: #5D4E37; text-align: right;">{esc_meeting}</td></tr>
            </table>
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(7, members * 0.5),
            color="transparent",
            fill=False,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{esc_leader} \u2014 {members} souls",
        ).add_to(m)

    # --- Kingdom legend ---
    _add_kingdom_legend(m, summary_df)

    # Mobile-responsive legend
    mobile_css = """
    <style>
    @media screen and (max-width: 480px) {
        div[style*="position: fixed"] {
            max-width: 140px !important;
            font-size: 9px !important;
            padding: 8px 10px !important;
            bottom: 5px !important;
            right: 5px !important;
        }
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(mobile_css))

    elapsed = time.perf_counter() - t0
    logger.info("Kingdom map built: %d markers in %.3fs", len(df), elapsed)
    return m


def _add_kingdom_legend(m: folium.Map, summary_df: pd.DataFrame) -> None:
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
        background: #FFFBF0;
        color: #5D4E37;
        padding: 16px 20px;
        border-radius: 10px;
        border: 1px solid #D4AF37;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        font-family: 'Palatino Linotype', 'Book Antiqua', 'Cinzel', serif;
        font-size: 12px;
        min-width: 200px;
        max-width: 240px;
    ">
        <div style="font-size: 14px; font-weight: bold; letter-spacing: 2px;
             text-transform: uppercase; margin-bottom: 10px;
             border-bottom: 1px solid #D4AF3744; padding-bottom: 8px;
             text-align: center; color: #8B6914;">
            &#9768; King's Kingdom
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #D4AF37;">&#9679;</span>
            <span style="color: #5D4E37; font-size: 11px;">
                Strong (30+ souls)</span>
        </div>
        <div style="margin-bottom: 8px;">
            <span style="color: #C0A060;">&#9679;</span>
            <span style="color: #5D4E37; font-size: 11px;">
                Growing (20-29 souls)</span>
        </div>
        <div style="margin-bottom: 12px;">
            <span style="color: #A0822A;">&#9679;</span>
            <span style="color: #5D4E37; font-size: 11px;">
                Emerging (&lt;20 souls)</span>
        </div>
        <div style="border-top: 1px solid #D4AF3744; padding-top: 8px;
             font-size: 11px; color: #7A6B50; line-height: 1.6;">
            {total_areas} Territories &middot;
            {total_groups} Shepherds<br>
            {total_members} Souls Gathered
        </div>
        <div style="font-size: 9px; color: #A0936E; margin-top: 6px;
             text-align: center; letter-spacing: 1px;">
            DASHED CIRCLE = TERRITORY REACH
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


# --- Territory Fill Colors ---
TERRITORY_PALETTE: list[dict[str, str]] = [
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

UNOCCUPIED_COLOR: dict[str, str] = {"fill": "#9E9E9E", "border": "#757575"}

KUKATPALLY_CENTER: list[float] = [17.4948, 78.3996]
KUKATPALLY_RADIUS: int = 3  # km

# Coverage layer color constants
COVERAGE_COLORS: dict[str, dict[str, str]] = {
    "Well Served": {"fill": "#2E7D32", "border": "#1B5E20"},
    "Partial": {"fill": "#F9A825", "border": "#F57F17"},
    "Underserved": {"fill": "#C62828", "border": "#B71C1C"},
    "No Data": {"fill": "#9E9E9E", "border": "#757575"},
}


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Compute convex hull using Andrew's monotone chain algorithm."""
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    # Build lower hull
    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _cross(
    o: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
) -> float:
    """2D cross product of vectors OA and OB."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _compute_voronoi_boundaries(
    centers: list[tuple[float, float] | list[float]],
    bbox: tuple[float, float, float, float],
    grid_size: int = 60,
) -> dict[int, list[list[float]]]:
    """Compute Voronoi-like polygon boundaries for each center point.

    Returns dict: center_index -> list of (lat, lng) boundary points.
    """
    lat_min, lat_max, lng_min, lng_max = bbox
    lat_step = (lat_max - lat_min) / grid_size
    lng_step = (lng_max - lng_min) / grid_size

    # Build assignment grid
    grid: list[list[int]] = []
    for row in range(grid_size):
        grid_row: list[int] = []
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
    cell_points: dict[int, list[tuple[float, float]]] = {i: [] for i in range(len(centers))}
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
    boundaries: dict[int, list[list[float]]] = {}
    for idx, pts in cell_points.items():
        if pts:
            hull = _convex_hull(pts)
            boundaries[idx] = [[p[0], p[1]] for p in hull]

    return boundaries


def _load_ward_data() -> tuple[dict, dict]:
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


def build_territory_map(
    df: pd.DataFrame,
    summary_df: pd.DataFrame,
    center_area: str = "Kukatpally",
    radius: float = KUKATPALLY_RADIUS,
) -> folium.Map:
    """Build a territory map with colored polygon boundaries for each area."""
    t0 = time.perf_counter()
    logger.info("Building territory map centered on %s", center_area)

    from src.data_loader import AREA_COORDINATES

    center_key = center_area.lower().strip()
    center_coords = AREA_COORDINATES.get(center_key, KUKATPALLY_CENTER)

    # Find nearby area coordinates using Haversine distance
    nearby: dict[str, tuple[float, float] | list[float]] = {}
    for area_name, coords in AREA_COORDINATES.items():
        dist = _haversine_km(
            center_coords[0], center_coords[1], coords[0], coords[1])
        if dist <= radius:
            nearby[area_name] = coords

    _, map_bounds = _compute_map_bounds()

    # OpenStreetMap as default base layer
    m = folium.Map(
        location=center_coords,
        zoom_start=14,
        tiles=None,
    )
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
        control=False,
    ).add_to(m)

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
    area_color_map: dict[str, dict[str, str]] = {}
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
    summary_lookup: dict[str, pd.Series] = {}
    for _, srow in summary_df.iterrows():
        summary_lookup[srow["area"].lower().strip()] = srow

    # Draw territory polygons
    for idx, boundary in boundaries.items():
        if len(boundary) < 3:
            continue
        name = area_names[idx]
        colors = area_color_map[name]
        is_occupied = name in occupied_areas
        display = html_escape(name.title())
        srow = summary_lookup.get(name)

        # Build popup
        if srow is not None:
            groups = int(srow["total_groups"])
            members = int(srow["total_members"])
            strength = html_escape(str(srow.get("strength", "")))
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
                f' \u2014 expansion opportunity</span></div>'
            )

        # The territory polygon -- colored fill + bold border
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

        esc_leader = html_escape(str(row["leader_name"]))
        esc_area = html_escape(str(row["area"]))
        esc_meeting = html_escape(str(meeting_day))

        popup_html = (
            f'<div style="font-family: Arial, sans-serif;'
            f' padding: 8px; min-width: 160px;">'
            f'<b>{esc_leader}</b>'
            f' &mdash; {esc_area}<hr style="margin: 4px 0;">'
            f'<div style="font-size: 12px;">'
            f'Families: {families}<br>'
            f'Individuals: {individuals}<br>'
            f'Total: <b>{members}</b><br>'
            f'Meeting: {esc_meeting}</div></div>'
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
                f"{esc_leader} \u2014 {members} members"
            ),
        ).add_to(m)

    # Legend
    _add_territory_legend(m, area_color_map, area_names,
                          summary_lookup, occupied_areas, center_area)

    # Mobile-responsive legend
    m.get_root().html.add_child(folium.Element("""
    <style>
    @media screen and (max-width: 480px) {
        div[style*="position: fixed"] {
            max-width: 140px !important;
            font-size: 9px !important;
            padding: 8px 10px !important;
            bottom: 5px !important;
        }
    }
    </style>
    """))

    elapsed = time.perf_counter() - t0
    logger.info("Territory map built in %.3fs", elapsed)
    return m


def _add_territory_legend(
    m: folium.Map,
    area_color_map: dict[str, dict[str, str]],
    area_names: list[str],
    summary_lookup: dict[str, pd.Series],
    occupied_areas: set[str],
    center_area: str,
) -> None:
    """Add territory legend."""
    items_html = ""
    for name in sorted(area_names):
        colors = area_color_map[name]
        is_occ = name in occupied_areas
        display = html_escape(name.title())
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
    esc_center = html_escape(center_area.title())

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
            {esc_center} Region
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
STRENGTH_TERRITORY: dict[str, dict[str, str]] = {
    "Strong": {"fill": "#2E7D32", "border": "#1B5E20"},
    "Medium": {"fill": "#F9A825", "border": "#F57F17"},
    "Weak":   {"fill": "#C62828", "border": "#B71C1C"},
}


def build_advanced_territory_map(
    df: pd.DataFrame,
    summary_df: pd.DataFrame,
    center_area: str = "Kukatpally",
    radius: float = KUKATPALLY_RADIUS,
    color_by: str = "area",
    layers: dict[str, bool] | None = None,
    coverage_scores: dict[str, dict] | None = None,
) -> folium.Map:
    """Build advanced territory map with real GHMC ward boundaries.

    Uses actual administrative polygon shapes from ward_boundaries.json.
    Layers controlled by ``layers`` dict from Streamlit checkboxes.

    Parameters
    ----------
    coverage_scores : dict, optional
        Mapping of area_name (lowercase) -> dict with keys:
        score (float), level (str), color (str).
        Used when the coverage layer is enabled.
    """
    if layers is None:
        layers = {
            "boundaries": True, "markers": True,
            "gaps": False, "strength": False, "density": False,
            "coverage": False, "heatmap": False,
        }
    t0 = time.perf_counter()
    logger.info("Building advanced territory map, color_by=%s", color_by)

    from src.data_loader import AREA_COORDINATES

    center_key = center_area.lower().strip()
    center_coords = AREA_COORDINATES.get(center_key, KUKATPALLY_CENTER)

    # Find nearby areas using Haversine distance
    nearby: dict[str, tuple[float, float] | list[float]] = {}
    for area_name, coords in AREA_COORDINATES.items():
        dist = _haversine_km(
            center_coords[0], center_coords[1], coords[0], coords[1])
        if dist <= radius:
            nearby[area_name] = coords

    _, map_bounds = _compute_map_bounds()

    m = folium.Map(
        location=center_coords, zoom_start=13,
        tiles=None,
    )
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
        control=False,
    ).add_to(m)

    _apply_fixed_bounds(m, map_bounds)

    if not nearby:
        return m

    # Load real ward boundary data
    ward_boundaries, area_ward_map = _load_ward_data()

    area_names = list(nearby.keys())
    occupied = set(df["area"].str.lower().str.strip().unique())

    slookup: dict[str, pd.Series] = {}
    for _, srow in summary_df.iterrows():
        slookup[srow["area"].lower().strip()] = srow

    # Find which wards are relevant (used by nearby areas)
    ward_to_areas: dict[str, list[str]] = {}
    for area_name in area_names:
        ward = area_ward_map.get(area_name)
        if ward:
            if ward not in ward_to_areas:
                ward_to_areas[ward] = []
            ward_to_areas[ward].append(area_name)

    # Determine if coverage layer is active
    show_coverage = layers.get("coverage", False) and coverage_scores

    # Assign colors per ward
    ward_color_map: dict[str, dict[str, str]] = {}
    cidx = 0
    for ward_name in ward_to_areas:
        areas_in_ward = ward_to_areas[ward_name]
        has_groups = any(a in occupied for a in areas_in_ward)

        # Coverage layer overrides ward coloring
        if show_coverage:
            # Find best coverage level among areas in this ward
            best_score = -1.0
            best_level = "No Data"
            for a in areas_in_ward:
                cs = coverage_scores.get(a)
                if cs is not None:
                    sc = cs.get("score", 0)
                    if sc > best_score:
                        best_score = sc
                        best_level = cs.get("level", "No Data")
            ward_color_map[ward_name] = COVERAGE_COLORS.get(
                best_level, COVERAGE_COLORS["No Data"]
            )
            continue

        if not has_groups:
            ward_color_map[ward_name] = UNOCCUPIED_COLOR
            continue

        if color_by == "strength":
            # Use the dominant strength of areas in this ward
            strengths: list[str] = []
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
    if layers.get("boundaries", True):
        t_layer = m  # add directly to map

    for ward_name, ward_areas in ward_to_areas.items():
        bnd = ward_boundaries.get(ward_name)
        if not bnd or len(bnd) < 3:
            continue
        colors = ward_color_map.get(ward_name, UNOCCUPIED_COLOR)
        has_groups = any(a in occupied for a in ward_areas)

        # Aggregate stats for this ward
        total_grp = 0
        total_mem = 0
        area_list: list[str] = []
        for a in ward_areas:
            sr = slookup.get(a)
            if sr is not None:
                total_grp += int(sr["total_groups"])
                total_mem += int(sr["total_members"])
                area_list.append(a.title())

        avg = total_mem / total_grp if total_grp > 0 else 0
        display = html_escape(ward_name.replace("Ward ", ""))
        esc_ward = html_escape(ward_name)

        # Build coverage info for popup when coverage layer is active
        coverage_popup_extra = ""
        if show_coverage:
            for a in ward_areas:
                cs = coverage_scores.get(a)
                if cs is not None:
                    csc = cs.get("score", 0)
                    clv = html_escape(str(cs.get("level", "")))
                    coverage_popup_extra += (
                        f'<div style="font-size:11px;margin-top:4px;">'
                        f'Coverage: <b style="color:{cs.get("color", "#333")};">'
                        f'{clv}</b> ({csc:.0f})</div>'
                    )

        if has_groups:
            areas_str = html_escape(
                ", ".join(area_list) if area_list else "\u2014"
            )
            popup_t = (
                f'<div style="font-family:Arial;padding:10px;'
                f'min-width:200px;">'
                f'<b style="font-size:14px;color:'
                f'{colors["border"]};">{esc_ward}</b>'
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
                f'</table>'
                f'{coverage_popup_extra}'
                f'</div>')
        else:
            popup_t = (
                f'<div style="font-family:Arial;padding:10px;">'
                f'<b style="font-size:14px;">{esc_ward}</b><br>'
                f'<span style="color:#e74c3c;font-weight:bold;">'
                f'No groups \u2014 expansion zone</span>'
                f'{coverage_popup_extra}'
                f'</div>')

        # Draw the real irregular ward polygon
        fill_opacity = 0.40 if has_groups else 0.10
        if show_coverage:
            fill_opacity = 0.45 if has_groups else 0.20

        folium.Polygon(
            locations=bnd, color=colors["border"],
            fill=True, fill_color=colors["fill"],
            fill_opacity=fill_opacity,
            weight=3,
            popup=folium.Popup(popup_t, max_width=280),
            tooltip=esc_ward,
        ).add_to(t_layer)

        # Ward label at centroid
        avg_lat = sum(p[0] for p in bnd) / len(bnd)
        avg_lng = sum(p[1] for p in bnd) / len(bnd)

        label_text = display
        if show_coverage:
            # Add coverage score to the label
            best_score = -1.0
            for a in ward_areas:
                cs = coverage_scores.get(a)
                if cs is not None:
                    sc = cs.get("score", 0)
                    if sc > best_score:
                        best_score = sc
            if best_score >= 0:
                label_text = f"{display} ({best_score:.0f})"

        folium.Marker(
            location=[avg_lat, avg_lng],
            icon=folium.DivIcon(html=(
                f'<div style="font-family:Arial;font-size:11px;'
                f'font-weight:bold;color:{colors["border"]};'
                f'text-shadow:1px 1px 2px white,-1px -1px 2px white,'
                f'1px -1px 2px white,-1px 1px 2px white;'
                f'text-align:center;pointer-events:none;'
                f'white-space:nowrap;">{label_text}</div>'),
                icon_size=(180, 18), icon_anchor=(90, 9)),
        ).add_to(t_layer)

    # Build area -> color lookup from ward colors
    area_color_map: dict[str, dict[str, str]] = {}
    for area_name in area_names:
        ward = area_ward_map.get(area_name)
        if ward and ward in ward_color_map:
            area_color_map[area_name] = ward_color_map[ward]
        elif area_name in occupied:
            area_color_map[area_name] = TERRITORY_PALETTE[0]
        else:
            area_color_map[area_name] = UNOCCUPIED_COLOR

    # --- Layer 2: Group Markers ---
    nearby_df = df[
        df["area"].str.lower().str.strip().isin(set(area_names))]
    if layers.get("markers", True):
        for _, row in nearby_df.iterrows():
            mem = int(row["members"])
            akey = row["area"].lower().strip()
            colors = area_color_map.get(akey, TERRITORY_PALETTE[0])

            esc_leader = html_escape(str(row["leader_name"]))
            esc_area = html_escape(str(row["area"]))
            esc_meeting = html_escape(str(row.get("meeting_day", "")))
            esc_strength = html_escape(str(row.get("strength", "")))

            popup_html = (
                f'<div style="font-family:Arial;padding:8px;'
                f'min-width:150px;">'
                f'<b style="color:{colors["border"]};">'
                f'{esc_leader}</b>'
                f' ({esc_area})<hr style="margin:4px 0;">'
                f'<div style="font-size:12px;">'
                f'Families: {int(row.get("families", 0))}<br>'
                f'Individuals: {int(row.get("individuals", 0))}<br>'
                f'Total: <b>{mem}</b><br>'
                f'Meeting: {esc_meeting}<br>'
                f'Strength: {esc_strength}'
                f'</div></div>')
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=max(6, mem * 0.4),
                color=colors["border"], fill=True,
                fill_color=colors["fill"],
                fill_opacity=0.9, weight=2,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=(
                    f"{esc_leader} \u2014 {mem} members"
                ),
            ).add_to(m)
    # --- Layer 3: Gap Analysis ---
    if layers.get("gaps", False):
        for name in area_names:
            if name in occupied:
                continue
            coords = nearby[name]
            display = html_escape(name.title())
            folium.CircleMarker(
                location=coords, radius=20, color="#e74c3c",
                fill=True, fill_color="#e74c3c",
                fill_opacity=0.15, weight=2, dash_array="5 5",
            ).add_to(m)
            folium.CircleMarker(
                location=coords, radius=8, color="#e74c3c",
                fill=True, fill_color="#e74c3c",
                fill_opacity=0.4, weight=0,
            ).add_to(m)
            folium.Marker(
                location=[coords[0] - 0.002, coords[1]],
                icon=folium.DivIcon(html=(
                    f'<div style="font-family:Arial;font-size:10px;'
                    f'color:#c0392b;font-weight:bold;'
                    f'text-shadow:1px 1px 2px white,'
                    f'-1px -1px 2px white;'
                    f'text-align:center;pointer-events:none;">'
                    f'{display}<br>'
                    f'<span style="font-size:9px;color:#e74c3c;">'
                    f'NO COVERAGE</span></div>'),
                    icon_size=(140, 28), icon_anchor=(70, 14)),
            ).add_to(m)
    # --- Layer 4: Strength Indicators ---
    if layers.get("strength", False):
        for _, row in nearby_df.iterrows():
            strength_val = row.get("strength", "Weak")
            mem = int(row["members"])
            sc = STRENGTH_TERRITORY.get(
                strength_val, STRENGTH_TERRITORY["Weak"])
            sym = {"Strong": "+", "Medium": "~", "Weak": "-"}.get(
                strength_val, "?")
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=max(10, mem * 0.5),
                color=sc["border"], fill=True,
                fill_color=sc["fill"], fill_opacity=0.3, weight=2,
            ).add_to(m)
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                icon=folium.DivIcon(html=(
                    f'<div style="font-family:Arial;font-size:11px;'
                    f'font-weight:bold;color:{sc["border"]};'
                    f'text-shadow:1px 1px 1px white;'
                    f'text-align:center;pointer-events:none;">'
                    f'{sym}{mem}</div>'),
                    icon_size=(40, 16), icon_anchor=(20, 8)),
            ).add_to(m)
    # --- Layer 5: Member Density Stats ---
    if layers.get("density", False):
        for name in area_names:
            srow = slookup.get(name)
            if srow is None:
                continue
            coords = nearby[name]
            mem = int(srow["total_members"])
            grp = int(srow["total_groups"])
            avg = mem / grp if grp > 0 else 0
            esc_name = html_escape(name.title())
            folium.Marker(
                location=[coords[0] - 0.001, coords[1]],
                icon=folium.DivIcon(html=(
                    f'<div style="font-family:Arial;background:white;'
                    f'border:1px solid #ddd;border-radius:6px;'
                    f'padding:6px 8px;box-shadow:0 1px 4px '
                    f'rgba(0,0,0,0.2);text-align:center;'
                    f'pointer-events:none;">'
                    f'<div style="font-size:11px;font-weight:bold;'
                    f'color:#333;">{esc_name}</div>'
                    f'<div style="font-size:18px;font-weight:bold;'
                    f'color:#2E7D32;">{mem}</div>'
                    f'<div style="font-size:9px;color:#888;">'
                    f'{grp} groups avg {avg:.0f}</div>'
                    f'</div>'),
                    icon_size=(130, 60), icon_anchor=(65, 30)),
            ).add_to(m)

    # --- Layer 6: Heatmap ---
    if layers.get("heatmap", False):
        heat_data = build_heatmap_layer(nearby_df)
        if heat_data:
            HeatMap(
                heat_data,
                min_opacity=0.3,
                radius=25,
                blur=20,
                gradient=HEATMAP_GRADIENT,
            ).add_to(m)

    # No Folium LayerControl -- layers controlled via Streamlit UI

    # Mobile-responsive styles for map UI elements
    mobile_css = """
    <style>
    .leaflet-control-layers {
        max-width: 180px !important;
        font-size: 12px !important;
    }
    @media screen and (max-width: 480px) {
        .leaflet-control-layers {
            max-width: 140px !important;
            font-size: 10px !important;
            top: 5px !important;
            right: 5px !important;
        }
        .leaflet-control-layers label {
            font-size: 10px !important;
            margin: 2px 0 !important;
        }
        div[style*="position: fixed"] {
            display: none !important;
        }
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(mobile_css))

    # Legend removed -- shown as KPIs in Streamlit UI instead

    elapsed = time.perf_counter() - t0
    logger.info("Advanced territory map built in %.3fs", elapsed)
    return m


def _add_advanced_legend(
    m: folium.Map,
    color_by: str,
    area_names: list[str],
    occupied: set[str],
    center_area: str,
) -> None:
    """Legend for advanced territory map."""
    occ = sum(1 for n in area_names if n in occupied)
    total = len(area_names)
    gap = total - occ  # noqa: F841
    esc_center = html_escape(center_area.title())

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
             padding-bottom:6px;">{esc_center} Region</div>
        {mode_items}
        <div style="margin-top:6px;padding-top:6px;
             border-top:1px solid #eee;">
            <div style="margin-bottom:2px;">
                <span style="display:inline-block;width:12px;
                      height:12px;background:#9E9E9E;
                      border-radius:2px;"></span>
                <span style="font-size:11px;">
                    Unoccupied</span></div></div>
        <div style="font-size:10px;color:#888;margin-top:6px;
             text-align:center;">
            {occ}/{total} territories occupied</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


def generate_territory_kml(df: pd.DataFrame, summary_df: pd.DataFrame) -> str:
    """Generate KML string for territory data export."""
    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '<name>LG GeoView Territories</name>',
    ]
    for _, row in summary_df.iterrows():
        area = xml_escape(str(row["area"]))
        mem = int(row["total_members"])
        grp = int(row["total_groups"])
        strength_val = xml_escape(str(row.get("strength", "")))
        lines.append('<Placemark>')
        lines.append(f'<name>{area}</name>')
        lines.append(
            f'<description>{grp} groups, {mem} members,'
            f' {strength_val}</description>')
        lines.append(
            f'<Point><coordinates>{row["longitude"]},'
            f'{row["latitude"]},0</coordinates></Point>')
        lines.append('</Placemark>')
    for _, row in df.iterrows():
        esc_leader = xml_escape(str(row["leader_name"]))
        esc_area = xml_escape(str(row["area"]))
        lines.append('<Placemark>')
        lines.append(
            f'<name>{esc_leader} - {esc_area}</name>')
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


# --- Coverage Overview Map (Pastor's View) ---

ZONE_STRENGTH_COLORS: dict[str, dict[str, str]] = {
    "Strong": {"fill": "#2E7D32", "border": "#4CAF50"},
    "Medium": {"fill": "#F57F17", "border": "#FFC107"},
    "Weak":   {"fill": "#C62828", "border": "#F44336"},
}


def build_coverage_overview_map(zone_summary: "pd.DataFrame") -> folium.Map:
    """Build a clean, full-screen coverage map with one marker per zone.

    Uses CartoDB Positron tiles for a schematic look.
    Each zone gets a circle marker with a popup showing area details.
    """
    t0 = time.perf_counter()
    logger.info("Building coverage overview map with %d zones", len(zone_summary))

    center, bounds = _compute_map_bounds()

    m = folium.Map(
        location=center,
        zoom_start=DEFAULT_ZOOM,
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Positron",
    )
    _apply_fixed_bounds(m, bounds)

    if zone_summary.empty:
        return m

    for _, row in zone_summary.iterrows():
        zone_name = str(row["zone"])
        total_members = int(row["total_members"])
        total_groups = int(row["total_groups"])
        strength = row.get("strength", "Weak")
        colors = ZONE_STRENGTH_COLORS.get(strength, ZONE_STRENGTH_COLORS["Weak"])

        leaders = row.get("leaders", [])
        meeting_days = row.get("meeting_days", [])
        areas = row.get("areas", [])

        esc_zone = html_escape(zone_name)

        # Build leader rows for popup
        leader_rows = ""
        for i, leader in enumerate(leaders):
            esc_leader = html_escape(str(leader))
            day = meeting_days[i] if i < len(meeting_days) else ""
            esc_day = html_escape(str(day))
            area_name = areas[i] if i < len(areas) else ""
            esc_area = html_escape(str(area_name))
            leader_rows += (
                f'<tr>'
                f'<td style="padding:3px 8px;font-size:12px;color:#5D4E37;">{esc_leader}</td>'
                f'<td style="padding:3px 8px;font-size:12px;color:#7A6B50;">{esc_day}</td>'
                f'</tr>'
            )

        # Sub-areas line (only if zone has multiple areas)
        sub_areas_html = ""
        if len(areas) > 1:
            esc_areas = ", ".join(html_escape(str(a)) for a in areas)
            sub_areas_html = (
                f'<div style="font-size:10px;color:#999;margin-top:2px;">'
                f'{esc_areas}</div>'
            )

        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;
             min-width: 220px; max-width: 300px;
             background: #FFFBF0; color: #5D4E37;
             padding: 14px 16px; border-radius: 8px;
             border: 1px solid {colors['border']};">
            <div style="font-size: 16px; font-weight: bold; color: {colors['fill']};
                 letter-spacing: 1px; margin-bottom: 4px;
                 border-bottom: 2px solid {colors['border']}; padding-bottom: 6px;">
                {esc_zone}
            </div>
            {sub_areas_html}
            <div style="display:flex; gap:16px; margin:8px 0;">
                <div>
                    <div style="font-size:20px;font-weight:bold;color:{colors['fill']};">{total_members}</div>
                    <div style="font-size:10px;color:#999;">Members</div>
                </div>
                <div>
                    <div style="font-size:20px;font-weight:bold;color:{colors['fill']};">{total_groups}</div>
                    <div style="font-size:10px;color:#999;">Care Groups</div>
                </div>
            </div>
            <table style="width:100%;border-collapse:collapse;margin-top:6px;">
                <tr style="border-bottom:1px solid #eee;">
                    <th style="text-align:left;padding:3px 8px;font-size:11px;color:#999;">Leader</th>
                    <th style="text-align:left;padding:3px 8px;font-size:11px;color:#999;">Meeting Day</th>
                </tr>
                {leader_rows}
            </table>
        </div>
        """

        # Zone circle marker -- size based on member count
        marker_radius = max(10, min(30, total_members * 0.4))
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=marker_radius,
            color=colors["border"],
            fill=True,
            fill_color=colors["fill"],
            fill_opacity=0.6,
            weight=2,
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(m)

        # Member count inside circle
        count_html = f"""
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif;
            color: white;
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            pointer-events: none;
        ">{total_members}</div>
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(
                html=count_html,
                icon_size=(40, 16),
                icon_anchor=(20, 8),
            ),
        ).add_to(m)

        # Zone name label above marker
        label_html = f"""
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #5D4E37;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            white-space: nowrap;
            text-shadow: 1px 1px 2px white, -1px -1px 2px white;
            pointer-events: none;
        ">{esc_zone}</div>
        """
        folium.Marker(
            location=[row["latitude"] + 0.005, row["longitude"]],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(200, 18),
                icon_anchor=(100, 9),
            ),
        ).add_to(m)

    elapsed = time.perf_counter() - t0
    logger.info("Coverage overview map built in %.3fs", elapsed)
    return m
