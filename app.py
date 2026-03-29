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
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ event_name }}</title>
        <style>
            /* Grund-Setup: Kein Scrollen, schwarzer Hintergrund */
            body, html { 
                margin: 0; 
                padding: 0; 
                width: 100%; 
                height: 100%; 
                background-color: black; 
                color: white; 
                font-family: sans-serif;
                overflow: hidden; /* Verhindert Scrollbalken im Vollbild */
            }

            /* Container für das Hauptbild */
            .fullscreen-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 100vw;
                height: 100vh;
                position: relative;
            }

            /* Das Bild selbst: Maximale Größe bei Erhalt der Proportionen */
            .main-img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain; /* Bild wird nicht beschnitten */
            }

            /* Overlay-Text (Titel der Parasha) */
            .overlay-title {
                position: absolute;
                top: 20px;
                background: rgba(0, 0, 0, 0.6);
                padding: 10px 20px;
                border-radius: 10px;
                color: #f1c40f;
                font-size: 2em;
                pointer-events: none; /* Klicks gehen durch den Text aufs Bild */
            }

            /* Mini-Galerie am unteren Rand (optional, sehr dezent) */
            .mini-footer {
                position: absolute;
                bottom: 10px;
                width: 100%;
                display: flex;
                justify-content: center;
                gap: 5px;
                opacity: 0.3;
                transition: opacity 0.3s;
            }
            .mini-footer:hover { opacity: 1; }
            .mini-footer img { height: 40px; border: 1px solid #fff; }

            .error-msg {
                text-align: center;
                border: 2px dashed #444;
                padding: 40px;
            }
        </style>
    </head>
    <body>

        <div class="fullscreen-container">
            {% if match %}
                <div class="overlay-title">{{ event_name }}</div>
                <img src="/bilder/{{ match }}" class="main-img" alt="{{ event_name }}">
            {% else %}
                <div class="error-msg">
                    <h1>{{ event_name }}</h1>
                    <p>Keine passende Datei gefunden.</p>
                    <p>Gesucht wurde nach: <b>{{ event_name }}</b></p>
                </div>
            {% endif %}
        </div>

        <div class="mini-footer">
            {% for img in images %}
                <img src="/bilder/{{ img }}" title="{{ img }}">
            {% endfor %}
        </div>

    </body>
    </html>
    """
    return render_template_string(html_template, event_name=event_name, match=match, images=images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
