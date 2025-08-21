from flask import Flask, jsonify
import folium
import requests
from bs4 import BeautifulSoup
import geocoder
import time

app = Flask(__name__)

WIKI_URL = "https://en.wikipedia.org/wiki/Category:Neighbourhoods_in_Bangalore"

def scrape_neighborhoods():
    """Scrape neighborhood names from Wikipedia."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36"
    }
    resp = requests.get(WIKI_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cats = soup.find_all("div", class_="mw-category")
    if not cats:
        return []
    items = cats[0].find_all("li")
    neighborhoods = [li.get_text(strip=True) for li in items if li.get_text(strip=True)]
    return neighborhoods

def geocode(name, retries=3, delay=0.8):
    """Geocode using ArcGIS with simple retries. Returns (lat, lng) or None."""
    query = f"{name}, Bengaluru, India"
    for attempt in range(retries):
        try:
            g = geocoder.arcgis(query)
            if g and g.ok and g.latlng:
                lat, lng = g.latlng
                if 12.5 <= lat <= 13.3 and 77.2 <= lng <= 77.9:
                    return float(lat), float(lng)
                return float(lat), float(lng)
        except Exception:
            pass
        time.sleep(delay)
    return None

def build_map():
    """Create a Folium map with markers for neighborhoods (where geocoding succeeds)."""
    neighborhoods = scrape_neighborhoods()
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, control_scale=True)
    count = 0
    for name in neighborhoods:
        coords = geocode(name)
        if coords:
            folium.Marker(
                location=list(coords),
                popup=name,
            ).add_to(m)
            count += 1
        if count >= 50:
            break
    return m

@app.route("/")
def home():
    m = build_map()
    return m._repr_html_()

@app.route("/api/neighborhoods")
def api_neighborhoods():
    neighborhoods = scrape_neighborhoods()
    out = []
    for name in neighborhoods:
        coords = geocode(name)
        out.append({"name": name, "latlng": coords})
        if len(out) >= 50:
            break
    return jsonify(out)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})
