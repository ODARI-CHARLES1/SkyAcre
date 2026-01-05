from flask import Flask, request, jsonify
import numpy as np
import joblib
import os

app = Flask(__name__)

# ✅ Always load models relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "Models")

MODEL_PATH = os.path.join(MODEL_DIR, "skyacre_fertilizer_model.pkl")
ENCODER_DISTRICT_PATH = os.path.join(MODEL_DIR, "encoder_district.pkl")
ENCODER_SOIL_PATH = os.path.join(MODEL_DIR, "encoder_soil.pkl")
MAP_CROPS_PATH = os.path.join(MODEL_DIR, "map_crops.pkl")
MAP_FERT_PATH = os.path.join(MODEL_DIR, "map_fertilizers.pkl")

# ✅ Debug: check if paths exist
print("Loading models from:", MODEL_DIR)

# ✅ Load all required models/encoders/maps
try:
    dt_model = joblib.load(MODEL_PATH)
    encoder_district = joblib.load(ENCODER_DISTRICT_PATH)
    encoder_soil = joblib.load(ENCODER_SOIL_PATH)
    map_crops = joblib.load(MAP_CROPS_PATH)
    map_fertilizers = joblib.load(MAP_FERT_PATH)
    print("All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    raise e


@app.route('/')
def index():
    return "SkyAcre Fertilizer & Crop Prediction API is running!"


@app.route('/farmer/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        required_features = [
            'District', 'Soil_color', 'Nitrogen', 'Phosphorus',
            'Potassium', 'pH', 'Rainfall', 'Temperature'
        ]

        # ✅ Check for missing fields
        if not all(f in data for f in required_features):
            return jsonify({"error": "Missing features"}), 400

        # ✅ Encode categorical inputs
        district_encoded = int(encoder_district.transform([data['District']]))
        soil_encoded = int(encoder_soil.transform([data['Soil_color']]))

        # ✅ Build feature array
        features = np.array([
            district_encoded,
            soil_encoded,
            data['Nitrogen'],
            data['Phosphorus'],
            data['Potassium'],
            data['pH'],
            data['Rainfall'],
            data['Temperature']
        ]).reshape(1, -1)

        # ✅ Predict crop & fertilizer
        pred_numeric = dt_model.predict(features)[0]

        predicted_crop = next(i[0] for i in map_crops if int(i[1]) == pred_numeric[0])
        predicted_fertilizer = next(i[0] for i in map_fertilizers if int(i[1]) == pred_numeric[1])

        return jsonify({
            "predicted_crop": predicted_crop,
            "predicted_fertilizer": predicted_fertilizer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
