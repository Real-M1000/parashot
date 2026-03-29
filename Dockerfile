# Nutze ein leichtgewichtiges Python-Image
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Installiere Flask
RUN pip install flask

# Kopiere die App in den Container
COPY app.py .

# Öffne Port 5000
EXPOSE 5000

# Startbefehl
CMD ["python", "app.py"]
