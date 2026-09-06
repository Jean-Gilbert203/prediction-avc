
FROM python:3.13-slim

# Définir le dossier de travail
WORKDIR /app

# Installation de git 
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copie et installation de toutes les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet 
COPY . .

# --- CONFIGURATION DVC POUR LE CLOUD ---
ARG GDRIVE_CLIENT_ID
ARG GDRIVE_CLIENT_SECRET
ARG GDRIVE_REFRESH_TOKEN

# Création de l'authentification DVC silencieuse
RUN mkdir -p /root/.config/dvc/ && \
    echo "{\"client_id\": \"$GDRIVE_CLIENT_ID\", \"client_secret\": \"$GDRIVE_CLIENT_SECRET\", \"refresh_token\": \"$GDRIVE_REFRESH_TOKEN\"}" > /root/.config/dvc/gdrive-user-credentials.json && \
    dvc remote modify storage --local gdrive_user_credentials_file /root/.config/dvc/gdrive-user-credentials.json && \
    dvc pull

# --- LANCEMENT ---
CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT