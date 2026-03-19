# Hyderabad LG Growth & Discipleship Map -- Sprint Plan

**Project:** Hyderabad LG Growth & Discipleship Map (LG GeoView)
**Start Date:** 2026-03-17 (Sprint 0 start)
**Sprint Duration:** 1 week each (Mon-Fri)
**Team Size:** 1-2 developers
**Current State:** Sprint 1 COMPLETE -- 90 tests passing, 99% coverage, 0 lint errors, CI/CD active
**Last Recalibrated:** 2026-03-19

---

## Sprint Overview

| Sprint      | Dates            | Theme                                      | Status          |
|-------------|------------------|---------------------------------------------|-----------------|
| Sprint 0    | Mar 17-21        | Tech Debt & Foundation                      | DONE (18 pts)   |
| Sprint 1    | Mar 19           | Deep Test Coverage                          | DONE (20 pts)   |
| Sprint 2    | Mar 17-19        | Data Export & UX Polish                     | DONE (17 pts)   |
| Sprint 3    | Next up          | Performance & v1.1 Release                  | IN PROGRESS (9/21 pts remaining) |
| Sprint 4-5  | After v1.1       | v2.0 Phase 1: Heatmap Layer                 | Blocked         |
| Sprint 6-7  | After Phase 1    | v2.0 Phase 2: Territory / Coverage          | Blocked         |
| Sprint 8-10 | After Phase 2    | v2.0 Phase 3: Growth Timeline               | Blocked         |
| Sprint 11-13| After Phase 3    | v2.0 Phase 4: Discipleship Journey          | Blocked         |
| Sprint 14-17| After Phase 4    | v2.0 Phase 5: Prayer, Impact & Expansion    | Blocked         |

**Velocity:** 18-20 story points per sprint (1-2 devs, 1-week sprint)

> **Note on timeline shift:** Sprints 1 and 2 were delivered ahead of schedule (during Mar 17-19). The original weekly cadence has been compressed. Sprint dates for v2.0 phases are no longer fixed to calendar weeks and will be scheduled based on data availability.

---

## Sprint 0: Tech Debt & Foundation -- COMPLETE

**Goal:** Establish testing infrastructure, add logging, set up CI/CD so all future work is built on a solid base.

**Capacity:** 18 points | **Delivered:** 18 points

### S0.1 -- Set Up Testing Infrastructure -- DONE
**Points:** 5

**Delivered:**
- `tests/` directory with `conftest.py` and shared fixtures
- `pyproject.toml` with pytest configuration
- `Makefile` with `make test`, `make lint`, `make coverage` targets
- `requirements-dev.txt` with pytest, pytest-cov, flake8
- 22 tests across 3 test files (`test_data_loader.py`, `test_map_builder.py`, `test_charts.py`)

---

### S0.2 -- Add Structured Logging -- DONE
**Points:** 3

**Delivered:**
- `src/logger.py` with rotating file handler (5MB rotation)
- Logging integrated into all `src/` modules (`data_loader.py`, `map_builder.py`, `charts.py`)
- `logs/` directory added to `.gitignore`

---

### S0.3 -- CI/CD Pipeline with GitHub Actions -- DONE
**Points:** 5

**Delivered:**
- `.github/workflows/ci.yml` with lint + test + coverage steps
- Runs on every push and PR to `main`
- Python 3.11 environment

---

### S0.4 -- Fix requirements.txt Inconsistency -- DONE
**Points:** 2

**Delivered:**
- Removed unused `pydeck` dependency
- Cleaned and pinned all dependency versions

---

### S0.5 -- Code Formatting & Linting Baseline -- DONE
**Points:** 3

**Delivered:**
- Removed unused `MarkerCluster` import from `map_builder.py`
- Fixed all long line violations
- `.flake8` config file committed
- 0 lint errors across entire codebase

---

### BONUS -- Bug Fix: get_area_summary() crash on empty DataFrame -- DONE

**Delivered:**
- Fixed crash when `get_area_summary()` received an empty DataFrame
- Added guard clause for empty input

---

### Sprint 0 Actuals

| Metric           | Value                                       |
|------------------|---------------------------------------------|
| Points Planned   | 18                                          |
| Points Delivered | 18                                          |
| Tests Passing    | 22                                          |
| Overall Coverage | 77%                                         |
| Lint Errors      | 0                                           |
| Bugs Fixed       | 1 (get_area_summary empty DataFrame crash)  |

---

## Sprint 1: Deep Test Coverage -- COMPLETE

**Goal:** Drive `data_loader.py` coverage from 49% to 85%+. Add edge case tests for all modules. Harden Google Sheets input validation.

**Capacity:** 20 points | **Delivered:** 20 points
**Completed:** 2026-03-19 (ahead of schedule)

### S1.1 -- data_loader.py Test Coverage Push -- DONE
**Points:** 8
**Priority:** Critical

**Delivered:**
- 22 new test cases for `data_loader.py`
- Coverage on `data_loader.py` raised from 49% to **100%**
- Tests for `load_from_excel()`: valid data, shifted columns, total rows, missing coords, exceptions, empty rows, NaN families/individuals, NaN total fallback, NaN meeting day
- Tests for `load_from_google_sheets()`: edit URL, pub URL, plain URL, exception, empty URL, None URL, invalid URL, non-string URL
- Tests for `load_from_upload()`: CSV upload, Excel upload
- Tests for `_validate_and_clean()`: missing columns, whitespace strip, missing optional columns, type coercion, invalid coordinates, all-NaN coordinates, whitespace in area names, non-numeric coordinates
- Tests for `validate_data_quality()`: empty DF, duplicates, zero members, high members, missing leaders, clean data
- Tests for `_normalize_excel_columns()`: whitespace/lowercase, comma-wrapped leader_name, Care Coordinator, Sync meeting on, fuzzy substring match
- Tests for `_load_area_coordinates()`: hardcoded fallback, JSON load, invalid JSON fallback
- Tests for `get_area_summary()`: single area, strength assignment
- All tests run without network access (fully mocked)

---

### S1.2 -- map_builder.py Edge Case Tests -- DONE
**Points:** 5
**Priority:** High

**Delivered:**
- 7 new test cases for `map_builder.py`
- Coverage on `map_builder.py` at **99%** (1 uncovered line: line 273, unreachable branch)
- Legend HTML verified: contains all leader names, area names, color bullets, "Care Groups" heading, "Circle size = member count" note
- `build_detailed_map()` offset cycling verified (5+ rows wrapping through 4 offset positions)
- Color cycling beyond 32 groups verified
- All 4 map styles tested with both `build_map()` and `build_detailed_map()`
- Empty DataFrame tests for both map functions

---

### S1.3 -- charts.py Edge Case Tests -- DONE
**Points:** 5
**Priority:** High

**Delivered:**
- 9 new edge case tests for `charts.py`
- Coverage remains at **100%**
- Empty DataFrame tests for all 6 chart functions (`members_by_area_chart`, `groups_by_area_chart`, `strength_pie_chart`, `meeting_day_chart`, `top_bottom_groups_chart`, `leader_members_chart`)
- `strength_pie_chart()` tested with 1 and 2 categories
- `meeting_day_chart()` tested with all blank meeting days
- `top_bottom_groups_chart()` tested with fewer than 5 groups and fewer than 10 groups
- `leader_members_chart()` tested with duplicate leader names
- `area_detail_table()` tested with special characters and non-existent area

---

### S1.4 -- Input Validation for Google Sheets URL -- DONE
**Points:** 2
**Priority:** Medium

**Delivered:**
- URL validation implemented in `load_from_google_sheets()`: checks for empty/None, non-string, and non-Google Sheets URLs
- Clear `st.error()` messages for each invalid case
- Logging for URL transformation steps
- 4 unit tests covering empty, None, invalid domain, and non-string URLs

---

### Sprint 1 Actuals

| Metric           | Value                                       |
|------------------|---------------------------------------------|
| Points Planned   | 20                                          |
| Points Delivered | 20                                          |
| Tests Passing    | 90 (was 52 at start of sprint)              |
| New Tests Added  | 38                                          |
| Overall Coverage | 99% (was 87% at start of sprint)            |
| Lint Errors      | 0                                           |

**Coverage Breakdown (Post-Sprint 1):**

| Module               | Before   | After    |
|----------------------|----------|----------|
| `src/charts.py`      | 100%     | 100%     |
| `src/map_builder.py` | 99%      | 99%      |
| `src/logger.py`      | 95%      | 95%      |
| `src/data_loader.py` | 78%      | 100%     |
| **Overall**          | **87%**  | **99%**  |

---

## Sprint 2: Data Export & UX Polish -- COMPLETE

**Goal:** Add data export capability, fix known fragilities in the Excel loader, and polish the user experience.

**Capacity:** 20 points | **Delivered:** 17 points (S2.3 partial)
**Completed:** 2026-03-19 (delivered ahead of schedule, during Sprint 0 implementation)

> **Note:** Most Sprint 2 stories were implemented during the initial build and Sprint 0 work. They were not recognized as "done" in the original plan because the plan was written after the code already existed.

### S2.1 -- CSV/Excel Download for Filtered Data -- DONE
**Points:** 5
**Priority:** High

**Delivered:**
- CSV download button below drill-down table (`app.py:376-382`)
- Excel download with two sheets (Filtered Data + Area Summary) (`app.py:383-393`)
- Filenames include date: `lg_geoview_filtered_YYYY-MM-DD.csv`, `lg_geoview_report_YYYY-MM-DD.xlsx`
- Downloads reflect current area filter selections

---

### S2.2 -- Harden Excel Column Name Handling -- DONE
**Points:** 5
**Priority:** High

**Delivered:**
- `_normalize_excel_columns()` function in `data_loader.py:89-112`
- `_EXCEL_COLUMN_MAP` dict with 13 known column name variations (`data_loader.py:71-86`)
- Strips whitespace, lowercases, removes special characters
- Fuzzy substring matching fallback with WARNING-level logging
- 5 unit tests covering normalization, mapping, and fuzzy matching

---

### S2.3 -- Data Validation and Duplicate Detection -- DONE
**Points:** 3
**Priority:** Medium

**Delivered:**
- `validate_data_quality()` function implemented (`data_loader.py:271-305`)
- Detects duplicate (leader_name, area) pairs
- Warns on members <= 0 or > 200
- Warns on missing leader names
- Wired into `app.py` sidebar with expander showing "X rows loaded, Y warnings"
- 6 unit tests covering all validation scenarios

---

### S2.4 -- Strength Pie Chart on Dashboard -- DONE
**Points:** 2
**Priority:** Medium

**Delivered:**
- Strength pie chart wired into Analytics section (`app.py:432-435`)
- Responds to area filter selections
- Wrapped in try/except for graceful degradation

---

### S2.5 -- Improve Error Handling in app.py -- DONE
**Points:** 3
**Priority:** Medium

**Delivered:**
- All 6 chart renderings wrapped in try/except (`app.py:402-441`)
- Both map renderings wrapped in try/except (`app.py:297-326`)
- User-friendly fallback messages: "Chart unavailable" / "Could not render map"
- Dashboard degrades gracefully on partial failures

---

### S2.6 -- Last-Updated Timestamp Display -- DONE
**Points:** 2
**Priority:** Low

**Delivered:**
- Timestamp stored in `st.session_state.last_updated` (`app.py:179-180`)
- Display formats: "just now", "X min ago", "HH:MM AM/PM" (`app.py:189-197`)
- Updates on refresh button click (`app.py:185`)

---

### Sprint 2 Actuals

| Metric           | Value                                       |
|------------------|---------------------------------------------|
| Points Planned   | 20                                          |
| Points Delivered | 20                                          |

---

## Sprint 3: Performance, Docs & v1.1 Release -- IN PROGRESS

**Goal:** Optimize performance, write documentation, enforce test coverage gates, and tag the v1.1 release.

**Capacity:** 21 points | **Delivered:** 20 points | **Remaining:** 1 point

### S3.1 -- Performance Optimization -- DONE
**Points:** 5
**Priority:** High

**Delivered:**
- `load_from_excel()` refactored from `iterrows()` to vectorized pandas operations (Series masks, vectorized string ops, `.map()` for geocoding)
- Timing instrumentation added to all data loaders (`load_from_csv`, `load_from_excel`, `load_from_upload`) and both map builders (`build_map`, `build_detailed_map`)
- All timings logged at INFO level with `time.perf_counter()` precision
- `build_map()` and `build_detailed_map()` retain `iterrows()` — Folium requires individual marker creation; no vectorized alternative exists
- Streamlit `@st.cache_data(ttl=300)` already caches loaded data

---

### S3.2 -- Geocoding Improvement -- DONE
**Points:** 5
**Priority:** Medium

**Delivered:**
- `data/area_coordinates.json` external config file with 32 area coordinates
- `_load_area_coordinates()` loads from JSON, falls back to hardcoded `_HARDCODED_COORDINATES`
- Unmapped areas logged at WARNING level (`data_loader.py:182-184`)
- `HOW_TO_RUN.md` documents how to add new area coordinates
- 3 unit tests covering JSON load, fallback, and invalid JSON

---

### S3.3 -- User Documentation -- DONE
**Points:** 3
**Priority:** Medium

**Delivered:**
- `HOW_TO_RUN.md` with complete setup instructions (Quick Start, Prerequisites, Virtual Environment)
- Data format requirements documented for all 4 sources (Excel, CSV, Google Sheets, Upload)
- Google Sheets setup documented (Publish to web flow)
- Troubleshooting section with 7 common error scenarios and solutions
- Project structure documented
- Development setup instructions (make test, make coverage, make lint)

---

### S3.4 -- Test Coverage Gate -- DONE
**Points:** 3
**Priority:** Medium

**Delivered:**
- CI pipeline enforces `--cov-fail-under=75` (`ci.yml:36`)
- Coverage currently at 99% (far exceeds 75% gate)
- Coverage XML report uploaded as CI artifact
- 2 integration tests added (`test_integration.py`): full pipeline (CSV -> strength -> summary -> maps -> all charts -> drill-down) and filtered pipeline (single-area flow)

---

### S3.5 -- Mobile/Responsive Improvements -- DONE
**Points:** 2
**Priority:** Low

**Delivered:**
- Added `@media screen and (max-width: 768px)` responsive CSS block
- KPI cards: reduced padding and font sizes for smaller screens
- Columns set `min-width: 120px` to allow Streamlit to stack naturally on narrow viewports
- Chart max-height capped at 300px on mobile
- Map iframe height reduced to 500px on mobile
- Print styles (A4 landscape) already in place from v1.0

---

### S3.6 -- v1.1 Release Prep -- PARTIAL
**Points:** 3 (2 delivered, 1 remaining)
**Priority:** High

**Delivered:**
- `CHANGELOG.md` updated with final state (92 tests, 99% coverage, vectorized Excel loader, data quality sidebar)
- Dashboard footer shows "LG GeoView v1.1" (`app.py:463`)

**Remaining:**
- Tag Git release `v1.1.0` on a clean, passing commit
- Verify all CI checks pass on the release commit

---

### Sprint 3 Remaining Work Summary

| Item | Story | Points | Priority |
|------|-------|--------|----------|
| Git tag `v1.1.0` on clean commit | S3.6 | 1 | High |
| **Total remaining to ship v1.1** | | **1** | |

---

## v2.0 Phase Sprints

> **Important:** All v2.0 phases depend on new data sources that do not currently exist. Each phase is blocked until the corresponding data collection track (see next section) delivers the required data. Story points for v2.0 sprints are rough estimates and will be recalibrated when data becomes available.

> **Timeline update:** v2.0 sprint dates are no longer pinned to fixed calendar weeks. They will be scheduled when their data dependencies are met. The original calendar dates (Apr 14 onward) are replaced with relative ordering.

---

### Phase 1 -- Member Density Heatmap (Est. 2 sprints)

**Goal:** Add a heatmap layer showing member concentrations across Hyderabad West.

**Status:** Blocked -- awaiting Members data collection

**Dependencies:** Members table with individual coordinates (latitude, longitude)

**Stories:**

- **P1.1 -- Members Data Loader** (8 pts): Build data loader for Members table (CSV/Excel/Sheets). Validate schema: member_id, name, lg_group, area, latitude, longitude. Add to existing data source selector.
- **P1.2 -- Heatmap Layer & Toggle** (8 pts): Integrate Folium HeatMap plugin. Add toggle control in sidebar to show/hide heatmap independently of group markers. Gradient scale from low to high density.
- **P1.3 -- Density KPIs & Insights** (5 pts): Add KPI cards for member count, density per area. Add chart showing member concentration by area. Identify high-density zones that may need group splitting.

**Phase 1 Total:** ~21 points

---

### Phase 2 -- Territory / Coverage Layer (Est. 2 sprints)

**Goal:** Add Voronoi territory boundaries and coverage gap analysis.

**Status:** Blocked -- awaiting GeoPandas/SciPy integration prototype

**Dependencies:** GeoPandas, SciPy (scipy.spatial.Voronoi), Members data (for coverage validation)

**Stories:**

- **P2.1 -- Voronoi Territory Engine** (13 pts): Integrate GeoPandas and SciPy. Compute Voronoi territories from LG group coordinates. Clip polygons to Hyderabad West boundary. Generate GeoJSON for Folium overlay.
- **P2.2 -- Coverage Gap Analysis** (8 pts): Classify territories: green (served, 20+ members), yellow (partial, 10-19), red (gap, <10 or no group). Add coverage summary panel. Identify top underserved areas.

**Phase 2 Total:** ~21 points

---

### Phase 3 -- Growth Timeline (Est. 3 sprints)

**Goal:** Animated or slider-based view of LG network expansion over time.

**Status:** Blocked -- awaiting historical data snapshots (minimum 6 months of periodic data)

**Dependencies:** Historical data snapshots with timestamps, `joined_year` field in Members table

**Stories:**

- **P3.1 -- Historical Snapshot Manager** (8 pts): Build system to load and index historical data snapshots. Define snapshot format. Create time-series data structure for group/member counts per area per period.
- **P3.2 -- Timeline Animation UI** (13 pts): Add Streamlit slider or play/pause control for time navigation. Animate map markers appearing/growing over time. Show growth trend chart synchronized with map state.
- **P3.3 -- Growth Trend Charts** (5 pts): Area-level growth trend lines. Network-wide growth summary. Fastest-growing and stagnant area identification.

**Phase 3 Total:** ~26 points

---

### Phase 4 -- Discipleship Journey Map (Est. 3 sprints)

**Goal:** Visualize member progression through discipleship stages.

**Status:** Blocked -- awaiting Members table with `stage` field and data entry workflow

**Dependencies:** Members table with `stage` enum (Visitor, Member, Leader, LG Founder), established tracking process

**Stories:**

- **P4.1 -- Discipleship Stage Visualization** (13 pts): Map markers colored/sized by discipleship stage. Filter by stage in sidebar. Stage distribution KPIs per area.
- **P4.2 -- Journey Funnel & Sankey Chart** (8 pts): Funnel chart showing stage distribution (Visitor -> Member -> Leader -> LG Founder). Sankey chart showing stage transitions. Conversion rate metrics per area.
- **P4.3 -- Mentor Assignment View** (5 pts): Show mentor-mentee relationships on map. Identify members without assigned mentors. Dashboard panel for discipleship health metrics.

**Phase 4 Total:** ~26 points

---

### Phase 5 -- Prayer Coverage, Community Impact & Expansion Intelligence (Est. 4 sprints)

**Goal:** Complete the geo-intelligence platform with prayer mapping, community impact scoring, and automated expansion recommendations.

**Status:** Blocked -- awaiting Prayer Teams table, census data, apartment density data

**Dependencies:** Prayer Teams table, census/population data, apartment density data, all prior phases complete

**Stories:**

- **P5.1 -- Prayer Coverage Map** (8 pts): Map overlay showing prayer team coverage areas. Color-coded by frequency: Weekly (green), Monthly (yellow), None (red). Gap analysis identifying areas without prayer coverage.
- **P5.2 -- Community Impact Scoring** (13 pts): Integrate census/population data. Score areas by apartment density, schools, population. Overlay highlighting priority outreach zones.
- **P5.3 -- Expansion Intelligence Engine** (13 pts): Automated suggestions for new LG planting locations. Scoring algorithm combining population density, distance from existing LGs, community need, and coverage gaps.

**Phase 5 Total:** ~34 points

---

## Data Collection Track

> This track runs in parallel with development. v2.0 features cannot begin until their required data is available.

| Data Source                 | Required For          | Owner              | Target Date    | Status      |
|-----------------------------|-----------------------|--------------------|----------------|-------------|
| Members table               | Phase 1, 3, 4         | Operations Team    | TBD            | Not Started |
| Historical data snapshots   | Phase 3               | Operations Team    | Begin now      | Not Started |
| Prayer Teams table          | Phase 5               | Prayer Ministry    | TBD            | Not Started |
| Census / population data    | Phase 5               | Development Team   | TBD            | Not Started |
| Apartment density data      | Phase 5               | Development Team   | TBD            | Not Started |

**Data Source Details:**

- **Members table**: member_id, name, stage, lg_group, area, lat, lon, joined_year (Google Sheet or CSV)
- **Historical snapshots**: Periodic exports of current LG data (CSV archive, monthly)
- **Prayer Teams table**: team_id, team_name, area, frequency, participants, leader (Google Sheet or CSV)
- **Census / population data**: Area-level population and demographics (JSON or CSV from govt open data)
- **Apartment density data**: Residential complex counts and unit counts per area (CSV from municipal sources)

### Data Collection Priorities

1. **Start immediately:** Begin archiving monthly snapshots of the current LG data (even before Members table exists, group-level snapshots enable Phase 3 partial functionality).
2. **Next:** Define Members table schema and begin pilot data entry with 1-2 areas.
3. **After pilot:** Members table populated for at least 5 areas (enough to prototype Phase 1 heatmap).
4. **Post-v1.1:** Prayer Teams table and external data sourcing can begin once v1.1 is released.

---

## Backlog

### Deferred (Not in v1.1 or v2.0 Roadmap)

| Item                          | Points | Notes                                   |
|-------------------------------|--------|-----------------------------------------|
| Authentication (SSO/password) | 8      | Required before member data goes live   |
| Multi-campus support          | 13     | Would require data model changes        |
| Email/Slack report delivery   | 5      | Automated weekly summaries              |
| Dark mode theme toggle        | 3      | CSS alternate theme; cosmetic           |
| Real-time Google Sheets sync  | 5      | Replace polling with webhook            |

### Moved to v2.0 Roadmap (Previously Backlog)

| Item                           | Original Status | Now In                              |
|--------------------------------|-----------------|-------------------------------------|
| Map clustering for dense areas | Backlog         | Superseded by Phase 1 Heatmap       |
| Historical data comparison     | Backlog         | Phase 3: Growth Timeline            |
| Choropleth / shaded boundaries | Out of scope    | Phase 2: Territory / Coverage Layer |
| Predictive analytics           | Out of scope    | Phase 5: Expansion Intelligence     |

---

## Definition of Done

A story is complete when:

1. Code is written and follows project style (black formatted, flake8 clean)
2. Unit tests pass with adequate coverage for the changed code
3. CI pipeline passes (lint + tests)
4. Code is reviewed (if team > 1)
5. Changes are merged to `main`
6. No regressions in existing functionality

---

## Risk Register

### v1.1 Risks

| Risk | Impact | Status |
|------|--------|--------|
| Excel column format changes | High | Mitigated -- column hardening delivered (S2.2) |
| Google Sheets API rate limiting | Medium | Mitigated -- caching + URL validation delivered (S1.4) |
| Single developer availability | High | Low risk -- most stories delivered ahead of schedule |
| Streamlit version upgrade breaks UI | Medium | Mitigated -- version pinned in requirements.txt |

### v2.0 Risks

| Risk                          | Likelihood | Impact   | Mitigation                                 |
|-------------------------------|------------|----------|--------------------------------------------|
| Data sources not established  | High       | Critical | Begin collection in parallel               |
| Member data privacy concerns  | Medium     | High     | Role-based access before member features   |
| Historical data gaps          | High       | Medium   | Start periodic snapshots immediately       |
| External data unavailability  | Medium     | Medium   | Design to work with partial data           |
| Scope creep across phases     | Medium     | Medium   | Strict phase gating                        |
| GeoPandas/SciPy complexity    | Low        | Medium   | Prototype early; fallback to simpler methods|
| Performance with layers       | Medium     | Medium   | Lazy-load layers; toggle controls          |
| Cloud deployment costs        | Low        | Low      | Start with Streamlit Cloud free tier       |
| Data collection bandwidth    | High       | High     | Assign dedicated owner; provide templates  |

---

## Summary

### v1.1 Progress

| Metric              | Planned  | Delivered | Remaining |
|---------------------|----------|-----------|-----------|
| Story Points        | 79       | 78        | 1         |
| Stories             | 19       | 18        | 1 (S3.6 git tag) |
| Tests               | 80%+ cov | 92 tests, 99% coverage | -- |
| Lint Errors         | 0        | 0         | -- |

### v1.1 Remaining to Ship

| Item | Points | Priority |
|------|--------|----------|
| Git tag `v1.1.0` on clean, passing commit | 1 | High |
| **Total** | **1** | |

### v2.0 Totals

| Metric              | Value                                      |
|---------------------|--------------------------------------------|
| Phases              | 5                                          |
| Story Points (Est.) | ~128                                       |
| Stories             | 14                                         |
| Timeline            | TBD (blocked on data collection)           |
| Key Outcome         | Heatmaps, territories, timeline, journey   |

### Grand Total

| Metric              | Value                                      |
|---------------------|--------------------------------------------|
| Total Story Points  | ~207                                       |
| Total Stories       | 33                                         |
| v1.1 Delivered      | 67/79 pts (85%)                            |
| v2.0 Delivered      | 0/128 pts (blocked on data)                |
| Critical Dependency | Data collection must deliver on schedule   |
