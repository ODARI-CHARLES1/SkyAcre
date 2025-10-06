# AI Models Overview

## Purpose

The AI models in SkyAcre are designed to provide intelligent recommendations for crop selection and fertilizer usage in agricultural settings. The system leverages machine learning to analyze environmental and soil parameters to suggest optimal crops and fertilizers, helping farmers make data-driven decisions to improve yield and sustainability.

## Key Features

- **Multi-output Prediction**: Simultaneously predicts both suitable crops and fertilizers based on input parameters.
- **Environmental Awareness**: Considers factors like district, soil color, nutrient levels (Nitrogen, Phosphorus, Potassium), pH, rainfall, and temperature.
- **Real-time Recommendations**: Provides instant predictions through a REST API for integration with web applications.

## Model Architecture

### Algorithm
- **Decision Tree Classifier**: Uses scikit-learn's DecisionTreeClassifier for interpretable and efficient predictions.
- **Multi-output Support**: Trained to predict both crop and fertilizer simultaneously.

### Input Features
- District (categorical, encoded)
- Soil_color (categorical, encoded)
- Nitrogen (numeric)
- Phosphorus (numeric)
- Potassium (numeric)
- pH (numeric)
- Rainfall (numeric)
- Temperature (numeric)

### Output
- Predicted Crop (string)
- Predicted Fertilizer (string)

## Data Source

The model is trained on the "Crop and Fertilizer Dataset for Western Maharashtra" from Kaggle, containing agricultural data specific to the Western Maharashtra region.

## Deployment

The trained model is deployed as a Flask REST API with the following endpoint:

- **POST /farmer/predict**
  - Accepts JSON payload with required features
  - Returns predicted crop and fertilizer recommendations

## Model Files

- `skyacre_fertilizer_model.pkl`: Trained Decision Tree model
- `encoder_district.pkl`: Label encoder for district categories
- `encoder_soil.pkl`: Label encoder for soil color categories
- `map_crops.pkl`: Mapping from numeric labels to crop names
- `map_fertilizers.pkl`: Mapping from numeric labels to fertilizer names

## Usage Context

This AI system is integrated into the SkyAcre platform to provide farmers with personalized agricultural recommendations, supporting precision farming practices and sustainable agriculture.