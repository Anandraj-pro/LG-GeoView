# Changelog

All notable changes to LG GeoView are documented here.

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
