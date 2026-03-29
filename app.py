import os
from flask import Flask

app = Flask(__name__)

@app.route('/dateien')
def liste_dateien():
    # Wir schauen in den Ordner, den wir via Volume gemountet haben
    pfad = '/app/Files/BzT'
    if os.path.exists(pfad):
        dateien = os.listdir(pfad)
        return f"Dateien auf dem Server: {', '.join(dateien)}"
    else:
        return "Ordner nicht gefunden!", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
