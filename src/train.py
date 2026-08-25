import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


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
    print(X_APPRENTISSAGE_STD[colonnesNumeriques].describe().loc[['mean', 'std']].round(4))