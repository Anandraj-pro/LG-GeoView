"""Data loading module — Excel, Google Sheets, CSV support."""

import pandas as pd
import streamlit as st

# Final clean columns for the dashboard
DASHBOARD_COLUMNS = ["area", "lg_group", "leader_name", "families", "individuals",
                     "members", "meeting_day", "latitude", "longitude"]

# Geocoded coordinates for Hyderabad West localities
AREA_COORDINATES = {
    "chintal 1": (17.4685, 78.3900),
    "chintal 2": (17.4710, 78.3925),
    "raju colony": (17.4635, 78.3820),          # Raju Colony, Balanagar
    "j. gutta": (17.4830, 78.3870),             # Jagathgirigutta
    "idpl": (17.4680, 78.3860),                 # IDPL Colony, near Chintal
    "gajularamaram": (17.4870, 78.3830),
    "jdm": (17.4980, 78.3810),                  # Jeedimetla
    "jeedimetla": (17.4980, 78.3810),
    "ferozguda": (17.4900, 78.3870),
    "borabanda": (17.4350, 78.4150),
    "moosapet": (17.4580, 78.4270),
    "maitreenagar": (17.4970, 78.3900),         # Mythri Nagar, Kukatpally
    "swan lake": (17.4940, 78.3920),            # Swan Lake Apartments, Kukatpally
    "kukatpally": (17.4948, 78.3996),
    "vadaypally": (17.4870, 78.3930),           # Vaddepally Enclave, Kukatpally
    "allwyn colony": (17.4920, 78.3920),
    "vvnagar": (17.4940, 78.3980),              # Vivekananda Nagar (VV Nagar), Kukatpally
    "jntu": (17.4960, 78.3950),
    "balajinagar": (17.4890, 78.3950),          # Balaji Nagar, Kukatpally
    "kphb": (17.4835, 78.3878),
    "kphb 2": (17.4850, 78.3900),
    "nizampet": (17.5100, 78.3830),
    "pragathinagar": (17.5150, 78.3750),
    "vasanthanagar": (17.4910, 78.3950),        # Vasanth Nagar, Kukatpally
    "bachupally": (17.5200, 78.3700),
    "mallampet": (17.5250, 78.3650),
    "hmt miyapur": (17.4965, 78.3537),
    "kondapur": (17.4600, 78.3700),             # Kondapur, corrected east
    "miyapur": (17.4965, 78.3540),
    "chandanagar": (17.4870, 78.3350),
    "nallagandla": (17.4748, 78.3103),            # Nallagandla, Tellapur side
    "beeramguda": (17.4920, 78.3200),
    "patancheruvu": (17.5300, 78.2700),
}


def load_from_excel(file_path: str = "data/West_Campus_Care_Groups_Area 2026.xlsx") -> pd.DataFrame:
    """Load and parse the West Campus Excel file with shifted column handling."""
    try:
        raw = pd.read_excel(file_path, sheet_name="Sheet1")
    except Exception as e:
        st.error(f"Failed to load Excel: {e}")
        return pd.DataFrame()

    rows = []
    for _, row in raw.iterrows():
        leader_name_col = row.get(",leader_name,")
        area_col = row.get("area")
        care_coord_col = row.get("Care Coordinator")

        # Determine leader and area based on which columns are populated
        if pd.notna(leader_name_col) and str(leader_name_col).strip():
            leader = str(leader_name_col).strip()
            area = str(area_col).strip() if pd.notna(area_col) else ""
        elif pd.notna(area_col) and str(area_col).strip():
            # Columns shifted: area has leader, Care Coordinator has area
            leader = str(area_col).strip()
            area = str(care_coord_col).strip() if pd.notna(care_coord_col) else ""
        else:
            continue

        # Skip total/summary rows
        if leader.lower() in ("total", "total "):
            continue

        families = pd.to_numeric(row.get("Families "), errors="coerce")
        individuals = pd.to_numeric(row.get("Individuals "), errors="coerce")
        total = pd.to_numeric(row.get("Total"), errors="coerce")
        meeting_day = row.get("Sync meeting on", "")
        if pd.isna(meeting_day):
            meeting_day = ""

        families = int(families) if pd.notna(families) else 0
        individuals = int(individuals) if pd.notna(individuals) else 0
        total = int(total) if pd.notna(total) else (families + individuals)

        # Create a meaningful LG group name: "Area - Leader"
        lg_group = f"{area} - {leader}"

        # Geocode
        area_lower = area.lower().strip()
        lat, lng = AREA_COORDINATES.get(area_lower, (None, None))

        rows.append({
            "area": area,
            "lg_group": lg_group,
            "leader_name": leader,
            "families": families,
            "individuals": individuals,
            "members": total,
            "meeting_day": str(meeting_day).strip().title(),
            "latitude": lat,
            "longitude": lng,
        })

    df = pd.DataFrame(rows)

    # Warn about missing coordinates
    missing_coords = df[df["latitude"].isna()]["area"].unique()
    if len(missing_coords) > 0:
        st.warning(f"Missing coordinates for: {', '.join(missing_coords)}")

    df = df.dropna(subset=["latitude", "longitude"])
    return df


def load_from_csv(file_path: str = "data/sample_data.csv") -> pd.DataFrame:
    """Load data from a CSV file."""
    df = pd.read_csv(file_path)
    return _validate_and_clean(df)


def load_from_upload(uploaded_file) -> pd.DataFrame:
    """Load data from a Streamlit uploaded file."""
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(uploaded_file, sheet_name=0)
    else:
        df = pd.read_csv(uploaded_file)
    return _validate_and_clean(df)


def load_from_google_sheets(sheet_url: str) -> pd.DataFrame:
    """Load data from a public Google Sheet (published as CSV)."""
    try:
        if "/edit" in sheet_url:
            csv_url = sheet_url.replace("/edit", "/export?format=csv")
        elif "/pub" in sheet_url:
            csv_url = sheet_url
        else:
            csv_url = sheet_url + "/export?format=csv"

        df = pd.read_csv(csv_url)
        return _validate_and_clean(df)
    except Exception as e:
        st.error(f"Failed to load Google Sheet: {e}")
        return pd.DataFrame()


def _validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate columns and clean data for CSV/Google Sheets format."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    required = ["area", "lg_group", "leader_name", "members", "latitude", "longitude"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        return pd.DataFrame()

    df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0).astype(int)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])
    df["area"] = df["area"].str.strip()
    df["lg_group"] = df["lg_group"].str.strip()

    # Add families/individuals if missing
    if "families" not in df.columns:
        df["families"] = 0
    if "individuals" not in df.columns:
        df["individuals"] = 0
    if "meeting_day" not in df.columns:
        df["meeting_day"] = ""

    return df


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
    return df


def get_area_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data by area."""
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
