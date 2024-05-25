    registerbutton.addEventListener('click', function(ev){

        // Añadir spinner y deshabilitar el botón
        registerbutton.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Procesando rostro...';
        registerbutton.disabled = true;

        context.drawImage(video, 0, 0, 640, 480);
        // Cambia 'image/png' a 'image/jpeg' y especifica la calidad (por ejemplo, 0.9 para el 90% de calidad)
        var data = tempCanvas.toDataURL('image/jpeg', 0.9);
            
        console.log(data);
        fetch('/procesar_frame/', {
            method: 'POST',
            headers: {
                  'Content-Type': 'application/json',
                  /*'X-CSRFToken': document.cookie.split(';').filter(function(item) {
                  return item.trim().startsWith('csrftoken=');
                 })[0].split('=')[1]*/
            },
            body: JSON.stringify({ imagen: data })
        }).then(response => response.json())
        .then(data => {
            console.log(data);
            // Aquí puedes manejar la respuesta del servidor, por ejemplo, mostrando un mensaje al usuario.
            window.location.href = '/register/';
        })
        .catch((error) => {
            console.error('Error:', error);
            // Manejar los errores de la solicitud aquí
        });

        //window.location.href = '/register/';
        ev.preventDefault();
    }, false);