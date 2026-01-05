# This file sets up a Flask web server for the AI microservice.
# It loads pre-trained machine learning models and provides an API endpoint for crop and fertilizer predictions.

# Import Flask for creating the web server
from flask import Flask, request, jsonify
# Import numpy for numerical operations and array handling
import numpy as np
# Import joblib for loading saved machine learning models
import joblib
# Import os for file path operations
import os

# Create a Flask application instance
app = Flask(__name__)

# Define the base directory as the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the models directory path
MODEL_DIR = os.path.join(BASE_DIR, "Models")

# Define paths to all the model and encoder files
MODEL_PATH = os.path.join(MODEL_DIR, "skyacre_fertilizer_model.pkl")
ENCODER_DISTRICT_PATH = os.path.join(MODEL_DIR, "encoder_district.pkl")
ENCODER_SOIL_PATH = os.path.join(MODEL_DIR, "encoder_soil.pkl")
MAP_CROPS_PATH = os.path.join(MODEL_DIR, "map_crops.pkl")
MAP_FERT_PATH = os.path.join(MODEL_DIR, "map_fertilizers.pkl")

# Print the models directory for debugging
print("Loading models from:", MODEL_DIR)

# Load all required models, encoders, and mappings
try:
    dt_model = joblib.load(MODEL_PATH)  # Load the decision tree model
    encoder_district = joblib.load(ENCODER_DISTRICT_PATH)  # Load district encoder
    encoder_soil = joblib.load(ENCODER_SOIL_PATH)  # Load soil color encoder
    map_crops = joblib.load(MAP_CROPS_PATH)  # Load crop name mappings
    map_fertilizers = joblib.load(MAP_FERT_PATH)  # Load fertilizer name mappings
    print("All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    raise e  # Re-raise the exception if loading fails


# Define the root route that returns a status message
@app.route('/')
def index():
    return "SkyAcre Fertilizer & Crop Prediction API is running!"


# Define the prediction route that accepts POST requests
@app.route('/farmer/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.json
        print(data)  # Print data for debugging

        # List of required features for prediction
        required_features = [
            'District', 'Soil_color', 'Nitrogen', 'Phosphorus',
            'Potassium', 'pH', 'Rainfall', 'Temperature'
        ]

        # Check if all required features are present in the data
        if not all(f in data for f in required_features):
            return jsonify({"error": "Missing features"}), 400

        # Encode categorical inputs (District and Soil_color) to numerical values
        district_encoded = int(encoder_district.transform([data['District']]))
        soil_encoded = int(encoder_soil.transform([data['Soil_color']]))

        # Build the feature array for the model input
        features = np.array([
            district_encoded,
            soil_encoded,
            data['Nitrogen'],
            data['Phosphorus'],
            data['Potassium'],
            data['pH'],
            data['Rainfall'],
            data['Temperature']
        ]).reshape(1, -1)  # Reshape to 2D array for model input

        # Make prediction using the loaded model
        pred_numeric = dt_model.predict(features)[0]

        # Map the numerical predictions back to crop and fertilizer names
        predicted_crop = next(i[0] for i in map_crops if int(i[1]) == pred_numeric[0])
        predicted_fertilizer = next(i[0] for i in map_fertilizers if int(i[1]) == pred_numeric[1])

        # Return the predictions as JSON
        return jsonify({
            "predicted_crop": predicted_crop,
            "predicted_fertilizer": predicted_fertilizer
        })

    except Exception as e:
        # Return error message if something goes wrong
        return jsonify({"error": str(e)}), 500


# Run the Flask app if this script is executed directly
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)  # Run on localhost port 5000 with debug mode
