import os
import requests
import re
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    today = datetime.now()
    days_until_shabbat = (5 - today.weekday()) % 7
    return today + timedelta(days=days_until_shabbat)

def get_current_parasha():
    shabbat = get_next_shabbat().strftime("%Y-%m-%d")
    url = "https://www.hebcal.com/hebcal"
    params = {"v": "1", "cfg": "json", "parashat": "on", "start": shabbat, "end": shabbat}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        for item in data.get("items", []):
            if item.get("category") == "parashat":
                return item.get("title")
    except Exception:
        return None
    return None

def clean_name(name):
    """Entfernt Sonderzeichen für einen besseren Vergleich."""
    return re.sub(r'[^a-z0-9]', '', name.lower())

@app.route('/bilder/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def gallery():
    parasha = get_current_parasha()  # z.B. "Shmini"
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    
    all_files = os.listdir(IMAGE_FOLDER)
    images = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    match = None
    if parasha:
        # Wir säubern den Namen von Hebcal (z.B. "Shmini" -> "shmini")
        search_term = clean_name(parasha)
        
        # Wir suchen nach einer Datei, die diesen Namen enthält
        for img in images:
            if search_term in clean_name(img):
                match = img
                break
        
        # Spezialfall für Shmini / Shemini (falls Hebcal 'Shmini' sagt, du aber 'Shemini' schreibst)
        if not match and search_term == "shmini":
            for img in images:
                if "shemini" in img.lower():
                    match = img
                    break

    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Parashat {{ parasha }}</title>
        <style>
            body { background: #000; color: #eee; font-family: 'Segoe UI', sans-serif; margin: 0; overflow-x: hidden; }
            .hero { 
                height: 100vh; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center;
                background: radial-gradient(circle, #222 0%, #000 100%);
            }
            .fullscreen-img { 
                max-width: 95vw; 
                max-height: 85vh; 
                object-fit: contain;
                box-shadow: 0 0 50px rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            .title { font-size: 3em; margin-bottom: 10px; color: #f1c40f; text-shadow: 2px 2px 4px #000; }
            .error-box { padding: 40px; border: 2px dashed #444; border-radius: 20px; }
            .footer-gallery { padding: 40px; display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; background: #111; }
            .thumb { width: 120px; opacity: 0.6; transition: 0.3s; }
            .thumb:hover { opacity: 1; transform: scale(1.1); }
            .thumb img { width: 100%; border-radius: 4px; }
        </style>
    </head>
    <body>

    <div class="hero">
        {% if match %}
            <div class="title">{{ parasha }}</div>
            <img src="/bilder/{{ match }}" class="fullscreen-img">
            <p style="color: #666; margin-top: 15px;">Datei: {{ match }}</p>
        {% else %}
            <div class="error-box">
                <h1 class="title">Parashat {{ parasha if parasha else "???" }}</h1>
                <p>Kein Bild gefunden. Benenne deine Datei z.B. <b>{{ parasha }}.jpg</b></p>
                <p style="font-size: 0.8em; color: #666;">Gesuchter Begriff: {{ parasha|lower }}</p>
            </div>
        {% endif %}
    </div>

    <div class="footer-gallery">
        {% for img in images %}
            <div class="thumb">
                <a href="/bilder/{{ img }}" target="_blank">
                    <img src="/bilder/{{ img }}" title="{{ img }}">
                </a>
            </div>
        {% endfor %}
    </div>

    </body>
    </html>
    """
    return render_template_string(html_template, images=images, parasha=parasha, match=match)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
