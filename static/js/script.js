const video = document.getElementById("camera");
const statusText = document.getElementById("status");

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.play();
    })
    .catch(() => {
        statusText.innerText = "No se pudo acceder a la cámara";
    });

function captureAndPredict() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append("frame", blob);

        fetch("/predict", {
            method: "POST",
            body: formData
        })
        .then(r => r.json())
        .then(d => {
            statusText.innerText = `Resultado: ${d.prediction}`;
        })
        .catch(() => {
            statusText.innerText = "Error en la predicción";
        });
    }, "image/jpeg");
}
