"""LG GeoView — Care Group Distribution Dashboard for Hyderabad West."""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from src.data_loader import load_from_excel, load_from_csv, load_from_upload, load_from_google_sheets, assign_strength, get_area_summary
from src.map_builder import build_map, build_detailed_map, MAP_STYLES
from src.charts import (members_by_area_chart, groups_by_area_chart, strength_pie_chart,
                        area_detail_table, meeting_day_chart, top_bottom_groups_chart, leader_members_chart)

# --- Page Config ---
st.set_page_config(
    page_title="LG GeoView",
    page_icon="\U0001f5fa\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* --- Light Mode Styles --- */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #00b894;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 5px;
    }
    .stApp > header { background-color: transparent; }

    /* Divider lines */
    hr {
        border-color: #dee2e6 !important;
    }

    /* --- Print Styles (A4) --- */
    @media print {
        @page {
            size: A4 landscape;
            margin: 10mm;
        }

        /* Hide sidebar, header, footer, toolbar */
        [data-testid="stSidebar"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        .stDeployButton,
        footer, header,
        [data-testid="stStatusWidget"],
        .stActionButton,
        button,
        [data-testid="baseButton-secondary"] {
            display: none !important;
        }

        /* Full width content */
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Prevent content clipping */
        html, body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stMain"], [data-testid="stMainBlockContainer"],
        [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
        .element-container, .stMarkdown, [data-testid="column"] {
            overflow: visible !important;
            max-height: none !important;
            height: auto !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Map iframe */
        iframe {
            width: 100% !important;
            max-width: 100% !important;
            height: 400px !important;
            page-break-inside: avoid;
        }

        /* Charts — prevent cutting */
        .js-plotly-plot, .plotly, .plot-container {
            width: 100% !important;
            max-width: 100% !important;
            page-break-inside: avoid;
        }

        /* Tables */
        [data-testid="stDataFrame"] {
            overflow: visible !important;
            page-break-inside: avoid;
        }

        /* Page breaks */
        .stSubheader, h2, h3 {
            page-break-after: avoid;
        }

        /* Preserve chart/marker colors */
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Data Loading ---
@st.cache_data(ttl=300)
def load_data(source: str, value: str = "") -> pd.DataFrame:
    """Load and cache data based on selected source."""
    if source == "Google Sheets" and value:
        df = load_from_google_sheets(value)
    elif source == "Excel":
        df = load_from_excel()
    else:
        df = load_from_csv()
    return assign_strength(df)


# --- Sidebar ---
with st.sidebar:
    st.title("LG GeoView")
    st.markdown("---")

    # Data source selection
    st.subheader("Data Source")
    data_source = st.radio(
        "Select source:",
        ["West Campus Data (Excel)", "Sample Data (CSV)", "Google Sheets", "Upload File"],
        index=0,
    )

    sheet_url = ""
    uploaded_file = None

    if data_source == "Google Sheets":
        sheet_url = st.text_input(
            "Google Sheet URL:",
            placeholder="Paste your published Google Sheet URL",
        )
    elif data_source == "Upload File":
        uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"])

    # Load data based on selection
    if data_source == "West Campus Data (Excel)":
        df = load_data("Excel")
    elif data_source == "Google Sheets" and sheet_url:
        df = load_data("Google Sheets", sheet_url)
    elif data_source == "Upload File" and uploaded_file is not None:
        df = load_from_upload(uploaded_file)
        df = assign_strength(df)
    else:
        df = load_data("CSV")

    # Refresh button
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Area filter
    if not df.empty:
        st.subheader("Filter by Area")
        areas = sorted(df["area"].unique())
        selected_areas = st.multiselect(
            "Select areas:",
            options=areas,
            default=areas,
        )
        df_filtered = df[df["area"].isin(selected_areas)].copy()
    else:
        df_filtered = df
        selected_areas = []

    st.markdown("---")

    # Map style selector
    st.subheader("Map Style")
    map_style_name = st.selectbox(
        "Choose map view:",
        options=list(MAP_STYLES.keys()),
        index=0,
    )

    st.markdown("---")
    st.caption("Built for LG Group Leadership")

# --- Main Content ---
if df_filtered.empty:
    st.warning("No data available. Please check your data source.")
    st.stop()

# Title
st.markdown("## LG GeoView — West Campus, Hyderabad")
st.markdown("Care group distribution, strength, and regional insights across Hyderabad West areas.")

# --- KPI Metrics ---
total_groups = len(df_filtered)
total_families = int(df_filtered["families"].sum())
total_individuals = int(df_filtered["individuals"].sum())
total_members = int(df_filtered["members"].sum())
num_areas = df_filtered["area"].nunique()
avg_per_group = total_members / total_groups if total_groups > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{num_areas}</div>
        <div class="metric-label">Areas</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_groups}</div>
        <div class="metric-label">Care Groups</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_families}</div>
        <div class="metric-label">Families</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_individuals}</div>
        <div class="metric-label">Individuals</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_members}</div>
        <div class="metric-label">Total Members</div>
    </div>""", unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_per_group:.1f}</div>
        <div class="metric-label">Avg per Group</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# --- Map ---
st.subheader("Interactive Map")
map_tab1, map_tab2 = st.tabs(["Overview Map", "Detailed Map"])

with map_tab1:
    st.caption("Hover or click markers for details")
    folium_map = build_map(df_filtered, map_style=map_style_name)
    st_folium(folium_map, use_container_width=True, height=920, key="overview_map")

with map_tab2:
    st.caption("All group details visible — no hover needed. Best for printing & screenshots.")
    sorted_areas = sorted(df_filtered["area"].unique())
    dm_col1, dm_col2 = st.columns([2, 2])
    with dm_col1:
        detail_area_picks = st.multiselect(
            "Filter areas for screenshot:",
            options=sorted_areas,
            default=sorted_areas,
            key="detail_map_areas",
        )
    with dm_col2:
        st.info("Deselect areas to reduce label overlap. Pick a few at a time for clean screenshots.")

    if detail_area_picks:
        detail_df = df_filtered[df_filtered["area"].isin(detail_area_picks)]
    else:
        detail_df = df_filtered

    detailed_map = build_detailed_map(detail_df, map_style=map_style_name)
    st_folium(detailed_map, use_container_width=True, height=920, key="detailed_map")

# --- Drill-Down Section (pushed to next scroll view) ---
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Area Drill-Down")

# Show "All Areas" by default, with option to filter
area_options = ["All Areas"] + sorted(df_filtered["area"].unique())
drill_col1, drill_col2 = st.columns([1, 2])

with drill_col1:
    selected_area = st.selectbox(
        "Select an area to explore:",
        options=area_options,
        index=0,
    )

if selected_area == "All Areas":
    drill_data = df_filtered
else:
    drill_data = df_filtered[df_filtered["area"] == selected_area]

area_groups = len(drill_data)
area_families = int(drill_data["families"].sum())
area_members = int(drill_data["members"].sum())
area_avg = drill_data["members"].mean()

with drill_col2:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Care Groups", area_groups)
    m2.metric("Families", area_families)
    m3.metric("Total Members", area_members)
    m4.metric("Avg Members", f"{area_avg:.1f}")

# Detail table — show all groups by default
all_detail = drill_data[[
    "area", "lg_group", "leader_name", "families", "individuals", "members", "meeting_day", "strength"
]].copy()
all_detail.columns = ["Area", "Care Group", "Leader", "Families", "Individuals", "Total", "Meeting Day", "Strength"]
all_detail = all_detail.sort_values(["Area", "Total"], ascending=[True, False]).reset_index(drop=True)
st.dataframe(
    all_detail,
    use_container_width=True,
    hide_index=True,
)

# --- Charts ---
st.markdown("---")
st.subheader("Analytics & Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.plotly_chart(members_by_area_chart(df_filtered), use_container_width=True)

with chart_col2:
    st.plotly_chart(groups_by_area_chart(df_filtered), use_container_width=True)

# Row 2: Meeting Day + Top/Bottom Groups
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.plotly_chart(meeting_day_chart(df_filtered), use_container_width=True)

with chart_col4:
    st.plotly_chart(top_bottom_groups_chart(df_filtered), use_container_width=True)

# Row 3: Members per Leader (full width)
st.plotly_chart(leader_members_chart(df_filtered), use_container_width=True)

# --- Area Summary Table ---
st.markdown("---")
st.subheader("Area Summary")
summary_df = get_area_summary(df_filtered)
st.dataframe(
    summary_df.rename(columns={
        "area": "Area",
        "total_groups": "Care Groups",
        "total_members": "Total Members",
        "total_families": "Families",
        "total_individuals": "Individuals",
        "avg_members": "Avg Members",
        "strength": "Strength",
    })[["Area", "Care Groups", "Families", "Individuals", "Total Members", "Avg Members", "Strength"]],
    use_container_width=True,
    hide_index=True,
)

# --- Footer ---
st.markdown("---")
st.caption("LG GeoView v1.0 | West Campus Care Group Distribution | Hyderabad")
