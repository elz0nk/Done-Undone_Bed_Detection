function isMobile() {
    return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

if (isMobile()) {
    const video = document.getElementById("camera");

    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(stream => {
                video.srcObject = stream;
                video.play();
            })
            .catch(err => {
                console.error("Error al acceder a la cámara:", err);
                document.getElementById("status").innerText = "No se puede acceder a la cámara";
            });
    }

    startCamera();

    function capture(state) {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);

        canvas.toBlob(blob => {
            const formData = new FormData();
            formData.append("frame", blob);
            formData.append("state", state);

            fetch("/capture_mobile", { method: "POST", body: formData })
                .then(r => r.json())
                .then(d => {
                    document.getElementById("status").innerText =
                        d.file ? `Imagen guardada: ${d.file}` : "Imagen guardada";
                })
                .catch(err => console.error("Error al enviar la imagen:", err));
        }, "image/jpeg");
    }

} else {
    function capture(state){
        fetch('/capture', {
            method: 'POST',
            headers: {'Content-Type':'application/x-www-form-urlencoded'},
            body: `state=${state}`
        })
        .then(r => r.json())
        .then(d => {
            document.getElementById("status").innerText =
                `Imagen guardada: ${d.file}`;
        });
    }
}
function retrain(){
    document.getElementById("status").innerText = "Reentrenando modelo...";
    fetch('/retrain', {method:'POST'})
    .then(r => r.json())
    .then(d => {
        document.getElementById("status").innerText =
            "Modelo reentrenado correctamente";
    });
}

function toggleInference(){
    fetch('/toggle_inference', {method:'POST'})
    .then(r => r.json())
    .then(d => {
        document.getElementById("status").innerText =
            d.enabled ? "Detección ACTIVADA" : "Detección DESACTIVADA";
    });
}
