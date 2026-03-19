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
    build_kingdom_map, build_advanced_territory_map,
    generate_territory_kml, MAP_STYLES,
)
from src.charts import (  # noqa: F401
    members_by_area_chart, groups_by_area_chart, strength_pie_chart,
    area_detail_table, meeting_day_chart, top_bottom_groups_chart,
    leader_members_chart,
)

# --- Page Config ---
st.set_page_config(
    page_title="TKT Kingdom - West Campus",
    page_icon="\u2720",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* --- Kingdom Theme — Warm Parchment + Gold --- */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

    .stApp {
        background: #FFFBF0 !important;
    }
    .stApp > header { background-color: transparent; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FAF5E8 0%, #F5EDD8 100%) !important;
        border-right: 2px solid #D4AF3733 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Cinzel', serif !important;
        color: #5D4E37 !important;
    }

    /* Main headings */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #5D4E37 !important;
        letter-spacing: 1px;
    }
    p, span, label, .stMarkdown {
        font-family: 'Cormorant Garamond', 'Palatino Linotype', serif !important;
    }

    /* KPI Metric Cards — parchment + gold */
    .metric-card {
        background: linear-gradient(135deg, #FFFBF0 0%, #F5EDD8 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #D4AF3744;
        box-shadow: 0 2px 8px rgba(139,105,20,0.08);
    }
    .metric-value {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #8B6914;
    }
    .metric-label {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.9rem;
        color: #7A6B50;
        margin-top: 5px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Divider lines */
    hr {
        border-color: #D4AF3733 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #D4AF3722 !important;
        border-radius: 8px;
    }

    /* Buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%) !important;
        color: white !important;
        border: none !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
    }

    /* --- Hero Banner with Animated Shapes --- */
    @keyframes float1 {
        0%, 100% { transform: translateY(0) rotate(12deg); }
        50% { transform: translateY(-18px) rotate(14deg); }
    }
    @keyframes float2 {
        0%, 100% { transform: translateY(0) rotate(-15deg); }
        50% { transform: translateY(15px) rotate(-13deg); }
    }
    @keyframes float3 {
        0%, 100% { transform: translateY(0) rotate(-8deg); }
        50% { transform: translateY(-12px) rotate(-6deg); }
    }
    @keyframes float4 {
        0%, 100% { transform: translateY(0) rotate(20deg); }
        50% { transform: translateY(10px) rotate(22deg); }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-banner {
        position: relative;
        background: #0a0a0a;
        border-radius: 16px;
        padding: 48px 32px 36px;
        margin-bottom: 24px;
        overflow: hidden;
        min-height: 340px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at 30% 20%,
                    rgba(139,92,246,0.06) 0%, transparent 50%),
                    radial-gradient(ellipse at 70% 80%,
                    rgba(212,175,55,0.06) 0%, transparent 50%);
        pointer-events: none;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(to top,
                    #0a0a0a 0%, transparent 30%, transparent 70%, rgba(10,10,10,0.8) 100%);
        pointer-events: none;
        z-index: 1;
    }

    /* Floating elegant shapes */
    .hero-shape {
        position: absolute;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(2px);
        box-shadow: 0 8px 32px rgba(255,255,255,0.05);
        pointer-events: none;
    }
    .hero-shape::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background: radial-gradient(circle at 50% 50%,
                    rgba(255,255,255,0.12), transparent 70%);
    }
    .hero-shape-1 {
        width: 500px; height: 120px;
        left: -8%; top: 18%;
        background: linear-gradient(to right, rgba(212,175,55,0.12), transparent);
        animation: float1 12s ease-in-out infinite;
    }
    .hero-shape-2 {
        width: 400px; height: 100px;
        right: -3%; top: 72%;
        background: linear-gradient(to right, rgba(139,92,246,0.10), transparent);
        animation: float2 14s ease-in-out infinite;
    }
    .hero-shape-3 {
        width: 250px; height: 70px;
        left: 8%; bottom: 8%;
        background: linear-gradient(to right, rgba(212,175,55,0.08), transparent);
        animation: float3 10s ease-in-out infinite;
    }
    .hero-shape-4 {
        width: 180px; height: 50px;
        right: 18%; top: 10%;
        background: linear-gradient(to right, rgba(244,114,182,0.08), transparent);
        animation: float4 11s ease-in-out infinite;
    }

    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 700px;
        margin: 0 auto;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 14px;
        border-radius: 50px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 20px;
        animation: fadeUp 1s ease-out 0.3s both;
    }
    .hero-badge-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #D4AF37;
    }
    .hero-badge-text {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
        letter-spacing: 2px;
    }

    @keyframes shimmer {
        0% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .hero-title-line1 {
        font-family: 'Cinzel', serif;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 5px;
        text-transform: uppercase;
        background: linear-gradient(to bottom, #ffffff, rgba(255,255,255,0.8));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
        animation: fadeUp 1s ease-out 0.5s both;
    }
    .hero-title-line2 {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 3px;
        background: linear-gradient(90deg,
            #D4AF37 0%, #D4AF37 40%,
            #FFFFFF 50%,
            #D4AF37 60%, #D4AF37 100%);
        background-size: 250% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 4px 0 0;
        line-height: 1.3;
        animation: fadeUp 1s ease-out 0.7s both, shimmer 3s linear infinite;
    }

    .hero-scripture {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 0.95rem;
        color: rgba(255,255,255,0.3);
        font-style: italic;
        margin-top: 18px;
        line-height: 1.6;
        max-width: 480px;
        margin-left: auto;
        margin-right: auto;
        animation: fadeUp 1s ease-out 0.9s both;
    }

    /* Hero KPI row inside banner */
    .hero-kpis {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 28px;
        flex-wrap: wrap;
        animation: fadeUp 1s ease-out 1.1s both;
    }
    .hero-kpi {
        text-align: center;
        padding: 12px 20px;
        min-width: 110px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(4px);
    }
    .hero-kpi-icon {
        font-size: 1.1rem;
        margin-bottom: 2px;
    }
    .hero-kpi-value {
        font-family: 'Cinzel', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #D4AF37;
    }
    .hero-kpi-label {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    /* Kingdom section headers */
    .kingdom-scripture {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.05rem;
        color: #7A6B50;
        text-align: center;
        font-style: italic;
        padding: 16px 40px;
        margin: 16px 0;
        border-left: 2px solid #D4AF3744;
        border-right: 2px solid #D4AF3744;
        background: linear-gradient(90deg,
                    rgba(212,175,55,0.05), transparent, rgba(212,175,55,0.05));
    }

    /* --- Responsive Styles (Tablet / Small Screens) --- */
    @media screen and (max-width: 768px) {
        .hero-banner { padding: 32px 16px 24px; min-height: 280px; }
        .hero-title-line1 { font-size: 1.8rem; letter-spacing: 3px; }
        .hero-title-line2 { font-size: 1.3rem; letter-spacing: 2px; }
        .hero-scripture { font-size: 0.8rem; padding: 0 8px; }
        .hero-kpis { gap: 8px; }
        .hero-kpi { padding: 8px 12px; min-width: 80px; }
        .hero-kpi-value { font-size: 1.2rem; }
        .hero-kpi-label { font-size: 0.65rem; }
        .hero-shape-1, .hero-shape-2 { display: none; }
        [data-testid="column"] {
            min-width: 120px !important;
        }
        .js-plotly-plot, .plotly, .plot-container {
            max-height: 300px;
        }
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
    st.markdown("""
    <div style="text-align: center; padding: 8px 0 4px 0;">
        <div style="font-family: 'Cinzel', serif; font-size: 1.3rem;
             font-weight: 700; color: #8B6914; letter-spacing: 2px;">
            &#x2726; TKT Kingdom</div>
        <div style="font-family: 'Cormorant Garamond', serif;
             font-size: 0.85rem; color: #A0936E; font-style: italic;">
            West Campus &middot; Hyderabad</div>
    </div>
    """, unsafe_allow_html=True)
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
    st.markdown("""
    <div style="font-family: 'Cormorant Garamond', serif;
         font-size: 0.85rem; color: #A0936E; font-style: italic;
         text-align: center; padding: 8px 12px; line-height: 1.5;">
        "Go and make disciples of all nations"
        <br><span style="font-size: 0.75rem; color: #BFA76A;">
        &mdash; Matthew 28:19</span>
    </div>
    """, unsafe_allow_html=True)

# --- Main Content ---
if df_filtered.empty:
    st.warning("No data available. Please check your data source.")
    st.stop()

# --- Kingdom Banner ---
total_groups = len(df_filtered)
total_families = int(df_filtered["families"].sum())
total_individuals = int(df_filtered["individuals"].sum())
total_members = int(df_filtered["members"].sum())
num_areas = df_filtered["area"].nunique()
avg_per_group = total_members / total_groups if total_groups > 0 else 0
strong_count = len(df_filtered[df_filtered["strength"] == "Strong"])
weak_count = len(df_filtered[df_filtered["strength"] == "Weak"])

hero_html = f"""<div class="hero-banner">\
<div class="hero-shape hero-shape-1"></div>\
<div class="hero-shape hero-shape-2"></div>\
<div class="hero-shape hero-shape-3"></div>\
<div class="hero-shape hero-shape-4"></div>\
<div class="hero-content">\
<div class="hero-badge">\
<div class="hero-badge-dot"></div>\
<span class="hero-badge-text">West Campus &middot; Hyderabad</span>\
</div>\
<div class="hero-title-line1">TKT Kingdom</div>\
<div class="hero-title-line2">Expanding His Territory</div>\
<div class="hero-scripture">\
&ldquo;The harvest is plentiful, but the workers are few.\
 Ask the Lord of the harvest to send out workers\
 into his harvest field.&rdquo;\
<br>&mdash; Matthew 9:37-38\
</div>\
</div>\
<div class="hero-kpis">\
<div class="hero-kpi">\
<div class="hero-kpi-icon">&#x25C8;</div>\
<div class="hero-kpi-value">{num_areas}</div>\
<div class="hero-kpi-label">Territories</div>\
</div>\
<div class="hero-kpi">\
<div class="hero-kpi-icon">&#x2740;</div>\
<div class="hero-kpi-value">{total_groups}</div>\
<div class="hero-kpi-label">Shepherds</div>\
</div>\
<div class="hero-kpi">\
<div class="hero-kpi-icon">&#x2739;</div>\
<div class="hero-kpi-value">{total_members}</div>\
<div class="hero-kpi-label">Souls Gathered</div>\
</div>\
<div class="hero-kpi">\
<div class="hero-kpi-icon">&#x2605;</div>\
<div class="hero-kpi-value">{strong_count}</div>\
<div class="hero-kpi-label">Strong Groups</div>\
</div>\
<div class="hero-kpi">\
<div class="hero-kpi-icon">&#x2698;</div>\
<div class="hero-kpi-value">{weak_count}</div>\
<div class="hero-kpi-label">Emerging</div>\
</div>\
</div>\
</div>"""
st.markdown(hero_html, unsafe_allow_html=True)

# --- Map ---
st.markdown("""
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
     color: #8B6914; letter-spacing: 2px; margin-bottom: 8px;">
    &#x2726; Kingdom Map</div>
""", unsafe_allow_html=True)
map_tab1, map_tab2 = st.tabs(
    ["TKT Kingdom", "Territory Analysis"]
)

with map_tab1:
    # --- TKT Kingdom Map ---
    kingdom_summary = get_area_summary(df_filtered)

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
    <div style="background: linear-gradient(145deg, #FAF5E8 0%, #F0E6CC 100%);
         padding: 16px 20px; border-radius: 10px; border: 1px solid #D4AF3733;
         margin-top: 16px;">
        <div style="font-family: 'Cinzel', serif; color: #8B6914; font-size: 14px;
             letter-spacing: 2px; text-transform: uppercase;
             text-align: center;">Territory Report</div>
        <div style="font-family: 'Cormorant Garamond', serif;
             font-size: 0.85rem; color: #A0936E; font-style: italic;
             text-align: center; margin-top: 4px;">
            "The Lord your God will bless you in all your harvest"
            &mdash; Deuteronomy 16:15</div>
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

with map_tab2:
    # --- Advanced Territory Analysis ---
    st.markdown("""
    <div style="font-family: 'Cinzel', serif; font-size: 1rem;
         color: #8B6914; letter-spacing: 2px; margin-bottom: 4px;">
        &#x2726; Territory Analysis</div>
    <div style="font-family: 'Cormorant Garamond', serif;
         font-size: 0.85rem; color: #A0936E; font-style: italic;
         margin-bottom: 12px;">
        "Ask of me, and I will make the nations your inheritance,
        the ends of the earth your possession"
        &mdash; Psalm 2:8</div>
    """, unsafe_allow_html=True)
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

# --- Drill-Down Section ---
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
     color: #8B6914; letter-spacing: 2px; margin-bottom: 4px;">
    &#x2726; Territory Drill-Down</div>
<div style="font-family: 'Cormorant Garamond', serif;
     font-size: 0.85rem; color: #A0936E; font-style: italic;
     margin-bottom: 12px;">
    "Where two or three gather in my name, there am I with them"
    &mdash; Matthew 18:20</div>
""", unsafe_allow_html=True)

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
st.markdown("""
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
     color: #8B6914; letter-spacing: 2px; margin-bottom: 4px;">
    &#x2726; Kingdom Insights</div>
<div style="font-family: 'Cormorant Garamond', serif;
     font-size: 0.85rem; color: #A0936E; font-style: italic;
     margin-bottom: 12px;">
    "For where your treasure is, there your heart will be also"
    &mdash; Matthew 6:21</div>
""", unsafe_allow_html=True)

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
st.markdown("""
<div style="font-family: 'Cinzel', serif; font-size: 1.1rem;
     color: #8B6914; letter-spacing: 2px; margin-bottom: 4px;">
    &#x2726; Territory Summary</div>
<div style="font-family: 'Cormorant Garamond', serif;
     font-size: 0.85rem; color: #A0936E; font-style: italic;
     margin-bottom: 12px;">
    "The earth is the Lord's, and everything in it"
    &mdash; Psalm 24:1</div>
""", unsafe_allow_html=True)
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
st.markdown("""
<div style="text-align: center; padding: 16px 0 8px 0;">
    <div style="font-family: 'Cormorant Garamond', serif;
         font-size: 0.9rem; color: #A0936E; font-style: italic;
         max-width: 500px; margin: 0 auto; line-height: 1.5;">
        "The harvest is plentiful, but the workers are few.
        Ask the Lord of the harvest to send out workers
        into his harvest field."
        <br><span style="font-size: 0.8rem; color: #BFA76A;">
        &mdash; Matthew 9:37-38</span>
    </div>
    <div style="width: 60px; height: 1px;
         background: linear-gradient(90deg, transparent, #D4AF37, transparent);
         margin: 12px auto;"></div>
    <div style="font-family: 'Cinzel', serif;
         color: #A0936E; font-size: 0.75rem; letter-spacing: 2px;">
        TKT Kingdom v1.1 &nbsp;&middot;&nbsp; West Campus &nbsp;&middot;&nbsp; Hyderabad
    </div>
</div>
""", unsafe_allow_html=True)
