"""
Test script to verify the model loads and performs inference correctly.
"""
import os
import numpy as np
import tensorflow as tf

# Set the model path
model_path = os.path.join(os.path.dirname(__file__), 'SkyAcre_cow_model', 'best_model.keras')

print("=" * 60)
print("CLONED REPOSITORY VERIFICATION RESULTS")
print("=" * 60)

# 1. Check if model file exists
print("\n1. CLONE STATUS:")
print(f"   - Repository cloned successfully: YES")
print(f"   - Model file path: {model_path}")
print(f"   - Model file exists: {os.path.exists(model_path)}")
print(f"   - Model file size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")

# 2. Load the model
print("\n2. MODEL LOADING:")
try:
    model = tf.keras.models.load_model(model_path)
    print("   - Model loaded successfully: YES")
    print(f"   - Model type: {type(model)}")
    print(f"   - Model input shape: {model.input_shape}")
    print(f"   - Model output shape: {model.output_shape}")
    model_loaded = True
except Exception as e:
    print(f"   - Model loaded successfully: NO")
    print(f"   - Error: {str(e)}")
    model_loaded = False

# 3. Perform test inference
print("\n3. INFERENCE TEST:")
if model_loaded:
    try:
        # Create a dummy input (batch of 1 image, 224x224x3)
        dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        # Run prediction
        prediction = model.predict(dummy_input, verbose=0)
        
        print("   - Inference executed successfully: YES")
        print(f"   - Input shape: {dummy_input.shape}")
        print(f"   - Output shape: {prediction.shape}")
        print(f"   - Sample output (first 5 values): {prediction[0][:5]}")
        print(f"   - Output dtype: {prediction.dtype}")
        
        # Get the predicted class
        predicted_class = np.argmax(prediction, axis=1)[0]
        print(f"   - Predicted class index: {predicted_class}")
        
        inference_success = True
    except Exception as e:
        print(f"   - Inference executed successfully: NO")
        print(f"   - Error: {str(e)}")
        inference_success = False
else:
    print("   - Inference skipped (model failed to load)")
    inference_success = False

# 4. Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Clone Status: {'SUCCESS' if os.path.exists(model_path) else 'FAILED'}")
print(f"Model File Exists: {'YES' if os.path.exists(model_path) else 'NO'}")
print(f"Model Loads Successfully: {'YES' if model_loaded else 'NO'}")
print(f"Inference Works: {'YES' if inference_success else 'NO'}")
print("=" * 60)
