"""
Upload Model to Hugging Face Hub

This script creates a repository on Hugging Face and uploads 
the trained model (.h5 file).

Usage:
    python upload_to_huggingface.py
"""

import os
from huggingface_hub import HfApi, create_repo
import getpass

# Configuration
MODEL_FILE = 'skyacre_cow_disease_model.h5'
REPO_ID = None  # Set your repo_id here, e.g., "your-username/skyacre-cow-disease"
# Or leave None to be prompted

def get_hf_token():
    """Get Hugging Face token from environment or prompt."""
    token = os.environ.get('HF_TOKEN')
    if token is None:
        token = getpass.getpass("Enter your Hugging Face token: ")
    
    # Validate token is not empty
    if not token or not token.strip():
        raise ValueError("Hugging Face token cannot be empty. Set HF_TOKEN env var or enter when prompted.")
    
    return token


def get_repo_id():
    """Get repository ID from user."""
    global REPO_ID
    
    if REPO_ID is not None:
        return REPO_ID
    
    username = input("Enter your Hugging Face username: ")
    repo_name = input("Enter repository name (e.g., skyacre-cow-disease): ")
    
    return f"{username}/{repo_name}"


def create_and_upload_model():
    """Create repo and upload the model to Hugging Face."""
    print("="*60)
    print("UPLOAD MODEL TO HUGGING FACE HUB")
    print("="*60 + "\n")
    
    # Check if model file exists
    if not os.path.exists(MODEL_FILE):
        print(f"Error: Model file '{MODEL_FILE}' not found!")
        print("Please run train.py first to train and save the model.")
        return None
    
    print(f"Found model file: {MODEL_FILE}")
    file_size = os.path.getsize(MODEL_FILE) / (1024 * 1024)  # MB
    print(f"Model size: {file_size:.2f} MB")
    
    # Get Hugging Face token
    token = get_hf_token()
    
    # Get repository ID
    repo_id = get_repo_id()
    print(f"\nRepository ID: {repo_id}")
    
    # Initialize API
    api = HfApi(token=token)
    
    # Create repository (if it doesn't exist)
    print(f"\nCreating repository '{repo_id}'...")
    try:
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type="model",
            exist_ok=True
        )
        print("Repository created or already exists.")
    except Exception as e:
        print(f"Error creating repository: {e}")
        return None
    
    # Upload the model file
    print(f"\nUploading {MODEL_FILE} to Hugging Face Hub...")
    try:
        api.upload_file(
            path_or_fileobj=MODEL_FILE,
            path_in_repo=MODEL_FILE,
            repo_id=repo_id,
            repo_type="model",
            commit_message="Upload cow disease classification model"
        )
        print(f"\nModel uploaded successfully!")
        print(f"Model URL: https://huggingface.co/{repo_id}")
        
        return repo_id
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None


def main():
    """Main function."""
    repo_id = create_and_upload_model()
    
    if repo_id:
        print("\n" + "="*60)
        print("UPLOAD COMPLETE!")
        print("="*60)
        print(f"\nTo load the model, use:")
        print(f'  repo_id = "{repo_id}"')
        print(f'  model_path = hf_hub_download(repo_id="{repo_id}", filename="{MODEL_FILE}")')
        print(f'  model = keras.models.load_model(model_path)')
    
    return repo_id


if __name__ == "__main__":
    main()
