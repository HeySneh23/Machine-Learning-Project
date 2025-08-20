# Deploying to Render (Quick Start)

## What this repo contains
- `app.py` — Flask web server that scrapes Bengaluru neighborhoods from Wikipedia, geocodes them, and renders a Folium map.
- `requirements.txt` — Python dependencies.
- `Procfile` — How to start the web server on Render (via gunicorn).
- `render.yaml` — Optional Render configuration for one-click deploys.

## Local run
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## Deploy to Render (UI)
1. Push these files to GitHub.
2. On https://render.com → New → Web Service → Connect your repo.
3. Environment: **Python**.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Click Deploy.

## Notes
- First page load may be slow because it scrapes Wikipedia and geocodes up to 50 items.
- Geocoding uses ArcGIS via `geocoder`. Free services have rate limits; repeated refreshes may temporarily fail to geocode some items.
- Use `/api/neighborhoods` to get JSON of names + coordinates.
- Health check at `/health`.
