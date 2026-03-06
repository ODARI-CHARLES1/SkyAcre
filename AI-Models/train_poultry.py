"""
Poultry Disease Classification - CNN Training Pipeline

This script provides a complete image preprocessing and CNN model training pipeline
for multi-class poultry disease classification. It mirrors the architecture and 
methodology implemented for the cattle disease identification project.

Dataset: Poultry Diseases Image Dataset
Classes: cocci (Coccidiosis), healthy, ncd (Newcastle Disease), salmo (Salmonella)
Total Images: 6,812

Usage:
    python train_poultry.py
    
Requirements:
    - TensorFlow 2.x
    - NumPy
    - Pandas
    - Matplotlib
    - Seaborn
    - Scikit-learn
    - OpenCV (cv2)
    - Pillow

Author: SkyAcre AI Team
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
    EarlyStopping, 
    ModelCheckpoint, 
    ReduceLROnPlateau,
    CSVLogger
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.regularizers import l2

# Sklearn imports
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix, 
    classification_report,
    roc_auc_score, 
    roc_curve,
    accuracy_score
)

# Image processing
import cv2
from PIL import Image

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Configuration settings for the poultry disease classification pipeline."""
    
    # Dataset paths
    DATA_DIR = 'AI-Models/Data/poultry_diseases'
    OUTPUT_DIR = 'AI-Models/Output/poultry'
    
    # Image parameters
    IMG_HEIGHT = 224
    IMG_WIDTH = 224
    CHANNELS = 3  # RGB
    
    # Training parameters
    BATCH_SIZE = 32
    EPOCHS = 50
    INITIAL_LEARNING_RATE = 0.001
    MIN_LEARNING_RATE = 1e-6
    
    # Class labels mapping
    CLASS_LABELS = {
        0: 'cocci',      # Coccidiosis
        1: 'healthy',    # Healthy
        2: 'ncd',        # Newcastle Disease
        3: 'salmo'       # Salmonella
    }
    
    NUM_CLASSES = len(CLASS_LABELS)
    
    # Data split ratios
    TRAIN_RATIO = 0.7
    VAL_RATIO = 0.15
    TEST_RATIO = 0.15
    
    # Model output
    MODEL_NAME = 'poultry_disease_model.keras'
    HISTORY_NAME = 'training_history.csv'

# Create output directory
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# =============================================================================
# STEP 1: DATA LOADING AND EXPLORATION
# =============================================================================

def load_dataset_exploration(data_dir):
    """
    Load and explore the poultry disease dataset.
    
    This function:
    - Counts images per class
    - Analyzes image properties (dimensions, channels)
    - Reports class distribution
    - Checks for corrupt images
    
    Args:
        data_dir: Path to the dataset directory
        
    Returns:
        Dictionary containing dataset statistics
    """
    print("=" * 70)
    print("STEP 1: DATA LOADING AND EXPLORATION")
    print("=" * 70)
    
    data_dir = Path(data_dir)
    stats = {
        'total_images': 0,
        'class_counts': {},
        'image_sizes': [],
        'corrupt_images': [],
        'valid_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    }
    
    # Get all class directories
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    class_dirs = sorted(class_dirs)
    
    print(f"\nDataset Location: {data_dir}")
    print(f"Found {len(class_dirs)} classes: {[d.name for d in class_dirs]}")
    print("\n" + "-" * 70)
    
    for class_dir in class_dirs:
        class_name = class_dir.name
        images = [f for f in class_dir.iterdir() 
                  if f.suffix.lower() in stats['valid_extensions']]
        
        stats['class_counts'][class_name] = len(images)
        stats['total_images'] += len(images)
        
        print(f"\nClass: {class_name}")
        print(f"  - Image count: {len(images)}")
        
        # Analyze sample images
        sample_count = min(5, len(images))
        for img_path in images[:sample_count]:
            try:
                img = cv2.imread(str(img_path))
                if img is not None:
                    h, w, c = img.shape
                    stats['image_sizes'].append((h, w, c))
                    if (h, w, c) == stats['image_sizes'][0]:
                        pass  # Same size as first
                else:
                    stats['corrupt_images'].append(str(img_path))
            except Exception as e:
                stats['corrupt_images'].append(str(img_path))
    
    # Calculate class distribution percentages
    print("\n" + "-" * 70)
    print("CLASS DISTRIBUTION:")
    print("-" * 70)
    print(f"{'Class':<15} {'Count':>10} {'Percentage':>15}")
    print("-" * 70)
    
    for class_name, count in stats['class_counts'].items():
        percentage = (count / stats['total_images']) * 100
        print(f"{class_name:<15} {count:>10} {percentage:>14.2f}%")
    
    print("-" * 70)
    print(f"{'TOTAL':<15} {stats['total_images']:>10} {'100.00%':>15}")
    
    # Report image size analysis
    if stats['image_sizes']:
        unique_sizes = set(stats['image_sizes'])
        print(f"\nImage Size Analysis:")
        print(f"  - Unique sizes found: {len(unique_sizes)}")
        print(f"  - Sample sizes: {list(unique_sizes)[:5]}")
    
    # Report corrupt images
    if stats['corrupt_images']:
        print(f"\n⚠️  WARNING: Found {len(stats['corrupt_images'])} corrupt images!")
    else:
        print(f"\n✅ All images are valid and readable.")
    
    # Visualize class distribution
    plt.figure(figsize=(10, 6))
    classes = list(stats['class_counts'].keys())
    counts = list(stats['class_counts'].values())
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    bars = plt.bar(classes, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    plt.xlabel('Disease Class', fontsize=12)
    plt.ylabel('Number of Images', fontsize=12)
    plt.title('Poultry Disease Dataset - Class Distribution', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(Config.OUTPUT_DIR, 'class_distribution.png'), dpi=150)
    plt.show()
    print(f"\n✅ Class distribution plot saved to {Config.OUTPUT_DIR}/class_distribution.png")
    
    return stats


# =============================================================================
# STEP 2: IMAGE PREPROCESSING
# =============================================================================

def preprocess_image(image, target_size=(Config.IMG_HEIGHT, Config.IMG_WIDTH)):
    """
    Preprocess a single image for model input.
    
    Preprocessing steps:
    1. Read image using OpenCV
    2. Resize to target dimensions
    3. Convert BGR to RGB (OpenCV uses BGR)
    4. Normalize pixel values to [0, 1]
    
    Args:
        image: Input image (file path, numpy array, or PIL Image)
        target_size: Target (height, width) for resizing
        
    Returns:
        Preprocessed image as numpy array
    """
    # Load image
    if isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise ValueError(f"Could not load image: {image}")
    elif isinstance(image, np.ndarray):
        img = image
    else:
        img = np.array(image)
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to target size
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    return img


def load_and_preprocess_dataset(data_dir, class_labels, img_size=(Config.IMG_HEIGHT, Config.IMG_WIDTH)):
    """
    Load and preprocess the entire dataset.
    
    Args:
        data_dir: Path to dataset directory
        class_labels: Dictionary mapping class names to indices
        img_size: Target image size
        
    Returns:
        Tuple of (X, y) arrays
    """
    print("\n" + "=" * 70)
    print("STEP 2: IMAGE PREPROCESSING")
    print("=" * 70)
    
    data_dir = Path(data_dir)
    images = []
    labels = []
    
    for class_name, class_idx in class_labels.items():
        class_dir = data_dir / class_name
        print(f"\nProcessing class: {class_name} (index: {class_idx})")
        
        # Get all image files
        image_files = list(class_dir.glob('*.jpg')) + \
                     list(class_dir.glob('*.jpeg')) + \
                     list(class_dir.glob('*.png')) + \
                     list(class_dir.glob('*.bmp'))
        
        for i, img_path in enumerate(image_files):
            try:
                img = preprocess_image(str(img_path), img_size)
                images.append(img)
                labels.append(class_idx)
                
                if (i + 1) % 500 == 0:
                    print(f"  Processed {i + 1}/{len(image_files)} images...")
            except Exception as e:
                print(f"  ⚠️  Error processing {img_path}: {e}")
        
        print(f"  Completed: {len(image_files)} images")
    
    X = np.array(images)
    y = np.array(labels)
    
    print(f"\n✅ Preprocessing complete!")
    print(f"   Total images: {len(X)}")
    print(f"   Image shape: {X[0].shape}")
    print(f"   Data type: {X.dtype}")
    print(f"   Value range: [{X.min():.4f}, {X.max():.4f}]")
    
    return X, y


# =============================================================================
# STEP 3: DATA AUGMENTATION
# =============================================================================

def create_data_augmentation():
    """
    Create data augmentation pipeline for training data.
    
    Augmentation techniques:
    - Random rotation (20 degrees)
    - Random horizontal/vertical flipping
    - Random brightness adjustment
    - Random zoom
    - Random shear
    - Channel shift
    
    Returns:
        ImageDataGenerator for training
    """
    print("\n" + "=" * 70)
    print("STEP 3: DATA AUGMENTATION")
    print("=" * 70)
    
    # Create training data generator with augmentation
    train_datagen = ImageDataGenerator(
        # Rotation
        rotation_range=20,
        
        # Flipping
        horizontal_flip=True,
        vertical_flip=True,
        
        # Brightness and contrast
        brightness_range=[0.8, 1.2],
        contrast_range=[0.8, 1.2],
        
        # Zoom
        zoom_range=[0.9, 1.1],
        
        # Shear
        shear_range=0.15,
        
        # Channel shift
        channel_shift_range=0.1,
        
        # Fill mode
        fill_mode='nearest',
        
        # Normalization (already done in preprocessing)
        rescale=None
    )
    
    # Validation/test data generator (no augmentation, just normalization)
    val_datagen = ImageDataGenerator()
    
    print("✅ Data augmentation pipeline created:")
    print("   - Random rotation: ±20 degrees")
    print("   - Random horizontal/vertical flipping")
    print("   - Random brightness adjustment: 0.8-1.2")
    print("   - Random zoom: 0.9-1.1")
    print("   - Random shear: 0.15")
    print("   - Channel shift: 0.1")
    
    return train_datagen, val_datagen


def visualize_augmentations(sample_image, train_datagen, save_path=None):
    """
    Visualize the effect of data augmentation on a sample image.
    
    Args:
        sample_image: Input image array
        train_datagen: ImageDataGenerator
        save_path: Path to save visualization
    """
    print("\n   Generating augmentation visualization...")
    
    # Reshape for generator
    sample_image = np.expand_dims(sample_image, axis=0)
    
    # Create figure
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    # Original image
    axes[0].imshow(sample_image[0])
    axes[0].set_title('Original', fontsize=10)
    axes[0].axis('off')
    
    # Generate augmented images
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
        print(f"   ✅ Augmentation visualization saved to {save_path}")
    
    plt.show()


# =============================================================================
# STEP 4: DATA SPLITTING
# =============================================================================

def split_data(X, y, train_ratio=Config.TRAIN_RATIO, 
               val_ratio=Config.VAL_RATIO, test_ratio=Config.TEST_RATIO,
               random_state=42):
    """
    Split data into training, validation, and test sets with stratification.
    
    Args:
        X: Feature array
        y: Label array
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for test
        random_state: Random seed
        
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    print("\n" + "=" * 70)
    print("STEP 4: DATA SPLITTING (WITH STRATIFICATION)")
    print("=" * 70)
    
    # First split: training + (validation + test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(val_ratio + test_ratio),
        random_state=random_state,
        stratify=y
    )
    
    # Second split: validation + test
    val_test_ratio = test_ratio / (val_ratio + test_ratio)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=val_test_ratio,
        random_state=random_state,
        stratify=y_temp
    )
    
    print(f"\nData Split Summary:")
    print(f"  - Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  - Validation set: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  - Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Show class distribution in each split
    print(f"\nClass Distribution (Stratified):")
    print(f"  {'Class':<15} {'Train':>8} {'Val':>8} {'Test':>8}")
    print(f"  {'-'*40}")
    
    unique, counts = np.unique(y_train, return_counts=True)
    train_dist = dict(zip(unique, counts))
    unique, counts = np.unique(y_val, return_counts=True)
    val_dist = dict(zip(unique, counts))
    unique, counts = np.unique(y_test, return_counts=True)
    test_dist = dict(zip(unique, counts))
    
    for class_idx, class_name in Config.CLASS_LABELS.items():
        print(f"  {class_name:<15} {train_dist.get(class_idx, 0):>8} "
              f"{val_dist.get(class_idx, 0):>8} {test_dist.get(class_idx, 0):>8}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def save_split_data(X_train, X_val, X_test, y_train, y_val, y_test, output_dir):
    """
    Save the split data as numpy arrays for later use.
    
    Args:
        X_train, X_val, X_test: Feature arrays
        y_train, y_val, y_test: Label arrays
        output_dir: Output directory
    """
    np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(output_dir, 'X_val.npy'), X_val)
    np.save(os.path.join(output_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
    np.save(os.path.join(output_dir, 'y_val.npy'), y_val)
    np.save(os.path.join(output_dir, 'y_test.npy'), y_test)
    print(f"\n✅ Split data saved to {output_dir}")


# =============================================================================
# STEP 5: CNN MODEL ARCHITECTURE
# =============================================================================

def build_cnn_model(input_shape=(Config.IMG_HEIGHT, Config.IMG_WIDTH, Config.CHANNELS),
                    num_classes=Config.NUM_CLASSES,
                    l2_reg=0.001):
    """
    Build a CNN model for multi-class poultry disease classification.
    
    Architecture:
    - 4 convolutional blocks with increasing filter sizes (32→64→128→256)
    - Each block: Conv2D → BatchNorm → ReLU → Conv2D → BatchNorm → ReLU → MaxPool → Dropout
    - Dense layers: 512 → 256 → num_classes
    - Regularization: L2 weight decay, Dropout, BatchNormalization
    
    Args:
        input_shape: Shape of input images
        num_classes: Number of output classes
        l2_reg: L2 regularization coefficient
        
    Returns:
        Compiled Keras model
    """
    print("\n" + "=" * 70)
    print("STEP 5: CNN MODEL ARCHITECTURE")
    print("=" * 70)
    
    model = keras.Sequential([
        # =====================================================================
        # First Convolutional Block (32 filters)
        # =====================================================================
        layers.Conv2D(
            32, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg),
            input_shape=input_shape
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(
            32, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # =====================================================================
        # Second Convolutional Block (64 filters)
        # =====================================================================
        layers.Conv2D(
            64, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(
            64, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # =====================================================================
        # Third Convolutional Block (128 filters)
        # =====================================================================
        layers.Conv2D(
            128, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(
            128, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # =====================================================================
        # Fourth Convolutional Block (256 filters)
        # =====================================================================
        layers.Conv2D(
            256, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        
        layers.Conv2D(
            256, (3, 3),
            padding='same',
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # =====================================================================
        # Dense Layers
        # =====================================================================
        layers.Flatten(),
        
        layers.Dense(
            512,
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        
        layers.Dense(
            256,
            kernel_regularizer=l2(l2_reg)
        ),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        
        # =====================================================================
        # Output Layer
        # =====================================================================
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
    Compile the model with optimizer, loss function, and metrics.
    
    Args:
        model: Keras model to compile
        learning_rate: Initial learning rate
        
    Returns:
        Compiled model
    """
    # Create optimizer with custom learning rate schedule
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    
    # Compile model
    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"\n✅ Model compiled with:")
    print(f"   - Optimizer: Adam (lr={learning_rate})")
    print(f"   - Loss: Sparse Categorical Crossentropy")
    print(f"   - Metrics: Accuracy")
    
    return model


# =============================================================================
# STEP 6: MODEL TRAINING WITH CALLBACKS
# =============================================================================

def create_callbacks(output_dir):
    """
    Create training callbacks for early stopping, checkpointing, and learning rate scheduling.
    
    Callbacks:
    - EarlyStopping: Stop if validation accuracy doesn't improve for 10 epochs
    - ModelCheckpoint: Save best model based on validation accuracy
    - ReduceLROnPlateau: Reduce learning rate when validation loss plateaus
    - CSVLogger: Log training history to CSV
    
    Args:
        output_dir: Output directory for saved files
        
    Returns:
        List of Keras callbacks
    """
    print("\n" + "=" * 70)
    print("STEP 6: TRAINING CALLBACKS")
    print("=" * 70)
    
    callbacks = [
        # Early stopping - stop if no improvement for 10 epochs
        EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1,
            mode='max'
        ),
        
        # Model checkpoint - save best model
        ModelCheckpoint(
            os.path.join(output_dir, 'best_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        ),
        
        # Learning rate reduction on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=Config.MIN_LEARNING_RATE,
            verbose=1,
            mode='min'
        ),
        
        # CSV logger for training history
        CSVLogger(
            os.path.join(output_dir, 'training_history.csv'),
            append=True
        )
    ]
    
    print("✅ Callbacks configured:")
    print("   - EarlyStopping: patience=10, restore_best_weights=True")
    print("   - ModelCheckpoint: save best model based on val_accuracy")
    print("   - ReduceLROnPlateau: factor=0.5, patience=5")
    print("   - CSVLogger: training history saved")
    
    return callbacks


def train_model(model, train_generator, val_generator,
                epochs=Config.EPOCHS, batch_size=Config.BATCH_SIZE,
                callbacks=None, steps_per_epoch=None):
    """
    Train the CNN model.
    
    Args:
        model: Keras model to train
        train_generator: Training data generator
        val_generator: Validation data generator
        epochs: Number of training epochs
        batch_size: Batch size
        callbacks: List of Keras callbacks
        steps_per_epoch: Steps per epoch (optional)
        
    Returns:
        Training history
    """
    print("\n" + "=" * 70)
    print("STEP 7: MODEL TRAINING")
    print("=" * 70)
    
    print(f"\nTraining Configuration:")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Steps per epoch: {steps_per_epoch}")
    
    # Train the model
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs,
        callbacks=callbacks,
        steps_per_epoch=steps_per_epoch,
        verbose=1
    )
    
    print("\n✅ Training completed!")
    
    return history


# =============================================================================
# STEP 8: MODEL EVALUATION
# =============================================================================

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model on test data.
    
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
    Comprehensive model evaluation with multiple metrics.
    
    Metrics:
    - Accuracy
    - Precision (per-class and weighted)
    - Recall (per-class and weighted)
    - F1-Score (per-class and weighted)
    - Confusion Matrix
    - ROC-AUC (One-vs-Rest)
    
    Args:
        model: Trained Keras model
        X_test: Test features
        y_test: Test labels
        class_labels: Dictionary mapping class indices to names
        output_dir: Directory to save visualizations
        
    Returns:
        Dictionary containing all evaluation metrics
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("=" * 70)
    
    # Get predictions
    y_pred_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    results = {}
    
    # 1. Accuracy
    test_accuracy = accuracy_score(y_test, y_pred)
    results['accuracy'] = test_accuracy
    print(f"\n1. ACCURACY: {test_accuracy:.4f}")
    
    # 2. Precision, Recall, F1-Score (per-class)
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
    
    # 3. Confusion Matrix
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
    print(f"\n   ✅ Confusion matrix saved")
    
    # 4. ROC-AUC
    print(f"\n4. ROC-AUC (One-vs-Rest):")
    try:
        roc_auc_ovr = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
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
        print(f"   ⚠️  Error computing ROC-AUC: {e}")
        results['roc_auc_ovr'] = None
        results['roc_auc_ovo'] = None
    
    # 5. Classification Report
    print(f"\n5. FULL CLASSIFICATION REPORT:")
    report = classification_report(y_test, y_pred, target_names=list(class_labels.values()))
    print(report)
    results['classification_report'] = report
    
    return results


def plot_roc_curves(y_true, y_pred_proba, class_labels, output_dir=None):
    """Plot ROC curves for each class."""
    plt.figure(figsize=(10, 8))
    
    for i, label in class_labels.items():
        y_test_binary = (y_true == i).astype(int)
        fpr, tpr, _ = roc_curve(y_test_binary, y_pred_proba[:, i])
        roc_auc = roc_auc_score(y_test_binary, y_pred_proba[:, i])
        plt.plot(fpr, tpr, label=f'{label} (AUC = {roc_auc:.4f})', linewidth=2)
    
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
    print(f"   ✅ ROC curves saved")


# =============================================================================
# STEP 9: VISUALIZATIONS
# =============================================================================

def plot_training_history(history, output_dir=None):
    """
    Plot training history (accuracy and loss curves).
    
    Args:
        history: Keras training history
        output_dir: Directory to save plot
    """
    print("\n" + "=" * 70)
    print("STEP 9: TRAINING HISTORY VISUALIZATION")
    print("=" * 70)
    
    # Extract metrics
    history_dict = history.history
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot accuracy
    ax1.plot(history_dict['accuracy'], label='Training Accuracy', linewidth=2)
    ax1.plot(history_dict['val_accuracy'], label='Validation Accuracy', linewidth=2)
    ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Accuracy', fontsize=12)
    ax1.legend(loc='lower right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot loss
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
    print("✅ Training history plot saved")


def visualize_feature_maps(model, X_sample, layer_name=None, output_dir=None):
    """
    Visualize the feature maps learned by convolutional layers.
    
    Args:
        model: Trained Keras model
        X_sample: Sample image(s) for visualization
        layer_name: Name of layer to visualize (optional)
        output_dir: Directory to save visualization
    """
    print("\n" + "=" * 70)
    print("FEATURE MAP VISUALIZATION")
    print("=" * 70)
    
    # Create feature extraction model
    layer_outputs = [layer.output for layer in model.layers if 'conv' in layer.name.lower()]
    feature_model = keras.Model(inputs=model.input, outputs=layer_outputs)
    
    # Get feature maps
    features = feature_model.predict(X_sample)
    
    # Visualize first conv layer's feature maps
    if features:
        first_conv_features = features[0]
        n_filters = min(16, first_conv_features.shape[-1])
        
        fig, axes = plt.subplots(4, 4, figsize=(12, 12))
        axes = axes.flatten()
        
        for i in range(n_filters):
            ax = axes[i]
            ax.imshow(first_conv_features[0, :, :, i], cmap='viridis')
            ax.set_title(f'Filter {i+1}', fontsize=8)
            ax.axis('off')
        
        plt.suptitle('Feature Maps - First Convolutional Layer', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(os.path.join(output_dir, 'feature_maps.png'), dpi=150)
        plt.show()
        print("✅ Feature maps visualization saved")


def visualize_misclassified_examples(model, X_test, y_test, 
                                      class_labels=Config.CLASS_LABELS,
                                      output_dir=None, n_examples=8):
    """
    Visualize misclassified examples from the test set.
    
    Args:
        model: Trained Keras model
        X_test: Test features
        y_test: Test labels
        class_labels: Class labels dictionary
        output_dir: Directory to save visualization
        n_examples: Number of misclassified examples to show
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
        print("✅ No misclassified examples!")
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
        
        # Get image (denormalize for display)
        img = X_test[idx]
        
        # Display image
        ax.imshow(img)
        
        # Get true and predicted labels
        true_label = class_labels[y_test[idx]]
        pred_label = class_labels[y_pred[idx]]
        confidence = y_pred_proba[idx][y_pred[idx]]
        
        # Set title with color based on correctness
        title_color = 'red'
        ax.set_title(f'True: {true_label}\nPred: {pred_label}\nConf: {confidence:.2f}',
                    color=title_color, fontsize=9)
        ax.axis('off')
    
    plt.suptitle('Misclassified Examples', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'misclassified_examples.png'), dpi=150)
    plt.show()
    print("✅ Misclassified examples visualization saved")


# =============================================================================
# STEP 10: SAVE MODEL
# =============================================================================

def save_model(model, output_dir, model_name=Config.MODEL_NAME):
    """
    Save the trained model with proper serialization.
    
    Args:
        model: Trained Keras model
        output_dir: Output directory
        model_name: Name for saved model
    """
    print("\n" + "=" * 70)
    print("STEP 10: MODEL SAVING")
    print("=" * 70)
    
    model_path = os.path.join(output_dir, model_name)
    model.save(model_path)
    
    print(f"✅ Model saved to: {model_path}")
    print(f"   Model size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    
    return model_path


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline():
    """
    Execute the complete poultry disease classification pipeline.
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
    print(f"\n📊 Final Results:")
    print(f"   - Test Accuracy: {test_accuracy:.4f}")
    print(f"   - Test Loss: {test_loss:.4f}")
    print(f"   - Weighted F1-Score: {results.get('f1_weighted', 'N/A')}")
    print(f"   - ROC-AUC (OvR): {results.get('roc_auc_ovr', 'N/A')}")
    print(f"\n📁 Output Files:")
    print(f"   - Model: {model_path}")
    print(f"   - Training History: {os.path.join(Config.OUTPUT_DIR, 'training_history.csv')}")
    print(f"   - Plots: {Config.OUTPUT_DIR}/*.png")
    print("=" * 70)
    
    return model, history, results


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Run the complete pipeline
    model, history, results = run_pipeline()
