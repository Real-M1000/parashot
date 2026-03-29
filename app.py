import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def check_files():
    pfad = '/app/Files/BzT'
    
    try:
        if os.path.exists(pfad):
            dateien = os.listdir(pfad)
            if not dateien:
                return "Der Ordner ist da, aber er ist leer."
            return f"Gefundene Dateien auf dem Server: {', '.join(dateien)}"
        else:
            return f"Fehler: Der Pfad {pfad} existiert im Container nicht!"
    except Exception as e:
        return f"Ein Fehler ist aufgetreten: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
