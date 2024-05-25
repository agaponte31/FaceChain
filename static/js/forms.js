function startProcess() {
    // Desactivar el botón para prevenir múltiples envíos
    $('#processButton').attr('disabled', true).html('<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Loading...');

    // Recoger los datos del formulario
    var formData = $('#query_form').serialize();

    // Enviar solicitud AJAX
    $.ajax({
        url: '{{ url }}',
        type: 'POST',
        data: formData,
        success: function(response) {
            alert('Proceso completado!');
            $('#processButton').html('Enviar').attr('disabled', false);
        },
        error: function() {
            alert('Error en el proceso');
            $('#processButton').html('Enviar').attr('disabled', false);
        }
    });
}
