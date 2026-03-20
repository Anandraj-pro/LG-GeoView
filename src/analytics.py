"""Business logic extracted from app.py for testability."""

from __future__ import annotations

import math

import pandas as pd


# Coverage scoring color constants
COVERAGE_GREEN = "#2E7D32"
COVERAGE_YELLOW = "#F9A825"
COVERAGE_RED = "#C62828"
COVERAGE_GRAY = "#9E9E9E"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compute_coverage_scores(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Score each area's coverage level.

    Scoring based on weighted components:
    - total_members: weight 40%
    - total_groups: weight 40%
    - avg_members per group: weight 20%

    Classification:
    - Green (Well Served): score >= 70
    - Yellow (Partial): score >= 40
    - Red (Underserved): score < 40

    Parameters
    ----------
    summary_df : pd.DataFrame
        Area summary with columns: area, total_members, total_groups,
        avg_members.

    Returns
    -------
    pd.DataFrame
        Copy of summary_df with added columns: coverage_score,
        coverage_level, coverage_color.
    """
    if summary_df.empty:
        result = summary_df.copy()
        result["coverage_score"] = pd.Series(dtype=float)
        result["coverage_level"] = pd.Series(dtype=str)
        result["coverage_color"] = pd.Series(dtype=str)
        return result

    result = summary_df.copy()

    members = pd.to_numeric(result["total_members"], errors="coerce").fillna(0)
    groups = pd.to_numeric(result["total_groups"], errors="coerce").fillna(0)
    avg = pd.to_numeric(result["avg_members"], errors="coerce").fillna(0)

    members_score = (members / 30 * 100).clip(upper=100)
    groups_score = (groups / 2 * 100).clip(upper=100)
    avg_score = (avg / 20 * 100).clip(upper=100)

    result["coverage_score"] = (
        members_score * 0.4 + groups_score * 0.4 + avg_score * 0.2
    ).round(1)

    def _classify(score: float) -> str:
        if score >= 70:
            return "Well Served"
        elif score >= 40:
            return "Partial"
        return "Underserved"

    def _color(score: float) -> str:
        if score >= 70:
            return COVERAGE_GREEN
        elif score >= 40:
            return COVERAGE_YELLOW
        return COVERAGE_RED

    result["coverage_level"] = result["coverage_score"].apply(_classify)
    result["coverage_color"] = result["coverage_score"].apply(_color)

    return result


def compute_territory_coverage(
    focus_area: str,
    radius_km: int,
    area_coordinates: dict[str, tuple[float, float]],
    occupied_areas: set[str],
) -> dict[str, set[str] | int | list[str]]:
    """Compute which areas are within radius and which are uncovered.

    Parameters
    ----------
    focus_area : str
        The area to center the analysis on (e.g. "Kukatpally").
    radius_km : int
        Search radius in kilometres.
    area_coordinates : dict
        Mapping of area name (lowercase) -> (lat, lng) tuple.
    occupied_areas : set
        Set of area names (lowercase, stripped) that have LG groups.

    Returns
    -------
    dict with keys:
        nearby_set : set of area names within radius
        occupied_count : int
        total_nearby : int
        uncovered : list of title-cased area names with no groups
    """
    ck = focus_area.lower().strip()
    cc = area_coordinates.get(ck, (17.4948, 78.3996))

    nearby_set: set[str] = set()
    for area_name, coords in area_coordinates.items():
        dist = haversine_km(cc[0], cc[1], coords[0], coords[1])
        if dist <= radius_km:
            nearby_set.add(area_name)

    occupied_count = sum(1 for n in nearby_set if n in occupied_areas)
    total_nearby = len(nearby_set)
    uncovered = [n.title() for n in nearby_set if n not in occupied_areas]

    return {
        "nearby_set": nearby_set,
        "occupied_count": occupied_count,
        "total_nearby": total_nearby,
        "uncovered": uncovered,
    }


def compute_kpi_metrics(df: pd.DataFrame) -> dict[str, int | float]:
    """Compute all KPI values from a filtered dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered dataframe with columns: families, individuals, members,
        area, strength.

    Returns
    -------
    dict with keys: total_groups, total_families, total_individuals,
        total_members, num_areas, avg_per_group, strong_count, weak_count
    """
    total_groups = len(df)
    total_families = int(df["families"].sum()) if not df.empty else 0
    total_individuals = int(df["individuals"].sum()) if not df.empty else 0
    total_members = int(df["members"].sum()) if not df.empty else 0
    num_areas = df["area"].nunique() if not df.empty else 0
    avg_per_group = total_members / total_groups if total_groups > 0 else 0
    strong_count = int((df["strength"] == "Strong").sum()) if not df.empty else 0
    weak_count = int((df["strength"] == "Weak").sum()) if not df.empty else 0

    return {
        "total_groups": total_groups,
        "total_families": total_families,
        "total_individuals": total_individuals,
        "total_members": total_members,
        "num_areas": num_areas,
        "avg_per_group": avg_per_group,
        "strong_count": strong_count,
        "weak_count": weak_count,
    }


def generate_html_report(df: pd.DataFrame, summary_df: pd.DataFrame, kpi: dict[str, int | float]) -> str:
    """Generate a printable HTML report.

    Parameters
    ----------
    df : pd.DataFrame
        Full filtered dataframe with group-level details.
    summary_df : pd.DataFrame
        Area-level summary dataframe.
    kpi : dict
        KPI metrics dict from compute_kpi_metrics.

    Returns
    -------
    str
        Complete HTML document string suitable for download.
    """
    # Build summary table rows
    summary_rows = ""
    for _, row in summary_df.iterrows():
        summary_rows += (
            "<tr>"
            f"<td>{row.get('area', '')}</td>"
            f"<td>{row.get('total_groups', '')}</td>"
            f"<td>{row.get('total_families', '')}</td>"
            f"<td>{row.get('total_members', '')}</td>"
            f"<td>{row.get('avg_members', '')}</td>"
            f"<td>{row.get('strength', '')}</td>"
            "</tr>"
        )

    # Build detail table rows
    detail_rows = ""
    detail_cols = ["area", "lg_group", "leader_name", "families",
                   "individuals", "members", "meeting_day"]
    available_cols = [c for c in detail_cols if c in df.columns]
    for _, row in df.iterrows():
        detail_rows += "<tr>"
        for col in available_cols:
            detail_rows += f"<td>{row[col]}</td>"
        detail_rows += "</tr>"

    detail_headers = ""
    col_labels: dict[str, str] = {
        "area": "Area",
        "lg_group": "Care Group",
        "leader_name": "Leader",
        "families": "Families",
        "individuals": "Individuals",
        "members": "Members",
        "meeting_day": "Meeting Day",
    }
    for col in available_cols:
        detail_headers += f"<th>{col_labels.get(col, col)}</th>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TKT Kingdom - Care Group Report</title>
<style>
    body {{
        font-family: Georgia, 'Times New Roman', serif;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background: #fff;
    }}
    h1 {{
        text-align: center;
        color: #8B6914;
        font-size: 1.8rem;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }}
    h2 {{
        color: #8B6914;
        font-size: 1.2rem;
        border-bottom: 1px solid #D4AF37;
        padding-bottom: 4px;
        margin-top: 28px;
    }}
    .subtitle {{
        text-align: center;
        color: #888;
        font-style: italic;
        margin-bottom: 24px;
    }}
    .kpi-row {{
        display: flex;
        justify-content: center;
        gap: 24px;
        margin: 20px 0;
        flex-wrap: wrap;
    }}
    .kpi-box {{
        text-align: center;
        padding: 12px 20px;
        border: 1px solid #D4AF37;
        border-radius: 8px;
        min-width: 100px;
    }}
    .kpi-value {{
        font-size: 1.6rem;
        font-weight: bold;
        color: #8B6914;
    }}
    .kpi-label {{
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        font-size: 0.9rem;
    }}
    th {{
        background: #F5EDD8;
        color: #5D4E37;
        padding: 8px 10px;
        text-align: left;
        border-bottom: 2px solid #D4AF37;
    }}
    td {{
        padding: 6px 10px;
        border-bottom: 1px solid #eee;
    }}
    tr:nth-child(even) {{
        background: #FDFAF2;
    }}
    .footer {{
        text-align: center;
        margin-top: 32px;
        color: #aaa;
        font-size: 0.8rem;
    }}
    @media print {{
        body {{ padding: 0; }}
        .kpi-box {{ border: 1px solid #ccc; }}
    }}
</style>
</head>
<body>
<h1>TKT Kingdom</h1>
<div class="subtitle">West Campus Care Group Report</div>

<div class="kpi-row">
    <div class="kpi-box">
        <div class="kpi-value">{kpi.get('num_areas', 0)}</div>
        <div class="kpi-label">Territories</div>
    </div>
    <div class="kpi-box">
        <div class="kpi-value">{kpi.get('total_groups', 0)}</div>
        <div class="kpi-label">Care Groups</div>
    </div>
    <div class="kpi-box">
        <div class="kpi-value">{kpi.get('total_members', 0)}</div>
        <div class="kpi-label">Total Members</div>
    </div>
    <div class="kpi-box">
        <div class="kpi-value">{kpi.get('total_families', 0)}</div>
        <div class="kpi-label">Families</div>
    </div>
    <div class="kpi-box">
        <div class="kpi-value">{kpi.get('strong_count', 0)}</div>
        <div class="kpi-label">Strong Groups</div>
    </div>
</div>

<h2>Area Summary</h2>
<table>
<thead>
<tr>
    <th>Area</th><th>Groups</th><th>Families</th>
    <th>Members</th><th>Avg/Group</th><th>Strength</th>
</tr>
</thead>
<tbody>
{summary_rows}
</tbody>
</table>

<h2>Group Details</h2>
<table>
<thead>
<tr>{detail_headers}</tr>
</thead>
<tbody>
{detail_rows}
</tbody>
</table>

<div class="footer">
    TKT Kingdom &middot; West Campus &middot; Hyderabad
</div>
</body>
</html>"""
    return html
