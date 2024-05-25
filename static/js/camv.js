    
    loginbutton.addEventListener('click', async function(ev){

        // Añadir spinner y deshabilitar el botón
        loginbutton.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Procesando rostro...';
        loginbutton.disabled = true;

        context.drawImage(video, 0, 0, 640, 480);
        var data = tempCanvas.toDataURL('image/jpeg', 0.9);
        var csrftoken = '{{ csrf_token }}';

        console.log(data);
    
        try {
            // Primero, esperamos a que se complete la llamada a '/procesar_frame/'
            let response = await fetch('/procesar_frame/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ imagen: data })
            });
            let processData = await response.json();
            console.log(processData);
            if (processData.redirect_url) {
                window.location.href = processData.redirect_url;
                return; // Importante para no continuar ejecutando el código siguiente
            }
        
            // Una vez completado, procedemos con la llamada a '/validar_face/'
            window.location.href = '/validar_face/';
        
        
        
        } catch (error) {
            console.error('Error:', error);
        }      
}, false);