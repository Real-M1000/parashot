import os
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)
# Das ist der Pfad im Container (dein Volume)
IMAGE_FOLDER = '/app/Files/BzT'

# Route, um die Bilder für den Browser verfügbar zu machen
@app.route('/bilder/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def gallery():
    # Liste alle Dateien auf, die Endungen wie jpg, png etc. haben
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    images = [f for f in os.listdir(IMAGE_FOLDER) 
              if f.lower().endswith(valid_extensions)]
    
    # Ein ganz einfaches HTML-Gerüst für die Anzeige
    html_template = """
    <h1>It works!</h1>
    <p>Hello World!</p>
    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
        {% for img in images %}
            <div style="text-align: center;">
                <img src="/bilder/{{ img }}" style="width: 200px; border-radius: 8px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                <p>{{ img }}</p>
            </div>
        {% endfor %}
    </div>
    {% if not images %}
        <p>Keine Bilder im Ordner gefunden. Lade mal ein .jpg hoch!</p>
    {% endif %}
    """
    return render_template_string(html_template, images=images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
