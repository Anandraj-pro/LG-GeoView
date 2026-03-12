# Architecture — LG GeoView

## Structure

```
C:/PythonProject/
├── app.py                  # Main Streamlit dashboard
├── src/
│   ├── data_loader.py      # Google Sheets + CSV data loading
│   ├── map_builder.py      # PyDeck map configuration
│   └── charts.py           # Plotly chart builders
├── data/
│   └── sample_data.csv     # Fallback/sample dataset
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Streamlit theme config
└── docs/
    ├── PRD.md
    └── architecture.md
```

## Data Flow

1. User opens dashboard → Streamlit loads
2. Data loaded from Google Sheets (or CSV fallback)
3. Pandas processes: cleaning, aggregation, color assignment
4. PyDeck renders map with colored scatter markers
5. Plotly renders bar/pie charts
6. User interacts: filter, hover, drill-down

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Map library | PyDeck | Native Streamlit support, good for scatter plots |
| Charts | Plotly | Interactive, works well with Streamlit |
| Data access | gspread + CSV | Google Sheets for live data, CSV as fallback |
| State management | Streamlit session_state | Simple, sufficient for this scale |
| Coordinate offsets | Jitter algorithm | Prevent marker overlap in same area |
