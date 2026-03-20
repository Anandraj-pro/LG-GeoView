# Changelog

All notable changes to LG GeoView are documented here.

## [1.2.0] - 2026-03-20

### Sprint 4: Kingdom Views
- King's Kingdom map with golden territory markers and strength-based glow
- Territory View with Voronoi polygon boundaries per area
- Ward boundaries using GHMC administrative polygons
- KML export for territory data

### Sprint 5: UI/UX Overhaul
- Animated hero banner with floating shapes and fade-up entrance
- Moving border animations on badge and KPI cards
- Shimmer text effect on "Expanding His Territory" heading
- Full kingdom theme (Cinzel + Cormorant Garamond fonts, gold palette)
- Dark/light mode toggle with CSS custom properties
- Glassmorphism sidebar with blur and gradient effects
- Mobile responsive layout (480px, 768px, 360px breakpoints)
- Scripture verses in section headers and footer
- TKT Kingdom rebrand (name, icons, copy)

### Sprint 6: Mobile Fixes
- Sidebar collapse button fix for mobile icon rendering
- Layer control positioned to avoid legend overlap
- Legend overlap fix on small screens (auto-hide on mobile)
- Map bounds locked to ORR west sector for consistent framing

### Sprint 7: Security Hardening
- Legal tile providers only (OpenStreetMap, ESRI, Stadia, CartoDB)
- HTML escaping on all user-supplied data in popups and labels
- Authentication gate with bcrypt hashed credentials (auth.yaml)
- Error boundaries around all charts and maps (graceful degradation)
- Analytics module extracted from app.py (compute_kpi_metrics, compute_territory_coverage)
- Dependency pinning in requirements.txt
- Google Sheets loader timeout and URL validation

### Sprint 8: Code Quality
- Removed dead code: build_map, build_detailed_map, _add_legend functions
- Haversine distance calculation replacing Euclidean approximation
- CI matrix expanded to Python 3.10, 3.11, 3.12
- Fixed variable shadowing (st -> strength_val in map_builder)
- Pre-commit hooks configured (trailing-whitespace, end-of-file, flake8)

### Sprint 9: UX Polish
- Chart dark mode support matching theme toggle
- Font preloading for Cinzel and Cormorant Garamond
- Area comparison side-by-side widget
- Keyboard focus-visible accessibility styling
- Downloadable printable HTML report
- Data snapshots with CSV and Excel export

## [1.1.0] - 2026-03-19

### Added
- Testing infrastructure with pytest (92 tests, 99% coverage)
- Integration tests covering full data pipeline (CSV -> maps -> charts)
- Structured logging with rotating file handler (`src/logger.py`)
- Performance timing instrumentation on all data loaders and map builders
- CI/CD pipeline with GitHub Actions (lint + test + coverage)
- CSV and Excel download buttons for filtered data and area summaries
- Strength distribution pie chart on dashboard
- Last-updated timestamp in sidebar
- Data quality validation in sidebar (duplicate detection, range checks, missing leaders)
- Google Sheets URL validation (domain check, format validation)
- Error boundaries around all charts and maps (graceful degradation)
- External geocoding config file (`data/area_coordinates.json`)
- Comprehensive user documentation (`HOW_TO_RUN.md`)
- Coverage enforcement gate in CI (75% minimum)
- `Makefile` with test, lint, coverage, and format targets
- `requirements-dev.txt` for development dependencies

### Changed
- Excel loader refactored from `iterrows()` to vectorized pandas operations
- Excel column handling hardened with normalization and fuzzy matching
- Footer updated to v1.1
- Maps use Folium (not PyDeck as originally planned)
- Removed unused `pydeck` dependency
- Removed unused `MarkerCluster` import

### Fixed
- Empty DataFrame handling in area summary aggregation
- `get_area_summary()` crash on empty DataFrames
- Pandas SettingWithCopyWarning in data validation pipeline

## [1.0.0] - 2026-03-11

### Added
- Interactive Folium map with 4 tile styles (Google Maps, Satellite, Terrain, OpenStreetMap)
- Two map modes: Overview (hover tooltips) and Detailed (always-visible labels)
- Color-coded circle markers with unique colors per care group
- 6 KPI metric cards (Areas, Care Groups, Families, Individuals, Total Members, Avg per Group)
- Data sources: Excel (primary), CSV, Google Sheets, file upload
- Sidebar filters: data source selector, area multiselect, map style selector
- Area drill-down panel with detail table
- 5 analytical charts (members by area, groups by area, meeting day, top/bottom groups, members per leader)
- Area summary table
- Print-friendly CSS (A4 landscape)
- Geocoding for 32 Hyderabad West areas
