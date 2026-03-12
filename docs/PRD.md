# Product Requirements Document (PRD)
# LG GeoView — LG Group Distribution

**Author:** Anand Pandiri
**Date:** 11 March 2026
**Version:** 1.0
**Status:** Approved for Development

---

## 1. Product Overview

An interactive, map-based dashboard that visualizes LG (Life Group) distribution across Hyderabad-West areas. Built with Streamlit and PyDeck, it enables leadership to quickly assess regional strength, identify weak zones, and make data-driven operational decisions.

---

## 2. Target Users

| Role | Needs |
|------|-------|
| **Leadership Team** | High-level overview of all regions at a glance |
| **Area Leaders** | Drill-down into their specific area's groups and members |
| **Operations Team** | Data filtering and export for planning |

---

## 3. Data Source

- **Primary source:** Google Sheets (read-only integration)
- **Fallback:** CSV upload
- **Update flow:** Data is maintained by operations team in Google Sheets; dashboard reads it on each load/refresh
- **No authentication required for v1** — open internal access

---

## 4. Data Model

| Field | Type | Description |
|-------|------|-------------|
| `area` | String | Geographic area name (e.g., Kukatpally, Kondapur) |
| `lg_group` | String | Unique group identifier (e.g., LG1, LG2) |
| `leader_name` | String | Group leader name |
| `members` | Integer | Number of active members |
| `latitude` | Float | Map coordinate |
| `longitude` | Float | Map coordinate |

**Notes:**
- Coordinates are per-group (not per-area). If multiple groups share the same area, slight lat/long offsets will be applied to prevent marker overlap.
- The number of LG groups and areas is dynamic — the system must handle varying dataset sizes.

---

## 5. Functional Requirements

### FR-1: Interactive Map
- Display LG groups as **scatter markers** on a Hyderabad-West map
- **Color-coded** by member strength:
  - Green (12+ members) — Strong
  - Orange (8–11 members) — Medium
  - Red (<8 members) — Weak
- Zoom, pan, hover tooltips (group name, members, leader)
- Click marker to drill down

### FR-2: Drill-Down Panel
- Clicking an area or marker shows:
  - List of all LG groups in that area
  - Member count per group
  - Leader name
  - Area-level summary (total groups, total members, strength classification)

### FR-3: Area Filter
- Sidebar dropdown/multiselect to filter by area
- Supported areas (dynamic from data): Kukatpally, Kondapur, KPHB, Motinagar, etc.
- Filtering updates both map and summary metrics

### FR-4: Summary Metrics
- Top-of-page KPI cards:
  - Total LG Groups
  - Total Members
  - Strong Areas count
  - Weak Areas count

### FR-5: Charts & Insights
- Bar chart: Members by area
- Bar chart: LG group count by area
- Pie chart: Strong / Medium / Weak distribution
- *(Growth patterns deferred — no historical data yet)*

### FR-6: Data Refresh
- "Refresh Data" button to re-read from Google Sheets
- Last-updated timestamp displayed

---

## 6. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Load time | < 3 seconds for map render |
| Browser support | Chrome, Edge (modern browsers) |
| Deployment | Internal server |
| Concurrent users | Up to 10 |
| Data security | No PII stored; internal access only |

---

## 7. Out of Scope (v1)

- Mobile app
- Real-time location tracking
- Predictive analytics / AI insights
- Authentication / role-based access
- Growth trend charts (no historical data)
- Choropleth / shaded region boundaries
- Automated member enrollment

---

## 8. Tech Stack

| Layer | Technology |
|-------|-----------|
| UI / Dashboard | Streamlit |
| Map Visualization | PyDeck |
| Data Processing | Pandas |
| Data Source | Google Sheets (via gspread) + CSV fallback |
| Deployment | Internal server (streamlit run) |

---

## 9. Architecture

```
Google Sheets (data source)
        |
        v
gspread / CSV loader
        |
        v
Pandas (clean, transform, aggregate)
        |
        v
PyDeck (map layer) + Plotly (charts)
        |
        v
Streamlit (dashboard UI)
        |
        v
Internal Server (browser access)
```

---

## 10. User Stories

### Epic 1: Data Ingestion
- **S1.1** — As an ops user, I can connect the dashboard to a Google Sheet so data stays current.
- **S1.2** — As a user, I can upload a CSV as a fallback data source.
- **S1.3** — As a user, I can click "Refresh Data" to reload the latest data.

### Epic 2: Map Visualization
- **S2.1** — As a leader, I can see all LG groups plotted on a Hyderabad map with color-coded markers.
- **S2.2** — As a leader, I can hover over a marker to see group name, members, and leader.
- **S2.3** — As a leader, I can click a marker to drill down into area details.

### Epic 3: Filters & Metrics
- **S3.1** — As a user, I can filter the map by area using a sidebar dropdown.
- **S3.2** — As a leader, I can see KPI cards (total groups, members, strong/weak counts) at the top.

### Epic 4: Charts
- **S4.1** — As a leader, I can view a bar chart of members by area.
- **S4.2** — As a leader, I can view LG group count by area.
- **S4.3** — As a leader, I can view a pie chart of strength distribution.

---

## 11. Development Plan

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Setup & Data Layer | Day 1 | Google Sheets integration, data model, CSV fallback |
| 2. Map & Core UI | Day 2 | Interactive map with markers, color coding, tooltips |
| 3. Filters & Metrics | Day 3 | Sidebar filters, KPI cards, drill-down panel |
| 4. Charts & Polish | Day 4 | Bar/pie charts, UI refinement |
| 5. Testing & Deploy | Day 5 | Bug fixes, internal server deployment |

---

## 12. Success Criteria

- Leadership can open dashboard and understand regional distribution in < 30 seconds
- All LG groups visible on map with correct color coding
- Filter and drill-down working for all areas
- Dashboard loads in < 3 seconds
- Adopted by leadership for weekly review meetings

---

## 13. Risks

| Risk | Mitigation |
|------|-----------|
| Incomplete/missing coordinates | Geocode area names as fallback |
| Google Sheets API rate limits | Cache data locally, manual refresh |
| Marker overlap in dense areas | Apply coordinate offsets |
| Low adoption | Keep UI simple, demo to stakeholders early |
