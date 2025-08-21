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
    try:
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
    except Exception as e:
        print("Scraping error:", e)
        return []

def geocode(name, retries=2, delay=0.5):
    """Geocode using ArcGIS with retries. Returns (lat, lng) or None."""
    query = f"{name}, Bengaluru, India"
    for attempt in range(retries):
        try:
            g = geocoder.arcgis(query)
            if g and g.ok and g.latlng:
                lat, lng = g.latlng
                if 12.5 <= lat <= 13.3 and 77.2 <= lng <= 77.9:
                    return float(lat), float(lng)
                return float(lat), float(lng)
        except Exception as e:
            print("Geocoding error:", e)
        time.sleep(delay)
    return None

def build_map():
    """Create a Folium map with markers for neighborhoods."""
    neighborhoods = scrape_neighborhoods()
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, control_scale=True)
    count = 0
    for name in neighborhoods:
        coords = geocode(name)
        if coords:
            folium.Marker(location=list(coords), popup=name).add_to(m)
            count += 1
        if count >= 20:  # reduced to avoid Vercel timeout
            break
    return m

@app.route("/")
def home():
    try:
        m = build_map()
        return m._repr_html_()
    except Exception as e:
        return f"<h3>Error generating map: {e}</h3>"

@app.route("/api/neighborhoods")
def api_neighborhoods():
    try:
        neighborhoods = scrape_neighborhoods()
        out = []
        for name in neighborhoods:
            coords = geocode(name)
            out.append({"name": name, "latlng": coords})
            if len(out) >= 20:  # reduced to avoid timeout
                break
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})
