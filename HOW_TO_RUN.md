# LG GeoView — Quick Start Guide

## First Time Setup (Clone & Run)

```bash
# 1. Clone the repository
git clone https://github.com/Anandraj-pro/LG-GeoView.git
cd LG-GeoView

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows CMD:
.venv\Scripts\activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the dashboard
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**

---

## Start the Application (After Setup)

```bash
cd LG-GeoView
.venv\Scripts\activate
streamlit run app.py
```

---

## Stop the Application

### Option 1: From the terminal
Press `Ctrl + C` in the terminal where Streamlit is running.

### Option 2: Kill the process (if terminal is closed)
```bash
# Find the Streamlit process
tasklist | findstr streamlit

# Kill it by PID
taskkill /F /PID <PID_NUMBER>
```

### Option 3: Kill all Streamlit instances
```bash
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq streamlit*" 2>nul
```

---

## Restart the Application

```bash
# Stop first (Ctrl+C in terminal), then:
streamlit run app.py
```

Or as a one-liner (stop any running instance and restart):
```bash
taskkill /F /IM streamlit.exe 2>nul & streamlit run app.py
```

---

## PowerShell Quick Commands

```powershell
# Start
Start-Process -NoNewWindow -FilePath ".venv\Scripts\streamlit.exe" -ArgumentList "run", "app.py"

# Stop
Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue

# Restart
Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue; Start-Sleep 2; .venv\Scripts\streamlit run app.py
```

---

## Prerequisites

- Python 3.10 or higher
- Git
- Web browser (Chrome recommended for printing)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8501 already in use | `netstat -ano \| findstr 8501` then `taskkill /F /PID <PID>` |
| Module not found | `pip install -r requirements.txt` |
| App won't load data | Check that `data/West_Campus_Care_Groups_Area 2026.xlsx` exists |
| Browser doesn't open | Manually go to http://localhost:8501 |
| Permission error on activate | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell |
