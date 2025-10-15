// Prévisualisation de l'image sélectionnée
function loadImg(event) {
    const file = event.target.files[0];
    if (file) {
        const imageUrl = URL.createObjectURL(file);
        $('#imagePreview').attr('src', imageUrl);
        console.log('✅ Image chargée pour prévisualisation');
    }
}

// Upload et détection avec gestion des paramètres
$('#upload').click(function() {
    const fileInput = $('#fileInput')[0];
    
    // Vérifier qu'un fichier est sélectionné
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('⚠️ Veuillez sélectionner une image');
        return;
    }
    
    // Créer le FormData
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    // Ajouter les paramètres de détection
    const threshold = $('#threshold').val() || 0.5;
    const modelName = $('#model_name').val() || '';
    
    formData.append('threshold', threshold);
    if (modelName) {
        formData.append('model_name', modelName);
    }
    
    console.log('📤 Upload en cours...', {
        file: fileInput.files[0].name,
        threshold: threshold,
        model: modelName
    });
    
    // Afficher un loader (optionnel)
    $('#upload').prop('disabled', true).text('⏳ Traitement...');
    
    // Requête AJAX
    $.ajax({
        url: '/imagerie/upload', // ✅ Route Flask corrigée
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            console.log('✅ Détection réussie:', response);
            
            // Afficher l'image traitée avec un timestamp pour éviter le cache
            const timestamp = new Date().getTime();
            $('#imagePreview').attr('src', response.url + '?t=' + timestamp);
            
            // Réactiver le bouton
            $('#upload').prop('disabled', false).text('🔍 Détecter');
        },
        error: function(xhr, status, error) {
            console.error('❌ Erreur:', error);
            
            let errorMsg = 'Erreur lors du traitement';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            
            alert('❌ ' + errorMsg);
            $('#upload').prop('disabled', false).text('🔍 Détecter');
        }
    });
});

// Associer loadImg au changement de fichier
$('#fileInput').change(loadImg);