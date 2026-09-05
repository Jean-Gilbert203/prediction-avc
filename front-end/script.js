const champAge = document.querySelector('input[name="age"]');
const champWorkType = document.getElementById("work-type");

champAge.addEventListener("input", function () {
    const age = parseFloat(champAge.value);

    if (age < 15) {
        champWorkType.value = "children";
        for (const option of champWorkType.options) {
            if (option.value !== "children") {
                option.disabled = true;
            }
        }
    } else {
        for (const option of champWorkType.options) {
            option.disabled = false;
        }
    }
});

document.getElementById("formulaire").addEventListener("submit", async function (e) {
    e.preventDefault();

    const donnees = Object.fromEntries(new FormData(e.target));
    donnees.age = parseFloat(donnees.age);
    donnees.hypertension = parseInt(donnees.hypertension);
    donnees.heart_disease = parseInt(donnees.heart_disease);
    donnees.avg_glucose_level = parseFloat(donnees.avg_glucose_level);
    donnees.bmi = parseFloat(donnees.bmi);

    const reponse = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(donnees)
    });

    const resultatDiv = document.getElementById("resultat");

    if (!reponse.ok) {
        resultatDiv.className = "risque";
        resultatDiv.textContent = "Erreur : données invalides.";
        return;
    }

    const resultat = await reponse.json();
    const pourcentage = Math.round(resultat.probabilite * 100);

    const messages = {
        eleve: `Risque élevé d'AVC (probabilité : ${pourcentage}%) - consultez un professionnel de santé`,
        modere: `Risque modéré d'AVC (probabilité : ${pourcentage}%) - surveillance recommandée`,
        faible: `Risque faible d'AVC (probabilité : ${pourcentage}%)`
    };
    const classes = {
        eleve: "risque",
        modere: "risque-modere",
        faible: "sans-risque"
    };

    resultatDiv.className = classes[resultat.niveau_risque];
    resultatDiv.textContent = messages[resultat.niveau_risque];
});
