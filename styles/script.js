document.addEventListener("DOMContentLoaded", function() {
    const inputsContainer = document.getElementById('inputs-container');
    const nbVarsInput = document.getElementById('nb_vars');
    const cancelBtn = document.getElementById('cancel-btn');
    const predictBtn = document.getElementById('predict-btn');

    // Met à jour les champs de variables selon le nombre sélectionné
    window.updateInputs = function(nb) {
        nb = parseInt(nb);
        inputsContainer.innerHTML = ''; // vide

        for (let i = 1; i <= nb; i++) {
            const div = document.createElement('div');
            div.className = 'form-line';

            const label = document.createElement('label');
            label.htmlFor = 'valeur' + i;
            label.textContent = 'valeur ' + i;

            const input = document.createElement('input');
            input.id = 'valeur' + i;
            input.className = 'form-input';
            input.placeholder = '...................';

            div.appendChild(label);
            div.appendChild(input);
            inputsContainer.appendChild(div);
        }
    }

    // Initialiser avec 3 variables
    updateInputs(nbVarsInput.value);

    cancelBtn.addEventListener('click', function() {
        if (confirm("Êtes-vous sûr de vouloir annuler la prédiction ?")) {
            const inputs = inputsContainer.querySelectorAll('input');
            inputs.forEach(input => input.value = '');
            if(nbVarsInput) nbVarsInput.value = 3;
            updateInputs(3);
        }
    });

    predictBtn.addEventListener('click', function() {
        if (confirm("Êtes-vous sûr de vouloir lancer la prédiction ?")) {
            alert("Prédiction en cours...");
            // Ici, tu peux déclencher la logique Python via API ou Streamlit (à faire côté backend)
        }
    });

    // Gestion simple dropdown profil (optionnel si besoin, déjà en CSS)
});



