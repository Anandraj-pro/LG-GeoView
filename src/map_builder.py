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

    # Dark tile layer for kingdom aesthetic
    m = folium.Map(
        location=HYDERABAD_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Dark Matter",
    )

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


# --- Territory Fill Colors ---
TERRITORY_PALETTE = [
    {"fill": "#1B5E20", "border": "#2E7D32"},    # deep green
    {"fill": "#0D47A1", "border": "#1565C0"},     # deep blue
    {"fill": "#B71C1C", "border": "#C62828"},     # deep red
    {"fill": "#4A148C", "border": "#6A1B9A"},     # purple
    {"fill": "#E65100", "border": "#EF6C00"},     # orange
    {"fill": "#006064", "border": "#00838F"},     # teal
    {"fill": "#880E4F", "border": "#AD1457"},     # burgundy
    {"fill": "#1A237E", "border": "#283593"},     # indigo
    {"fill": "#33691E", "border": "#558B2F"},     # olive
    {"fill": "#BF360C", "border": "#D84315"},     # terracotta
    {"fill": "#004D40", "border": "#00695C"},     # emerald
    {"fill": "#311B92", "border": "#4527A0"},     # violet
    {"fill": "#827717", "border": "#9E9D24"},     # moss
    {"fill": "#01579B", "border": "#0277BD"},     # steel blue
    {"fill": "#F57F17", "border": "#F9A825"},     # amber
    {"fill": "#263238", "border": "#37474F"},     # charcoal
    {"fill": "#3E2723", "border": "#4E342E"},     # mahogany
    {"fill": "#1B5E20", "border": "#388E3C"},     # jade
]

UNOCCUPIED_COLOR = {"fill": "#333333", "border": "#555555"}

KUKATPALLY_CENTER = [17.4948, 78.3996]
KUKATPALLY_RADIUS = 0.03


def _compute_voronoi_cells(centers, bbox):
    """Compute Voronoi-like polygons using grid sampling (no scipy)."""
    lat_min, lat_max, lng_min, lng_max = bbox
    grid_size = 40
    lat_step = (lat_max - lat_min) / grid_size
    lng_step = (lng_max - lng_min) / grid_size

    # Assign each grid cell to the nearest center
    # Key: center_index -> list of (lat, lng) grid corners
    cell_assignments = {i: [] for i in range(len(centers))}

    for row in range(grid_size):
        for col in range(grid_size):
            cell_lat = lat_min + row * lat_step
            cell_lng = lng_min + col * lng_step
            mid_lat = cell_lat + lat_step / 2
            mid_lng = cell_lng + lng_step / 2

            # Find nearest center
            min_dist = float("inf")
            nearest = 0
            for i, (clat, clng) in enumerate(centers):
                d = ((mid_lat - clat) ** 2 +
                     (mid_lng - clng) ** 2)
                if d < min_dist:
                    min_dist = d
                    nearest = i

            cell_assignments[nearest].append(
                (cell_lat, cell_lng, lat_step, lng_step)
            )

    return cell_assignments


def build_territory_map(df: pd.DataFrame, summary_df: pd.DataFrame,
                        center_area: str = "Kukatpally",
                        radius: float = KUKATPALLY_RADIUS) -> folium.Map:
    """Build a full-fill territory map. Every cell on the map is colored
    by its nearest area — occupied areas in color, empty zones gray."""
    t0 = time.perf_counter()
    logger.info("Building territory map centered on %s", center_area)

    from src.data_loader import AREA_COORDINATES

    # Get center coordinates
    center_key = center_area.lower().strip()
    center_coords = AREA_COORDINATES.get(center_key, KUKATPALLY_CENTER)

    # Find nearby area coordinates
    nearby = {}
    for area_name, coords in AREA_COORDINATES.items():
        dist = ((coords[0] - center_coords[0]) ** 2 +
                (coords[1] - center_coords[1]) ** 2) ** 0.5
        if dist <= radius:
            nearby[area_name] = coords

    # Dark map
    m = folium.Map(
        location=center_coords,
        zoom_start=14,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB Dark Matter",
    )

    if not nearby:
        return m

    # Bounding box with padding
    lats = [c[0] for c in nearby.values()]
    lngs = [c[1] for c in nearby.values()]
    pad = 0.005
    bbox = (min(lats) - pad, max(lats) + pad,
            min(lngs) - pad, max(lngs) + pad)

    # Build centers list and track which are occupied
    area_names = list(nearby.keys())
    centers = [nearby[a] for a in area_names]

    # Which areas have data (occupied)?
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

    # Compute grid cells assigned to each area center
    cell_assignments = _compute_voronoi_cells(centers, bbox)

    # Draw filled rectangles for each cell
    for center_idx, cells in cell_assignments.items():
        name = area_names[center_idx]
        colors = area_color_map[name]
        is_occupied = name in occupied_areas
        opacity = 0.45 if is_occupied else 0.15

        for (clat, clng, dlat, dlng) in cells:
            bounds = [
                [clat, clng],
                [clat + dlat, clng],
                [clat + dlat, clng + dlng],
                [clat, clng + dlng],
            ]
            folium.Polygon(
                locations=bounds,
                color=colors["border"],
                fill=True,
                fill_color=colors["fill"],
                fill_opacity=opacity,
                weight=0.5,
            ).add_to(m)

    # Draw bold borders between different areas
    grid_size = 40
    lat_step = (bbox[1] - bbox[0]) / grid_size
    lng_step = (bbox[3] - bbox[2]) / grid_size

    # Build a 2D grid of assignments for border detection
    grid = []
    for row in range(grid_size):
        grid_row = []
        for col in range(grid_size):
            mid_lat = bbox[0] + row * lat_step + lat_step / 2
            mid_lng = bbox[2] + col * lng_step + lng_step / 2
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

    # Draw border lines where neighboring cells differ
    for row in range(grid_size):
        for col in range(grid_size):
            curr = grid[row][col]
            lat0 = bbox[0] + row * lat_step
            lng0 = bbox[2] + col * lng_step
            # Right neighbor
            if col + 1 < grid_size and grid[row][col + 1] != curr:
                folium.PolyLine(
                    [[lat0, lng0 + lng_step],
                     [lat0 + lat_step, lng0 + lng_step]],
                    color="#FFFFFF", weight=2, opacity=0.6,
                ).add_to(m)
            # Bottom neighbor
            if row + 1 < grid_size and grid[row + 1][col] != curr:
                folium.PolyLine(
                    [[lat0 + lat_step, lng0],
                     [lat0 + lat_step, lng0 + lng_step]],
                    color="#FFFFFF", weight=2, opacity=0.6,
                ).add_to(m)

    # Area name labels + stats at each center
    nearby_summary = summary_df[
        summary_df["area"].str.lower().str.strip().isin(
            set(area_names)
        )
    ]

    # Map display name -> summary row for occupied areas
    summary_lookup = {}
    for _, srow in nearby_summary.iterrows():
        summary_lookup[srow["area"].lower().strip()] = srow

    for name in area_names:
        coords = nearby[name]
        colors = area_color_map[name]
        is_occupied = name in occupied_areas
        srow = summary_lookup.get(name)

        # Area name
        display = name.title()
        label_color = colors["border"] if is_occupied else "#777"
        label_html = (
            f'<div style="font-family: Cinzel, serif;'
            f' font-size: 12px; font-weight: 700;'
            f' color: {label_color};'
            f' text-shadow: 0 0 8px rgba(0,0,0,0.9);'
            f' text-align: center; letter-spacing: 1px;'
            f' text-transform: uppercase; white-space: nowrap;'
            f' pointer-events: none;">{display}</div>'
        )
        folium.Marker(
            location=[coords[0] + 0.002, coords[1]],
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(160, 18),
                icon_anchor=(80, 9),
            ),
        ).add_to(m)

        # Stats line
        if srow is not None:
            groups = int(srow["total_groups"])
            members = int(srow["total_members"])
            stats_html = (
                f'<div style="font-size: 10px; color: #bbb;'
                f' text-shadow: 0 0 4px rgba(0,0,0,0.9);'
                f' text-align: center; pointer-events: none;">'
                f'{groups} groups &middot; {members} members</div>'
            )
        else:
            stats_html = (
                '<div style="font-size: 10px; color: #666;'
                ' text-shadow: 0 0 4px rgba(0,0,0,0.9);'
                ' text-align: center; pointer-events: none;">'
                'No groups yet</div>'
            )
        folium.Marker(
            location=[coords[0], coords[1]],
            icon=folium.DivIcon(
                html=stats_html,
                icon_size=(160, 14),
                icon_anchor=(80, 7),
            ),
        ).add_to(m)

    # Group markers on top
    nearby_df = df[
        df["area"].str.lower().str.strip().isin(set(area_names))
    ]
    for _, row in nearby_df.iterrows():
        members = int(row["members"])
        akey = row["area"].lower().strip()
        colors = area_color_map.get(akey, TERRITORY_PALETTE[0])

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(5, members * 0.35),
            color="#FFFFFF",
            fill=True,
            fill_color=colors["border"],
            fill_opacity=0.9,
            weight=1.5,
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
    """Add territory color legend."""
    items_html = ""
    for name in sorted(area_names):
        colors = area_color_map[name]
        is_occ = name in occupied_areas
        display = name.title()
        srow = summary_lookup.get(name)
        if srow is not None:
            members = int(srow["total_members"])
            groups = int(srow["total_groups"])
            detail = f"{groups}g &middot; {members}m"
        else:
            detail = "empty"
        label_color = "#e0e0e0" if is_occ else "#666"
        items_html += (
            f'<div style="margin-bottom: 5px; display: flex;'
            f' align-items: center;">'
            f'<div style="width: 14px; height: 14px;'
            f' border-radius: 2px;'
            f' background: {colors["fill"]};'
            f' border: 1px solid {colors["border"]};'
            f' margin-right: 8px; flex-shrink: 0;'
            f' opacity: {"1" if is_occ else "0.4"};"></div>'
            f'<div><span style="color: {label_color};'
            f' font-size: 11px;">{display}</span>'
            f' <span style="color: #888; font-size: 9px;">'
            f'{detail}</span></div></div>'
        )

    occ_count = sum(1 for n in area_names if n in occupied_areas)
    total_count = len(area_names)

    legend_html = f"""
    <div style="
        position: fixed; bottom: 20px; right: 10px; z-index: 1000;
        background: linear-gradient(145deg, #1e1e2f 0%, #252540 100%);
        color: #e0e0e0; padding: 16px 18px; border-radius: 10px;
        border: 1px solid #444; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        font-family: 'Palatino Linotype', serif; font-size: 12px;
        min-width: 180px; max-width: 260px;
        max-height: 420px; overflow-y: auto;
    ">
        <div style="font-family: Cinzel, serif; font-size: 13px;
             font-weight: 700; letter-spacing: 2px;
             text-transform: uppercase; margin-bottom: 10px;
             border-bottom: 1px solid #444; padding-bottom: 8px;
             text-align: center; color: #ccc;">
            {center_area.title()} Region
        </div>
        {items_html}
        <div style="border-top: 1px solid #444; padding-top: 8px;
             margin-top: 8px; font-size: 10px; color: #888;
             text-align: center;">
            {occ_count}/{total_count} territories occupied
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
