import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseModel, Field
from fastapi import HTTPException
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_avc")

app = FastAPI(title="API Prediction AVC")

app.mount("/static", StaticFiles(directory="front-end"), name="static")

artefact = joblib.load("modele/modele_avc.pkl")
modele = artefact["modele"]
scaler = artefact["scaler"]
colonnes_numeriques = artefact["colonnes_numeriques"]
colonnes_features = artefact["colonnes_features"]


@app.get("/")
def accueil():
    return FileResponse("front-end/index.html")



@app.get("/health")
def health():
    return {"status": "ok"}

class Patient(BaseModel):
    gender: str = Field(..., pattern="^(Male|Female)$")
    age: float = Field(..., ge=0, le=120)
    hypertension: int = Field(..., ge=0, le=1)
    heart_disease: int = Field(..., ge=0, le=1)
    ever_married: str = Field(..., pattern="^(Yes|No)$")
    work_type: str
    Residence_type: str = Field(..., pattern="^(Urban|Rural)$")
    avg_glucose_level: float = Field(..., gt=0)
    bmi: float = Field(..., gt=0)
    smoking_status: str



@app.post("/predict")
def predict(patient: Patient):
    try:
        logger.info(f"Requete recue : age={patient.age}, hypertension={patient.hypertension}")
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
        logger.info(f"Prediction : stroke_risque={int(prediction)}, probabilite={round(float(probabilite),4)}")
        return {
            "stroke_risque": int(prediction),
            "probabilite": round(float(probabilite), 4),
            "niveau_risque": niveau_risque
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prediction : {str(e)}")

