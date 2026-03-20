# TKT Kingdom (LG GeoView) -- Sprint Plan

**Project:** TKT Kingdom - West Campus (formerly LG GeoView)
**Start Date:** 2026-03-17 (Sprint 0 start)
**Sprint Duration:** 1 week each
**Team Size:** 1-2 developers
**Current State:** Sprint 6 IN PROGRESS -- 124 tests, 98% coverage, 0 lint errors, live on Streamlit Cloud
**Last Updated:** 2026-03-20

---

## Epics

| Epic ID | Epic Name | Sprints | Status | Total Points |
|---------|-----------|---------|--------|--------------|
| E1 | Tech Debt & Foundation | Sprint 0 | DONE | 18 |
| E2 | Test Coverage & Quality | Sprint 1 | DONE | 20 |
| E3 | Data Export & UX Polish | Sprint 2 | DONE | 20 |
| E4 | Performance & v1.1 Release | Sprint 3 | DONE | 21 |
| E5 | Kingdom Views & Territory Maps | Sprint 4 | DONE | 30 |
| E6 | UI/UX Overhaul (Kingdom Theme) | Sprint 5 | DONE | 30 |
| E7 | Mobile Fixes & Polish | Sprint 6 | IN PROGRESS | TBD |
| E8 | v2.0 - Member Density Heatmap | Future | BLOCKED | ~21 |
| E9 | v2.0 - Territory / Coverage | Future | BLOCKED | ~21 |
| E10 | v2.0 - Growth Timeline | Future | BLOCKED | ~26 |
| E11 | v2.0 - Discipleship Journey | Future | BLOCKED | ~26 |
| E12 | v2.0 - Prayer & Expansion Intel | Future | BLOCKED | ~34 |

---

## Sprint Overview

| Sprint | Theme | Status | Planned | Delivered | Velocity |
|--------|-------|--------|---------|-----------|----------|
| Sprint 0 | Tech Debt & Foundation | DONE | 18 | 18 | 18 |
| Sprint 1 | Deep Test Coverage | DONE | 20 | 20 | 20 |
| Sprint 2 | Data Export & UX Polish | DONE | 20 | 20 | 20 |
| Sprint 3 | Performance & v1.1 Release | DONE | 21 | 21 | 21 |
| Sprint 4 | Kingdom Views & Territory Maps | DONE | 30 | 30 | 30 |
| Sprint 5 | UI/UX Overhaul (Kingdom Theme) | DONE | 30 | 30 | 30 |
| Sprint 6 | Mobile Fixes & Polish | IN PROGRESS | TBD | -- | -- |

**Average Velocity:** 23.2 pts/sprint (Sprints 0-5)
**Total Delivered:** 139 story points across 6 completed sprints

---

## Sprint 0: Tech Debt & Foundation -- DONE

**Epic:** E1 - Tech Debt & Foundation
**Goal:** Establish testing infrastructure, add logging, set up CI/CD so all future work is built on a solid base.
**Capacity:** 18 points | **Delivered:** 18 points

### Stories

#### S0.1 -- Set Up Testing Infrastructure
**Points:** 5 | **Priority:** Critical | **Status:** DONE

**Description:** As a developer, I need a testing infrastructure so that all code changes are verified automatically.

**Acceptance Criteria:**
- [x] `tests/` directory with `conftest.py` and shared fixtures
- [x] `pyproject.toml` with pytest configuration
- [x] `Makefile` with `make test`, `make lint`, `make coverage` targets
- [x] `requirements-dev.txt` with pytest, pytest-cov, flake8
- [x] Minimum 20 tests across all source modules
- [x] All tests pass on clean checkout

**Delivered:**
- 22 tests across 3 test files (`test_data_loader.py`, `test_map_builder.py`, `test_charts.py`)

---

#### S0.2 -- Add Structured Logging
**Points:** 3 | **Priority:** High | **Status:** DONE

**Description:** As a developer, I need structured logging so that I can diagnose production issues from log files.

**Acceptance Criteria:**
- [x] Centralized logger module with rotating file handler
- [x] Log rotation at 5MB file size
- [x] Logging integrated into all `src/` modules
- [x] `logs/` directory excluded from version control

**Delivered:**
- `src/logger.py` with rotating file handler (5MB rotation)
- Logging integrated into `data_loader.py`, `map_builder.py`, `charts.py`

---

#### S0.3 -- CI/CD Pipeline with GitHub Actions
**Points:** 5 | **Priority:** Critical | **Status:** DONE

**Description:** As a developer, I need a CI/CD pipeline so that every push and PR is automatically validated.

**Acceptance Criteria:**
- [x] GitHub Actions workflow with lint + test + coverage steps
- [x] Triggers on every push and PR to `main`
- [x] Python 3.11 environment
- [x] Clear pass/fail status on PRs

**Delivered:**
- `.github/workflows/ci.yml` fully configured

---

#### S0.4 -- Fix requirements.txt Inconsistency
**Points:** 2 | **Priority:** Medium | **Status:** DONE

**Description:** As a developer, I need clean dependencies so that the project installs reliably.

**Acceptance Criteria:**
- [x] Remove unused dependencies (pydeck)
- [x] Pin all dependency versions
- [x] Clean install works from scratch

---

#### S0.5 -- Code Formatting & Linting Baseline
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a developer, I need a linting baseline so that code quality is enforced consistently.

**Acceptance Criteria:**
- [x] Remove unused imports
- [x] Fix all long line violations
- [x] `.flake8` config file committed
- [x] 0 lint errors across entire codebase

---

#### BONUS -- Bug Fix: Empty DataFrame Crash
**Points:** 0 (unplanned) | **Status:** DONE

**Delivered:**
- Fixed crash when `get_area_summary()` received an empty DataFrame
- Added guard clause for empty input

---

### Sprint 0 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 18 |
| Points Delivered | 18 |
| Tests Passing | 22 |
| Overall Coverage | 77% |
| Lint Errors | 0 |
| Bugs Fixed | 1 (empty DataFrame crash) |

---

## Sprint 1: Deep Test Coverage -- DONE

**Epic:** E2 - Test Coverage & Quality
**Goal:** Drive `data_loader.py` coverage from 49% to 85%+. Add edge case tests for all modules.
**Capacity:** 20 points | **Delivered:** 20 points

### Stories

#### S1.1 -- data_loader.py Test Coverage Push
**Points:** 8 | **Priority:** Critical | **Status:** DONE

**Description:** As a developer, I need comprehensive test coverage on the data loader so that data ingestion is reliable.

**Acceptance Criteria:**
- [x] Coverage on `data_loader.py` raised from 49% to 85%+
- [x] Tests for all public functions: `load_from_excel()`, `load_from_google_sheets()`, `load_from_upload()`
- [x] Tests for internal functions: `_validate_and_clean()`, `_normalize_excel_columns()`, `_load_area_coordinates()`
- [x] Edge cases: empty rows, NaN values, shifted columns, missing coords
- [x] All tests run without network access (fully mocked)

**Delivered:**
- 22 new test cases
- Coverage on `data_loader.py`: 49% --> **100%**

---

#### S1.2 -- map_builder.py Edge Case Tests
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a developer, I need edge case tests for map building so that map rendering is robust.

**Acceptance Criteria:**
- [x] Legend HTML verification (leader names, area names, color bullets)
- [x] Offset cycling verified (5+ rows wrapping through 4 positions)
- [x] Color cycling beyond 32 groups verified
- [x] All 4 map styles tested with both map functions
- [x] Empty DataFrame handling for both map functions

**Delivered:**
- 7 new test cases
- Coverage on `map_builder.py`: **99%**

---

#### S1.3 -- charts.py Edge Case Tests
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a developer, I need edge case tests for chart rendering so that charts degrade gracefully.

**Acceptance Criteria:**
- [x] Empty DataFrame tests for all 6 chart functions
- [x] Boundary conditions: 1 category, blank meeting days, fewer than 5 groups
- [x] Duplicate leader names handled
- [x] Special characters and non-existent areas tested

**Delivered:**
- 9 new edge case tests
- Coverage on `charts.py`: **100%**

---

#### S1.4 -- Input Validation for Google Sheets URL
**Points:** 2 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I need URL validation so that invalid Google Sheets URLs show clear error messages.

**Acceptance Criteria:**
- [x] Validates empty/None URLs
- [x] Validates non-string input
- [x] Validates non-Google Sheets domains
- [x] Clear `st.error()` messages for each case
- [x] Logging for URL transformation steps

---

### Sprint 1 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 20 |
| Points Delivered | 20 |
| Tests Passing | 90 (was 52 at start) |
| New Tests Added | 38 |
| Overall Coverage | 99% (was 87%) |
| Lint Errors | 0 |

**Coverage Breakdown (Post-Sprint 1):**

| Module | Before | After |
|--------|--------|-------|
| `src/charts.py` | 100% | 100% |
| `src/map_builder.py` | 99% | 99% |
| `src/logger.py` | 95% | 95% |
| `src/data_loader.py` | 78% | 100% |
| **Overall** | **87%** | **99%** |

---

## Sprint 2: Data Export & UX Polish -- DONE

**Epic:** E3 - Data Export & UX Polish
**Goal:** Add data export capability, fix known fragilities in the Excel loader, and polish the user experience.
**Capacity:** 20 points | **Delivered:** 20 points

### Stories

#### S2.1 -- CSV/Excel Download for Filtered Data
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As an operations user, I need to download filtered data so that I can share reports offline.

**Acceptance Criteria:**
- [x] CSV download button below drill-down table
- [x] Excel download with two sheets (Filtered Data + Area Summary)
- [x] Filenames include date: `lg_geoview_filtered_YYYY-MM-DD.csv`
- [x] Downloads reflect current area filter selections

---

#### S2.2 -- Harden Excel Column Name Handling
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a developer, I need robust column mapping so that the Excel loader handles messy headers.

**Acceptance Criteria:**
- [x] `_normalize_excel_columns()` function with strip/lowercase/special char removal
- [x] `_EXCEL_COLUMN_MAP` dict with 13+ known column name variations
- [x] Fuzzy substring matching fallback with WARNING-level logging
- [x] Unit tests covering normalization, mapping, and fuzzy matching

---

#### S2.3 -- Data Validation and Duplicate Detection
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I need data quality warnings so that I can fix issues in the source data.

**Acceptance Criteria:**
- [x] `validate_data_quality()` function implemented
- [x] Detects duplicate (leader_name, area) pairs
- [x] Warns on members <= 0 or > 200
- [x] Warns on missing leader names
- [x] Sidebar expander showing "X rows loaded, Y warnings"

---

#### S2.4 -- Strength Pie Chart on Dashboard
**Points:** 2 | **Priority:** Medium | **Status:** DONE

**Description:** As a leader, I need a strength distribution pie chart so that I can see the overall health at a glance.

**Acceptance Criteria:**
- [x] Strength pie chart in Analytics section
- [x] Responds to area filter selections
- [x] Graceful degradation on error

---

#### S2.5 -- Improve Error Handling in app.py
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I need graceful error handling so that the dashboard remains usable when individual components fail.

**Acceptance Criteria:**
- [x] All 6 chart renderings wrapped in try/except
- [x] Both map renderings wrapped in try/except
- [x] User-friendly fallback messages
- [x] Dashboard degrades gracefully on partial failures

---

#### S2.6 -- Last-Updated Timestamp Display
**Points:** 2 | **Priority:** Low | **Status:** DONE

**Description:** As a user, I need to see when the data was last refreshed so that I know how current the dashboard is.

**Acceptance Criteria:**
- [x] Timestamp stored in session state
- [x] Display formats: "just now", "X min ago", "HH:MM AM/PM"
- [x] Updates on refresh button click

---

### Sprint 2 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 20 |
| Points Delivered | 20 |
| Stories Completed | 6/6 |

---

## Sprint 3: Performance & v1.1 Release -- DONE

**Epic:** E4 - Performance & v1.1 Release
**Goal:** Optimize performance, write documentation, enforce test coverage gates, and tag the v1.1 release.
**Capacity:** 21 points | **Delivered:** 21 points

### Stories

#### S3.1 -- Performance Optimization
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a user, I need faster data loading so that the dashboard feels responsive.

**Acceptance Criteria:**
- [x] `load_from_excel()` refactored from `iterrows()` to vectorized pandas operations
- [x] Timing instrumentation on all data loaders and map builders
- [x] Timings logged at INFO level with `time.perf_counter()` precision
- [x] `@st.cache_data(ttl=300)` caching verified

---

#### S3.2 -- Geocoding Improvement
**Points:** 5 | **Priority:** Medium | **Status:** DONE

**Description:** As a developer, I need external geocoding configuration so that adding new areas does not require code changes.

**Acceptance Criteria:**
- [x] `data/area_coordinates.json` external config file with 32 area coordinates
- [x] Falls back to hardcoded `_HARDCODED_COORDINATES` if JSON missing/invalid
- [x] Unmapped areas logged at WARNING level
- [x] Documentation in `HOW_TO_RUN.md`

---

#### S3.3 -- User Documentation
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a new user, I need clear setup instructions so that I can run the dashboard independently.

**Acceptance Criteria:**
- [x] Complete setup instructions (Quick Start, Prerequisites, Virtual Environment)
- [x] Data format requirements for all 4 sources
- [x] Google Sheets setup guide
- [x] Troubleshooting section (7+ common errors)
- [x] Project structure documented

---

#### S3.4 -- Test Coverage Gate + Integration Tests
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a developer, I need CI-enforced coverage thresholds so that quality does not regress.

**Acceptance Criteria:**
- [x] CI pipeline enforces `--cov-fail-under=75`
- [x] Coverage XML report uploaded as CI artifact
- [x] Integration tests: full pipeline (CSV -> strength -> summary -> maps -> charts)
- [x] Integration tests: filtered pipeline (single-area flow)

---

#### S3.5 -- Mobile/Responsive Improvements
**Points:** 2 | **Priority:** Low | **Status:** DONE

**Description:** As a mobile user, I need responsive layout so that the dashboard is usable on phones and tablets.

**Acceptance Criteria:**
- [x] `@media screen and (max-width: 768px)` responsive CSS block
- [x] KPI cards: reduced padding and font sizes on small screens
- [x] Chart max-height capped at 300px on mobile
- [x] Map iframe height reduced to 500px on mobile

---

#### S3.6 -- v1.1 Release Prep
**Points:** 3 | **Priority:** High | **Status:** DONE

**Description:** As a project lead, I need a clean tagged release so that the v1.1 milestone is formally completed.

**Acceptance Criteria:**
- [x] `CHANGELOG.md` updated with final state
- [x] Dashboard footer shows "LG GeoView v1.1"
- [x] Git tag `v1.1.0` on clean, passing commit
- [x] All CI checks pass on the release commit

---

### Sprint 3 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 21 |
| Points Delivered | 21 |
| Release | v1.1.0 tagged |

---

## Sprint 4: Kingdom Views & Territory Maps -- DONE

**Epic:** E5 - Kingdom Views & Territory Maps
**Goal:** Add pastoral "King's Kingdom" map view and territory analysis with real GHMC ward boundaries.
**Capacity:** 30 points | **Delivered:** 30 points

### Stories

#### S4.1 -- King's Kingdom Pastoral Map View
**Points:** 8 | **Priority:** High | **Status:** DONE

**Description:** As a pastoral leader, I need a dedicated "King's Kingdom" map view with golden markers so that I can see the church's territorial presence with a kingdom perspective.

**Acceptance Criteria:**
- [x] Separate map view mode for "King's Kingdom"
- [x] Golden-themed markers distinguishing this view from standard maps
- [x] Pastoral data overlays
- [x] Accessible from main navigation

---

#### S4.2 -- Territory View with GHMC Ward Boundaries
**Points:** 8 | **Priority:** High | **Status:** DONE

**Description:** As a leader, I need territory views with real GHMC ward boundary polygons so that I can see which municipal wards have LG coverage.

**Acceptance Criteria:**
- [x] Real GHMC ward boundary polygons loaded and rendered
- [x] Ward boundaries overlay on the map
- [x] Visual distinction between covered and uncovered wards
- [x] Performance acceptable with polygon rendering

---

#### S4.3 -- Advanced Territory Analysis
**Points:** 5 | **Priority:** Medium | **Status:** DONE

**Description:** As a strategist, I need layered territory analysis so that I can toggle between different views of the data.

**Acceptance Criteria:**
- [x] 5 toggleable map layers
- [x] Layer controls accessible in sidebar or map controls
- [x] Layers render independently without performance degradation
- [x] Clear visual legend for each active layer

---

#### S4.4 -- KML/CSV Export Functionality
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I need KML and CSV export so that I can use the territory data in Google Earth and spreadsheets.

**Acceptance Criteria:**
- [x] KML export of map data
- [x] CSV export of territory analysis
- [x] Downloads include relevant metadata

---

#### S4.5 -- Fix Map Bounds to Nehru ORR Region
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I need the map constrained to the Nehru ORR region so that I see only the relevant geographic area.

**Acceptance Criteria:**
- [x] Map bounds fixed to Nehru Outer Ring Road region
- [x] Prevents users from panning to irrelevant areas
- [x] All LG markers visible within bounds

---

#### S4.6 -- Map Builder Test Coverage Expansion
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a developer, I need comprehensive map builder tests so that territory features do not introduce regressions.

**Acceptance Criteria:**
- [x] `map_builder.py` coverage raised from 26% to 95%+
- [x] 32 new tests added
- [x] Territory-related functions fully tested

**Delivered:**
- Coverage: 26% --> **98%**
- 32 new tests added

---

### Sprint 4 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 30 |
| Points Delivered | 30 |
| New Tests Added | 32 |
| map_builder.py Coverage | 26% --> 98% |

---

## Sprint 5: UI/UX Overhaul (Kingdom Theme) -- DONE

**Epic:** E6 - UI/UX Overhaul (Kingdom Theme)
**Goal:** Transform the dashboard with a kingdom-themed UI including animations, typography, dark mode, and responsive design.
**Capacity:** 30 points | **Delivered:** 30 points

### Stories

#### S5.1 -- Animated Hero Banner
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a user, I want an animated hero banner so that the dashboard has a polished, professional entrance.

**Acceptance Criteria:**
- [x] React-inspired animation using pure CSS
- [x] Smooth entrance animation on page load
- [x] Branding consistent with "TKT Kingdom - West Campus"
- [x] Performs well (no jank or layout shift)

---

#### S5.2 -- Moving Border Glow Effect on KPI Cards
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I want visually distinctive KPI cards so that key metrics stand out.

**Acceptance Criteria:**
- [x] Moving border glow effect using CSS animations
- [x] Applied to all 6 KPI cards
- [x] Works in both dark and light modes

---

#### S5.3 -- Shimmer Text Animation
**Points:** 2 | **Priority:** Low | **Status:** DONE

**Description:** As a user, I want subtle text shimmer effects so that headings feel dynamic.

**Acceptance Criteria:**
- [x] CSS shimmer animation on key headings
- [x] Subtle and non-distracting
- [x] Graceful fallback in browsers that do not support animation

---

#### S5.4 -- Kingdom Theme Typography
**Points:** 3 | **Priority:** Medium | **Status:** DONE

**Description:** As a user, I want kingdom-themed typography so that the dashboard feels intentional and branded.

**Acceptance Criteria:**
- [x] Cinzel font for headings
- [x] Cormorant Garamond font for body text
- [x] Google Fonts loaded via CDN
- [x] Consistent application across all dashboard sections

---

#### S5.5 -- Dark/Light Mode Toggle
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a user, I want to toggle between dark and light themes so that I can use the dashboard in different lighting conditions.

**Acceptance Criteria:**
- [x] CSS custom properties (variables) for theme colors
- [x] Toggle control in sidebar or header
- [x] All components respect theme (KPIs, charts, maps, tables)
- [x] Theme preference persists during session

---

#### S5.6 -- Glassmorphism Sidebar Effect
**Points:** 3 | **Priority:** Low | **Status:** DONE

**Description:** As a user, I want a modern glassmorphism sidebar so that the UI feels contemporary.

**Acceptance Criteria:**
- [x] Frosted glass / blur effect on sidebar
- [x] Subtle transparency
- [x] Text remains readable over the effect

---

#### S5.7 -- Mobile Responsive Design (3 Breakpoints)
**Points:** 5 | **Priority:** High | **Status:** DONE

**Description:** As a mobile user, I need the dashboard to adapt to phone, tablet, and desktop screens.

**Acceptance Criteria:**
- [x] 3 CSS breakpoints (phone, tablet, desktop)
- [x] KPI cards reflow properly at each breakpoint
- [x] Charts resize appropriately
- [x] Map takes full width on mobile
- [x] Navigation remains accessible at all sizes

---

#### S5.8 -- Scripture Verses Integration
**Points:** 2 | **Priority:** Low | **Status:** DONE

**Description:** As a ministry user, I want scripture verses throughout the dashboard so that the tool reflects its spiritual purpose.

**Acceptance Criteria:**
- [x] Scripture verses placed in relevant dashboard sections
- [x] Verses are contextually appropriate
- [x] Non-intrusive placement

---

#### S5.9 -- Rebranding to TKT Kingdom - West Campus
**Points:** 2 | **Priority:** Medium | **Status:** DONE

**Description:** As a stakeholder, I need the dashboard rebranded to "TKT Kingdom - West Campus" to reflect the ministry identity.

**Acceptance Criteria:**
- [x] Title updated throughout UI
- [x] Browser tab title updated
- [x] Footer and header reflect new branding

---

### Sprint 5 Metrics

| Metric | Value |
|--------|-------|
| Points Planned | 30 |
| Points Delivered | 30 |
| UI Components Added | 9 |
| CSS Animations | 3 (hero, glow, shimmer) |

---

## Sprint 6: Mobile Fixes & Polish -- IN PROGRESS

**Epic:** E7 - Mobile Fixes & Polish
**Goal:** Fix mobile-specific rendering issues discovered after Sprint 5 UI overhaul.

### Stories

#### S6.1 -- Fix Mobile Icon Rendering
**Points:** 2 | **Priority:** High | **Status:** DONE

**Description:** As a mobile user, I need the double_arrow_right icon to render correctly instead of showing raw text.

**Acceptance Criteria:**
- [x] Icon renders as graphical arrow on mobile browsers
- [x] Fallback text if icon font fails to load

---

#### S6.2 -- Fix Map Layer Control Overlap
**Points:** 2 | **Priority:** High | **Status:** DONE

**Description:** As a mobile user, I need the layer control to not overlap with map content.

**Acceptance Criteria:**
- [x] Layer control repositioned to avoid overlap
- [x] Controls moved to sidebar expander for mobile

---

#### S6.3 -- Fix Legend Overlap
**Points:** 2 | **Priority:** High | **Status:** DONE

**Description:** As a user, I need the legend to not overlap with map content on small screens.

**Acceptance Criteria:**
- [x] Legend moved to KPIs section instead of floating on map
- [x] Clear and readable on all screen sizes

---

#### S6.4 -- Map Controls to Sidebar Expander
**Points:** 2 | **Priority:** Medium | **Status:** DONE

**Description:** As a mobile user, I need map controls in the sidebar so they do not clutter the map.

**Acceptance Criteria:**
- [x] All map controls accessible via sidebar expander
- [x] Sidebar collapsed by default on mobile
- [x] Territory radius default set to 15km

---

#### S6.5 -- Map Height Optimization
**Points:** 1 | **Priority:** Low | **Status:** DONE

**Description:** As a mobile user, I need optimized map height so that map and content are balanced.

**Acceptance Criteria:**
- [x] Map height adapts to viewport size
- [x] No excessive scrolling required to see map and KPIs

---

### Sprint 6 Metrics (Partial -- Sprint In Progress)

| Metric | Value |
|--------|-------|
| Stories Completed | 5 |
| Points Estimated | ~9 |
| Tests Passing | 124 |
| Overall Coverage | 98% |

---

## Velocity Tracking

### Velocity Chart

```
Sprint 0  |##################   | 18 pts
Sprint 1  |####################  | 20 pts
Sprint 2  |####################  | 20 pts
Sprint 3  |#####################  | 21 pts
Sprint 4  |##############################| 30 pts
Sprint 5  |##############################| 30 pts
          0    5   10   15   20   25   30
```

### Velocity Trend

| Metric | Value |
|--------|-------|
| Average Velocity | 23.2 pts/sprint |
| Min Velocity | 18 pts (Sprint 0) |
| Max Velocity | 30 pts (Sprints 4, 5) |
| Total Delivered | 139 pts |
| Total Stories Done | 30+ stories |
| Total Sprints | 6 complete, 1 in progress |

### Burnup Chart (Cumulative)

```
Points
 140 |                                        *
 120 |                                  *
 100 |                            *
  80 |                      *
  60 |                *
  40 |          *
  20 |    *
   0 |
     S0    S1    S2    S3    S4    S5
```

---

## Quality Metrics (Current State)

| Metric | Value |
|--------|-------|
| Total Tests | 124 |
| Test Coverage | 98% |
| Lint Errors | 0 |
| CI/CD | GitHub Actions (active) |
| Coverage Gate | 75% minimum (CI-enforced) |
| Production Status | Live on Streamlit Cloud |
| Release Tag | v1.1.0 |
| PRs Merged | #1 through #8 |

### Test Growth Over Time

| Sprint | Tests | Coverage |
|--------|-------|----------|
| Sprint 0 | 22 | 77% |
| Sprint 1 | 90 | 99% |
| Sprint 2 | 90 | 99% |
| Sprint 3 | 92 | 99% |
| Sprint 4 | 124 | 98% |
| Sprint 5 | 124 | 98% |

---

## v2.0 Future Phases -- BLOCKED on Data

> All v2.0 phases depend on new data sources that do not currently exist. Each phase is blocked until the corresponding data collection delivers the required data.

---

### Epic E8: Phase 1 -- Member Density Heatmap (Est. 2 sprints, ~21 pts)

**Status:** BLOCKED -- awaiting Members data collection

**Dependencies:** Members table with individual coordinates (latitude, longitude)

| Story | Points | Description |
|-------|--------|-------------|
| P1.1 | 8 | Members Data Loader -- Build loader for Members table (CSV/Excel/Sheets). Validate schema: member_id, name, lg_group, area, lat, lon. |
| P1.2 | 8 | Heatmap Layer & Toggle -- Integrate Folium HeatMap plugin. Toggle control in sidebar. Gradient scale. |
| P1.3 | 5 | Density KPIs & Insights -- Member count/density KPIs per area. High-density zone identification for group splitting. |

---

### Epic E9: Phase 2 -- Territory / Coverage Layer (Est. 2 sprints, ~21 pts)

**Status:** BLOCKED -- awaiting GeoPandas/SciPy integration prototype

**Dependencies:** GeoPandas, SciPy (scipy.spatial.Voronoi), Members data

| Story | Points | Description |
|-------|--------|-------------|
| P2.1 | 13 | Voronoi Territory Engine -- Compute Voronoi territories from LG coordinates. Clip to Hyderabad West boundary. GeoJSON overlay. |
| P2.2 | 8 | Coverage Gap Analysis -- Classify: green (20+ members), yellow (10-19), red (<10). Coverage summary panel. |

---

### Epic E10: Phase 3 -- Growth Timeline (Est. 3 sprints, ~26 pts)

**Status:** BLOCKED -- awaiting historical data snapshots (6+ months)

**Dependencies:** Historical data snapshots with timestamps, `joined_year` field

| Story | Points | Description |
|-------|--------|-------------|
| P3.1 | 8 | Historical Snapshot Manager -- Load and index historical snapshots. Time-series data structure. |
| P3.2 | 13 | Timeline Animation UI -- Slider/play-pause for time navigation. Animated markers. Synchronized growth chart. |
| P3.3 | 5 | Growth Trend Charts -- Area-level growth trend lines. Fastest-growing/stagnant area identification. |

---

### Epic E11: Phase 4 -- Discipleship Journey Map (Est. 3 sprints, ~26 pts)

**Status:** BLOCKED -- awaiting Members table with `stage` field

**Dependencies:** Members table with `stage` enum (Visitor, Member, Leader, LG Founder)

| Story | Points | Description |
|-------|--------|-------------|
| P4.1 | 13 | Discipleship Stage Visualization -- Map markers colored/sized by stage. Filter by stage. Stage distribution KPIs. |
| P4.2 | 8 | Journey Funnel & Sankey Chart -- Stage funnel chart. Sankey transitions. Conversion rate metrics. |
| P4.3 | 5 | Mentor Assignment View -- Mentor-mentee relationships on map. Unassigned member identification. |

---

### Epic E12: Phase 5 -- Prayer Coverage & Expansion Intelligence (Est. 4 sprints, ~34 pts)

**Status:** BLOCKED -- awaiting Prayer Teams table, census data, apartment density data

**Dependencies:** Prayer Teams table, census/population data, all prior phases

| Story | Points | Description |
|-------|--------|-------------|
| P5.1 | 8 | Prayer Coverage Map -- Prayer team coverage overlay. Color-coded by frequency (Weekly/Monthly/None). Gap analysis. |
| P5.2 | 13 | Community Impact Scoring -- Census/population data integration. Area scoring by density, schools, population. Priority outreach zones. |
| P5.3 | 13 | Expansion Intelligence Engine -- Automated new LG planting suggestions. Scoring algorithm combining density, distance, need, gaps. |

---

## Data Collection Track (Parallel)

> This track runs in parallel with development. v2.0 features cannot begin until their required data is available.

| Data Source | Required For | Owner | Status |
|-------------|-------------|-------|--------|
| Members table | Phase 1, 3, 4 | Operations Team | Not Started |
| Historical snapshots | Phase 3 | Operations Team | Not Started |
| Prayer Teams table | Phase 5 | Prayer Ministry | Not Started |
| Census / population data | Phase 5 | Development Team | Not Started |
| Apartment density data | Phase 5 | Development Team | Not Started |

**Data Collection Priorities:**
1. Begin archiving monthly snapshots of current LG data immediately
2. Define Members table schema and pilot data entry with 1-2 areas
3. Members table populated for 5+ areas (enough for Phase 1 heatmap prototype)
4. Prayer Teams table and external data sourcing after v1.1 release

---

## Backlog

### Deferred (Not in v1.x or v2.0 Roadmap)

| Item | Points | Notes |
|------|--------|-------|
| Authentication (SSO/password) | 8 | Required before member data goes live |
| Multi-campus support | 13 | Would require data model changes |
| Email/Slack report delivery | 5 | Automated weekly summaries |
| Real-time Google Sheets sync | 5 | Replace polling with webhook |
| PDF report generation | 5 | One-click pastoral reports |

---

## Definition of Done

A story is complete when:

1. Code is written and follows project style (black formatted, flake8 clean)
2. Unit tests pass with adequate coverage for changed code
3. CI pipeline passes (lint + tests + coverage gate)
4. Code is reviewed (if team > 1)
5. Changes are merged to `main`
6. No regressions in existing functionality
7. Acceptance criteria verified

---

## Risk Register

### Mitigated Risks (v1.x)

| Risk | Status |
|------|--------|
| Excel column format changes | Mitigated -- fuzzy column matching (S2.2) |
| Google Sheets API rate limiting | Mitigated -- caching + URL validation (S1.4) |
| Single developer availability | Low risk -- ahead of schedule |
| Streamlit version breaks UI | Mitigated -- version pinned |
| Mobile rendering issues | Mitigated -- Sprint 5-6 responsive work |

### Active Risks (v2.0)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data sources not established | High | Critical | Begin collection in parallel |
| Member data privacy | Medium | High | Role-based access before member features |
| Historical data gaps | High | Medium | Start periodic snapshots immediately |
| External data unavailability | Medium | Medium | Design for partial data |
| Scope creep across phases | Medium | Medium | Strict phase gating |
| Performance with layers | Medium | Medium | Lazy-load layers; toggle controls |

---

## Summary

### Overall Progress

| Metric | Value |
|--------|-------|
| Total Story Points Delivered | 139 |
| Total Sprints Completed | 6 |
| Average Velocity | 23.2 pts/sprint |
| Tests | 124 |
| Coverage | 98% |
| Lint Errors | 0 |
| Production | Live on Streamlit Cloud |
| Release | v1.1.0 |

### v2.0 Estimated Totals

| Metric | Value |
|--------|-------|
| Phases | 5 |
| Story Points (Est.) | ~128 |
| Stories | 14 |
| Timeline | Blocked on data collection |

### Grand Total (v1.x + v2.0)

| Metric | Value |
|--------|-------|
| Total Story Points | ~267 |
| Delivered | 139 pts (52%) |
| Remaining | ~128 pts (blocked on data) |
