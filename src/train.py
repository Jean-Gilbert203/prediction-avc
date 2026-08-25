import pandas as pd


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


if __name__ == "__main__":
    nosPatients = charger_donnees("data/healthcare-dataset-stroke-data.csv")
    print("Donnees chargees :", nosPatients.shape)

    nosPatients = nettoyer_donnees(nosPatients)
    print("Valeurs manquantes après nettoyage :")
    print(nosPatients.isnull().sum())

    dataset = encoder_donnees(nosPatients)
    print("Donnees encodees :", dataset.shape)
    print("Colonnes :", dataset.columns.values)