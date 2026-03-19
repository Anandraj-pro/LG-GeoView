# LG GeoView -- User Guide

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Git
- Web browser (Chrome recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/Anandraj-pro/LG-GeoView.git
cd LG-GeoView

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows CMD
.venv\Scripts\Activate.ps1       # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**

---

## Data Sources

LG GeoView supports 4 data sources:

### 1. West Campus Excel (Default)
- File: `data/West_Campus_Care_Groups_Area 2026.xlsx`
- Expected columns: leader_name, area, Families, Individuals, Total, Sync meeting on, Care Coordinator
- The Excel loader handles column name variations (trailing spaces, different casing)

### 2. CSV Upload
Upload any CSV file with these required columns:

| Column | Type | Description |
|--------|------|-------------|
| `area` | String | Geographic area name |
| `lg_group` | String | Group identifier |
| `leader_name` | String | Leader's name |
| `members` | Integer | Active member count |
| `latitude` | Float | GPS latitude |
| `longitude` | Float | GPS longitude |

Optional columns: `families`, `individuals`, `meeting_day`

### 3. Google Sheets
1. Open your Google Sheet
2. Go to File > Share > Publish to the web
3. Copy the published URL
4. Paste it in the dashboard's Google Sheets URL field

The URL must contain `docs.google.com/spreadsheets`. The sheet must have the same columns as the CSV format above.

### 4. File Upload
Drag and drop a CSV or Excel file directly into the upload widget.

---

## Adding New Areas

Area coordinates are stored in `data/area_coordinates.json`. To add a new area:

1. Open `data/area_coordinates.json`
2. Add a new entry with the area name (lowercase) and coordinates:
   ```json
   "new area name": [17.4500, 78.3800]
   ```
3. Restart the dashboard

Find coordinates using [Google Maps](https://maps.google.com): right-click any location > "What's here?" to get lat/lng.

---

## Strength Categories

Groups are categorized by total member count:

| Category | Members | Color |
|----------|---------|-------|
| Strong | 30+ | Green |
| Medium | 20-29 | Yellow |
| Weak | <20 | Red |

---

## Dashboard Features

- **KPI Cards**: Areas, Care Groups, Families, Individuals, Total Members, Avg per Group
- **Interactive Map**: Overview mode (hover tooltips) and Detailed mode (always-visible labels)
- **4 Map Styles**: Google Maps, Google Satellite, Google Terrain, OpenStreetMap
- **Area Filter**: Multi-select filter in sidebar updates all views
- **Drill-Down**: Select specific areas to view group details
- **Download**: Export filtered data as CSV or Excel report
- **Charts**: Members by area, Groups by area, Meeting day distribution, Top/Bottom groups, Strength distribution, Members per leader
- **Print**: Use browser Print (Ctrl+P) for A4 landscape output

---

## Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
make test

# Run tests with coverage
make coverage

# Run linter
make lint

# Format code
make format
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8501 in use | Kill existing process: `lsof -ti:8501 \| xargs kill` (Mac) or `netstat -ano \| findstr 8501` then `taskkill /F /PID <PID>` (Windows) |
| Module not found | Run `pip install -r requirements.txt` |
| Excel data won't load | Check that `data/West_Campus_Care_Groups_Area 2026.xlsx` exists |
| Google Sheets error | Ensure the sheet is published to web and URL contains `docs.google.com/spreadsheets` |
| Area not showing on map | Check if the area name exists in `data/area_coordinates.json` (case-insensitive) |
| Charts not rendering | Check browser console for JavaScript errors; try refreshing the page |
| Permission error (Windows) | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell |

---

## Project Structure

```
LG-GeoView/
  app.py                    # Main Streamlit dashboard
  requirements.txt          # Production dependencies
  requirements-dev.txt      # Development dependencies
  Makefile                  # Test/lint/format commands
  data/
    sample_data.csv         # Sample dataset (20 groups)
    area_coordinates.json   # Geocoding configuration
    *.xlsx                  # Excel data files
  src/
    data_loader.py          # Data loading and validation
    map_builder.py          # Folium map visualization
    charts.py               # Plotly chart builders
    logger.py               # Logging configuration
  tests/                    # pytest test suite
  .github/workflows/        # CI/CD pipeline
  docs/                     # PRD and sprint plan
```
