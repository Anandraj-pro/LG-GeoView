# Deployment Guide

## Streamlit Cloud (Current)
- App auto-deploys from `main` branch on push
- URL: [your-app].streamlit.app
- Config: `.streamlit/config.toml`
- Auth: `config/auth.yaml` (bcrypt hashed passwords)

## Local Development
- `streamlit run app.py`
- Port 8501 by default
- No auth when `config/auth.yaml` is missing

## Environment
- Python 3.10+ required
- Dependencies: `pip install -r requirements.txt`
- Dev deps: `pip install -r requirements-dev.txt`

## CI/CD
- GitHub Actions runs on every push/PR
- Lint (flake8) + Tests (pytest) + Coverage (75% minimum)
- Tests run on Python 3.10, 3.11, 3.12

## Data Files
- `data/West_Campus_Care_Groups_Area 2026.xlsx` - primary data
- `data/area_coordinates.json` - geocoding config
- `data/ward_boundaries.json` - GHMC ward polygons
- `data/area_ward_mapping.json` - area-to-ward mapping
- `data/sample_data.csv` - sample dataset for testing

## Snapshots
- `make snapshot` saves timestamped copy of Excel data
- Stored in `data/snapshots/` (gitignored)

## Authentication
- Credentials in `config/auth.yaml`
- Passwords are bcrypt hashed
- To add a user: generate hash with `python -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt()).decode())"`
