from flask import Flask
app = Flask(__name__)

@app.route('/')  # <--- Diese Zeile ist entscheidend für die Startseite!
def home():
    return "Hallo Welt!"

# Wenn du /dateien aufrufst, muss das hier stehen:
@app.route('/dateien')
def dateien():
    return "Hier sind deine Dateien"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
