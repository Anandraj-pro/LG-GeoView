"""LG GeoView — Care Group Distribution Dashboard for Hyderabad West."""

import io
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from src.data_loader import (
    load_from_excel, load_from_csv, load_from_upload,
    load_from_google_sheets, assign_strength, get_area_summary,
    validate_data_quality,
)
from src.map_builder import (
    build_map, build_detailed_map, build_kingdom_map,
    build_advanced_territory_map,
    generate_territory_kml, MAP_STYLES,
)
from src.charts import (  # noqa: F401
    members_by_area_chart, groups_by_area_chart, strength_pie_chart,
    area_detail_table, meeting_day_chart, top_bottom_groups_chart,
    leader_members_chart,
)

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

    /* --- King's Kingdom View Styles --- */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

    .kingdom-header {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 28px 32px;
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.25);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(212, 175, 55, 0.1);
        text-align: center;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .kingdom-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at 50% 0%,
                    rgba(212, 175, 55, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .kingdom-title {
        font-family: 'Cinzel', 'Palatino Linotype', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #D4AF37;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
        margin: 0;
    }
    .kingdom-subtitle {
        font-family: 'Cormorant Garamond', 'Palatino Linotype', serif;
        font-size: 1rem;
        color: #BFA76A;
        letter-spacing: 2px;
        margin-top: 6px;
        font-style: italic;
    }
    .kingdom-divider {
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
        margin: 12px auto;
    }

    .kingdom-metric {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        padding: 18px 14px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .kingdom-metric::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    }
    .kingdom-metric-icon {
        font-size: 1.4rem;
        margin-bottom: 4px;
    }
    .kingdom-metric-value {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #D4AF37;
        text-shadow: 0 0 12px rgba(212, 175, 55, 0.2);
    }
    .kingdom-metric-label {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.85rem;
        color: #BFA76A;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    .kingdom-scripture {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.05rem;
        color: #BFA76A;
        text-align: center;
        font-style: italic;
        padding: 16px 40px;
        margin: 16px 0;
        border-left: 2px solid #D4AF3744;
        border-right: 2px solid #D4AF3744;
        background: linear-gradient(90deg,
                    rgba(212,175,55,0.03), transparent, rgba(212,175,55,0.03));
    }

    /* --- Responsive Styles (Tablet / Small Screens) --- */
    @media screen and (max-width: 768px) {
        .metric-card {
            padding: 12px 8px;
        }
        .metric-value {
            font-size: 1.5rem;
        }
        .metric-label {
            font-size: 0.75rem;
        }
        /* Let Streamlit stack columns naturally on narrow screens */
        [data-testid="column"] {
            min-width: 120px !important;
        }
        /* Reduce chart heights for smaller viewports */
        .js-plotly-plot, .plotly, .plot-container {
            max-height: 300px;
        }
        /* Map iframe */
        iframe {
            height: 500px !important;
        }
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

    # Data quality check
    if not df.empty:
        df, quality_warnings = validate_data_quality(df)
        row_count = len(df)
        warn_count = len(quality_warnings)
        if warn_count > 0:
            with st.expander(f"Data Quality: {row_count} rows, {warn_count} warnings"):
                for w in quality_warnings:
                    st.warning(w)
        else:
            st.caption(f"Data Quality: {row_count} rows loaded, no warnings")

    # Track last update time
    if "last_updated" not in st.session_state:
        st.session_state.last_updated = pd.Timestamp.now()

    # Refresh button
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.session_state.last_updated = pd.Timestamp.now()
        st.rerun()

    # Display last updated timestamp
    if "last_updated" in st.session_state:
        elapsed = pd.Timestamp.now() - st.session_state.last_updated
        minutes = int(elapsed.total_seconds() / 60)
        if minutes < 1:
            st.caption("Last updated: just now")
        elif minutes < 60:
            st.caption(f"Last updated: {minutes} min ago")
        else:
            st.caption(f"Last updated: {st.session_state.last_updated.strftime('%I:%M %p')}")

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
map_tab1, map_tab2, map_tab3, map_tab4 = st.tabs(
    ["Overview Map", "Detailed Map", "King's Kingdom", "Territory View"]
)

with map_tab1:
    st.caption("Hover or click markers for details")
    try:
        folium_map = build_map(df_filtered, map_style=map_style_name)
        st_folium(folium_map, use_container_width=True, height=920, key="overview_map")
    except Exception as e:
        st.error(f"Could not render overview map: {e}")

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

    try:
        detailed_map = build_detailed_map(detail_df, map_style=map_style_name)
        st_folium(detailed_map, use_container_width=True, height=920, key="detailed_map")
    except Exception as e:
        st.error(f"Could not render detailed map: {e}")

with map_tab3:
    # --- King's Kingdom View ---
    st.markdown("""
    <div class="kingdom-header">
        <div class="kingdom-title">&#9768; King's Kingdom</div>
        <div class="kingdom-divider"></div>
        <div class="kingdom-subtitle">West Campus &mdash; Hyderabad</div>
    </div>
    """, unsafe_allow_html=True)

    # Kingdom KPI metrics
    strong_count = len(df_filtered[df_filtered["strength"] == "Strong"])
    medium_count = len(df_filtered[df_filtered["strength"] == "Medium"])
    weak_count = len(df_filtered[df_filtered["strength"] == "Weak"])
    kingdom_summary = get_area_summary(df_filtered)

    kk1, kk2, kk3, kk4, kk5 = st.columns(5)
    with kk1:
        st.markdown(f"""
        <div class="kingdom-metric">
            <div class="kingdom-metric-icon">&#127968;</div>
            <div class="kingdom-metric-value">{num_areas}</div>
            <div class="kingdom-metric-label">Territories</div>
        </div>""", unsafe_allow_html=True)
    with kk2:
        st.markdown(f"""
        <div class="kingdom-metric">
            <div class="kingdom-metric-icon">&#9879;</div>
            <div class="kingdom-metric-value">{total_groups}</div>
            <div class="kingdom-metric-label">Shepherds</div>
        </div>""", unsafe_allow_html=True)
    with kk3:
        st.markdown(f"""
        <div class="kingdom-metric">
            <div class="kingdom-metric-icon">&#10025;</div>
            <div class="kingdom-metric-value">{total_members}</div>
            <div class="kingdom-metric-label">Souls Gathered</div>
        </div>""", unsafe_allow_html=True)
    with kk4:
        st.markdown(f"""
        <div class="kingdom-metric">
            <div class="kingdom-metric-icon">&#9733;</div>
            <div class="kingdom-metric-value">{strong_count}</div>
            <div class="kingdom-metric-label">Strong Groups</div>
        </div>""", unsafe_allow_html=True)
    with kk5:
        st.markdown(f"""
        <div class="kingdom-metric">
            <div class="kingdom-metric-icon">&#127793;</div>
            <div class="kingdom-metric-value">{weak_count}</div>
            <div class="kingdom-metric-label">Emerging</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Scripture quote
    st.markdown("""
    <div class="kingdom-scripture">
        "The harvest is plentiful, but the workers are few.
        Ask the Lord of the harvest to send out workers into his harvest field."
        <br><span style="color: #8B7340; font-size: 0.85rem;">&mdash; Matthew 9:37-38</span>
    </div>
    """, unsafe_allow_html=True)

    # Kingdom map
    try:
        kingdom_map = build_kingdom_map(
            df_filtered, kingdom_summary, map_style=map_style_name
        )
        st_folium(kingdom_map, use_container_width=True, height=920,
                  key="kingdom_map")
    except Exception as e:
        st.error(f"Could not render Kingdom map: {e}")

    # Territory strength breakdown
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
         padding: 20px; border-radius: 10px; border: 1px solid rgba(212,175,55,0.2);
         margin-top: 16px;">
        <div style="font-family: 'Cinzel', serif; color: #D4AF37; font-size: 14px;
             letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;
             text-align: center;">Territory Report</div>
    </div>
    """, unsafe_allow_html=True)

    territory_data = kingdom_summary.rename(columns={
        "area": "Territory",
        "total_groups": "Shepherds",
        "total_members": "Souls",
        "total_families": "Families",
        "avg_members": "Avg per Group",
        "strength": "Strength",
    })[["Territory", "Shepherds", "Families", "Souls",
        "Avg per Group", "Strength"]]
    territory_data = territory_data.sort_values("Souls", ascending=False)
    territory_data = territory_data.reset_index(drop=True)
    st.dataframe(territory_data, use_container_width=True, hide_index=True)

with map_tab4:
    # --- Advanced Territory Analysis ---
    st.markdown("#### Territory Analysis")
    st.caption("Toggle layers using the checkboxes on the map. "
               "Click any territory for detailed stats.")

    # Controls row
    tv_c1, tv_c2, tv_c3 = st.columns([1, 1, 1])
    with tv_c1:
        focus_area = st.selectbox(
            "Center on area:",
            options=sorted(df_filtered["area"].unique()),
            index=0,
            key="territory_focus_area",
        )
    with tv_c2:
        territory_radius = st.slider(
            "Nearby radius (km):",
            min_value=1, max_value=10, value=3,
            key="territory_radius",
        )
    with tv_c3:
        color_mode = st.selectbox(
            "Color territories by:",
            options=["Area (unique colors)", "Strength", "Member Density"],
            index=0,
            key="territory_color_mode",
        )

    color_by_map = {
        "Area (unique colors)": "area",
        "Strength": "strength",
        "Member Density": "density",
    }
    color_by = color_by_map[color_mode]

    territory_summary = get_area_summary(df_filtered)

    try:
        t_map = build_advanced_territory_map(
            df_filtered, territory_summary,
            center_area=focus_area,
            radius=territory_radius * 0.01,
            color_by=color_by,
        )
        st_folium(t_map, use_container_width=True, height=920,
                  key="territory_map")
    except Exception as e:
        st.error(f"Could not render territory map: {e}")

    # Export section
    st.markdown("---")
    exp_c1, exp_c2, exp_c3 = st.columns(3)
    with exp_c1:
        kml_data = generate_territory_kml(
            df_filtered, territory_summary
        )
        st.download_button(
            label="Export KML (Google Earth)",
            data=kml_data.encode("utf-8"),
            file_name="lg_geoview_territories.kml",
            mime="application/vnd.google-earth.kml+xml",
        )
    with exp_c2:
        csv_export = territory_summary.to_csv(index=False)
        st.download_button(
            label="Export Territory Data (CSV)",
            data=csv_export.encode("utf-8"),
            file_name=f"territory_data_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )
    with exp_c3:
        from src.data_loader import AREA_COORDINATES
        nearby_set = set()
        ck = focus_area.lower().strip()
        cc = AREA_COORDINATES.get(ck, [17.4948, 78.3996])
        for an, ac in AREA_COORDINATES.items():
            dist = ((ac[0] - cc[0])**2 + (ac[1] - cc[1])**2)**0.5
            if dist <= territory_radius * 0.01:
                nearby_set.add(an)
        occ = set(df_filtered["area"].str.lower().str.strip().unique())
        gaps = [n.title() for n in nearby_set if n not in occ]
        if gaps:
            st.info(f"**{len(gaps)} expansion zones:** {', '.join(sorted(gaps))}")
        else:
            st.success("All nearby territories occupied!")

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

# Download buttons for drill-down data
dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    csv_data = all_detail.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv_data,
        file_name=f"lg_geoview_filtered_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
with dl_col2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        all_detail.to_excel(writer, sheet_name="Filtered Data", index=False)
        get_area_summary(df_filtered).to_excel(writer, sheet_name="Area Summary", index=False)
    st.download_button(
        label="Download Report (Excel)",
        data=buffer.getvalue(),
        file_name=f"lg_geoview_report_{pd.Timestamp.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# --- Charts ---
st.markdown("---")
st.subheader("Analytics & Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    try:
        st.plotly_chart(members_by_area_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Members by area chart unavailable.")

with chart_col2:
    try:
        st.plotly_chart(groups_by_area_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Groups by area chart unavailable.")

# Row 2: Meeting Day + Top/Bottom Groups
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    try:
        st.plotly_chart(meeting_day_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Meeting day chart unavailable.")

with chart_col4:
    try:
        st.plotly_chart(top_bottom_groups_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Top/bottom groups chart unavailable.")

# Row 3: Strength Distribution + Members per Leader
chart_col5, chart_col6 = st.columns(2)

with chart_col5:
    try:
        st.plotly_chart(strength_pie_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Strength distribution chart unavailable.")

with chart_col6:
    try:
        st.plotly_chart(leader_members_chart(df_filtered), use_container_width=True)
    except Exception:
        st.warning("Leader members chart unavailable.")

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
st.caption("LG GeoView v1.1 | West Campus Care Group Distribution | Hyderabad")
