import os
import requests
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

# Pfad zu deinen Bildern
IMAGE_FOLDER = '/app/Files/BzT'

def get_next_shabbat():
    today = datetime.now()
    # Wochentag 5 ist Samstag. Wir suchen den nächsten Samstag.
    days_until_shabbat = (5 - today.weekday()) % 7
    # Wenn heute Samstag ist, nehmen wir den heutigen Tag oder +7 für den nächsten
    # In diesem Fall nehmen wir den kommenden/heutigen Samstag
    return today + timedelta(days=days_until_shabbat)

def get_current_parasha():
    shabbat = get_next_shabbat().strftime("%Y-%m-%d")
    url = "https://www.hebcal.com/hebcal"
    params = {
        "v": "1",
        "cfg": "json",
        "maj": "on",
        "parashat": "on",
        "start": shabbat,
        "end": shabbat
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        for item in data.get("items", []):
            if item.get("category") == "parashat":
                # Wir geben nur den Namen zurück, z.B. "Vayakhel"
                return item.get("title")
    except Exception as e:
        print(f"Fehler bei Hebcal-Abfrage: {e}")
    return None

@app.route('/bilder/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def gallery():
    parasha = get_current_parasha()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    
    # Alle Bilder im Ordner auflisten
    all_files = os.listdir(IMAGE_FOLDER)
    images = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    match = None
    if parasha:
        # Suche nach einem Bild, das den Namen der Parasha enthält (z.B. "Parashat Vayakhel.jpg")
        # Wir suchen case-insensitive nach dem Wort der Parasha
        search_term = parasha.lower()
        for img in images:
            if search_term in img.lower():
                match = img
                break

    # HTML Template mit Vollbild-Logik
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Parashat haShavua</title>
        <style>
            body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
            .fullscreen-box { width: 100%; height: 90vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
            .fullscreen-img { max-width: 95%; max-height: 80vh; border-radius: 15px; shadow: 0 0 20px rgba(0,0,0,0.5); }
            .gallery { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 50px; border-top: 1px solid #444; padding-top: 20px; }
            .thumb { width: 150px; text-align: center; font-size: 12px; }
            .thumb img { width: 100%; border-radius: 5px; }
            h1 { color: #f1c40f; }
        </style>
    </head>
    <body>
        <h1>Parashat haShavua: {{ parasha if parasha else "Unbekannt" }}</h1>

        {% if match %}
            <div class="fullscreen-box">
                <img src="/bilder/{{ match }}" class="fullscreen-img">
                <p style="font-size: 1.5em; margin-top: 10px;">Gefundenes Bild: {{ match }}</p>
            </div>
        {% else %}
            <div style="padding: 50px; background: #333; border-radius: 20px;">
                <h2>Kein spezifisches Bild für "{{ parasha }}" gefunden.</h2>
                <p>Stelle sicher, dass der Dateiname den Namen der Parasha enthält.</p>
            </div>
        {% endif %}

        <h3>Alle verfügbaren Bilder (Archiv)</h3>
        <div class="gallery">
            {% for img in images %}
                <div class="thumb">
                    <img src="/bilder/{{ img }}">
                    <p>{{ img }}</p>
                </div>
            {% endfor %}
        </div>

        {% if not images %}
            <p>Keine Bilder gefunden. Check deinen Pfad: {{ folder }}</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, 
                                 images=images, 
                                 parasha=parasha, 
                                 match=match, 
                                 folder=IMAGE_FOLDER)

if __name__ == '__main__':
    # Debug-Mode für Entwicklung
    app.run(host='0.0.0.0', port=5000, debug=True)
