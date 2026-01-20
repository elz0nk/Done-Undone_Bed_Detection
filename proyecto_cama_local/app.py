from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from pathlib import Path

app = Flask(__name__)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    raise RuntimeError("ERROR: Cannot open camera")
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "cama_cnn.keras"
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH} (resolved from {BASE_DIR})"
    )

model = load_model(str(MODEL_PATH))
infer_enabled = True

def preprocess(frame):
    img = cv2.resize(frame, (224,224))
    img = img.astype("float") / 255.0
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    return img

def gen_frames():
    global model
    while True:
        success, frame = cap.read()
        if not success:
            print("WARNING: Failed to read frame from camera")
            continue
        print("Frame shape:", frame.shape)
        if infer_enabled:
            pred = model.predict(preprocess(frame))[0][0]
            label = "HECHA" if pred < 0.5 else "NO_HECHA"

            cv2.putText(frame, f"Cama: {label}", (30,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error al codificar frame")
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    state = request.form['state']
    ret, frame = cap.read()
    if not ret:
        return jsonify({"status":"error"})

    os.makedirs(f"dataset/{state}", exist_ok=True)
    filename = f"{state}_{len(os.listdir(f'dataset/{state}'))}.jpg"
    cv2.imwrite(f"dataset/{state}/{filename}", frame)
    return jsonify({"status":"ok", "file": filename})

@app.route('/retrain', methods=['POST'])
def retrain():
    os.system("python train_cnn.py")
    global model
    model = load_model(str(MODEL_PATH))
    return jsonify({"status":"retrained"})

@app.route('/toggle_inference', methods=['POST'])
def toggle_inference():
    global infer_enabled
    infer_enabled = not infer_enabled
    return jsonify({"enabled": infer_enabled})

if __name__ == "__main__":
    app.run(debug=True)
