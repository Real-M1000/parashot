import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Pfad zu deinen Bildern
IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    today = datetime.now()
    days_until_shabbat = (5 - today.weekday()) % 7
    target_date = today + timedelta(days=days_until_shabbat)
    return target_date.strftime("%Y-%m-%d")

def get_current_event():
    shabbat_date = get_next_shabbat()
    url = "https://www.hebcal.com/hebcal"
    params = {
        "v": "1", "cfg": "json", "maj": "on", 
        "parashat": "on", "start": shabbat_date, "end": shabbat_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        items = data.get("items", []
        for item in items:
            if item.get("category") == "parashat":
                return item.get("title").replace("Parashat ", "")
        for item in items:
            if item.get("category") == "holiday":
                return item.get("title")
    except:
        pass
    return "Kein Event"

def clean_name(name):
    if not name: return ""
    return re.sub(r'[^a-z0-9]', '', name.lower())

@app.route('/bilder/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def gallery():
    event_name = get_current_event()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    
    try:
        all_files = os.listdir(IMAGE_FOLDER)
    except:
        all_files = []
        
    images = [f for f in all_files if f.lower().endswith(valid_extensions)]
    match = None
    search_term = clean_name(event_name)
    
    for img in images:
        if search_term in clean_name(img):
            match = img
            break
            
    if not match and "pesach" in search_term:
        for img in images:
            if "pesach" in clean_name(img):
                match = img
                break

    # Das HTML-Gerüst für GROSS & RUNDE ECKEN
    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>{{ event_name }}</title>
        <style>
            /* Entfernt alle Standard-Ränder des Browsers */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body, html { 
                width: 100%; 
                height: 100%; 
                background-color: #000; /* Tiefschwarzer Hintergrund */
                overflow: hidden; /* Verhindert Scrollbalken komplett */
                font-family: 'Segoe UI', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            /* Der Container füllt den Viewport, lässt aber etwas Luft */
            .fullscreen-box {
                width: 100vw;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                padding: 15px; /* Kleiner Abstand zum Rand, damit die Ecken sichtbar sind */
            }

            /* Das Bild: Skaliert auf maximale Größe, behält Proportionen, RUNDE ECKEN */
            .main-img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain; /* Füllt den Platz optimal aus */
                display: block;
                
                /* --- RUNDE ECKEN & STYLE --- */
                border-radius: 20px; /* Hier stellst du die Rundung ein (z.B. 10px bis 50px) */
                box-shadow: 0 10px 30px rgba(0,0,0,0.7); /* Ein weicher Schatten für Tiefe */
                border: 2px solid #222; /* Ein dezenter Rahmen */
            }

            /* Der Titel schwebt dezent oben, über dem Bild */
            .title-overlay {
                position: absolute;
                top: 25px;
                padding: 8px 25px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 50px;
                color: #f1c40f;
                font-size: 2.2rem;
                font-weight: bold;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
                z-index: 10;
                pointer-events: none; /* Klicks gehen durch den Titel */
            }

            /* Falls kein Bild da ist */
            .empty-state { text-align: center; color: #555; border: 2px dashed #333; padding: 50px; border-radius: 15px; }
        </style>
    </head>
    <body>
        <div class="fullscreen-box">
            {% if match %}
                <div class="title-overlay">{{ event_name }}</div>
                <img src="/bilder/{{ match }}" class="main-img">
            {% else %}
                <div class="empty-state">
                    <div class="title-overlay" style="position: static; font-size: 1.5rem;">{{ event_name }}</div>
                    <p style="margin-top: 15px;">Kein Bild gefunden.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, event_name=event_name, match=match)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
