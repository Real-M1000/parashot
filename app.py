import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    today = datetime.now()
    # Berechnet Tage bis zum nächsten Samstag
    days_until_shabbat = (5 - today.weekday()) % 7
    target_date = today + timedelta(days=days_until_shabbat)
    return target_date.strftime("%Y-%m-%d")

def get_current_event():
    shabbat_date = get_next_shabbat()
    url = "https://www.hebcal.com/hebcal"
    params = {
        "v": "1",
        "cfg": "json",
        "maj": "on", # Große Feiertage
        "parashat": "on",
        "start": shabbat_date,
        "end": shabbat_date
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        items = data.get("items", [])
        
        # 1. Suche nach Parasha (Normalfall)
        for item in items:
            if item.get("category") == "parashat":
                return item.get("title").replace("Parashat ", "")
        
        # 2. Falls keine Parasha (z.B. wegen Pessach), nimm den Feiertag
        for item in items:
            if item.get("category") == "holiday":
                return item.get("title")
                
    except Exception as e:
        print(f"Fehler: {e}")
    return "Kein Event"

def clean_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

@app.route('/bilder/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def gallery():
    event_name = get_current_event() # Dies wird am 4. April "Pesach I" o.ä. sein
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    
    try:
        all_files = os.listdir(IMAGE_FOLDER)
    except:
        all_files = []
        
    images = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    match = None
    search_term = clean_name(event_name)
    
    # Suche nach Match im Dateinamen
    for img in images:
        if search_term in clean_name(img):
            match = img
            break

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ event_name }}</title>
        <style>
            body { background: #000; color: #fff; font-family: sans-serif; text-align: center; margin: 0; }
            .hero { height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
            .main-img { max-width: 95%; max-height: 80vh; border-radius: 12px; box-shadow: 0 0 30px rgba(255,215,0,0.2); }
            h1 { color: #f1c40f; margin-bottom: 5px; }
            .msg { background: #222; padding: 20px; border-radius: 10px; border: 1px dashed #444; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>{{ event_name }}</h1>
            
            {% if match %}
                <img src="/bilder/{{ match }}" class="main-img">
                <p style="color: #666;">Datei: {{ match }}</p>
            {% else %}
                <div class="msg">
                    <p>Keine Parasha diese Woche (Feiertag).</p>
                    <p>Suchbegriff: <b>{{ event_name }}</b></p>
                    <p>Lade ein Bild mit dem Namen <b>{{ event_name }}.jpg</b> hoch.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, event_name=event_name, match=match, images=images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
