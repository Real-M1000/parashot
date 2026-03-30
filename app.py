import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Pfad zu deinen Bildern
IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    today = datetime.today()
    days_until_shabbat = (5 - today.weekday()) % 7
    target_date = today + timedelta(days=days_until_shabbat)
    return target_date.strftime("%Y-%m-%d")

def get_current_event():
    shabbat_date = get_next_shabbat()
    url = "https://www.hebcal.com/hebcal"
    # Erweiterte Parameter, damit Parashot (s="on") sicher geliefert werden
    params = {
        "v": "1", "cfg": "json", "maj": "on", "s": "on",
        "start": shabbat_date, "end": shabbat_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        items = data.get("items", [])
        
        # 1. Suche nach Parasha
        for item in items:
            if item.get("category") == "parashat":
                return item.get("title").replace("Parashat ", "")
        
        # 2. Suche nach Feiertag
        for item in items:
            if item.get("category") == "holiday":
                return item.get("title")
    except Exception as e:
        print(f"Fehler: {e}")
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

    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>{{ event_name }}</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body, html { 
                width: 100%; height: 100%; background-color: #000; 
                overflow: hidden; font-family: sans-serif;
                display: flex; justify-content: center; align-items: center;
            }
            .fullscreen-box {
                width: 100vw; height: 100vh; display: flex;
                justify-content: center; align-items: center;
                position: relative; padding: 30px;
            }
            .main-img {
                max-width: 100%; max-height: 100%; object-fit: contain;
                display: block; border-radius: 40px;
                box-shadow: 0 0 50px rgba(255, 255, 255, 0.1);
            }
            .title-overlay {
                position: absolute; top: 40px; padding: 12px 35px;
                background: rgba(0, 0, 0, 0.7); border-radius: 60px;
                color: #f1c40f; font-size: 2.8rem; font-weight: bold;
                text-shadow: 2px 2px 10px #000; z-index: 10;
            }
        </style>
    </head>
    <body>
        <div class="fullscreen-box">
            {% if match %}
                <img src="/bilder/{{ match }}" class="main-img">
            {% else %}
                <div style="color: #666; text-align: center; border: 2px dashed #444; padding: 40px; border-radius: 20px;">
                    <h1>{{ event_name }}</h1>
                    <p>Kein Bild gefunden.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, event_name=event_name, match=match)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
