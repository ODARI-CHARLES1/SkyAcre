"""
Load Model from Hugging Face Hub

This script downloads and loads a trained model from 
Hugging Face Hub.

Usage:
    python load_from_huggingface.py
"""

import os
from huggingface_hub import hf_hub_download
from tensorflow import keras
import getpass

# Configuration
MODEL_FILENAME = 'skyacre_cow_disease_model.h5'
REPO_ID = None  # Set your repo_id here, e.g., "your-username/skyacre-cow-disease"


def get_hf_token():
    """Get Hugging Face token from environment or prompt."""
    token = os.environ.get('HF_TOKEN')
    if token is None:
        token = getpass.getpass("Enter your Hugging Face token (press Enter if public model): ")
    return token if token else None


def get_repo_id():
    """Get repository ID from user."""
    global REPO_ID
    
    if REPO_ID is not None:
        return REPO_ID
    
    repo_id = input("Enter the Hugging Face repository ID (e.g., username/skyacre-cow-disease): ")
    return repo_id


def load_model_from_hub(repo_id=None, filename=MODEL_FILENAME):
    """
    Download and load a model from Hugging Face Hub.
    
    Args:
        repo_id: Hugging Face repository ID (e.g., "username/repo-name")
        filename: Name of the model file in the repository
    
    Returns:
        Loaded Keras model
    """
    print("="*60)
    print("LOAD MODEL FROM HUGGING FACE HUB")
    print("="*60 + "\n")
    
    if repo_id is None:
        repo_id = get_repo_id()
    
    print(f"Repository ID: {repo_id}")
    print(f"Model filename: {filename}")
    
    # Get token (optional for public models)
    token = get_hf_token()
    
    # Download and cache the model locally
    print("\nDownloading model from Hugging Face Hub...")
    model_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        token=token
    )
    
    print(f"Model downloaded to: {model_path}")
    
    # Load the model
    print("Loading model...")
    model = keras.models.load_model(model_path)
    
    print("\nModel loaded successfully!")
    
    return model, model_path


def main():
    """Main function."""
    model, model_path = load_model_from_hub()
    
    # Display model summary
    print("\n" + "="*60)
    print("MODEL SUMMARY")
    print("="*60)
    model.summary()
    
    print("\n" + "="*60)
    print("MODEL READY!")
    print("="*60)
    print(f"Model is loaded and ready for inference.")
    print(f"Local model path: {model_path}")
    
    return model


if __name__ == "__main__":
    model = main()
