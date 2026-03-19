"""Data loading module — Excel, Google Sheets, CSV support."""

import json
import os
import time

import pandas as pd
import streamlit as st

from src.logger import get_logger

logger = get_logger(__name__)

# Final clean columns for the dashboard
DASHBOARD_COLUMNS = ["area", "lg_group", "leader_name", "families", "individuals",
                     "members", "meeting_day", "latitude", "longitude"]

# Hardcoded fallback coordinates for Hyderabad West localities
_HARDCODED_COORDINATES = {
    "chintal 1": (17.4685, 78.3900),
    "chintal 2": (17.4710, 78.3925),
    "raju colony": (17.4635, 78.3820),
    "j. gutta": (17.4830, 78.3870),
    "idpl": (17.4680, 78.3860),
    "gajularamaram": (17.4870, 78.3830),
    "jdm": (17.4980, 78.3810),
    "jeedimetla": (17.4980, 78.3810),
    "ferozguda": (17.4900, 78.3870),
    "borabanda": (17.4350, 78.4150),
    "moosapet": (17.4580, 78.4270),
    "maitreenagar": (17.4970, 78.3900),
    "swan lake": (17.4940, 78.3920),
    "kukatpally": (17.4948, 78.3996),
    "vadaypally": (17.4870, 78.3930),
    "allwyn colony": (17.4920, 78.3920),
    "vvnagar": (17.4940, 78.3980),
    "jntu": (17.4960, 78.3950),
    "balajinagar": (17.4890, 78.3950),
    "kphb": (17.4835, 78.3878),
    "kphb 2": (17.4850, 78.3900),
    "nizampet": (17.5100, 78.3830),
    "pragathinagar": (17.5150, 78.3750),
    "vasanthanagar": (17.4910, 78.3950),
    "bachupally": (17.5200, 78.3700),
    "mallampet": (17.5250, 78.3650),
    "hmt miyapur": (17.4965, 78.3537),
    "kondapur": (17.4600, 78.3700),
    "miyapur": (17.4965, 78.3540),
    "chandanagar": (17.4870, 78.3350),
    "nallagandla": (17.4748, 78.3103),
    "beeramguda": (17.4920, 78.3200),
    "patancheruvu": (17.5300, 78.2700),
}


def _load_area_coordinates() -> dict:
    """Load area coordinates from JSON config file, falling back to hardcoded defaults."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "area_coordinates.json")
    try:
        with open(config_path, "r") as f:
            coords = json.load(f)
            # Convert lists to tuples for consistency
            return {k: tuple(v) for k, v in coords.items()}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Could not load area_coordinates.json, using hardcoded defaults: %s", e)
        return _HARDCODED_COORDINATES


AREA_COORDINATES = _load_area_coordinates()

# Known column name mappings for Excel format normalization
_EXCEL_COLUMN_MAP = {
    "leader_name": "leader_name",
    ",leader_name,": "leader_name",
    "leader name": "leader_name",
    "leadername": "leader_name",
    "care coordinator": "care_coordinator",
    "carecoordinator": "care_coordinator",
    "coordinator": "care_coordinator",
    "families": "families",
    "individuals": "individuals",
    "total": "total",
    "sync meeting on": "meeting_day",
    "meeting day": "meeting_day",
    "meetingday": "meeting_day",
    "area": "area",
}


def _normalize_excel_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize Excel column names: strip, lowercase, map known variations."""
    normalized = {}
    for col in df.columns:
        clean = str(col).strip().lower().replace("_", " ").replace(",", "").strip()
        if clean in _EXCEL_COLUMN_MAP:
            normalized[col] = _EXCEL_COLUMN_MAP[clean]
        else:
            normalized[col] = clean

    # Check for fuzzy matches on unmapped columns
    mapped_values = set(normalized.values())
    for orig_col, mapped_col in list(normalized.items()):
        if mapped_col not in _EXCEL_COLUMN_MAP.values():
            # Try substring matching
            for known_key, known_val in _EXCEL_COLUMN_MAP.items():
                if known_val not in mapped_values and known_key in mapped_col:
                    logger.warning("Fuzzy column match: '%s' -> '%s'", orig_col, known_val)
                    normalized[orig_col] = known_val
                    mapped_values.add(known_val)
                    break

    df = df.rename(columns=normalized)
    return df


def load_from_excel(file_path: str = "data/West_Campus_Care_Groups_Area 2026.xlsx") -> pd.DataFrame:
    """Load and parse the West Campus Excel file with shifted column handling."""
    t0 = time.perf_counter()
    logger.info("Loading Excel data from %s", file_path)
    try:
        raw = pd.read_excel(file_path, sheet_name="Sheet1")
    except Exception as e:
        st.error(f"Failed to load Excel: {e}")
        logger.error("Failed to load Excel file %s", file_path, exc_info=True)
        return pd.DataFrame()

    raw = _normalize_excel_columns(raw)

    # Ensure expected columns exist with defaults
    expected_cols = ["leader_name", "area", "care_coordinator",
                     "families", "individuals", "total", "meeting_day"]
    for col in expected_cols:
        if col not in raw.columns:
            raw[col] = None

    # Convert columns to string for vectorized operations
    ln = raw["leader_name"].astype(str).where(raw["leader_name"].notna(), "").str.strip()
    ar = raw["area"].astype(str).where(raw["area"].notna(), "").str.strip()
    cc = raw["care_coordinator"].astype(str).where(raw["care_coordinator"].notna(), "").str.strip()

    # Determine leader and area: normal vs shifted columns
    normal_mask = ln != ""
    shifted_mask = (~normal_mask) & (ar != "")
    valid_mask = normal_mask | shifted_mask

    leader = pd.Series("", index=raw.index)
    area = pd.Series("", index=raw.index)
    leader[normal_mask] = ln[normal_mask]
    area[normal_mask] = ar[normal_mask]
    leader[shifted_mask] = ar[shifted_mask]
    area[shifted_mask] = cc[shifted_mask]

    # Build working DataFrame with only valid rows
    df = pd.DataFrame({
        "leader_name": leader,
        "area": area,
    }, index=raw.index)
    df = df[valid_mask].copy()

    # Skip total/summary rows
    df = df[~df["leader_name"].str.lower().str.strip().isin(("total",))].copy()

    if df.empty:
        return pd.DataFrame()

    # Vectorized numeric conversions
    df["families"] = pd.to_numeric(raw.loc[df.index, "families"], errors="coerce").fillna(0).astype(int)
    df["individuals"] = pd.to_numeric(raw.loc[df.index, "individuals"], errors="coerce").fillna(0).astype(int)
    total = pd.to_numeric(raw.loc[df.index, "total"], errors="coerce")
    df["members"] = total.fillna(df["families"] + df["individuals"]).astype(int)

    # Meeting day
    md = raw.loc[df.index, "meeting_day"].fillna("").astype(str).str.strip().str.title()
    df["meeting_day"] = md

    # LG group name
    df["lg_group"] = df["area"] + " - " + df["leader_name"]

    # Vectorized geocoding
    area_lower = df["area"].str.lower().str.strip()
    df["latitude"] = area_lower.map(lambda a: AREA_COORDINATES.get(a, (None, None))[0])
    df["longitude"] = area_lower.map(lambda a: AREA_COORDINATES.get(a, (None, None))[1])

    # Warn about missing coordinates
    missing_coords = df[df["latitude"].isna()]["area"].unique()
    if len(missing_coords) > 0:
        st.warning(f"Missing coordinates for: {', '.join(missing_coords)}")
        logger.warning("Missing coordinates for areas: %s", ", ".join(missing_coords))

    df = df.dropna(subset=["latitude", "longitude"])

    # Reorder columns to match expected schema
    df = df[DASHBOARD_COLUMNS].reset_index(drop=True)

    elapsed = time.perf_counter() - t0
    logger.info("Excel processing complete: %d rows in %.3fs", len(df), elapsed)
    return df


def load_from_csv(file_path: str = "data/sample_data.csv") -> pd.DataFrame:
    """Load data from a CSV file."""
    t0 = time.perf_counter()
    logger.info("Loading CSV data from %s", file_path)
    df = pd.read_csv(file_path)
    result = _validate_and_clean(df)
    logger.info("CSV load complete: %d rows in %.3fs", len(result), time.perf_counter() - t0)
    return result


def load_from_upload(uploaded_file) -> pd.DataFrame:
    """Load data from a Streamlit uploaded file."""
    t0 = time.perf_counter()
    name = uploaded_file.name.lower()
    logger.info("Loading uploaded file: %s", name)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(uploaded_file, sheet_name=0)
    else:
        df = pd.read_csv(uploaded_file)
    result = _validate_and_clean(df)
    logger.info("Upload load complete: %d rows in %.3fs", len(result), time.perf_counter() - t0)
    return result


def load_from_google_sheets(sheet_url: str) -> pd.DataFrame:
    """Load data from a public Google Sheet (published as CSV)."""
    logger.info("Loading data from Google Sheets")

    # Validate URL format
    if not sheet_url or not isinstance(sheet_url, str):
        st.error("Please provide a valid Google Sheets URL.")
        logger.error("Empty or invalid Google Sheets URL provided")
        return pd.DataFrame()

    if "docs.google.com/spreadsheets" not in sheet_url:
        st.error("Invalid URL. Please provide a Google Sheets URL (must contain docs.google.com/spreadsheets).")
        logger.error("URL does not match Google Sheets pattern")
        return pd.DataFrame()

    try:
        if "/edit" in sheet_url:
            csv_url = sheet_url.replace("/edit", "/export?format=csv")
        elif "/pub" in sheet_url:
            csv_url = sheet_url
        else:
            csv_url = sheet_url + "/export?format=csv"

        logger.info("Fetching CSV from transformed URL")
        df = pd.read_csv(csv_url)
        return _validate_and_clean(df)
    except Exception as e:
        st.error(f"Failed to load Google Sheet: {e}")
        logger.error("Failed to load Google Sheet", exc_info=True)
        return pd.DataFrame()


def _validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate columns and clean data for CSV/Google Sheets format."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    required = ["area", "lg_group", "leader_name", "members", "latitude", "longitude"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        logger.error("Missing required columns: %s", ", ".join(missing))
        return pd.DataFrame()

    df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0).astype(int)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    df["area"] = df["area"].str.strip()
    df["lg_group"] = df["lg_group"].str.strip()

    # Add families/individuals if missing
    if "families" not in df.columns:
        df["families"] = 0
    if "individuals" not in df.columns:
        df["individuals"] = 0
    if "meeting_day" not in df.columns:
        df["meeting_day"] = ""

    logger.info("Validation and cleaning complete: %d rows", len(df))
    return df


def validate_data_quality(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Check data quality and return (dataframe, list of warning messages)."""
    warnings = []

    if df.empty:
        return df, warnings

    # Check for duplicates by (leader_name, area)
    if "leader_name" in df.columns and "area" in df.columns:
        dupes = df.duplicated(subset=["leader_name", "area"], keep=False)
        if dupes.any():
            dupe_pairs = df[dupes][["leader_name", "area"]].drop_duplicates()
            dupe_list = [f"{r['leader_name']} ({r['area']})" for _, r in dupe_pairs.iterrows()]
            warnings.append(f"Duplicate entries found: {', '.join(dupe_list)}")
            logger.warning("Duplicate entries detected: %s", dupe_list)

    # Check for out-of-range member counts
    if "members" in df.columns:
        invalid_low = df[df["members"] <= 0]
        if not invalid_low.empty:
            warnings.append(f"{len(invalid_low)} groups have 0 or fewer members")
            logger.warning("%d groups have 0 or fewer members", len(invalid_low))

        invalid_high = df[df["members"] > 200]
        if not invalid_high.empty:
            warnings.append(f"{len(invalid_high)} groups have >200 members (possible data entry error)")
            logger.warning("%d groups have >200 members", len(invalid_high))

    # Check for missing leader names
    if "leader_name" in df.columns:
        missing_leaders = df[df["leader_name"].str.strip() == ""]
        if not missing_leaders.empty:
            warnings.append(f"{len(missing_leaders)} groups have no leader name")

    return df, warnings


def assign_strength(df: pd.DataFrame) -> pd.DataFrame:
    """Add strength category based on total member count."""
    def _categorize(members):
        if members >= 30:
            return "Strong"
        elif members >= 20:
            return "Medium"
        else:
            return "Weak"

    df = df.copy()
    df["strength"] = df["members"].apply(_categorize)

    strength_counts = df["strength"].value_counts().to_dict()
    logger.info("Strength distribution: %s", strength_counts)
    return df


def get_area_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data by area."""
    if df.empty:
        return pd.DataFrame(columns=["area", "total_groups", "total_members", "total_families",
                                     "total_individuals", "avg_members", "latitude", "longitude", "strength"])

    summary = df.groupby("area").agg(
        total_groups=("lg_group", "count"),
        total_members=("members", "sum"),
        total_families=("families", "sum"),
        total_individuals=("individuals", "sum"),
        avg_members=("members", "mean"),
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
    ).reset_index()

    summary["avg_members"] = summary["avg_members"].round(1)

    def _area_strength(avg):
        if avg >= 30:
            return "Strong"
        elif avg >= 20:
            return "Medium"
        else:
            return "Weak"

    summary["strength"] = summary["avg_members"].apply(_area_strength)
    return summary
