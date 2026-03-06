"""
Upload best_model.keras to Hugging Face Space

This script uploads the trained cow disease model to the 
Hugging Face Space at https://huggingface.co/spaces/Storm00212/SkyAcre_cow_model

Usage:
    python upload_to_huggingface_space.py
"""

import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, create_repo

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL_FILE = 'best_model.keras'
REPO_ID = 'Storm00212/SkyAcre_cow_model'

def get_hf_token():
    """Get Hugging Face token from environment."""
    token = os.environ.get('HF_TOKEN')
    if not token or not token.strip():
        raise ValueError("Hugging Face token cannot be empty. Set HF_TOKEN env var.")
    return token


def upload_model_to_space():
    """Upload the model to Hugging Face Space."""
    print("="*60)
    print("UPLOAD MODEL TO HUGGING FACE SPACE")
    print("="*60 + "\n")
    
    # Check if model file exists
    if not os.path.exists(MODEL_FILE):
        print(f"Error: Model file '{MODEL_FILE}' not found!")
        return None
    
    print(f"Found model file: {MODEL_FILE}")
    file_size = os.path.getsize(MODEL_FILE) / (1024 * 1024)  # MB
    print(f"Model size: {file_size:.2f} MB")
    
    # Get Hugging Face token
    token = get_hf_token()
    print(f"\nRepository ID: {REPO_ID}")
    
    # Initialize API
    api = HfApi(token=token)
    
    # Create repository (if it doesn't exist) - using repo_type="space"
    print(f"\nCreating/accessing Space '{REPO_ID}'...")
    try:
        create_repo(
            repo_id=REPO_ID,
            token=token,
            repo_type="space",
            exist_ok=True
        )
        print("Space created or already exists.")
    except Exception as e:
        print(f"Error creating Space: {e}")
        return None
    
    # Upload the model file
    print(f"\nUploading {MODEL_FILE} to Hugging Face Space...")
    try:
        api.upload_file(
            path_or_fileobj=MODEL_FILE,
            path_in_repo=MODEL_FILE,
            repo_id=REPO_ID,
            repo_type="space",
            commit_message="Upload cow disease classification model (best_model.keras)"
        )
        print(f"\nModel uploaded successfully!")
        print(f"Space URL: https://huggingface.co/spaces/{REPO_ID}")
        
        return REPO_ID
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None


def main():
    """Main function."""
    repo_id = upload_model_to_space()
    
    if repo_id:
        print("\n" + "="*60)
        print("UPLOAD COMPLETE!")
        print("="*60)
        print(f"\nModel available at: https://huggingface.co/spaces/{repo_id}")
    
    return repo_id


if __name__ == "__main__":
    main()
