import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Pfad zu deinen Bildern im Container
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
        "v": "1",
        "cfg": "json",
        "maj": "on",
        "parashat": "on",
        "start": shabbat_date,
        "end": shabbat_date
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        items = data.get("items", [])
        for item in items:
            if item.get("category") == "parashat":
                return item.get("title").replace("Parashat ", "")
        for item in items:
            if item.get("category") == "holiday":
                return item.get("title")
    except Exception as e:
        print(f"Fehler bei API: {e}")
    return "Kein Event"

def clean_name(name):
    if not name:
        return ""
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ event_name }}</title>
        <style>
            body, html { 
                margin: 0; padding: 0; width: 100vw; height: 100vh; 
                background-color: black; color: white; font-family: sans-serif;
                overflow: hidden; 
            }
            .fullscreen-wrapper {
                position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
                display: flex; justify-content: center; align-items: center; z-index: 1;
            }
            .main-img {
                max-width: 100%; max-height: 100%; width: auto; height: auto;
                object-fit: contain;
            }
            .overlay-header {
                position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 10; background: rgba(0, 0, 0, 0.7); padding: 10px 25px;
                border-radius: 10px; color: #f1c40f; font-size: 2.2em;
                text-shadow: 2px 2px 4px #000; pointer-events: none;
            }
            .decent-footer {
                position: fixed; bottom: 5px; left: 0; width: 100%;
                display: flex; justify-content: center; gap: 5px; z-index: 5;
                opacity: 0.1; transition: opacity 0.4s;
            }
            .decent-footer:hover { opacity: 1; }
            .decent-footer img { height: 40px; border: 1px solid #444; }
            .error-box { text-align: center; border: 2px dashed #666; padding: 40px; }
        </style>
    </head>
    <body>
        <div class="fullscreen-wrapper">
            {% if match %}
                <div class="overlay-header">{{ event_name }}</div>
                <img src="/bilder/{{ match }}" class="main-img">
            {% else %}
                <div class="error-box">
                    <h1>{{ event_name }}</h1>
                    <p>Kein passendes Bild gefunden.</p>
                </div>
            {% endif %}
        </div>
        <div class="decent-footer">
            {% for img in images %}<img src="/bilder/{{ img }}">{% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, event_name=event_name, match=match, images=images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
