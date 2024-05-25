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
