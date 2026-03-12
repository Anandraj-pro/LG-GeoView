# LG GeoView — Quick Start Guide

## Prerequisites

- Python 3.10+ installed
- Virtual environment already set up in `.venv/`

---

## Start the Application

```bash
cd C:\PythonProject
.venv\Scripts\activate
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**

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
# Or kill the Python process running it:
for /f "tokens=2" %i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr PID') do taskkill /F /PID %i
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

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8501 already in use | `netstat -ano \| findstr 8501` then `taskkill /F /PID <PID>` |
| Module not found | `pip install -r requirements.txt` |
| App won't load data | Check that `data/West_Campus_Care_Groups_Area 2026.xlsx` exists |
| Browser doesn't open | Manually go to http://localhost:8501 |
