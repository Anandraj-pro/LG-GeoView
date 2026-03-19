# Product Requirements Document (PRD)
# LG GeoView — Hyderabad LG Growth & Discipleship Map

**Author:** Anand Pandiri
**Date:** 19 March 2026
**Version:** 2.0
**Status:** v1.0 Released | v1.1 In Development | v2.0 Planning

---

## 1. Product Overview

LG GeoView is a geo-intelligence dashboard that visualizes Life Group (LG) distribution, growth, and discipleship progress across Hyderabad-West areas. Built with Streamlit, Folium, and Plotly, it enables leadership to assess regional strength, identify weak zones, track member journeys, and make data-driven operational decisions.

**v1.0** delivered a fully functional interactive map dashboard with care group visualization, KPI metrics, multi-source data loading, and analytical charts. The expanded vision (v2.0+) transforms LG GeoView from a distribution dashboard into a comprehensive geo-intelligence platform with heatmaps, expansion intelligence, discipleship tracking, prayer coverage mapping, and community impact analysis.

---

## 2. Product Vision

> Turn raw location data into an interactive, insight-rich map that helps leaders see where groups thrive, where gaps exist, and where to plant next.

LG GeoView aims to become the central strategic tool for LG leadership by layering multiple intelligence dimensions onto a single geographic view:

- **Distribution Intelligence** (v1.0 -- Delivered) -- Where are groups located and how strong are they?
- **Density Intelligence** (v2.0 -- Planned) -- Where are members concentrated?
- **Growth Intelligence** (v2.0 -- Planned) -- How has the network expanded over time?
- **Discipleship Intelligence** (v2.0 -- Planned) -- Where are members in their spiritual journey?
- **Coverage Intelligence** (v2.0 -- Planned) -- Which areas are served and which are gaps?
- **Expansion Intelligence** (v2.0 -- Planned) -- Where should new groups be planted?
- **Prayer Intelligence** (v2.0 -- Planned) -- Which areas have active prayer coverage?
- **Community Impact Intelligence** (v2.0 -- Planned) -- Which areas have the highest outreach potential?

---

## 3. Target Users

| Role | Needs | Version |
|------|-------|---------|
| **Leadership Team** | High-level overview of all regions at a glance | v1.0 |
| **Area Leaders** | Drill-down into their specific area's groups and members | v1.0 |
| **Operations Team** | Data filtering and export for planning | v1.0 |
| **Prayer Team Coordinators** | View prayer coverage, identify areas needing prayer teams | v2.0 |
| **Outreach Planners** | Identify high-impact zones for community engagement | v2.0 |
| **Discipleship Mentors** | Track member progression from Visitor to LG Founder | v2.0 |

---

## 4. Data Sources

### v1.0 -- Implemented

| Source | Status | Notes |
|--------|--------|-------|
| **Excel file** | Primary | `data/West_Campus_Care_Groups_Area 2026.xlsx` |
| **CSV upload** | Active | File upload via sidebar |
| **Google Sheets** | Active | Read-only integration via gspread |
| **File upload** | Active | Drag-and-drop Excel/CSV upload |

- **Update flow:** Data is maintained by operations team; dashboard reads on each load/refresh.
- **No authentication required** -- open internal access.

### v2.0 -- Planned Additions

| Source | Status | Notes |
|--------|--------|-------|
| **Members database** | Planned | Individual member records with discipleship stage and join year |
| **Prayer Teams database** | Planned | Prayer team assignments, frequencies, and coverage areas |
| **Historical snapshots** | Planned | Periodic data snapshots for growth timeline analysis |
| **Census / population data** | Planned | External data for community impact scoring |
| **Apartment density data** | Planned | External data for expansion intelligence |

> **Note:** The v2.0 data sources do not currently exist. They must be defined, collected, and maintained before the corresponding features can be built.

---

## 5. Data Model

### v1.0 -- Implemented

| Field | Type | Description |
|-------|------|-------------|
| `area` | String | Geographic area name (e.g., Kukatpally, Kondapur) |
| `lg_group` | String | Unique group identifier (e.g., LG1, LG2) |
| `leader_name` | String | Group leader name |
| `members` | Integer | Number of active members |
| `latitude` | Float | Map coordinate |
| `longitude` | Float | Map coordinate |
| `meeting_day` | String | Day of the week the group meets |
| `families` | Integer | Number of families in the group |
| `individuals` | Integer | Number of individuals in the group |

**Notes:**
- Coordinates are per-group (not per-area). If multiple groups share the same area, slight lat/long offsets are applied to prevent marker overlap.
- Geocoding covers 32 Hyderabad West areas via hardcoded coordinates.
- The number of LG groups and areas is dynamic -- the system handles varying dataset sizes.
- Strength categories: **Strong** (30+ members), **Medium** (20-29 members), **Weak** (<20 members).

### v2.0 -- Planned: Members Table

| Field | Type | Description |
|-------|------|-------------|
| `member_id` | String | Unique member identifier |
| `name` | String | Member name |
| `stage` | Enum | Discipleship stage: Visitor, Member, Leader, LG Founder |
| `lg_group` | String | FK to LG group |
| `area` | String | Residential area |
| `latitude` | Float | Member location coordinate |
| `longitude` | Float | Member location coordinate |
| `joined_year` | Integer | Year the member joined |

### v2.0 -- Planned: Prayer Teams Table

| Field | Type | Description |
|-------|------|-------------|
| `team_id` | String | Unique team identifier |
| `team_name` | String | Prayer team name |
| `area` | String | Coverage area |
| `frequency` | Enum | Meeting frequency: Weekly, Monthly, None |
| `participants` | Integer | Number of active participants |
| `leader_name` | String | Team leader |

---

## 6. Functional Requirements

### v1.0 -- Implemented

| ID | Requirement | Status |
|----|-------------|--------|
| **FR-1** | **Interactive Map** | Implemented |
| | Folium-based map with circle markers for each LG group | Done |
| | Color-coded by care group (unique color per group) | Done |
| | 4 tile styles: Google Maps, Satellite, Terrain, OpenStreetMap | Done |
| | Two map modes: Overview (hover tooltips) and Detailed (always-visible labels) | Done |
| | Zoom, pan, hover tooltips (group name, members, leader, area) | Done |
| **FR-2** | **Drill-Down Panel** | Implemented |
| | Area drill-down with detail table | Done |
| | Area-level summary (total groups, total members, strength classification) | Done |
| **FR-3** | **Sidebar Filters** | Implemented |
| | Data source selector (Excel, CSV, Google Sheets, Upload) | Done |
| | Area multiselect filter | Done |
| | Map style selector | Done |
| | Filtering updates both map and all metrics/charts | Done |
| **FR-4** | **KPI Metric Cards** | Implemented |
| | 6 KPI cards: Areas, Care Groups, Families, Individuals, Total Members, Avg per Group | Done |
| **FR-5** | **Charts & Insights** | Implemented |
| | Stacked bar chart: Members by area | Done |
| | Bar chart: Groups by area | Done |
| | Bar chart: Meeting day distribution | Done |
| | Bar chart: Top 5 and Bottom 5 groups by members | Done |
| | Bar chart: Members per leader | Done |
| **FR-6** | **Area Summary Table** | Implemented |
| | Tabular summary of all areas with key metrics | Done |
| **FR-7** | **Print Support** | Implemented |
| | Print-friendly CSS (A4 landscape) | Done |

### v2.0 -- Planned

| ID | Requirement | Status | Dependencies |
|----|-------------|--------|--------------|
| **FR-8** | **Member Density Heatmap** | Planned | Members table with individual coordinates |
| | Heat layer overlay showing member concentrations | | |
| | Toggle on/off independently of group markers | | |
| | Gradient scale from low to high density | | |
| **FR-9** | **Expansion Intelligence** | Planned | Population data, apartment density data |
| | Automated suggestions for new LG planting areas | | |
| | Score areas by: population density, distance from existing LGs, community need | | |
| | Visual overlay highlighting recommended expansion zones | | |
| **FR-10** | **Growth Timeline** | Planned | Historical data snapshots, `joined_year` field |
| | Animated or slider-based view of LG expansion over years | | |
| | Chart showing group count growth over time | | |
| | Member growth trend lines per area | | |
| **FR-11** | **Member Journey Map** | Planned | Members table with `stage` field |
| | Discipleship progression visualization | | |
| | Stages: Visitor -> Member -> Leader -> LG Founder | | |
| | Funnel or Sankey chart showing stage distribution | | |
| | Map markers colored/sized by discipleship stage | | |
| **FR-12** | **Prayer Coverage Map** | Planned | Prayer Teams table |
| | Map overlay showing prayer team coverage areas | | |
| | Color-coded by frequency: Weekly (green), Monthly (yellow), None (red) | | |
| | Gap analysis: areas without prayer coverage | | |
| **FR-13** | **Community Impact Map** | Planned | External census/population data |
| | High-impact outreach zone identification | | |
| | Scoring based on apartment density, schools, population | | |
| | Overlay highlighting priority outreach areas | | |
| **FR-14** | **Territory / Coverage Layer** | Planned | GeoPandas, SciPy |
| | Voronoi diagram territories for each LG group | | |
| | Coverage classification: green (served), yellow (partial), red (gap) | | |
| | Visual boundaries showing each group's natural territory | | |

---

## 7. Non-Functional Requirements

| Requirement | v1.0 Target | v1.0 Actual | v2.0 Target |
|-------------|-------------|-------------|-------------|
| Load time | < 3 seconds | Met | < 5 seconds (with additional layers) |
| Browser support | Chrome, Edge | Chrome, Edge, Firefox | All modern browsers |
| Deployment | Internal server | `streamlit run app.py` | Streamlit Cloud / AWS / GCR |
| Concurrent users | Up to 10 | Supported | Up to 50 |
| Data security | No PII; internal only | Met | Role-based access for member data |
| Test coverage | Basic | 22 tests passing | 80%+ coverage |
| Code quality | Linted | Flake8 + structured logging | Linted + type-checked |
| CI/CD | None | GitHub Actions pipeline | Automated deploy |

---

## 8. Out of Scope

### Permanently Out of Scope
- Mobile native app (web-responsive is sufficient)
- Real-time GPS location tracking of members
- Automated member enrollment / registration system
- Financial or budget tracking

### Moved to v2.0 Roadmap (Previously Out of Scope)
| Item | Original Status | v2.0 Plan |
|------|----------------|-----------|
| Growth trend charts | Deferred (no historical data) | FR-10: Growth Timeline |
| Predictive analytics / AI insights | Out of scope | FR-9: Expansion Intelligence |
| Choropleth / shaded region boundaries | Out of scope | FR-14: Territory / Coverage Layer |
| Authentication / role-based access | Out of scope | NFR: Required for member data privacy |

---

## 9. Tech Stack

### v1.0 -- Current (Implemented)

| Layer | Technology |
|-------|-----------|
| UI / Dashboard | Streamlit (>=1.30.0) |
| Map Visualization | **Folium** (>=0.15.0) + streamlit-folium (>=0.17.0) |
| Charts | Plotly (>=5.18.0) |
| Data Processing | Pandas (>=2.0.0) |
| Excel Support | openpyxl (>=3.1.0) |
| Google Sheets | gspread (>=6.0.0) + google-auth (>=2.25.0) |
| Deployment | Local server (`streamlit run app.py`) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Linting | Flake8 |

> **Note:** The original PRD specified PyDeck for map visualization. During implementation, Folium was chosen instead for its richer marker customization, multiple tile layer support, and better integration with Streamlit via streamlit-folium.

### v2.0 -- Planned Additions

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Spatial Analysis | GeoPandas | Territory boundaries, spatial queries |
| Voronoi Computation | SciPy (scipy.spatial) | Territory / coverage layer generation |
| Heatmap Layer | Folium HeatMap plugin | Member density visualization |
| Authentication | Streamlit auth or external provider | Role-based access for member data |
| Deployment | Streamlit Cloud, AWS EC2, or Google Cloud Run | Production hosting |

---

## 10. Architecture

### v1.0 -- Current

```
Data Sources
  |-- Excel file (primary)
  |-- CSV upload
  |-- Google Sheets (gspread)
  |-- File upload (Excel/CSV)
        |
        v
  Data Layer (Pandas)
  |-- load, clean, transform, aggregate
  |-- assign strength categories
  |-- generate area summaries
  |-- hardcoded geocoding (32 areas)
        |
        v
  Visualization Layer
  |-- Folium (interactive map with circle markers, tile styles)
  |-- Plotly (bar charts, distribution charts)
        |
        v
  Streamlit Dashboard
  |-- Sidebar (filters, data source, map style)
  |-- KPI metric cards
  |-- Map display (streamlit-folium)
  |-- Charts section
  |-- Area summary table
  |-- Print-ready CSS
        |
        v
  Browser (localhost:8501)
```

### v2.0 -- Planned Architecture

```
Data Sources
  |-- Current: Excel, CSV, Google Sheets, Upload
  |-- Planned: Members DB, Prayer Teams DB, Census/Population data
        |
        v
  Data Layer (Pandas + GeoPandas)
  |-- Current loaders (unchanged)
  |-- Member data loader
  |-- Prayer team data loader
  |-- Historical snapshot manager
        |
        v
  Geo-Intelligence Engine (NEW)
  |-- Voronoi territory generator (SciPy)
  |-- Heatmap engine (Folium HeatMap)
  |-- Expansion analyzer (scoring algorithm)
  |-- Coverage gap detector
        |
        v
  Visualization Layer
  |-- Folium (maps + heatmap + territory overlays)
  |-- Plotly (charts + timeline + Sankey/funnel)
        |
        v
  Streamlit Dashboard
  |-- Current UI (unchanged)
  |-- Layer toggle controls (heatmap, territories, prayer, impact)
  |-- Growth timeline slider
  |-- Member journey panel
  |-- Expansion recommendations panel
        |
        v
  Deployment (Streamlit Cloud / AWS EC2 / Google Cloud Run)
```

---

## 11. User Stories

### Epic 1: Data Ingestion -- COMPLETE (v1.0)

| ID | Story | Status |
|----|-------|--------|
| S1.1 | As an ops user, I can load data from an Excel file so the dashboard reflects current group data. | Done |
| S1.2 | As a user, I can upload a CSV or Excel file as an alternative data source. | Done |
| S1.3 | As a user, I can connect the dashboard to a Google Sheet for live data. | Done |
| S1.4 | As a user, I can switch between data sources from the sidebar. | Done |

### Epic 2: Map Visualization -- COMPLETE (v1.0)

| ID | Story | Status |
|----|-------|--------|
| S2.1 | As a leader, I can see all LG groups plotted on a Hyderabad map with color-coded circle markers (unique color per care group). | Done |
| S2.2 | As a leader, I can hover over a marker to see group name, members, leader, and area in a tooltip. | Done |
| S2.3 | As a leader, I can switch to Detailed mode to see always-visible labels on all markers. | Done |
| S2.4 | As a leader, I can switch between 4 map tile styles (Google Maps, Satellite, Terrain, OpenStreetMap). | Done |

### Epic 3: Filters & Metrics -- COMPLETE (v1.0)

| ID | Story | Status |
|----|-------|--------|
| S3.1 | As a user, I can filter the map by area using a sidebar multiselect. | Done |
| S3.2 | As a leader, I can see 6 KPI cards (Areas, Care Groups, Families, Individuals, Total Members, Avg per Group). | Done |
| S3.3 | As a leader, I can view an area summary table with key metrics. | Done |

### Epic 4: Charts & Analysis -- COMPLETE (v1.0)

| ID | Story | Status |
|----|-------|--------|
| S4.1 | As a leader, I can view a stacked bar chart of members by area. | Done |
| S4.2 | As a leader, I can view a chart of LG group count by area. | Done |
| S4.3 | As a leader, I can view meeting day distribution across groups. | Done |
| S4.4 | As a leader, I can view top 5 and bottom 5 groups by member count. | Done |
| S4.5 | As a leader, I can view members per leader chart. | Done |

### Epic 5: Print & Export -- COMPLETE (v1.0)

| ID | Story | Status |
|----|-------|--------|
| S5.1 | As a user, I can print the dashboard in A4 landscape format with clean output. | Done |

### Epic 6: Member Density & Heatmap -- PLANNED (v2.0)

| ID | Story | Status |
|----|-------|--------|
| S6.1 | As a leader, I can toggle a heatmap layer to see member concentration areas. | Planned |
| S6.2 | As a leader, I can identify high-density zones that may need group splitting. | Planned |

### Epic 7: Growth Timeline -- PLANNED (v2.0)

| ID | Story | Status |
|----|-------|--------|
| S7.1 | As a leader, I can view an animated timeline of LG expansion over years. | Planned |
| S7.2 | As a leader, I can see growth trend charts per area. | Planned |

### Epic 8: Member Journey & Discipleship -- PLANNED (v2.0)

| ID | Story | Status |
|----|-------|--------|
| S8.1 | As a mentor, I can see where each member is in their discipleship journey (Visitor -> Member -> Leader -> LG Founder). | Planned |
| S8.2 | As a leader, I can view a funnel chart of discipleship stage distribution. | Planned |

### Epic 9: Prayer Coverage -- PLANNED (v2.0)

| ID | Story | Status |
|----|-------|--------|
| S9.1 | As a prayer coordinator, I can see which areas have active prayer teams and their meeting frequency. | Planned |
| S9.2 | As a leader, I can identify areas without prayer coverage for team deployment. | Planned |

### Epic 10: Expansion & Territory Intelligence -- PLANNED (v2.0)

| ID | Story | Status |
|----|-------|--------|
| S10.1 | As a leader, I can see Voronoi territory boundaries showing each group's coverage area. | Planned |
| S10.2 | As a planner, I can receive automated suggestions for optimal new LG planting locations. | Planned |
| S10.3 | As a leader, I can view a community impact map highlighting high-potential outreach zones. | Planned |

---

## 12. Development Plan

### v1.0 -- Released

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| 1. Setup & Data Layer | Day 1 | Excel/CSV/Google Sheets integration, data model | Done |
| 2. Map & Core UI | Day 2 | Folium interactive map, circle markers, color coding, tooltips | Done |
| 3. Filters & Metrics | Day 3 | Sidebar filters, 6 KPI cards, area drill-down | Done |
| 4. Charts & Polish | Day 4 | 5 chart types, area summary table, print CSS | Done |
| 5. Testing & Deploy | Day 5 | 22 tests, CI/CD pipeline, linting, structured logging | Done |

### v1.1 -- In Development (Hardening)

| Phase | Focus | Status |
|-------|-------|--------|
| Code quality | Refactoring, additional test coverage, documentation | In Progress |
| Bug fixes | Edge cases, data validation improvements | In Progress |
| UI polish | Responsive improvements, accessibility | In Progress |

### v2.0 -- Future Phases

| Phase | Features | Prerequisites | Estimated Effort |
|-------|----------|---------------|-----------------|
| Phase 1: Heatmap | Member density heatmap layer | Members table with coordinates | 1-2 weeks |
| Phase 2: Territories | Voronoi coverage layer, gap analysis | GeoPandas, SciPy integration | 2-3 weeks |
| Phase 3: Growth Timeline | Historical expansion animation, trend charts | Historical data collection (6+ months of snapshots) | 2-3 weeks |
| Phase 4: Discipleship | Member journey map, stage tracking, funnel charts | Members table with `stage` field, data entry process | 3-4 weeks |
| Phase 5: Prayer & Impact | Prayer coverage map, community impact scoring, expansion intelligence | Prayer Teams table, census/population data, apartment density data | 4-6 weeks |

---

## 13. Roadmap

```
2026 Q1          2026 Q2          2026 Q3          2026 Q4          2027 Q1
  |                |                |                |                |
  v1.0 Released    v1.1 Hardening   Phase 1-2        Phase 3-4        Phase 5
  (Distribution    (Bug fixes,      (Heatmap,        (Growth          (Prayer,
   Dashboard)       tests,           Voronoi          Timeline,        Impact,
                    polish)          Territories)     Discipleship)    Expansion)
```

| Phase | Target | Key Deliverables |
|-------|--------|-----------------|
| **v1.0** | 2026 Q1 (Done) | Interactive map, KPIs, charts, multi-source data, print support |
| **v1.1** | 2026 Q2 | Hardening, test coverage, documentation, minor UI improvements |
| **Phase 1** | 2026 Q3 | Member density heatmap, layer toggle controls |
| **Phase 2** | 2026 Q3 | Voronoi territory boundaries, coverage gap analysis |
| **Phase 3** | 2026 Q4 | Growth timeline animation, historical trend charts |
| **Phase 4** | 2026 Q4 | Member journey tracking, discipleship funnel/Sankey charts |
| **Phase 5** | 2027 Q1 | Prayer coverage map, community impact scoring, expansion intelligence |

### Data Collection Milestones

Several v2.0 features require new data sources that must be established before development begins:

| Data Needed | Required For | Action |
|-------------|-------------|--------|
| Individual member records with coordinates | Heatmap, Journey Map | Design data entry process, begin collection |
| Discipleship stage tracking | Journey Map | Define stages, establish tracking workflow |
| Historical data snapshots | Growth Timeline | Begin periodic data archiving now |
| Prayer team records | Prayer Coverage | Design schema, begin collection |
| Census / population data | Community Impact | Source from government open data |
| Apartment density data | Expansion Intelligence | Source from real estate / municipal data |

---

## 14. Success Criteria

### v1.0 -- Achieved

- [x] Leadership can open dashboard and understand regional distribution in < 30 seconds
- [x] All LG groups visible on map with correct color coding
- [x] Filter and drill-down working for all areas
- [x] Dashboard loads in < 3 seconds
- [x] Multiple data sources supported (Excel, CSV, Google Sheets, Upload)
- [x] 5 analytical chart types available
- [x] Print-friendly output

### v1.1 -- In Progress

- [ ] Test coverage reaches 80%+
- [ ] All known bugs resolved
- [ ] Documentation complete
- [ ] Adopted by leadership for weekly review meetings

### v2.0 -- Planned

- [ ] Heatmap layer provides actionable density insights
- [ ] Territory view identifies at least 3 underserved areas
- [ ] Growth timeline shows expansion trends across 2+ years of data
- [ ] Member journey tracking covers 80%+ of active members
- [ ] Prayer coverage map identifies gaps leading to new team deployments
- [ ] Expansion intelligence recommendations result in at least 2 new LG plants
- [ ] Dashboard supports 50 concurrent users in cloud deployment

---

## 15. Risks

### v1.0 Risks -- Mitigated

| Risk | Status | Mitigation Applied |
|------|--------|-------------------|
| Incomplete/missing coordinates | Mitigated | Hardcoded geocoding for 32 Hyderabad West areas |
| Google Sheets API rate limits | Mitigated | Excel as primary source, multiple source options |
| Marker overlap in dense areas | Mitigated | Coordinate offsets applied per group |
| Low adoption | Monitoring | Clean UI, demonstrated to stakeholders |

### v2.0 Risks -- Active

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **New data sources not established** | High | Critical | Begin data collection process in v1.1 phase; features cannot ship without data |
| **Member data privacy concerns** | Medium | High | Implement role-based access before member-level features; no PII on public dashboard |
| **Historical data gaps** | High | Medium | Start periodic snapshots immediately; growth timeline value increases over time |
| **External data unavailability** | Medium | Medium | Census and apartment data may be incomplete; design expansion intelligence to work with partial data |
| **Scope creep across phases** | Medium | Medium | Strict phase gating; each phase must complete before next begins |
| **GeoPandas/SciPy complexity** | Low | Medium | Prototype Voronoi computation early; have fallback to simpler boundary methods |
| **Cloud deployment costs** | Low | Low | Start with Streamlit Cloud free tier; scale to AWS/GCR only if needed |
| **Performance with additional layers** | Medium | Medium | Lazy-load layers; allow users to toggle layers on/off; optimize data queries |
