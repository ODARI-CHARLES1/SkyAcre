"""
Load Model from Hugging Face Hub

This script downloads and loads a trained model from 
Hugging Face Hub using the `hf://` protocol.

Usage:
    python load_from_huggingface.py
"""

import os

# Available backend options are: "jax", "torch", "tensorflow".
# Using tensorflow as it is listed in requirements.txt
os.environ["KERAS_BACKEND"] = "jax"
# To use the Hugging Face Hub, a token needs to be available.
# It can be set as an environment variable `HF_TOKEN`.
# A .env file can be used to store this token.

import keras


def load_model_from_hub(repo_id="Storm00212/SkyAcre"):
    """
    Download and load a model from Hugging Face Hub.
    
    Args:
        repo_id: Hugging Face repository ID (e.g., "username/repo-name")
    
    Returns:
        Loaded Keras model
    """
    print("="*60)
    print("LOAD MODEL FROM HUGGING FACE HUB")
    print("="*60 + "\n")
    
    hf_path = f"hf://{repo_id}"
    print(f"Loading model from: {hf_path}")
    
    # Load the model directly from the Hugging Face Hub
    # This requires the `huggingface_hub` package and a valid token
    # if the repository is private.
    try:
        model = keras.saving.load_model(hf_path)
        print("\nModel loaded successfully!")
        return model
    except Exception as e:
        print(f"\nError loading model: {e}")
        print("\nPlease ensure you have `huggingface_hub` installed (`pip install huggingface_hub`).")
        print("If the repository is private, make sure your Hugging Face token is available as an environment variable (HF_TOKEN).")
        return None


def main():
    """Main function."""
    model = load_model_from_hub()
    
    if model:
        # Display model summary
        print("\n" + "="*60)
        print("MODEL SUMMARY")
        print("="*60)
        model.summary()
        
        print("\n" + "="*60)
        print("MODEL READY!")
        print("="*60)
        print(f"Model is loaded and ready for inference.")
        
        return model


if __name__ == "__main__":
    model = main()
