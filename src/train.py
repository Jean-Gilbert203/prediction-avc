import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, recall_score
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("sqlite:///mlflow.db")

def charger_donnees(chemin_csv):
    nosPatients = pd.read_csv(chemin_csv)
    nosPatients = nosPatients.drop(columns=["id"])
    return nosPatients


def nettoyer_donnees(nosPatients):
    nosPatients['bmi'] = pd.to_numeric(nosPatients['bmi'], errors='coerce')
    medianeBmi = nosPatients['bmi'].median()
    nosPatients['bmi'] = nosPatients['bmi'].fillna(medianeBmi)
    nosPatients = nosPatients[nosPatients['gender'] != 'Other']
    return nosPatients


def encoder_donnees(nosPatients):
    colonnesCategorielles = ['gender', 'ever_married', 'work_type',
                              'Residence_type', 'smoking_status']
    dataset = pd.get_dummies(nosPatients, columns=colonnesCategorielles, drop_first=True)
    return dataset

def separer_donnees(dataset):
    X = dataset.drop(columns=['stroke'])
    y = dataset['stroke']

    X_APPRENTISSAGE, X_VALIDATION, Y_APPRENTISSAGE, Y_VALIDATION = train_test_split(
        X, y, test_size=0.2, random_state=0, stratify=y
    )
    return X, X_APPRENTISSAGE, X_VALIDATION, Y_APPRENTISSAGE, Y_VALIDATION


def standardiser_donnees(X_APPRENTISSAGE, X_VALIDATION, colonnesNumeriques):
    scaler = StandardScaler()

    X_APPRENTISSAGE_STD = X_APPRENTISSAGE.copy()
    X_VALIDATION_STD = X_VALIDATION.copy()

    X_APPRENTISSAGE_STD[colonnesNumeriques] = scaler.fit_transform(X_APPRENTISSAGE[colonnesNumeriques])
    X_VALIDATION_STD[colonnesNumeriques] = scaler.transform(X_VALIDATION[colonnesNumeriques])

    return X_APPRENTISSAGE_STD, X_VALIDATION_STD, scaler

def entrainer_modele(X_APPRENTISSAGE_STD, Y_APPRENTISSAGE):
    modele = LogisticRegression(max_iter=1000, class_weight='balanced')
    modele.fit(X_APPRENTISSAGE_STD, Y_APPRENTISSAGE)
    return modele


def evaluer_modele(modele, X_VALIDATION_STD, Y_VALIDATION):
    predictions = modele.predict(X_VALIDATION_STD)
    probabilites = modele.predict_proba(X_VALIDATION_STD)[:, 1]

    print(classification_report(Y_VALIDATION, predictions, target_names=["Pas d'AVC", "AVC"]))
    print("ROC-AUC :", round(roc_auc_score(Y_VALIDATION, probabilites), 4))
    
def sauvegarder_artefact(modele, scaler, colonnesNumeriques, colonnesFeatures, chemin_sortie):
    os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)

    artefact = {
        "modele": modele,
        "scaler": scaler,
        "colonnes_numeriques": colonnesNumeriques,
        "colonnes_features": colonnesFeatures,
    }

    joblib.dump(artefact, chemin_sortie)
    print("\nArtefact sauvegarde dans :", chemin_sortie)


if __name__ == "__main__":
    nosPatients = charger_donnees("data/healthcare-dataset-stroke-data.csv")
    print("Donnees chargees :", nosPatients.shape)

    nosPatients = nettoyer_donnees(nosPatients)
    print("Valeurs manquantes après nettoyage :")
    print(nosPatients.isnull().sum())

    dataset = encoder_donnees(nosPatients)
    print("Donnees encodees :", dataset.shape)
    print("Colonnes :", dataset.columns.values)
    
    colonnesNumeriques = ['age', 'avg_glucose_level', 'bmi']

    X, X_APPRENTISSAGE, X_VALIDATION, Y_APPRENTISSAGE, Y_VALIDATION = separer_donnees(dataset)
    print("\nTaille apprentissage :", X_APPRENTISSAGE.shape)
    print("Taille validation :", X_VALIDATION.shape)

    X_APPRENTISSAGE_STD, X_VALIDATION_STD, scaler = standardiser_donnees(
        X_APPRENTISSAGE, X_VALIDATION, colonnesNumeriques
    )
    print("Standardisation terminee")
    
    mlflow.set_experiment("prediction-avc")
    
    with mlflow.start_run():
        mlflow.log_param("modele", "LogisticRegression")
        mlflow.log_param("class_weight", "balanced")
        mlflow.log_param("max_iter", 1000)
        
        modele = entrainer_modele(X_APPRENTISSAGE_STD, Y_APPRENTISSAGE)
        print("\nModele entraine")
        
        predictions = modele.predict(X_VALIDATION_STD)
        probabilites = modele.predict_proba(X_VALIDATION_STD)[:, 1]

        print(classification_report(Y_VALIDATION, predictions, target_names=["Pas d'AVC", "AVC"]))
        recall = recall_score(Y_VALIDATION, predictions)
        rocauc = roc_auc_score(Y_VALIDATION, probabilites)
        print("ROC-AUC :", round(rocauc, 4))

        mlflow.log_metric("recall", recall)
        mlflow.log_metric("roc_auc", rocauc)
        mlflow.sklearn.log_model(modele, "modele_avc")
    
    sauvegarder_artefact(
        modele, scaler, colonnesNumeriques, list(X.columns),
        "modele/modele_avc.pkl"
    )