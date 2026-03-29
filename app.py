html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ event_name }}</title>
        <style>
            /* Grund-Setup: Vollständige Übernahme des Bildschirms */
            body, html { 
                margin: 0; 
                padding: 0; 
                width: 100vw; 
                height: 100vh; 
                background-color: black; 
                color: white; 
                font-family: 'Segoe UI', sans-serif;
                overflow: hidden; /* Verhindert Scrollbalken */
            }

            /* Container für das Hauptbild: Nimmt den vollen Platz ein */
            .fullscreen-wrapper {
                position: absolute;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1; /* Basis-Ebene */
            }

            /* Das Bild selbst: Skaliert auf maximale Größe, aber behält Proportionen */
            .main-img {
                max-width: 100%;
                max-height: 100%;
                width: auto;
                height: auto;
                object-fit: contain; /* Bild wird maximiert, aber nie abgeschnitten */
            }

            /* Overlay-Text (Parasha-Titel): Schwebt über dem Bild */
            .overlay-header {
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10; /* Schwebt über dem Bild */
                background: rgba(0, 0, 0, 0.7);
                padding: 15px 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                color: #f1c40f;
                font-size: 2.2em;
                text-shadow: 2px 2px 4px #000;
                pointer-events: none; /* Klicks gehen durch den Text */
            }

            /* Footer-Galerie (Optional, sehr dezent) */
            .decent-footer {
                position: fixed;
                bottom: 5px;
                left: 0;
                width: 100%;
                display: flex;
                justify-content: center;
                gap: 5px;
                z-index: 5; /* Schwebt über dem Bild, aber unter dem Titel */
                opacity: 0.15;
                transition: opacity 0.4s;
            }
            .decent-footer:hover { opacity: 1; }
            .decent-footer img { height: 40px; border: 1px solid #444; border-radius: 2px; }

            /* Fehlermeldung: Falls kein Bild gefunden wird */
            .error-box {
                text-align: center;
                border: 2px dashed #666;
                padding: 50px;
                background: rgba(20,20,20,0.8);
                border-radius: 15px;
            }
        </style>
    </head>
    <body>

        <div class="fullscreen-wrapper">
            {% if match %}
                <div class="overlay-header">{{ event_name }}</div>
                <img src="/bilder/{{ match }}" class="main-img" alt="{{ event_name }}">
            {% else %}
                <div class="error-box">
                    <h1>{{ event_name }}</h1>
                    <p>Keine passende Datei gefunden.</p>
                    <p>Gefunden in {{ folder }}:</p>
                    <p style="color: #666; font-size: 0.9em;">
                    {% for img in images %}{{ img }}, {% endfor %}
                    </p>
                </div>
            {% endif %}
        </div>

        <div class="decent-footer">
            {% for img in images %}
                <img src="/bilder/{{ img }}" title="{{ img }}">
            {% endfor %}
        </div>

    </body>
    </html>
    """
    # ... und füge 'folder=IMAGE_FOLDER' in den 'return render_template_string'-Aufruf ein:
    return render_template_string(html_template, event_name=event_name, match=match, images=images, folder=IMAGE_FOLDER)
