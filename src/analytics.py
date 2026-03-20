"""Business logic extracted from app.py for testability."""

from __future__ import annotations

import pandas as pd


def compute_territory_coverage(
    focus_area: str,
    radius_km: int,
    area_coordinates: dict,
    occupied_areas: set,
) -> dict:
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
        dist = ((coords[0] - cc[0]) ** 2 + (coords[1] - cc[1]) ** 2) ** 0.5
        if dist <= radius_km * 0.01:
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


def compute_kpi_metrics(df: pd.DataFrame) -> dict:
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
