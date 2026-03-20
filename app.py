"""TKT Kingdom -- West Campus Care Group Dashboard."""

import io
import os

import bcrypt
import streamlit as st
import pandas as pd
import yaml
from streamlit_folium import st_folium
from src.data_loader import (
    load_from_excel, load_from_csv, load_from_upload,
    load_from_google_sheets, assign_strength, get_area_summary,
    validate_data_quality, AREA_COORDINATES,
)
from src.map_builder import (
    build_kingdom_map, build_advanced_territory_map,
    generate_territory_kml, MAP_STYLES,
)
from src.charts import (  # noqa: F401
    members_by_area_chart, groups_by_area_chart, strength_pie_chart,
    area_detail_table, meeting_day_chart, top_bottom_groups_chart,
    leader_members_chart,
)
from src.analytics import (
    compute_kpi_metrics, compute_territory_coverage, generate_html_report,
    compute_coverage_scores,
)
from src.components import hero_banner_html, section_header_html, footer_html

# --- Page Config ---
st.set_page_config(
    page_title="TKT Kingdom - West Campus",
    page_icon="\u2720",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --- Authentication ---
def _check_auth():
    """Simple password auth using bcrypt hashed credentials."""
    auth_path = os.path.join(
        os.path.dirname(__file__), "config", "auth.yaml"
    )
    try:
        with open(auth_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return True  # No config = open access (dev mode)

    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <div style="font-family: 'Cinzel', serif; font-size: 2rem;
             color: #D4AF37; letter-spacing: 3px;
             margin-bottom: 8px;">TKT Kingdom</div>
        <div style="font-family: 'Cormorant Garamond', serif;
             font-size: 1rem; color: #888;
             font-style: italic;">
             West Campus - Hyderabad</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        username = st.text_input("Username", key="login_user")
        password = st.text_input(
            "Password", type="password", key="login_pass"
        )
        if st.button("Login", use_container_width=True):
            users = config.get("credentials", {}).get("usernames", {})
            if username in users:
                stored_hash = users[username]["password"]
                if bcrypt.checkpw(
                    password.encode(), stored_hash.encode()
                ):
                    st.session_state["authenticated"] = True
                    st.session_state["auth_user"] = username
                    st.session_state["auth_name"] = users[
                        username
                    ].get("name", username)
                    st.rerun()
            st.error("Invalid username or password")
    return False


if not _check_auth():
    st.stop()

# --- Viewport meta for mobile ---
st.markdown(
    '<meta name="viewport" content="width=device-width, '
    'initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
    unsafe_allow_html=True,
)

# --- Font Preloading (Task 2) ---
st.markdown(
    '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap"'
    ' as="style" onload="this.onload=null;this.rel=\'stylesheet\'">'
    '<link rel="preload" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond'
    ':ital,wght@0,400;0,600;1,400&display=swap"'
    ' as="style" onload="this.onload=null;this.rel=\'stylesheet\'">',
    unsafe_allow_html=True,
)

# --- Custom Styling (loaded from external CSS file) ---
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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
    st.markdown("""
    <div style="text-align: center; padding: 8px 0 4px 0;">
        <div style="font-family: 'Cinzel', serif; font-size: 1.3rem;
             font-weight: 700; color: var(--text-heading); letter-spacing: 2px;">
            &#x2666; TKT Kingdom</div>
        <div style="font-family: 'Cormorant Garamond', serif;
             font-size: 0.85rem; color: var(--text-muted); font-style: italic;">
            West Campus &#183; Hyderabad</div>
    </div>
    """, unsafe_allow_html=True)

    # User info + logout
    if st.session_state.get("authenticated"):
        user_name = st.session_state.get("auth_name", "User")
        st.caption(f"Logged in as: {user_name}")
        if st.button("Logout", key="logout_btn"):
            st.session_state["authenticated"] = False
            st.session_state.pop("auth_user", None)
            st.session_state.pop("auth_name", None)
            st.rerun()

    st.markdown("---")

    # Theme toggle
    light_mode = st.toggle("Light Mode", value=False, key="theme_toggle")

    # Dynamic light mode CSS override stays in app.py (conditional)
    if light_mode:
        st.markdown(
            '<style>'
            ':root {'
            '--bg:#FFFBF0!important;'
            '--bg-secondary:#F5EDD8!important;'
            '--bg-card:rgba(255,251,240,0.9)!important;'
            '--text:#5D4E37!important;'
            '--text-muted:#7A6B50!important;'
            '--text-heading:#8B6914!important;'
            '--accent:#D4AF37!important;'
            '--accent-dim:rgba(212,175,55,0.15)!important;'
            '--border:rgba(212,175,55,0.25)!important;'
            '--sidebar-bg:linear-gradient(180deg,#FAF5E8,#F5EDD8)!important;'
            '--scripture-bg:rgba(212,175,55,0.05)!important;'
            '--section-bg:rgba(245,237,216,0.6)!important;'
            '}'
            '.hero-banner{background:#F5EDD8!important}'
            '.hero-banner::after{background:linear-gradient(to top,'
            '#F5EDD8 0%,transparent 30%,'
            'transparent 70%,rgba(245,237,216,0.8) 100%)!important}'
            '.hero-title-line1{background:linear-gradient(to bottom,'
            '#5D4E37,#8B6914)!important;'
            '-webkit-background-clip:text!important;'
            '-webkit-text-fill-color:transparent!important}'
            '.hero-scripture{color:#7A6B50!important}'
            '.hero-badge-text{color:#7A6B50!important}'
            '.hero-badge-dot{background:#8B6914!important}'
            '.hero-kpi::after{background:rgba(255,251,240,0.92)!important}'
            '.hero-kpi-label{color:#7A6B50!important}'
            '.hero-shape{opacity:0.4!important}'
            '</style>',
            unsafe_allow_html=True,
        )

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

    with st.expander("Map & Territory Controls", expanded=False):
        map_style_name = st.selectbox(
            "Map style:",
            options=list(MAP_STYLES.keys()),
            index=0,
        )

        st.markdown("---")

        area_options = sorted(df["area"].unique()) if not df.empty else []
        default_idx = 0
        for i, a in enumerate(area_options):
            if a.lower().strip() == "kukatpally":
                default_idx = i
                break
        focus_area = st.selectbox(
            "Center on area:",
            options=area_options,
            index=default_idx,
            key="territory_focus_area",
        )
        territory_radius = st.slider(
            "Nearby radius (km):",
            min_value=1, max_value=20, value=15,
            key="territory_radius",
        )
        color_mode = st.selectbox(
            "Color by:",
            options=["Area (unique colors)", "Strength", "Member Density"],
            index=0,
            key="territory_color_mode",
        )

    st.markdown("---")
    st.markdown("""
    <div style="font-family: 'Cormorant Garamond', serif;
         font-size: 0.85rem; color: var(--text-muted); font-style: italic;
         text-align: center; padding: 8px 12px; line-height: 1.5;">
        "Go and make disciples of all nations"
        <br><span style="font-size: 0.75rem; color: var(--text-muted);">
        - Matthew 28:19</span>
    </div>
    """, unsafe_allow_html=True)

# --- Main Content ---
if df_filtered.empty:
    st.warning("No data available. Please check your data source.")
    st.stop()

# --- Kingdom Banner (KPIs via analytics module) ---
kpi = compute_kpi_metrics(df_filtered)
st.markdown(hero_banner_html(kpi), unsafe_allow_html=True)

# Determine chart dark mode based on light_mode toggle
chart_dark = not light_mode

# --- Map ---
map_tab1, map_tab2 = st.tabs(
    ["Territory Analysis", "TKT Kingdom"]
)

with map_tab1:
    # --- Layer settings above map ---
    with st.expander("Layer Settings", expanded=False):
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            show_boundaries = st.checkbox(
                "Ward Boundaries", value=True, key="lyr_boundaries")
            show_markers = st.checkbox(
                "Group Markers", value=True, key="lyr_markers")
        with lc2:
            show_gaps = st.checkbox(
                "Gap Analysis", value=False, key="lyr_gaps")
            show_strength = st.checkbox(
                "Strength Indicators", value=False, key="lyr_strength")
        with lc3:
            show_density = st.checkbox(
                "Member Density", value=False, key="lyr_density")
            show_coverage = st.checkbox(
                "Coverage Scoring", value=False, key="lyr_coverage")

    color_by_map = {
        "Area (unique colors)": "area",
        "Strength": "strength",
        "Member Density": "density",
    }
    color_by = color_by_map[color_mode]

    territory_summary = get_area_summary(df_filtered)

    # Territory coverage KPIs (via analytics module)
    occ_set = set(df_filtered["area"].str.lower().str.strip().unique())
    coverage = compute_territory_coverage(
        focus_area, territory_radius, AREA_COORDINATES, occ_set,
    )
    occupied_count = coverage["occupied_count"]
    total_nearby = coverage["total_nearby"]
    uncovered = coverage["uncovered"]

    tk1, tk2, tk3 = st.columns(3)
    tk1.metric("Occupied", f"{occupied_count}/{total_nearby}")
    tk2.metric("Uncovered", len(uncovered))
    if uncovered:
        tk3.caption(f"{', '.join(sorted(uncovered))}")
    else:
        tk3.success("All covered")

    # Compute coverage scores for coverage layer
    coverage_scores_dict: dict[str, dict] | None = None
    scored_summary = None
    if show_coverage and not territory_summary.empty:
        scored_summary = compute_coverage_scores(territory_summary)
        coverage_scores_dict = {}
        for _, crow in scored_summary.iterrows():
            area_key = crow["area"].lower().strip()
            coverage_scores_dict[area_key] = {
                "score": float(crow["coverage_score"]),
                "level": str(crow["coverage_level"]),
                "color": str(crow["coverage_color"]),
            }

    layer_config = {
        "boundaries": show_boundaries,
        "markers": show_markers,
        "gaps": show_gaps,
        "strength": show_strength,
        "density": show_density,
        "coverage": show_coverage,
    }

    try:
        t_map = build_advanced_territory_map(
            df_filtered, territory_summary,
            center_area=focus_area,
            radius=territory_radius,
            color_by=color_by,
            layers=layer_config,
            coverage_scores=coverage_scores_dict,
        )
        st_folium(t_map, use_container_width=True, height=550,
                  key="territory_map")
    except Exception as e:
        st.error(f"Could not render territory map: {e}")

    # --- Coverage Summary Panel (Task 4) ---
    if show_coverage and scored_summary is not None and not scored_summary.empty:
        st.markdown("---")
        st.markdown("**Coverage Scoring Summary**")

        green_areas = scored_summary[scored_summary["coverage_level"] == "Well Served"]
        yellow_areas = scored_summary[scored_summary["coverage_level"] == "Partial"]
        red_areas = scored_summary[scored_summary["coverage_level"] == "Underserved"]

        green_count = len(green_areas)
        yellow_count = len(yellow_areas)
        red_count = len(red_areas)

        cv1, cv2, cv3 = st.columns(3)
        with cv1:
            st.markdown(
                f'<div style="background:#E8F5E9;border-left:4px solid #2E7D32;'
                f'padding:12px 16px;border-radius:4px;">'
                f'<div style="font-size:24px;font-weight:bold;color:#2E7D32;">'
                f'{green_count}</div>'
                f'<div style="font-size:12px;color:#2E7D32;">Well Served</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cv2:
            st.markdown(
                f'<div style="background:#FFF8E1;border-left:4px solid #F9A825;'
                f'padding:12px 16px;border-radius:4px;">'
                f'<div style="font-size:24px;font-weight:bold;color:#F57F17;">'
                f'{yellow_count}</div>'
                f'<div style="font-size:12px;color:#F57F17;">Partial Coverage</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with cv3:
            st.markdown(
                f'<div style="background:#FFEBEE;border-left:4px solid #C62828;'
                f'padding:12px 16px;border-radius:4px;">'
                f'<div style="font-size:24px;font-weight:bold;color:#C62828;">'
                f'{red_count}</div>'
                f'<div style="font-size:12px;color:#C62828;">Underserved</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # List underserved areas as expansion priorities
        if red_count > 0:
            red_names = sorted(red_areas["area"].tolist())
            st.markdown(
                f'<div style="margin-top:12px;padding:10px 14px;'
                f'background:#FFEBEE;border-radius:6px;'
                f'border:1px solid #FFCDD2;">'
                f'<div style="font-weight:bold;color:#C62828;'
                f'margin-bottom:4px;">Expansion Priorities (Underserved)</div>'
                f'<div style="color:#B71C1C;font-size:13px;">'
                f'{", ".join(red_names)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Export section
    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        kml_data = generate_territory_kml(
            df_filtered, territory_summary
        )
        st.download_button(
            label="Export KML",
            data=kml_data.encode("utf-8"),
            file_name="lg_geoview_territories.kml",
            mime="application/vnd.google-earth.kml+xml",
        )
    with exp_c2:
        csv_export = territory_summary.to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv_export.encode("utf-8"),
            file_name=f"territory_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )

with map_tab2:
    # --- TKT Kingdom Map ---
    kingdom_summary = get_area_summary(df_filtered)

    try:
        kingdom_map = build_kingdom_map(
            df_filtered, kingdom_summary, map_style=map_style_name
        )
        st_folium(kingdom_map, use_container_width=True, height=550,
                  key="kingdom_map")
    except Exception as e:
        st.error(f"Could not render Kingdom map: {e}")

    st.markdown(
        section_header_html(
            "", "Territory Report",
            verse="The Lord your God will bless you in all your harvest",
            reference="Deuteronomy 16:15",
        ),
        unsafe_allow_html=True,
    )

    territory_data = kingdom_summary.rename(columns={
        "area": "Territory",
        "total_groups": "Shepherds",
        "total_members": "Souls",
        "total_families": "Families",
        "avg_members": "Avg per Group",
        "strength": "Strength",
    })[["Territory", "Shepherds", "Families", "Souls",
        "Avg per Group", "Strength"]]
    territory_data = territory_data.sort_values(
        "Souls", ascending=False
    ).reset_index(drop=True)
    st.dataframe(territory_data, use_container_width=True,
                 hide_index=True)

# --- Area Comparison (Task 4) ---
st.markdown("---")
st.markdown(
    section_header_html("&#x2666;", "Area Comparison"),
    unsafe_allow_html=True,
)

comp_c1, comp_c2 = st.columns(2)
area_list = sorted(df_filtered["area"].unique())
with comp_c1:
    area_a = st.selectbox("Area A:", area_list, index=0, key="comp_a")
with comp_c2:
    area_b = st.selectbox(
        "Area B:", area_list,
        index=min(1, len(area_list) - 1), key="comp_b",
    )

if area_a and area_b:
    data_a = df_filtered[df_filtered["area"] == area_a]
    data_b = df_filtered[df_filtered["area"] == area_b]

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"**{area_a}**")
        st.metric("Groups", len(data_a))
        st.metric("Total Members", int(data_a["members"].sum()))
        st.metric("Families", int(data_a["families"].sum()))
        st.metric("Avg per Group", f"{data_a['members'].mean():.1f}")
    with mc2:
        st.markdown(f"**{area_b}**")
        st.metric("Groups", len(data_b))
        st.metric("Total Members", int(data_b["members"].sum()))
        st.metric("Families", int(data_b["families"].sum()))
        st.metric("Avg per Group", f"{data_b['members'].mean():.1f}")

# --- Drill-Down Section ---
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    section_header_html(
        "&#x2666;", "Territory Drill-Down",
        verse="Where two or three gather in my name, there am I with them",
        reference="Matthew 18:20",
    ),
    unsafe_allow_html=True,
)

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

# Detail table -- show all groups by default
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
st.markdown(
    section_header_html(
        "&#x2666;", "Kingdom Insights",
        verse="For where your treasure is, there your heart will be also",
        reference="Matthew 6:21",
    ),
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    try:
        st.plotly_chart(members_by_area_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Members by area chart unavailable.")

with chart_col2:
    try:
        st.plotly_chart(groups_by_area_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Groups by area chart unavailable.")

# Row 2: Meeting Day + Top/Bottom Groups
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    try:
        st.plotly_chart(meeting_day_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Meeting day chart unavailable.")

with chart_col4:
    try:
        st.plotly_chart(top_bottom_groups_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Top/bottom groups chart unavailable.")

# Row 3: Strength Distribution + Members per Leader
chart_col5, chart_col6 = st.columns(2)

with chart_col5:
    try:
        st.plotly_chart(strength_pie_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Strength distribution chart unavailable.")

with chart_col6:
    try:
        st.plotly_chart(leader_members_chart(df_filtered, dark=chart_dark), use_container_width=True)
    except Exception:
        st.warning("Leader members chart unavailable.")

# --- Area Summary Table ---
st.markdown("---")
st.markdown(
    section_header_html(
        "&#x2666;", "Territory Summary",
        verse="The earth is the Lord's, and everything in it",
        reference="Psalm 24:1",
    ),
    unsafe_allow_html=True,
)
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

# --- Print Report (Task 6) ---
report_html = generate_html_report(df_filtered, summary_df, kpi)
st.download_button(
    label="Download Printable Report (HTML)",
    data=report_html.encode("utf-8"),
    file_name=f"tkt_kingdom_report_{pd.Timestamp.now().strftime('%Y-%m-%d')}.html",
    mime="text/html",
    key="print_report_btn",
)

# --- Footer ---
st.markdown("---")
st.markdown(footer_html(), unsafe_allow_html=True)
