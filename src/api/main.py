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
class Patient(BaseModel):
    gender: str
    age: float
    hypertension: int
    heart_disease: int
    ever_married: str
    work_type: str
    Residence_type: str
    avg_glucose_level: float
    bmi: float
    smoking_status: str


@app.post("/predict")
def predict(patient: Patient):
    df = pd.DataFrame([patient.dict()])

    colonnes_categorielles = ['gender', 'ever_married', 'work_type',
                               'Residence_type', 'smoking_status']
    df = pd.get_dummies(df, columns=colonnes_categorielles, drop_first=True)

    df = df.reindex(columns=colonnes_features, fill_value=0)

    df[colonnes_numeriques] = scaler.transform(df[colonnes_numeriques])

    prediction = modele.predict(df)[0]
    probabilite = modele.predict_proba(df)[0][1]

    pourcentage = round(float(probabilite) * 100, 2)
    if pourcentage >= 50:
        niveau_risque = "eleve"
    elif pourcentage >= 20:
        niveau_risque = "modere"
    else:
        niveau_risque = "faible"

    return {
        "stroke_risque": int(prediction),
        "probabilite": round(float(probabilite), 4),
        "niveau_risque": niveau_risque
    }
