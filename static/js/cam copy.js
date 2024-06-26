var video = document.getElementById('video');
// Crea un canvas temporal en memoria
var tempCanvas = document.createElement('canvas');
tempCanvas.width = 640;
tempCanvas.height = 480;
var context = tempCanvas.getContext('2d');
    
    
    //navigator = window.navigator;



    /*navigator.getUserMedia = ( navigator.getUserMedia ||
                               navigator.webkitGetUserMedia ||
                               navigator.mozGetUserMedia ||
                               navigator.msGetUserMedia);
    */
    //startbutton.addEventListener('click', function(ev){
    /*   if (navigator.getUserMedia) {
            navigator.getUserMedia({video: true}, function(stream) {                    // COMPATIBILIDAD CON NAVEGADORES ANTIGUOS
                video.srcObject = stream;
                video.play();
            }, function(error) {
                console.log("Error: ", error);
            });
        }*/
    //    ev.preventDefault();
    //}, false);



    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Usar navigator.mediaDevices.getUserMedia según las prácticas modernas
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video.srcObject = stream;
            video.play();
        }).catch(function(err) {
            console.log("Error: ", err);
        });
    }

    
    loginbutton.addEventListener('click', async function(ev){
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
        
        // Una vez completado, procedemos con la llamada a '/login/'
        window.location.href = '/login1/';
        
        
        
    } catch (error) {
        console.error('Error:', error);
    }      
}, false);
   
   

    registerbutton.addEventListener('click', function(ev){
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