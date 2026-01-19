from flask import Flask, render_template, request, jsonify
import numpy as np
import gdown
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from io import BytesIO

app = Flask(__name__)

MODEL_DIR = "model"
MODEL_FILENAME = "cama_cnn.keras"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

FILE_ID = "1xDqy3KG9qveOq4gcDZ0sJOv1UIwV5uQU"

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_DIR, exist_ok=True)
        gdown.download(
                url=f"https://drive.google.com/uc?id={FILE_ID}",
                output=MODEL_PATH,
                quiet=False
        )

download_model()
model = load_model(MODEL_PATH)

def preprocess(image):
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return image

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("frame")
    if not file:
        return jsonify({"error": "No image received"}), 400

    image = Image.open(BytesIO(file.read())).convert("RGB")
    img = preprocess(image)

    pred = model.predict(img)[0][0]
    label = "HECHA" if pred < 0.5 else "NO_HECHA"

    return jsonify({
        "prediction": label,
        "confidence": float(pred)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
