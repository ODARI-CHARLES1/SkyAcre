# AI Models Workflow Description

## Overview
This folder contains the AI models and code for the SkyAcre fertilizer and crop recommendation system. The system uses machine learning to predict suitable crops and fertilizers based on environmental and soil parameters.

## Workflow

### 1. Data Acquisition
- Dataset: "Crop and Fertilizer Dataset for Western Maharashtra" from Kaggle
- Source: https://www.kaggle.com/datasets/sanchitagholap/crop-and-fertilizer-dataset-for-westernmaharashtra
- Raw data is stored in `Data/Raw/Crop and fertilizer dataset.csv`
- Processed data is stored in `Data/Processed/Crop and fertilizer dataset.csv`

### 2. Data Preprocessing
- Remove unnecessary columns (e.g., 'Link')
- Handle missing values and duplicates
- Encode categorical variables:
  - District_Name → encoded using LabelEncoder
  - Soil_color → encoded using LabelEncoder
- Create mappings for target variables:
  - Map crop names to numeric labels
  - Map fertilizer names to numeric labels

### 3. Feature Engineering
- Input features: District (encoded), Soil_color (encoded), Nitrogen, Phosphorus, Potassium, pH, Rainfall, Temperature
- Target variables: Crop (numeric), Fertilizer (numeric) - multi-output prediction

### 4. Model Training
- Algorithm: Decision Tree Classifier (sklearn.tree.DecisionTreeClassifier)
- Training process:
  - Split data into train/test sets (75/25 split)
  - Train model on encoded features to predict crop and fertilizer simultaneously
- Evaluation: Classification reports for both crop and fertilizer predictions

### 5. Model Persistence
- Save trained model: `Models/skyacre_fertilizer_model.pkl`
- Save encoders: `Models/encoder_district.pkl`, `Models/encoder_soil.pkl`
- Save mappings: `Models/map_crops.pkl`, `Models/map_fertilizers.pkl`

### 6. Model Deployment
- Flask API (`app.py`) loads saved models and provides prediction service
- Endpoint: `/farmer/predict` (POST)
- Input: JSON with District, Soil_color, Nitrogen, Phosphorus, Potassium, pH, Rainfall, Temperature
- Output: JSON with predicted_crop and predicted_fertilizer

## Files Structure
- `app.py`: Flask API for model inference
- `train.py`: Empty (training logic moved to Src/)
- `requirements.txt`: Python dependencies
- `Src/train_skyacre_fertilizer_model.py`: Model training script
- `Notebooks/Crop_and_Fertilizer_Recommender.ipynb`: Jupyter notebook with complete workflow
- `Data/`: Raw and processed datasets
- `Models/`: Saved model artifacts

## Usage
1. Train the model (if needed): Run `Src/train_skyacre_fertilizer_model.py`
2. Start the API: `python app.py`
3. Make predictions: POST to `http://127.0.0.1:5000/farmer/predict` with required features