
# This file sets up a Flask web server for the AI microservice.
# It loads pre-trained machine learning models and provides API endpoints.

import os
import io

# Set Keras backend
os.environ["KERAS_BACKEND"] = "tensorflow"

from flask import Flask, request, jsonify
import numpy as np
import joblib
import keras
from PIL import Image

# Create a Flask application instance
app = Flask(__name__)

# --- Fertilizer & Crop Prediction Model Loading ---

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "Models")
MODEL_PATH = os.path.join(MODEL_DIR, "skyacre_fertilizer_model.pkl")
ENCODER_DISTRICT_PATH = os.path.join(MODEL_DIR, "encoder_district.pkl")
ENCODER_SOIL_PATH = os.path.join(MODEL_DIR, "encoder_soil.pkl")
MAP_CROPS_PATH = os.path.join(MODEL_DIR, "map_crops.pkl")
MAP_FERT_PATH = os.path.join(MODEL_DIR, "map_fertilizers.pkl")

print("Loading fertilizer and crop models...")
try:
    dt_model = joblib.load(MODEL_PATH)
    encoder_district = joblib.load(ENCODER_DISTRICT_PATH)
    encoder_soil = joblib.load(ENCODER_SOIL_PATH)
    map_crops = joblib.load(MAP_CROPS_PATH)
    map_fertilizers = joblib.load(MAP_FERT_PATH)
    print("Fertilizer and crop models loaded successfully!")
except Exception as e:
    print(f"Error loading fertilizer and crop models: {e}")
    # We don't raise the exception to allow the other model to load
    dt_model = None

# --- Cow Disease Classification Model Loading ---

COW_DISEASE_REPO_ID = "Storm00212/SkyAcre"
COW_DISEASE_CLASS_LABELS = {0: 'foot-and-mouth', 1: 'lumpy', 2: 'healthy'}
cow_disease_model = None

print(f"Loading cow disease model from Hugging Face repo: {COW_DISEASE_REPO_ID}...")
try:
    hf_path = f"hf://{COW_DISEASE_REPO_ID}"
    cow_disease_model = keras.saving.load_.model(hf_path)
    print("Cow disease model loaded successfully!")
    cow_disease_model.summary()
except Exception as e:
    print(f"Error loading cow disease model: {e}")
    print("Please ensure `huggingface_hub` is installed and you are logged in if the repo is private.")


# --- API Routes ---

@app.route('/')
def index():
    return "SkyAcre AI Prediction API is running!"


@app.route('/farmer/predict', methods=['POST'])
def predict_fertilizer_crop():
    if not dt_model:
        return jsonify({"error": "Fertilizer/crop model is not available."}), 503
        
    try:
        data = request.json
        required_features = [
            'District', 'Soil_color', 'Nitrogen', 'Phosphorus',
            'Potassium', 'pH', 'Rainfall', 'Temperature'
        ]

        if not all(f in data for f in required_features):
            return jsonify({"error": "Missing features for fertilizer/crop prediction"}), 400

        district_encoded = int(encoder_district.transform([data['District']]))
        soil_encoded = int(encoder_soil.transform([data['Soil_color']]))

        features = np.array([
            district_encoded, soil_encoded, data['Nitrogen'], data['Phosphorus'],
            data['Potassium'], data['pH'], data['Rainfall'], data['Temperature']
        ]).reshape(1, -1)

        pred_numeric = dt_model.predict(features)[0]

        predicted_crop = next(i[0] for i in map_crops if int(i[1]) == pred_numeric[0])
        predicted_fertilizer = next(i[0] for i in map_fertilizers if int(i[1]) == pred_numeric[1])

        return jsonify({
            "predicted_crop": predicted_crop,
            "predicted_fertilizer": predicted_fertilizer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def preprocess_image(image_bytes, target_size=(224, 224)):
    """Preprocesses a single image for the cow disease model."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalize to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


@app.route('/predict/cow-disease', methods=['POST'])
def predict_cow_disease():
    if not cow_disease_model:
        return jsonify({"error": "Cow disease model is not available."}), 503

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        # Make prediction
        predictions = cow_disease_model.predict(processed_image)
        
        # Get the class with the highest probability
        predicted_class_index = np.argmax(predictions[0])
        predicted_class_name = COW_DISEASE_CLASS_LABELS[predicted_class_index]
        confidence = float(predictions[0][predicted_class_index])
        
        return jsonify({
            "predicted_class": predicted_class_name,
            "confidence": f"{confidence:.4f}",
            "all_predictions": {label: float(conf) for label, conf in zip(COW_DISEASE_CLASS_LABELS.values(), predictions[0])}
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
