from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_accueil():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_patient_a_risque():
    patient = {
        "gender": "Male", "age": 67, "hypertension": 0,
        "heart_disease": 1, "ever_married": "Yes", "work_type": "Private",
        "Residence_type": "Urban", "avg_glucose_level": 228.69,
        "bmi": 36.6, "smoking_status": "formerly smoked"
    }
    response = client.post("/predict", json=patient)
    assert response.status_code == 200
    assert "stroke_risque" in response.json()

def test_predict_donnee_invalide():
    patient = {
        "gender": "Male", "age": -5, "hypertension": 0,
        "heart_disease": 1, "ever_married": "Yes", "work_type": "Private",
        "Residence_type": "Urban", "avg_glucose_level": 228.69,
        "bmi": 36.6, "smoking_status": "formerly smoked"
    }
    response = client.post("/predict", json=patient)
    assert response.status_code == 422
