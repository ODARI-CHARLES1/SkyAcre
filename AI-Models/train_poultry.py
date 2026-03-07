"""
================================================================================
POULTRY DISEASE CLASSIFICATION - CNN TRAINING PIPELINE
================================================================================

This script provides a complete image preprocessing and CNN model training pipeline
for multi-class poultry disease classification. It mirrors the architecture and 
methodology implemented for the cattle disease identification project.

================================================================================
DATASET OVERVIEW
================================================================================

Location: Data/poultry_diseases
Classes (4 total):
    - cocci   (Coccidiosis)     : 2,103 images (30.87%)
    - healthy (Healthy)          : 2,057 images (30.20%)
    - ncd     (Newcastle Disease):   376 images (5.52%)  <-- minority class
    - salmo   (Salmonella)       : 2,276 images (33.41%)
    
Total Images: 6,812
Image Sizes: Variable (resized to 224x224 during preprocessing)

================================================================================
PIPELINE STEPS
================================================================================

1. DATA LOADING & EXPLORATION
   - Count images per class
   - Analyze image properties
   - Report class distribution
   - Check for corrupt images

2. IMAGE PREPROCESSING
   - Resize all images to 224x224
   - Convert BGR to RGB (OpenCV uses BGR)
   - Normalize pixel values to [0, 1]

3. DATA AUGMENTATION
   - Random rotation (±20°)
   - Horizontal/vertical flipping
   - Brightness adjustment (0.8-1.2)
   - Random zoom (0.9-1.1)
   - Shear transformation
   - Channel shift

4. DATA SPLITTING
   - Training: 70%
   - Validation: 15%
   - Test: 15%
   - Stratified to maintain class balance

5. CNN MODEL ARCHITECTURE
   - 4 convolutional blocks (32→64→128→256 filters)
   - Each block: Conv2D → BatchNorm → ReLU → Conv2D → BatchNorm → ReLU → MaxPool → Dropout
   - Dense layers: 512 → 256 → 4 (output)
   - Regularization: L2 weight decay, Dropout, BatchNormalization

6. MODEL TRAINING
   - Optimizer: Adam (lr=0.001)
   - Loss: Sparse Categorical Crossentropy
   - Callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, CSVLogger

7. MODEL EVALUATION
   - Accuracy, Precision, Recall, F1-Score
   - Confusion Matrix
   - ROC-AUC (One-vs-Rest)
   - Overfitting Detection
   - Visualizations

8. MODEL SAVING
   - Serialized to .keras format

================================================================================
USAGE
================================================================================

    python train_poultry.py

Requirements:
    - TensorFlow 2.x
    - NumPy, Pandas
    - Matplotlib, Seaborn
    - Scikit-learn
    - OpenCV, Pillow

Output:
    - Model: AI-Models/Output/poultry/poultry_disease_model.keras
    - Plots: AI-Models/Output/poultry/*.png

================================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# TensorFlow and Keras imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import (
    EarlyStopping,           # Stop training when validation metric stops improving
    ModelCheckpoint,          # Save model at best epoch
    ReduceLROnPlateau,        # Reduce learning rate when training plateaus
    CSVLogger                 # Log training metrics to CSV
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # For data augmentation
from tensorflow.keras.regularizers import l2  # L2 regularization for weight decay

# Sklearn imports for evaluation metrics
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    precision_score,           # Ratio of true positives to predicted positives
    recall_score,             # Ratio of true positives to actual positives
    f1_score,                 # Harmonic mean of precision and recall
    confusion_matrix,         # Matrix showing true vs predicted classifications
    classification_report,    # Text report with per-class metrics
    roc_auc_score,            # Area under ROC curve
    roc_curve,                # ROC curve data points
    accuracy_score            # Overall accuracy
)

# Image processing libraries
import cv2                    # OpenCV for image manipulation
from PIL import Image         # Python Imaging Library

# =============================================================================
# Set random seeds for reproducibility
# =============================================================================
# Setting random seeds ensures that the model produces the same results
# each time it's run, which is important for debugging and experiments
np.random.seed(42)
tf.random.set_seed(42)

# =============================================================================
# CONFIGURATION CLASS
# =============================================================================
# This class contains all the hyperparameters and settings for the pipeline
# Changing these values will affect the entire training process

class Config:
    """
    Configuration settings for the poultry disease classification pipeline.
    
    All paths and parameters are centralized here for easy modification.
    """
    
    # ==========================================================================
    # Dataset paths - where to find input data and where to save outputs
    # ==========================================================================
    DATA_DIR = 'Data/poultry_diseases'        # Path to the image dataset
    OUTPUT_DIR = 'AI-Models/Output/poultry'  # Where to save model and plots
    
    # ==========================================================================
    # Image parameters - these determine input size for the CNN
    # ==========================================================================
    IMG_HEIGHT = 224    # Standard size for many CNN architectures (e.g., VGG, ResNet)
    IMG_WIDTH = 224     # Square images are easier to process
    CHANNELS = 3        # RGB color images (use 1 for grayscale)
    
    # ==========================================================================
    # Training parameters - control the training process
    # ==========================================================================
    BATCH_SIZE = 32          # Number of samples processed before updating weights
                             # Higher = faster but requires more memory
    EPOCHS = 50              # Maximum number of times to iterate through dataset
    INITIAL_LEARNING_RATE = 0.001  # Starting learning rate for Adam optimizer
    MIN_LEARNING_RATE = 1e-6      # Minimum learning rate (floor)
    
    # ==========================================================================
    # Class labels - mapping between class indices and disease names
    # ==========================================================================
    # The model outputs numbers 0-3, these are their meanings
    CLASS_LABELS = {
        0: 'cocci',      # Coccidiosis - parasitic intestinal disease
        1: 'healthy',    # Healthy poultry
        2: 'ncd',        # Newcastle Disease - viral respiratory infection
        3: 'salmo'       # Salmonella - bacterial infection
    }
    
    NUM_CLASSES = len(CLASS_LABELS)  # 4 classes
    
    # ==========================================================================
    # Data split ratios - how to divide the dataset
    # ==========================================================================
    # Total must equal 1.0 (100%)
    TRAIN_RATIO = 0.70   # 70% for training
    VAL_RATIO = 0.15     # 15% for validation
    TEST_RATIO = 0.15    # 15% for final testing
    
    # ==========================================================================
    # Model output filenames
    # ==========================================================================
    MODEL_NAME = 'poultry_disease_model.keras'  # Keras format (recommended)
    HISTORY_NAME = 'training_history.csv'       # Log file

# Create output directory if it doesn't exist
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)


# =============================================================================
# STEP 1: DATA LOADING AND EXPLORATION
# =============================================================================

def load_dataset_exploration(data_dir):
    """
    =============================================================================
    STEP 1: DATA LOADING AND EXPLORATION
    =============================================================================
    
    This function explores the dataset to understand its structure before training.
    It performs several important checks:
    
    1. Counts total images per class - helps identify class imbalance
    2. Analyzes image dimensions - ensures all images are usable
    3. Checks for corrupt images - prevents training failures
    4. Generates a class distribution visualization - helps with analysis
    
    Why this is important:
    - Class imbalance (like ncd with only 376 images vs salmo with 2276) can
      cause the model to be biased toward majority classes
    - Variable image sizes need to be normalized
    - Corrupt images will cause errors during training
    
    Args:
        data_dir: Path to the poultry_diseases folder
        
    Returns:
        Dictionary containing dataset statistics
    """
    print("=" * 70)
    print("STEP 1: DATA LOADING AND EXPLORATION")
    print("=" * 70)
    
    data_dir = Path(data_dir)  # Convert string to Path object for easier manipulation
    
    # Initialize statistics dictionary
    stats = {
        'total_images': 0,
        'class_counts': {},
        'image_sizes': [],
        'corrupt_images': [],
        'valid_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.gif']  # Supported formats
    }
    
    # Get all class directories (folders like cocci, healthy, ncd, salmo)
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    class_dirs = sorted(class_dirs)  # Sort for consistent ordering
    
    print(f"\nDataset Location: {data_dir}")
    print(f"Found {len(class_dirs)} classes: {[d.name for d in class_dirs]}")
    print("\n" + "-" * 70)
    
    # Iterate through each class directory
    for class_dir in class_dirs:
        class_name = class_dir.name
        
        # Get all valid image files in this class folder
        images = [f for f in class_dir.iterdir() 
                  if f.suffix.lower() in stats['valid_extensions']]
        
        stats['class_counts'][class_name] = len(images)
        stats['total_images'] += len(images)
        
        print(f"\nClass: {class_name}")
        print(f"  - Image count: {len(images)}")
        
        # Analyze a sample of images to get dimensions
        # We check first 5 images to estimate typical size
        sample_count = min(5, len(images))
        for img_path in images[:sample_count]:
            try:
                # Read image with OpenCV
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Get dimensions (height, width, channels)
                    h, w, c = img.shape
                    stats['image_sizes'].append((h, w, c))
                else:
                    # Image couldn't be read - might be corrupt
                    stats['corrupt_images'].append(str(img_path))
            except Exception as e:
                # Any error means the image is likely corrupt
                stats['corrupt_images'].append(str(img_path))
    
    # ==========================================================================
    # Display class distribution
    # ==========================================================================
    print("\n" + "-" * 70)
    print("CLASS DISTRIBUTION:")
    print("-" * 70)
    print(f"{'Class':<15} {'Count':>10} {'Percentage':>15}")
    print("-" * 70)
    
    for class_name, count in stats['class_counts'].items():
        # Calculate percentage of total
        percentage = (count / stats['total_images']) * 100
        print(f"{class_name:<15} {count:>10} {percentage:>14.2f}%")
    
    print("-" * 70)
    print(f"{'TOTAL':<15} {stats['total_images']:>10} {'100.00%':>15}")
    
    # ==========================================================================
    # Report image size analysis
    # ==========================================================================
    if stats['image_sizes']:
        unique_sizes = set(stats['image_sizes'])
        print(f"\nImage Size Analysis:")
        print(f"  - Unique sizes found: {len(unique_sizes)}")
        print(f"  - Sample sizes: {list(unique_sizes)[:5]}")
    
    # ==========================================================================
    # Report on corrupt images
    # ==========================================================================
    if stats['corrupt_images']:
        print(f"\n[WARNING] Found {len(stats['corrupt_images'])} corrupt images!")
    else:
        print(f"\n[OK] All images are valid and readable.")
    
    # ==========================================================================
    # Create visualization of class distribution
    # ==========================================================================
    plt.figure(figsize=(10, 6))
    classes = list(stats['class_counts'].keys())
    counts = list(stats['class_counts'].values())
    
    # Use distinct colors for each class
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    bars = plt.bar(classes, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.xlabel('Disease Class', fontsize=12)
    plt.ylabel('Number of Images', fontsize=12)
    plt.title('Poultry Disease Dataset - Class Distribution', fontsize=14, fontweight='bold')
    
    # Add value labels on top of each bar
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(Config.OUTPUT_DIR, 'class_distribution.png'), dpi=150)
    plt.show()
    print(f"\n[OK] Class distribution plot saved to {Config.OUTPUT_DIR}/class_distribution.png")
    
    return stats


# =============================================================================
# STEP 2: IMAGE PREPROCESSING
# =============================================================================

def preprocess_image(image, target_size=(Config.IMG_HEIGHT, Config.IMG_WIDTH)):
    """
    =============================================================================
    IMAGE PREPROCESSING FUNCTION
    =============================================================================
    
    This function prepares a single image for the CNN model. It performs:
    
    1. Reading the image file
    2. Converting color format (BGR → RGB)
    3. Resizing to standard dimensions
    4. Normalizing pixel values
    
    Why each step is necessary:
    
    a) Color conversion:
       - OpenCV reads images in BGR format (Blue-Green-Red)
       - Most ML libraries expect RGB (Red-Green-Blue)
       - Converting ensures consistent color representation
    
    b) Resizing:
       - CNNs require fixed-size inputs
       - 224x224 is a standard size used by VGG, ResNet, etc.
       - Larger sizes capture more detail but need more memory
    
    c) Normalization:
       - Raw pixel values are 0-255 (8-bit)
       - Neural networks train better with smaller, normalized values
       - Dividing by 255 scales to [0, 1] range
       - This helps with gradient descent convergence
    
    Args:
        image: Can be a file path (str), numpy array, or PIL Image
        target_size: Tuple of (height, width) to resize to
        
    Returns:
        Preprocessed image as numpy array with values in [0, 1]
    """
    # ==========================================================================
    # Step 1: Load the image
    # ==========================================================================
    if isinstance(image, str):
        # Image is a file path - read it with OpenCV
        img = cv2.imread(str(image))
        if img is None:
            raise ValueError(f"Could not load image: {image}")
    elif isinstance(image, np.ndarray):
        # Image is already a numpy array
        img = image
    else:
        # Image is PIL Image - convert to numpy array
        img = np.array(image)
    
    # ==========================================================================
    # Step 2: Convert BGR to RGB
    # ==========================================================================
    # OpenCV uses BGR, but most ML libraries use RGB
    # This ensures colors are interpreted correctly
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # ==========================================================================
    # Step 3: Resize to target dimensions
    # ==========================================================================
    # INTER_LINEAR is a fast, good-quality interpolation method
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    
    # ==========================================================================
    # Step 4: Normalize pixel values to [0, 1]
    # ==========================================================================
    # Convert to float32 first (high precision for calculations)
    # Then divide by 255 (max pixel value)
    img = img.astype(np.float32) / 255.0
    
    return img


def load_and_preprocess_dataset(data_dir, class_labels, img_size=(Config.IMG_HEIGHT, Config.IMG_WIDTH)):
    """
    =============================================================================
    LOAD AND PREPROCESS ENTIRE DATASET
    =============================================================================
    
    This function processes all images in the dataset and prepares them for training.
    It loads every image, applies preprocessing, and stores them in numpy arrays.
    
    Args:
        data_dir: Path to the dataset folder
        class_labels: Dictionary mapping class names to numeric indices
                     Example: {'cocci': 0, 'healthy': 1, 'ncd': 2, 'salmo': 3}
        img_size: Target image size (height, width)
        
    Returns:
        Tuple of (X, y):
            - X: Numpy array of shape (num_images, height, width, channels)
            - y: Numpy array of shape (num_images,) with class indices
    """
    print("\n" + "=" * 70)
    print("STEP 2: IMAGE PREPROCESSING")
    print("=" * 70)
    
    data_dir = Path(data_dir)
    images = []
    labels = []
    
    # Process each class
    for class_name, class_idx in class_labels.items():
        class_dir = data_dir / class_name
        print(f"\nProcessing class: {class_name} (index: {class_idx})")
        
        # Get all valid image files in this class folder
        image_files = (list(class_dir.glob('*.jpg')) + 
                     list(class_dir.glob('*.jpeg')) + 
                     list(class_dir.glob('*.png')) + 
                     list(class_dir.glob('*.bmp')))
        
        # Process each image in the class
        for i, img_path in enumerate(image_files):
            try:
                # Apply preprocessing to each image
                img = preprocess_image(str(img_path), img_size)
                images.append(img)
                labels.append(class_idx)
                
                # Print progress every 500 images
                if (i + 1) % 500 == 0:
                    print(f"  Processed {i + 1}/{len(image_files)} images...")
            except Exception as e:
                print(f"   [WARNING] Error processing {img_path}: {e}")
        
        print(f"  Completed: {len(image_files)} images")
    
    # Convert lists to numpy arrays for efficient computation
    X = np.array(images)
    y = np.array(labels)
    
    print(f"\n[OK] Preprocessing complete!")
    print(f"   Total images: {len(X)}")
    print(f"   Image shape: {X[0].shape}")  # Should be (224, 224, 3)
    print(f"   Data type: {X.dtype}")        # Should be float32
    print(f"   Value range: [{X.min():.4f}, {X.max():.4f}]")  # Should be [0, 1]
    
    return X, y


# =============================================================================
# STEP 3: DATA AUGMENTATION
# =============================================================================

def create_data_augmentation():
    """
    =============================================================================
    DATA AUGMENTATION - INCREASING DATASET DIVERSITY
    =============================================================================
    
    Data augmentation artificially increases the training dataset by applying
    random transformations to existing images. This helps the model:
    
    1. Generalize better - sees many variations of each class
    2. Avoid overfitting - model doesn't memorize training images
    3. Handle real-world variations - different angles, lighting, etc.
    
    HOW IT WORKS:
    - During training, each batch is generated on-the-fly
    - Random transformations are applied to each image
    - The model sees different versions of each image each epoch
    
    IMPORTANT: Augmentation is ONLY applied to training data!
    Validation and test data must remain unchanged for fair evaluation.
    
    Returns:
        Tuple of (train_datagen, val_datagen):
            - train_datagen: Applies augmentation
            - val_datagen: No augmentation (for evaluation)
    """
    print("\n" + "=" * 70)
    print("STEP 3: DATA AUGMENTATION")
    print("=" * 70)
    
    # ==========================================================================
    # Create training data generator with augmentation
    # ==========================================================================
    train_datagen = ImageDataGenerator(
        # -------------------------------------------------------------------------
        # ROTATION: Randomly rotate images
        # -------------------------------------------------------------------------
        # rotation_range=20 means rotate randomly between -20 and +20 degrees
        # This helps the model recognize objects at different angles
        rotation_range=20,
        
        # -------------------------------------------------------------------------
        # FLIPPING: Mirror images horizontally and vertically
        # -------------------------------------------------------------------------
        # Most objects look similar when flipped (not text, not numbers)
        # This doubles the effective dataset size per flip direction
        horizontal_flip=True,
        vertical_flip=True,
        
        # -------------------------------------------------------------------------
        # BRIGHTNESS: Vary image brightness
        # -------------------------------------------------------------------------
        # brightness_range=[0.8, 1.2] means:
        #   - 0.8 = 80% as bright (darker)
        #   - 1.2 = 120% as bright (brighter)
        # Real images have varying lighting conditions
        brightness_range=[0.8, 1.2],
        contrast_range=[0.8, 1.2],  # Similar for contrast
        
        # -------------------------------------------------------------------------
        # ZOOM: Randomly zoom in/out
        # -------------------------------------------------------------------------
        # zoom_range=[0.9, 1.1] means:
        #   - 0.9 = zoom out to 90% (image appears smaller)
        #   - 1.1 = zoom in to 110% (image appears larger)
        # This simulates different distances from the subject
        zoom_range=[0.9, 1.1],
        
        # -------------------------------------------------------------------------
        # SHEAR: Tilt the image
        # -------------------------------------------------------------------------
        # shear_range=0.15 tilts the image up to 15%
        # This simulates different viewing angles
        shear_range=0.15,
        
        # -------------------------------------------------------------------------
        # CHANNEL SHIFT: Vary color channels
        # -------------------------------------------------------------------------
        # Shifts the RGB values randomly
        # Helps model become color-invariant
        channel_shift_range=0.1,
        
        # -------------------------------------------------------------------------
        # FILL MODE: How to fill empty space after transformation
        # -------------------------------------------------------------------------
        # 'nearest' fills with the nearest pixel value (fastest)
        # Other options: 'reflect', 'wrap', 'constant'
        fill_mode='nearest',
        
        # -------------------------------------------------------------------------
        # RESCALE: Normalization (already done in preprocessing)
        # -------------------------------------------------------------------------
        # Set to None because we already normalized in preprocess_image()
        rescale=None
    )
    
    # ==========================================================================
    # Validation/test generator (no augmentation!)
    # ==========================================================================
    # This is crucial: validation data should NOT be augmented
    # Otherwise we'd be evaluating on artificially modified images
    val_datagen = ImageDataGenerator()
    
    print("[OK] Data augmentation pipeline created:")
    print("   - Random rotation: ±20 degrees")
    print("   - Random horizontal/vertical flipping")
    print("   - Random brightness adjustment: 0.8-1.2")
    print("   - Random zoom: 0.9-1.1")
    print("   - Random shear: 0.15")
    print("   - Channel shift: 0.1")
    
    return train_datagen, val_datagen


def visualize_augmentations(sample_image, train_datagen, save_path=None):
    """
    =============================================================================
    VISUALIZE AUGMENTATION EFFECTS
    =============================================================================
    
    This function shows what the augmented images look like.
    It's helpful for understanding and debugging the augmentation pipeline.
    
    Args:
        sample_image: A single preprocessed image
        train_datagen: The augmentation generator
        save_path: Where to save the visualization
    """
    print("\n   Generating augmentation visualization...")
    
    # Reshape for the generator: (batch_size, height, width, channels)
    sample_image = np.expand_dims(sample_image, axis=0)
    
    # Create figure with 8 subplots (1 original + 7 augmented)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    # First subplot is original image
    axes[0].imshow(sample_image[0])
    axes[0].set_title('Original', fontsize=10)
    axes[0].axis('off')
    
    # Generate 7 augmented versions
    augmented_count = 1
    for batch in train_datagen.flow(sample_image, batch_size=1):
        axes[augmented_count].imshow(batch[0])
        axes[augmented_count].set_title(f'Augmented {augmented_count}', fontsize=10)
        axes[augmented_count].axis('off')
        augmented_count += 1
        if augmented_count >= 8:
            break
    
    plt.suptitle('Data Augmentation Examples', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"   [OK] Augmentation visualization saved to {save_path}")
    
    plt.show()


# =============================================================================
# STEP 4: DATA SPLITTING
# =============================================================================

def split_data(X, y, train_ratio=Config.TRAIN_RATIO, 
               val_ratio=Config.VAL_RATIO, test_ratio=Config.TEST_RATIO,
               random_state=42):
    """
    =============================================================================
    SPLIT DATA INTO TRAIN/VALIDATION/TEST SETS
    =============================================================================
    
    This function divides the dataset into three parts:
    
    1. TRAINING SET (70%): Used to train the model
       - The model learns patterns from these examples
       
    2. VALIDATION SET (15%): Used during training
       - Evaluated after each epoch to monitor progress
       - Used for early stopping and learning rate adjustment
       - Helps prevent overfitting
       
    3. TEST SET (15%): Used for final evaluation
       - ONLY used after training is complete
       - Represents unseen data for fair evaluation
       - Should not influence training decisions
    
    STRATIFICATION:
    - Ensures each set has the same class distribution as the original
    - Important for imbalanced datasets (like ours with ncd having fewer images)
    - Without stratification, test set might have no ncd images!
    
    Args:
        X: Feature array (images)
        y: Label array
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        random_state: Seed for reproducibility
        
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    print("\n" + "=" * 70)
    print("STEP 4: DATA SPLITTING (WITH STRATIFICATION)")
    print("=" * 70)
    
    # ==========================================================================
    # First split: Separate training data from temporary (val + test) data
    # ==========================================================================
    # stratify=y ensures each class is represented proportionally
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(val_ratio + test_ratio),  # 30% goes to temp
        random_state=random_state,
        stratify=y  # IMPORTANT: Maintains class balance
    )
    
    # ==========================================================================
    # Second split: Separate temp into validation and test
    # ==========================================================================
    val_test_ratio = test_ratio / (val_ratio + test_ratio)  # 15%/30% = 0.5
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=val_test_ratio,  # Half of 30% = 15%
        random_state=random_state,
        stratify=y_temp  # Maintain balance in both sets
    )
    
    print(f"\nData Split Summary:")
    print(f"  - Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  - Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  - Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # ==========================================================================
    # Show class distribution in each split
    # ==========================================================================
    print(f"\nClass Distribution (Stratified):")
    print(f"  {'Class':<15} {'Train':>8} {'Val':>8} {'Test':>8}")
    print(f"  {'-'*40}")
    
    # Get unique classes and their counts in each set
    unique, counts = np.unique(y_train, return_counts=True)
    train_dist = dict(zip(unique, counts))
    unique, counts = np.unique(y_val, return_counts=True)
    val_dist = dict(zip(unique, counts))
    unique, counts = np.unique(y_test, return_counts=True)
    test_dist = dict(zip(unique, counts))
    
    # Print each class
    for class_idx, class_name in Config.CLASS_LABELS.items():
        print(f"  {class_name:<15} {train_dist.get(class_idx, 0):>8} "
              f"{val_dist.get(class_idx, 0):>8} {test_dist.get(class_idx, 0):>8}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def save_split_data(X_train, X_val, X_test, y_train, y_val, y_test, output_dir):
    """
    Save the split data as numpy files for future use.
    
    Args:
        X_train, X_val, X_test: Feature arrays
        y_train, y_val, y_test: Label arrays
        output_dir: Where to save files
    """
    np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(output_dir, 'X_val.npy'), X_val)
    np.save(os.path.join(output_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
    np.save(os.path.join(output_dir, 'y_val.npy'), y_val)
    np.save(os.path.join(output_dir, 'y_test.npy'), y_test)
    print(f"\n[OK] Split data saved to {output_dir}")


# =============================================================================
# STEP 5: CNN MODEL ARCHITECTURE
# =============================================================================

def build_cnn_model(input_shape=(Config.IMG_HEIGHT, Config.IMG_WIDTH, Config.CHANNELS),
                    num_classes=Config.NUM_CLASSES,
                    l2_reg=0.001):
    """
    =============================================================================
    CONVOLUTIONAL NEURAL NETWORK (CNN) ARCHITECTURE
    =============================================================================
    
    This function builds a CNN for image classification. Here's the architecture:
    
    =============================================================================
    ARCHITECTURE OVERVIEW
    =============================================================================
    
    INPUT LAYER
    │
    ├─ CONV BLOCK 1 (32 filters)
    │   ├─ Conv2D(32, 3x3)  → Extracts basic features (edges, colors)
    │   ├─ BatchNorm       → Normalizes activations
    │   ├─ ReLU             → Introduces non-linearity
    │   ├─ Conv2D(32, 3x3)  → More complex patterns
    │   ├─ BatchNorm
    │   ├─ ReLU
    │   ├─ MaxPool(2x2)     → Reduces size, captures spatial invariance
    │   └─ Dropout(0.25)    → Prevents overfitting
    │
    ├─ CONV BLOCK 2 (64 filters)
    │   └─ Same structure with 64 filters
    │   → Extracts textures, shapes
    │
    ├─ CONV BLOCK 3 (128 filters)
    │   └─ Same structure with 128 filters
    │   → Extracts parts of objects
    │
    ├─ CONV BLOCK 4 (256 filters)
    │   └─ Same structure with 256 filters
    │   → Extracts high-level features
    │
    ├─ DENSE LAYERS
    │   ├─ Flatten           → Converts 2D to 1D
    │   ├─ Dense(512)        → Fully connected layer
    │   ├─ BatchNorm
    │   ├─ ReLU
    │   ├─ Dropout(0.5)
    │   ├─ Dense(256)
    │   ├─ BatchNorm
    │   ├─ ReLU
    │   └─ Dropout(0.5)
    │
    └─ OUTPUT LAYER
        └─ Dense(4, softmax) → Class probabilities
    
    =============================================================================
    WHY THIS ARCHITECTURE WORKS
    =============================================================================
    
    1. PROGRESSIVE FILTER INCREASE (32→64→128→256):
       - Early layers: detect simple features (edges, colors)
       - Later layers: combine simple features into complex ones
       
    2. CONV2D LAYERS:
       - 3x3 kernels are the standard - small enough to be efficient,
         large enough to capture patterns
       - 'same' padding keeps spatial dimensions
       
    3. BATCH NORMALIZATION:
       - Normalizes inputs to each layer
       - Allows faster training, higher learning rates
       - Acts as regularization
       
    4. RELU ACTIVATION:
       - Fast to compute
       - Avoids vanishing gradient problem
       - Introduces non-linearity
       
    5. MAXPOOLING:
       - Reduces spatial dimensions (2x2 with stride 2 = 75% reduction)
       - Makes features more abstract
       - Provides spatial invariance
       
    6. DROPOUT:
       - Randomly "drops" (sets to zero) some neurons during training
       - Forces network to not rely on any single neuron
       - Prevents overfitting
       - 0.25 in conv layers, 0.5 in dense layers
       
    7. L2 REGULARIZATION:
       - Penalizes large weights
       - Keeps weights small, preventing overfitting
       
    8. TWO DENSE LAYERS (512→256):
       - Combines extracted features for final classification
       - Progressive reduction allows learning of complex decisions
    
    Args:
        input_shape: Shape of input images (height, width, channels)
        num_classes: Number of output classes (4 for poultry diseases)
        l2_reg: L2 regularization coefficient
        
    Returns:
        Compiled Keras model
    """
    print("\n" + "=" * 70)
    print("STEP 5: CNN MODEL ARCHITECTURE")
    print("=" * 70)
    
    # Initialize sequential model
    model = keras.Sequential([
        # ==========================================================================
        # FIRST CONVOLUTIONAL BLOCK (32 filters)
        # ==========================================================================
        # First Conv2D layer - extracts basic features
        # 32 filters = 32 different feature detectors
        # kernel_size=(3,3) = each filter is 3x3 pixels
        layers.Conv2D(
            32, (3, 3),
            padding='same',  # Output same size as input
            kernel_regularizer=l2(l2_reg),  # L2 regularization
            input_shape=input_shape  # Only needed for first layer
        ),
        layers.BatchNormalization(),  # Normalize activations
        layers.Activation('relu'),   # ReLU activation
        
        # Second Conv2D layer - combines basic features
        layers.Conv2D(
            32, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        # MaxPooling - reduces spatial dimensions
        layers.MaxPooling2D(pool_size=(2, 2)),  # 224x224 → 112x112
        layers.Dropout(0.25),  # Drop 25% of neurons
        
        # ==========================================================================
        # SECOND CONVOLUTIONAL BLOCK (64 filters)
        # ==========================================================================
        layers.Conv2D(64, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(64, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),  # 112x112 → 56x56
        layers.Dropout(0.25),
        
        # ==========================================================================
        # THIRD CONVOLUTIONAL BLOCK (128 filters)
        # ==========================================================================
        layers.Conv2D(128, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(128, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),  # 56x56 → 28x28
        layers.Dropout(0.25),
        
        # ==========================================================================
        # FOURTH CONVOLUTIONAL BLOCK (256 filters)
        # ==========================================================================
        layers.Conv2D(256, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(256, (3, 3), padding='same', kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),  # 28x28 → 14x14
        layers.Dropout(0.25),
        
        # ==========================================================================
        # DENSE (FULLY CONNECTED) LAYERS
        # ==========================================================================
        # Flatten: Convert 2D feature maps to 1D vector
        layers.Flatten(),  # 14x14x256 = 50,176 features
        
        # First dense layer
        layers.Dense(512, kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),  # Higher dropout in dense layers
        
        # Second dense layer
        layers.Dense(256, kernel_regularizer=l2(l2_reg)),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        
        # ==========================================================================
        # OUTPUT LAYER
        # ==========================================================================
        # 4 neurons for 4 classes, softmax for probability distribution
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Print model summary
    print("\nModel Architecture:")
    print("-" * 70)
    model.summary()
    
    # Count parameters
    total_params = model.count_params()
    trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    non_trainable = total_params - trainable_params
    
    print("-" * 70)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Non-trainable parameters: {non_trainable:,}")
    print("-" * 70)
    
    return model


def compile_model(model, learning_rate=Config.INITIAL_LEARNING_RATE):
    """
    =============================================================================
    COMPILE THE MODEL
    =============================================================================
    
    Before training, we must "compile" the model, which configures:
    
    1. OPTIMIZER: How to update weights based on loss
       - Adam: Adaptive learning rates, combines Momentum and RMSprop
       - Learning rate controls step size in gradient descent
       
    2. LOSS FUNCTION: How to measure prediction error
       - Sparse Categorical Crossentropy:
         * Used when labels are integers (0, 1, 2, 3)
         * Measures difference between predicted and true probability distributions
         
    3. METRICS: What to track during training
       - Accuracy: Percentage of correct predictions
    
    Args:
        model: Keras model to compile
        learning_rate: Initial learning rate
        
    Returns:
        Compiled model
    """
    # ==========================================================================
    # Create Adam optimizer
    # ==========================================================================
    # Adam (Adaptive Moment Estimation) combines:
    # - Momentum: accelerates in relevant directions
    # - RMSProp: adapts learning rate per parameter
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    
    # ==========================================================================
    # Compile with loss and metrics
    # ==========================================================================
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',  # For integer class labels
        metrics=['accuracy']  # Track accuracy during training
    )
    
    print(f"\n[OK] Model compiled with:")
    print(f"   - Optimizer: Adam (lr={learning_rate})")
    print(f"   - Loss: Sparse Categorical Crossentropy")
    print(f"   - Metrics: Accuracy")
    
    return model


# =============================================================================
# STEP 6: MODEL TRAINING WITH CALLBACKS
# =============================================================================

def create_callbacks(output_dir):
    """
    =============================================================================
    TRAINING CALLBACKS - AUTOMATIC TRAINING CONTROL
    =============================================================================
    
    Callbacks are functions that are called at specific points during training.
    They allow for automatic adjustments and saving.
    
    1. EARLY STOPPING
       - Monitors validation accuracy
       - If no improvement for 10 epochs, stops training
       - Restores best weights (those from highest val_accuracy)
       - Prevents wasting time on overfitting model
       
    2. MODEL CHECKPOINT
       - Saves the model after each epoch (if val_accuracy improved)
       - Only keeps the best model
       - Allows loading best version after training
       
    3. REDUCE LR ON PLATEAU
       - Monitors validation loss
       - If loss stops decreasing for 5 epochs, reduces learning rate
       - Multiplies lr by 0.5 (halves it)
       - Helps fine-tune as we approach optimal solution
       - Minimum lr is 1e-6 (prevents it from becoming too small)
       
    4. CSV LOGGER
       - Records metrics after each epoch to CSV file
       - Useful for analysis and plotting later
    
    Args:
        output_dir: Where to save model checkpoints
        
    Returns:
        List of Keras callbacks
    """
    print("\n" + "=" * 70)
    print("STEP 6: TRAINING CALLBACKS")
    print("=" * 70)
    
    callbacks = [
        # ==========================================================================
        # Early Stopping - Prevent overfitting by stopping early
        # ==========================================================================
        EarlyStopping(
            monitor='val_accuracy',   # Watch validation accuracy
            patience=10,              # Stop if no improvement for 10 epochs
            restore_best_weights=True,  # Restore weights from best epoch
            verbose=1,
            mode='max'  # We want to MAXIMIZE accuracy
        ),
        
        # ==========================================================================
        # Model Checkpoint - Save best model
        # ==========================================================================
        ModelCheckpoint(
            os.path.join(output_dir, 'best_poultry_disease_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,  # Only save if val_accuracy improved
            verbose=1,
            mode='max'
        ),
        
        # ==========================================================================
        # Reduce Learning Rate - Fine-tune as training progresses
        # ==========================================================================
        ReduceLROnPlateau(
            monitor='val_loss',  # Watch validation loss
            factor=0.5,  # Multiply lr by 0.5
            patience=5,  # Wait 5 epochs with no improvement
            min_lr=Config.MIN_LEARNING_RATE,  # Floor
            verbose=1,
            mode='min'  # We want to MINIMIZE loss
        ),
        
        # ==========================================================================
        # CSV Logger - Record training history
        # ==========================================================================
        CSVLogger(
            os.path.join(output_dir, 'training_history.csv'),
            append=True  # Append if file exists
        )
    ]
    
    print("[OK] Callbacks configured:")
    print("   - EarlyStopping: patience=10, restore_best_weights=True")
    print("   - ModelCheckpoint: save best model based on val_accuracy")
    print("   - ReduceLROnPlateau: factor=0.5, patience=5")
    print("   - CSVLogger: training history saved")
    
    return callbacks


def train_model(model, train_generator, val_generator,
                epochs=Config.EPOCHS, batch_size=Config.BATCH_SIZE,
                callbacks=None, steps_per_epoch=None):
    """
    =============================================================================
    TRAIN THE MODEL
    =============================================================================
    
    This function runs the actual training process.
    
    HOW TRAINING WORKS:
    1. Forward pass: Input image → CNN → Predictions
    2. Calculate loss: Compare predictions to true labels
    3. Backward pass: Calculate gradients
    4. Update weights: Use optimizer to adjust weights
    5. Repeat for batch_size samples (one "batch")
    6. After all batches, one "epoch" is complete
    
    The validation generator evaluates the model after each epoch
    to monitor progress without affecting training.
    
    Args:
        model: Keras model to train
        train_generator: Data generator for training
        val_generator: Data generator for validation
        epochs: Maximum number of epochs
        batch_size: Samples per batch
        callbacks: List of callbacks
        steps_per_epoch: Batches per epoch (optional)
        
    Returns:
        Training history object
    """
    print("\n" + "=" * 70)
    print("STEP 7: MODEL TRAINING")
    print("=" * 70)
    
    print(f"\nTraining Configuration:")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Steps per epoch: {steps_per_epoch}")
    
    # ==========================================================================
    # Train the model
    # ==========================================================================
    # model.fit() returns a History object with training metrics
    history = model.fit(
        train_generator,      # Training data with augmentation
        validation_data=val_generator,  # Validation data (no augmentation)
        epochs=epochs,        # Maximum epochs
        callbacks=callbacks,  # Early stopping, checkpointing, etc.
        steps_per_epoch=steps_per_epoch,  # Batches per epoch
        verbose=1            # Show progress bar
    )
    
    print("\n[OK] Training completed!")
    
    return history


# =============================================================================
# STEP 8: MODEL EVALUATION
# =============================================================================

def evaluate_model(model, X_test, y_test):
    """
    =============================================================================
    BASIC MODEL EVALUATION
    =============================================================================
    
    Evaluates the model on test data and returns loss and accuracy.
    
    Args:
        model: Trained Keras model
        X_test: Test features
        y_test: Test labels
        
    Returns:
        Tuple of (test_loss, test_accuracy)
    """
    print("\n" + "=" * 70)
    print("STEP 8: MODEL EVALUATION")
    print("=" * 70)
    
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=1)
    
    print(f"\nTest Results:")
    print(f"  - Loss: {test_loss:.4f}")
    print(f"  - Accuracy: {test_accuracy:.4f}")
    
    return test_loss, test_accuracy


def comprehensive_evaluation(model, X_test, y_test, class_labels=Config.CLASS_LABELS, output_dir=None):
    """
    =============================================================================
    COMPREHENSIVE MODEL EVALUATION
    =============================================================================
    
    This function performs detailed evaluation with multiple metrics:
    
    1. ACCURACY
       - Overall percentage of correct predictions
       - Simple but can be misleading with imbalanced classes
       
    2. PRECISION
       - Of all positive predictions, how many were correct?
       - High precision = low false positive rate
       
    3. RECALL (Sensitivity)
       - Of all actual positives, how many did we find?
       - High recall = low false negative rate
       
    4. F1-SCORE
       - Harmonic mean of precision and recall
       - Best single metric for imbalanced classes
       
    5. CONFUSION MATRIX
       - Shows true vs predicted for each class
       - Helps identify which classes are confused
       
    6. ROC-AUC
       - Area under Receiver Operating Characteristic curve
       - Measures ability to distinguish between classes
       - 1.0 = perfect, 0.5 = random
    
    Args:
        model: Trained Keras model
        X_test: Test features
        y_test: Test labels
        class_labels: Dictionary mapping indices to names
        output_dir: Directory for saving plots
        
    Returns:
        Dictionary with all evaluation metrics
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("=" * 70)
    
    # ==========================================================================
    # Get predictions
    # ==========================================================================
    # Predict probabilities for each class
    y_pred_proba = model.predict(X_test, verbose=0)
    # Get class with highest probability
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    results = {}
    
    # ==========================================================================
    # 1. Overall Accuracy
    # ==========================================================================
    test_accuracy = accuracy_score(y_test, y_pred)
    results['accuracy'] = test_accuracy
    print(f"\n1. ACCURACY: {test_accuracy:.4f}")
    
    # ==========================================================================
    # 2. Precision, Recall, F1-Score (per-class and weighted)
    # ==========================================================================
    # average=None: Returns array for each class
    # average='weighted': Weights by class frequency
    precision_per_class = precision_score(y_test, y_pred, average=None)
    recall_per_class = recall_score(y_test, y_pred, average=None)
    f1_per_class = f1_score(y_test, y_pred, average=None)
    
    precision_weighted = precision_score(y_test, y_pred, average='weighted')
    recall_weighted = recall_score(y_test, y_pred, average='weighted')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    results['precision_per_class'] = dict(zip(class_labels.values(), precision_per_class))
    results['recall_per_class'] = dict(zip(class_labels.values(), recall_per_class))
    results['f1_per_class'] = dict(zip(class_labels.values(), f1_per_class))
    results['precision_weighted'] = precision_weighted
    results['recall_weighted'] = recall_weighted
    results['f1_weighted'] = f1_weighted
    
    print(f"\n2. PER-CLASS METRICS:")
    print(f"   {'Class':<15} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
    print(f"   {'-'*50}")
    for idx, label in class_labels.items():
        print(f"   {label:<15} {precision_per_class[idx]:>10.4f} "
              f"{recall_per_class[idx]:>10.4f} {f1_per_class[idx]:>10.4f}")
    
    print(f"\n   Weighted Average:")
    print(f"   Precision: {precision_weighted:.4f}")
    print(f"   Recall: {recall_weighted:.4f}")
    print(f"   F1-Score: {f1_weighted:.4f}")
    
    # ==========================================================================
    # 3. Confusion Matrix
    # ==========================================================================
    cm = confusion_matrix(y_test, y_pred)
    results['confusion_matrix'] = cm
    
    print(f"\n3. CONFUSION MATRIX:")
    print(f"   Predicted ->", end='')
    for label in class_labels.values():
        print(f" {label:>12}", end='')
    print()
    for i, label in class_labels.items():
        print(f"   Actual {label:<10}", end='')
        for j in range(len(class_labels)):
            print(f" {cm[i, j]:>12}", end='')
        print()
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=list(class_labels.values()),
                yticklabels=list(class_labels.values()),
                annot_kws={'size': 12})
    plt.title('Confusion Matrix - Poultry Disease Classification', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.tight_layout()
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=150)
    plt.show()
    print(f"\n   [OK] Confusion matrix saved")
    
    # ==========================================================================
    # 4. ROC-AUC
    # ==========================================================================
    print(f"\n4. ROC-AUC (One-vs-Rest):")
    try:
        # One-vs-Rest: Treats each class as positive, others as negative
        roc_auc_ovr = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        # One-vs-One: Treats each pair of classes separately
        roc_auc_ovo = roc_auc_score(y_test, y_pred_proba, multi_class='ovo', average='weighted')
        
        results['roc_auc_ovr'] = roc_auc_ovr
        results['roc_auc_ovo'] = roc_auc_ovo
        
        print(f"   One-vs-Rest (Weighted): {roc_auc_ovr:.4f}")
        print(f"   One-vs-One (Weighted): {roc_auc_ovo:.4f}")
        
        # Per-class ROC-AUC
        print(f"\n   Per-Class ROC-AUC:")
        for i, label in class_labels.items():
            y_test_binary = (y_test == i).astype(int)
            roc_auc_class = roc_auc_score(y_test_binary, y_pred_proba[:, i])
            print(f"   {label}: {roc_auc_class:.4f}")
        
        # Plot ROC curves
        plot_roc_curves(y_test, y_pred_proba, class_labels, output_dir)
        
    except Exception as e:
        print(f"   [WARNING] Error computing ROC-AUC: {e}")
        results['roc_auc_ovr'] = None
        results['roc_auc_ovo'] = None
    
    # ==========================================================================
    # 5. Classification Report
    # ==========================================================================
    print(f"\n5. FULL CLASSIFICATION REPORT:")
    report = classification_report(y_test, y_pred, target_names=list(class_labels.values()))
    print(report)
    results['classification_report'] = report
    
    return results


def plot_roc_curves(y_true, y_pred_proba, class_labels, output_dir=None):
    """
    =============================================================================
    PLOT ROC CURVES
    =============================================================================
    
    ROC (Receiver Operating Characteristic) curve shows:
    - True Positive Rate (y-axis) vs False Positive Rate (x-axis)
    - At various classification thresholds
    
    AUC = Area Under Curve
    - 1.0 = perfect classifier
    - 0.5 = random guessing
    - Higher is better
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        class_labels: Class name mapping
        output_dir: Save location
    """
    plt.figure(figsize=(10, 8))
    
    # Plot ROC curve for each class
    for i, label in class_labels.items():
        # Convert to binary: this class vs all others
        y_test_binary = (y_true == i).astype(int)
        
        # Calculate ROC curve
        fpr, tpr, _ = roc_curve(y_test_binary, y_pred_proba[:, i])
        roc_auc = roc_auc_score(y_test_binary, y_pred_proba[:, i])
        
        plt.plot(fpr, tpr, label=f'{label} (AUC = {roc_auc:.4f})', linewidth=2)
    
    # Diagonal line = random classifier
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves (One-vs-Rest) - Poultry Disease Classification', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'roc_curves.png'), dpi=150)
    plt.show()
    print(f"   [OK] ROC curves saved")


# =============================================================================
# STEP 9: VISUALIZATIONS
# =============================================================================

def plot_training_history(history, output_dir=None):
    """
    =============================================================================
    PLOT TRAINING HISTORY
    =============================================================================
    
    This function visualizes how the model improved during training.
    
    Key things to look for:
    
    1. ACCURACY PLOT:
       - Training and validation should both increase
       - Large gap = overfitting
       - Validation > training sometimes = underfitting
       
    2. LOSS PLOT:
       - Both should decrease
       - Training loss much lower than validation = overfitting
       - Both increasing = something wrong
    
    Args:
        history: Keras History object
        output_dir: Save location
    """
    print("\n" + "=" * 70)
    print("STEP 9: TRAINING HISTORY VISUALIZATION")
    print("=" * 70)
    
    # Get metrics from history
    history_dict = history.history
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # ==========================================================================
    # Plot Accuracy
    # ==========================================================================
    ax1.plot(history_dict['accuracy'], label='Training Accuracy', linewidth=2)
    ax1.plot(history_dict['val_accuracy'], label='Validation Accuracy', linewidth=2)
    ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Accuracy', fontsize=12)
    ax1.legend(loc='lower right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # ==========================================================================
    # Plot Loss
    # ==========================================================================
    ax2.plot(history_dict['loss'], label='Training Loss', linewidth=2)
    ax2.plot(history_dict['val_loss'], label='Validation Loss', linewidth=2)
    ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Loss', fontsize=12)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('Training History - Poultry Disease Classification', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'training_history.png'), dpi=150)
    plt.show()
    print("[OK] Training history plot saved")


def detect_overfitting(history, output_dir=None):
    """
    =============================================================================
    OVERFITTING DETECTION
    =============================================================================
    
    This function analyzes the training history to detect overfitting or underfitting.
    
    OVERFITTING:
    - Training accuracy much higher than validation accuracy
    - Training loss much lower than validation loss
    - Model memorizes training data but doesn't generalize
    
    UNDERFITTING:
    - Both training and validation accuracy are low
    - Model hasn't learned the patterns
    
    GOOD FIT:
    - Training and validation metrics are close
    - Both improve together
    
    Args:
        history: Keras History object
        output_dir: Save location
        
    Returns:
        Dictionary with analysis results
    """
    print("\n" + "=" * 70)
    print("OVERFITTING/UNDERFITTING DETECTION")
    print("=" * 70)
    
    # Get metrics
    train_acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    train_loss = history.history['loss']
    val_loss = history.history['val_loss']
    
    results = {}
    
    # Calculate final metrics
    final_train_acc = train_acc[-1]
    final_val_acc = val_acc[-1]
    final_train_loss = train_loss[-1]
    final_val_loss = val_loss[-1]
    
    # Gap analysis - key indicators
    acc_gap = final_train_acc - final_val_acc
    loss_gap = final_val_loss - final_train_loss
    
    results['final_train_accuracy'] = final_train_acc
    results['final_val_accuracy'] = final_val_acc
    results['final_train_loss'] = final_train_loss
    results['final_val_loss'] = final_val_loss
    results['accuracy_gap'] = acc_gap
    results['loss_gap'] = loss_gap
    
    print(f"\nFinal Training Metrics:")
    print(f"   Training Accuracy: {final_train_acc:.4f}")
    print(f"   Validation Accuracy: {final_val_acc:.4f}")
    print(f"   Training Loss: {final_train_loss:.4f}")
    print(f"   Validation Loss: {final_val_loss:.4f}")
    
    print(f"\nGap Analysis:")
    print(f"   Accuracy Gap (Train - Val): {acc_gap:.4f}")
    print(f"   Loss Gap (Val - Train): {loss_gap:.4f}")
    
    # ==========================================================================
    # Diagnosis
    # ==========================================================================
    print(f"\nDiagnosis:")
    
    if acc_gap > 0.15 and loss_gap > 0.1:
        print("   [WARNING] OVERFITTING DETECTED!")
        print("   The model is memorizing training data but not generalizing well.")
        print("   Suggestions:")
        print("   - Increase dropout rate")
        print("   - Add more regularization (L1/L2)")
        print("   - Use data augmentation")
        print("   - Reduce model complexity")
        print("   - Collect more training data")
        results['diagnosis'] = 'overfitting'
    elif acc_gap < -0.1:
        print("   [WARNING] UNDERFITTING DETECTED!")
        print("   The model is not learning the training data well.")
        print("   Suggestions:")
        print("   - Increase model complexity")
        print("   - Train for more epochs")
        print("   - Reduce regularization")
        print("   - Check data quality")
        results['diagnosis'] = 'underfitting'
    else:
        print("   [OK] MODEL APPEARS WELL-FITTED!")
        print("   Training and validation metrics are reasonably close.")
        results['diagnosis'] = 'good_fit'
    
    # ==========================================================================
    # Plot overfitting detection
    # ==========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy plot with gap visualization
    ax1.plot(train_acc, label='Training Accuracy', linewidth=2)
    ax1.plot(val_acc, label='Validation Accuracy', linewidth=2)
    ax1.fill_between(range(len(train_acc)), train_acc, val_acc, 
                     alpha=0.3, color='red' if acc_gap > 0.15 else 'green')
    ax1.set_title('Accuracy: Overfitting Detection', fontsize=12)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Loss plot with gap visualization
    ax2.plot(train_loss, label='Training Loss', linewidth=2)
    ax2.plot(val_loss, label='Validation Loss', linewidth=2)
    ax2.fill_between(range(len(train_loss)), train_loss, val_loss,
                     alpha=0.3, color='red' if loss_gap > 0.1 else 'green')
    ax2.set_title('Loss: Overfitting Detection', fontsize=12)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'overfitting_detection.png'), dpi=150)
    plt.show()
    print("\n   [OK] Overfitting detection plot saved")
    
    return results


def visualize_feature_maps(model, X_sample, layer_name=None, output_dir=None):
    """
    =============================================================================
    VISUALIZE FEATURE MAPS
    =============================================================================
    
    This function shows what features the CNN is detecting at each layer.
    
    Feature maps are 2D arrays showing the activation of each filter.
    - Early layers detect edges, colors, textures
    - Later layers detect more complex patterns
    
    This helps understand what the model is "looking at."
    
    Args:
        model: Trained Keras model
        X_sample: Sample image(s) for visualization
        layer_name: Name of layer to visualize (optional)
        output_dir: Save location
    """
    print("\n" + "=" * 70)
    print("FEATURE MAP VISUALIZATION")
    print("=" * 70)
    
    # ==========================================================================
    # Create feature extraction model
    # ==========================================================================
    # Get outputs of all convolutional layers
    layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name.lower()]
    
    # Create new model that outputs feature maps
    feature_model = keras.Model(inputs=model.input, outputs=layer_outputs)
    
    # Get feature maps for sample image
    features = feature_model.predict(X_sample)
    
    # Visualize first conv layer's feature maps
    if features:
        first_conv_features = features[0]
        n_filters = min(16, first_conv_features.shape[-1])
        
        fig, axes = plt.subplots(4, 4, figsize=(12, 12))
        axes = axes.flatten()
        
        for i in range(n_filters):
            ax = axes[i]
            # Show the feature map
            ax.imshow(first_conv_features[0, :, :, i], cmap='viridis')
            ax.set_title(f'Filter {i+1}', fontsize=8)
            ax.axis('off')
        
        plt.suptitle('Feature Maps - First Convolutional Layer', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(os.path.join(output_dir, 'feature_maps.png'), dpi=150)
        plt.show()
        print("[OK] Feature maps visualization saved")


def visualize_misclassified_examples(model, X_test, y_test, 
                                      class_labels=Config.CLASS_LABELS,
                                      output_dir=None, n_examples=8):
    """
    =============================================================================
    VISUALIZE MISCLASSIFIED EXAMPLES
    =============================================================================
    
    This function shows images that were incorrectly classified.
    
    Analyzing misclassifications helps:
    - Identify confusing classes
    - Find data quality issues
    - Understand model limitations
    
    Args:
        model: Trained model
        X_test: Test images
        y_test: True labels
        class_labels: Label mapping
        output_dir: Save location
        n_examples: Number to display
    """
    print("\n" + "=" * 70)
    print("MISCLASSIFIED EXAMPLES VISUALIZATION")
    print("=" * 70)
    
    # Get predictions
    y_pred_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Find misclassified indices
    misclassified_idx = np.where(y_pred != y_test)[0]
    
    if len(misclassified_idx) == 0:
        print("[OK] No misclassified examples!")
        return
    
    print(f"Found {len(misclassified_idx)} misclassified examples out of {len(y_test)}")
    
    # Select examples to display
    n_display = min(n_examples, len(misclassified_idx))
    selected_idx = misclassified_idx[:n_display]
    
    # Create visualization
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    for i, idx in enumerate(selected_idx):
        ax = axes[i]
        
        # Get image
        img = X_test[idx]
        
        # Display
        ax.imshow(img)
        
        # Get labels
        true_label = class_labels[y_test[idx]]
        pred_label = class_labels[y_pred[idx]]
        confidence = y_pred_proba[idx][y_pred[idx]]
        
        # Set title with color
        title_color = 'red'
        ax.set_title(f'True: {true_label}\nPred: {pred_label}\nConf: {confidence:.2f}',
                    color=title_color, fontsize=9)
        ax.axis('off')
    
    plt.suptitle('Misclassified Examples', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'misclassified_examples.png'), dpi=150)
    plt.show()
    print("[OK] Misclassified examples visualization saved")


# =============================================================================
# STEP 10: SAVE MODEL
# =============================================================================

def save_model(model, output_dir, model_name=Config.MODEL_NAME):
    """
    =============================================================================
    SAVE TRAINED MODEL
    =============================================================================
    
    Saves the trained model in Keras format (.keras).
    
    The .keras format:
    - Includes model architecture
    - Includes model weights
    - Includes optimizer state (can resume training)
    - Recommended format for TensorFlow/Keras
    
    Args:
        model: Trained Keras model
        output_dir: Save directory
        model_name: Filename
        
    Returns:
        Path to saved model
    """
    print("\n" + "=" * 70)
    print("STEP 10: MODEL SAVING")
    print("=" * 70)
    
    model_path = os.path.join(output_dir, model_name)
    model.save(model_path)
    
    print(f"[OK] Model saved to: {model_path}")
    print(f"   Model size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    return model_path


# =============================================================================
# MAIN PIPELINE - ORCHESTRATES ALL STEPS
# =============================================================================

def run_pipeline():
    """
    =============================================================================
    MAIN PIPELINE - RUNS ALL STEPS IN ORDER
    =============================================================================
    
    This is the main function that orchestrates the entire pipeline.
    It calls each function in the correct order to:
    
    1. Load and explore data
    2. Preprocess images
    3. Apply augmentation
    4. Split data
    5. Build model
    6. Train model
    7. Evaluate model
    8. Visualize results
    9. Save model
    
    Returns:
        Tuple of (model, history, results)
    """
    print("\n" + "=" * 70)
    print("POULTRY DISEASE CLASSIFICATION - CNN TRAINING PIPELINE")
    print("=" * 70)
    print(f"\nDataset: {Config.DATA_DIR}")
    print(f"Classes: {list(Config.CLASS_LABELS.values())}")
    print(f"Image Size: {Config.IMG_HEIGHT}x{Config.IMG_WIDTH}")
    print(f"Output Directory: {Config.OUTPUT_DIR}")
    
    # ==========================================================================
    # STEP 1: Data Loading and Exploration
    # ==========================================================================
    stats = load_dataset_exploration(Config.DATA_DIR)
    
    # ==========================================================================
    # STEP 2: Image Preprocessing
    # ==========================================================================
    # Create reverse mapping (class name -> index)
    class_to_idx = {v: k for k, v in Config.CLASS_LABELS.items()}
    
    X, y = load_and_preprocess_dataset(
        Config.DATA_DIR,
        class_to_idx,
        img_size=(Config.IMG_HEIGHT, Config.IMG_WIDTH)
    )
    
    # ==========================================================================
    # STEP 3: Data Augmentation
    # ==========================================================================
    train_datagen, val_datagen = create_data_augmentation()
    
    # Visualize augmentations on a sample image
    visualize_augmentations(
        X[0], 
        train_datagen,
        os.path.join(Config.OUTPUT_DIR, 'augmentation_examples.png')
    )
    
    # ==========================================================================
    # STEP 4: Data Splitting
    # ==========================================================================
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        X, y,
        train_ratio=Config.TRAIN_RATIO,
        val_ratio=Config.VAL_RATIO,
        test_ratio=Config.TEST_RATIO
    )
    
    # Save split data
    save_split_data(X_train, X_val, X_test, y_train, y_val, y_test, Config.OUTPUT_DIR)
    
    # Create data generators for training
    train_generator = train_datagen.flow(
        X_train, y_train,
        batch_size=Config.BATCH_SIZE,
        shuffle=True
    )
    
    val_generator = val_datagen.flow(
        X_val, y_val,
        batch_size=Config.BATCH_SIZE,
        shuffle=False
    )
    
    # ==========================================================================
    # STEP 5: Build CNN Model
    # ==========================================================================
    model = build_cnn_model()
    model = compile_model(model)
    
    # ==========================================================================
    # STEP 6: Training Callbacks
    # ==========================================================================
    callbacks = create_callbacks(Config.OUTPUT_DIR)
    
    # ==========================================================================
    # STEP 7: Train Model
    # ==========================================================================
    history = train_model(
        model,
        train_generator,
        val_generator,
        epochs=Config.EPOCHS,
        batch_size=Config.BATCH_SIZE,
        callbacks=callbacks,
        steps_per_epoch=len(X_train) // Config.BATCH_SIZE
    )
    
    # ==========================================================================
    # STEP 8: Evaluate Model
    # ==========================================================================
    test_loss, test_accuracy = evaluate_model(model, X_test, y_test)
    
    # Comprehensive evaluation
    results = comprehensive_evaluation(
        model, X_test, y_test,
        class_labels=Config.CLASS_LABELS,
        output_dir=Config.OUTPUT_DIR
    )
    
    # ==========================================================================
    # STEP 9: Visualizations
    # ==========================================================================
    plot_training_history(history, Config.OUTPUT_DIR)
    
    # Overfitting detection
    overfitting_results = detect_overfitting(history, Config.OUTPUT_DIR)
    
    # Feature maps visualization (using a sample)
    visualize_feature_maps(model, X_test[:1], output_dir=Config.OUTPUT_DIR)
    
    # Misclassified examples
    visualize_misclassified_examples(
        model, X_test, y_test,
        class_labels=Config.CLASS_LABELS,
        output_dir=Config.OUTPUT_DIR
    )
    
    # ==========================================================================
    # STEP 10: Save Model
    # ==========================================================================
    model_path = save_model(model, Config.OUTPUT_DIR)
    
    # ==========================================================================
    # Final Summary
    # ==========================================================================
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\n[INFO] Final Results:")
    print(f"   - Test Accuracy: {test_accuracy:.4f}")
    print(f"   - Test Loss: {test_loss:.4f}")
    print(f"   - Weighted F1-Score: {results.get('f1_weighted', 'N/A')}")
    print(f"   - ROC-AUC (OvR): {results.get('roc_auc_ovr', 'N/A')}")
    print(f"\n[INFO] Overfitting Detection:")
    print(f"   - Diagnosis: {overfitting_results.get('diagnosis', 'N/A')}")
    print(f"   - Accuracy Gap: {overfitting_results.get('accuracy_gap', 'N/A'):.4f}")
    print(f"   - Loss Gap: {overfitting_results.get('loss_gap', 'N/A'):.4f}")
    print(f"\n[INFO] Output Files:")
    print(f"   - Model: {model_path}")
    print(f"   - Training History: {os.path.join(Config.OUTPUT_DIR, 'training_history.csv')}")
    print(f"   - Plots: {Config.OUTPUT_DIR}/*.png")
    print("=" * 70)
    
    return model, history, results


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    """
    =============================================================================
    SCRIPT ENTRY POINT
    =============================================================================
    
    When this script is run directly (not imported), execute the pipeline.
    """
    # Run the complete pipeline
    model, history, results = run_pipeline()
