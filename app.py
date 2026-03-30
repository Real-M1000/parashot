import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    # TEST-DATUM: 29. April 2026 (Mittwoch)
    today = datetime(2026, 4, 29)
    # Berechnet den nächsten Samstag (Wochentag 5)
    days_until_shabbat = (5 - today.weekday()) % 7
    target_date = today + timedelta(days=days_until_shabbat)
    return target_date.strftime("%Y-%m-%d")

def get_current_event():
    shabbat_date = get_next_shabbat()
    url = "https://www.hebcal.com/hebcal"
    # Wichtig: 's' (sedrot) auf 'on', damit Parashot immer geliefert werden
    params = {
        "v": "1", 
        "cfg": "json", 
        "maj": "on", 
        "min": "on",
        "mod": "on",
        "nx": "on",  # Zeigt auch Events an, die knapp daneben liegen
        "year": "2026",
        "month": "5", # Wir schauen in den Mai, da der nächste Schabbat dort liegt
        "ss": "on"    # Sedrot/Parashat
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        items = data.get("items", [])
        
        # Debugging für dich: Schau im Terminal, was ankommt
        print(f"Suche Event für: {shabbat_date}")

        # Wir suchen das Event, das genau auf unseren Ziel-Samstag fällt
        for item in items:
            if item.get("date") == shabbat_date:
                if item.get("category") == "parashat":
                    return item.get("title").replace("Parashat ", "")
                if item.get("category") == "holiday":
                    return item.get("title")
    except Exception as e:
        print(f"Fehler: {e}")
    
    return "Kein Event gefunden"

# ... (Rest deines Codes für clean_name, serve_image und gallery bleibt gleich)
