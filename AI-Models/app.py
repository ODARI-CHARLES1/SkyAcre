
# This file sets up a Flask web server for the AI microservice.
# It loads pre-trained machine learning models and provides API endpoints.

import os
import io

# Set Keras backend
os.environ["KERAS_BACKEND"] = "tensorflow"

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import keras
from PIL import Image

# Create a Flask application instance
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

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

COW_DISEASE_REPO_ID = "Storm00212/SkyAcre_cow_model"
COW_DISEASE_CLASS_LABELS = {0: 'foot-and-mouth', 1: 'lumpy', 2: 'healthy'}
cow_disease_model = None

print(f"Loading cow disease model from Hugging Face repo: {COW_DISEASE_REPO_ID}...")
try:
    hf_path = f"hf://{COW_DISEASE_REPO_ID}"
    cow_disease_model = keras.saving.load_model(hf_path)
    print("Cow disease model loaded successfully from HuggingFace!")
    cow_disease_model.summary()
except Exception as e:
    print(f"Error loading from HuggingFace: {e}")
    print("Attempting to load from local model file...")
    
    # Try loading from local file as fallback
    local_model_path = os.path.join(BASE_DIR, "best_model.keras")
    if os.path.exists(local_model_path):
        try:
            cow_disease_model = keras.saving.load_model(local_model_path)
            print("Cow disease model loaded successfully from local file!")
            cow_disease_model.summary()
        except Exception as e2:
            print(f"Error loading local model: {e2}")
    else:
        print(f"Local model file not found at: {local_model_path}")

if cow_disease_model is None:
    print("WARNING: Cow disease model is not available. /predict/cow-disease endpoint will return 503.")


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
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img = img.resize(target_size)
        img_array = np.array(img)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array
    except Exception as e:
        raise ValueError(f"Invalid or corrupt image: {str(e)}")


@app.route('/predict/cow-disease', methods=['POST'])
def predict_cow_disease():
    if not cow_disease_model:
        return jsonify({"error": "Cow disease model is not available."}), 503

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        return jsonify({
            "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        }), 400

    # Read file content for size validation
    image_bytes = file.read()
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    if len(image_bytes) > max_size:
        return jsonify({
            "error": f"File too large. Maximum size is 10MB, got {len(image_bytes) / (1024*1024):.2f}MB"
        }), 400

    try:
        processed_image = preprocess_image(image_bytes)
        
        # Make prediction
        predictions = cow_disease_model.predict(processed_image)
        
        # Get the class with the highest probability
        predicted_class_index = np.argmax(predictions[0])
        predicted_class_name = COW_DISEASE_CLASS_LABELS[predicted_class_index]
        confidence = float(predictions[0][predicted_class_index])
        
        return jsonify({
            "predicted_class": predicted_class_name,
            "confidence": round(confidence, 4),
            "all_predictions": {label: float(conf) for label, conf in zip(COW_DISEASE_CLASS_LABELS.values(), predictions[0])}
        })

    except ValueError as e:
        # Handle invalid/corrupt image errors
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
