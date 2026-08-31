import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Prediction AVC")

artefact = joblib.load("modele/modele_avc.pkl")
modele = artefact["modele"]
scaler = artefact["scaler"]
colonnes_numeriques = artefact["colonnes_numeriques"]
colonnes_features = artefact["colonnes_features"]


@app.get("/")
def accueil():
    return {"message": "API de prediction du risque d'AVC"}


@app.get("/health")
def health():
    return {"status": "ok"}
