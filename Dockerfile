# Nutze ein leichtgewichtiges Python-Image
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere die App in den Container
COPY app.py .

# Öffne Port 5000
EXPOSE 5000

# Startbefehl
CMD ["python", "app.py"]
