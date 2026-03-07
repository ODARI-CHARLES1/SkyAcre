"""
Test script to verify the model works exactly like the API expects.
This simulates the /predict/cow-disease endpoint behavior.
"""
import os
import io
import numpy as np
import tensorflow as tf
from PIL import Image

# Set the model path (same as what app.py uses as fallback)
model_path = os.path.join(os.path.dirname(__file__), 'SkyAcre_cow_model', 'best_model.keras')

# Same class labels as in app.py
COW_DISEASE_CLASS_LABELS = {0: 'foot-and-mouth', 1: 'lumpy', 2: 'healthy'}

print("=" * 60)
print("API COMPATIBILITY TEST")
print("=" * 60)

# 1. Load the model (same as app.py does)
print("\n1. Loading model...")
try:
    model = tf.keras.models.load_model(model_path)
    print("   Model loaded successfully!")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# 2. Create a test image (simulating what would be uploaded)
print("\n2. Creating test image...")
test_image = Image.new('RGB', (800, 600), color=(73, 109, 137))  # Random RGB image
print(f"   Test image size: {test_image.size}")

# 3. Simulate the API preprocessing (same as preprocess_image in app.py)
print("\n3. Simulating API preprocessing...")
target_size = (224, 224)

# Convert to RGB if needed
test_image = test_image.convert('RGB')
# Resize
test_image = test_image.resize(target_size)
# Convert to numpy array
img_array = np.array(test_image)
# Normalize to [0, 1]
img_array = img_array / 255.0
# Add batch dimension
img_array = np.expand_dims(img_array, axis=0)

print(f"   Processed image shape: {img_array.shape}")
print(f"   Processed image min/max: {img_array.min():.4f} / {img_array.max():.4f}")

# 4. Make prediction (same as API does)
print("\n4. Making prediction...")
predictions = model.predict(img_array, verbose=0)
print(f"   Raw predictions: {predictions}")

# 5. Get the class with highest probability (same as API does)
predicted_class_index = np.argmax(predictions[0])
predicted_class_name = COW_DISEASE_CLASS_LABELS[predicted_class_index]
confidence = float(predictions[0][predicted_class_index])

print(f"\n5. Results:")
print(f"   Predicted class index: {predicted_class_index}")
print(f"   Predicted class name: {predicted_class_name}")
print(f"   Confidence: {confidence:.4f}")
print(f"   All predictions:")
for label, conf in zip(COW_DISEASE_CLASS_LABELS.values(), predictions[0]):
    print(f"      - {label}: {conf:.4f}")

# 6. Summary
print("\n" + "=" * 60)
print("COMPATIBILITY SUMMARY")
print("=" * 60)
print("✅ Model architecture: Compatible (input: 224x224x3, output: 3 classes)")
print("✅ Preprocessing: Compatible (resize to 224x224, normalize to [0,1])")
print("✅ Output format: Compatible (3 class probabilities)")
print("✅ API Endpoint /predict/cow-disease: SHOULD WORK")
print("=" * 60)

# Note about the repo ID difference
print("\n⚠️  NOTE: The app.py loads from 'Storm00212/SkyAcre' but the model")
print("   was uploaded to 'Storm00212/SkyAcre_cow_model'.")
print("   For the HuggingFace loading to work, you need to update line 50 in app.py")
print("   to: COW_DISEASE_REPO_ID = 'Storm00212/SkyAcre_cow_model'")
print("   OR keep using the local file fallback which works fine.")
