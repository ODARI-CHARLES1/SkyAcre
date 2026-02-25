"""
Training Script for Cow Disease Classification Model

This script trains a CNN model to classify cow diseases using 
the preprocessed data from preprocess.py.

Usage:
    python train.py
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Configuration
IMG_HEIGHT = 224
IMG_WIDTH = 224
CHANNELS = 3  # RGB
BATCH_SIZE = 32
EPOCHS = 50
MODEL_OUTPUT_PATH = 'skyacre_cow_disease_model.keras'
DATA_DIR = 'Data/preprocessed'
NUM_CLASSES = 3  # foot-and-mouth, lumpy, healthy

# Class labels for reference
CLASS_LABELS = {
    0: 'foot-and-mouth',
    1: 'lumpy',
    2: 'healthy'
}


def build_cnn_model(input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS), num_classes=NUM_CLASSES):
    """
    Build a CNN model for multi-class classification.
    
    Args:
        input_shape: Shape of input images
        num_classes: Number of output classes (3 for foot-and-mouth, lumpy, healthy)
    
    Returns:
        Compiled Keras model
    """
    model = keras.Sequential([
        # First Conv Block
        layers.Conv2D(32, (3, 3), padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(32, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Second Conv Block
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(64, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Third Conv Block
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(128, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Fourth Conv Block
        layers.Conv2D(256, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Conv2D(256, (3, 3), padding='same'),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('relu'),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def load_preprocessed_data(data_dir=DATA_DIR):
    """Load preprocessed data from numpy files."""
    print("Loading preprocessed data...")
    
    X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
    X_val = np.load(os.path.join(data_dir, 'X_val.npy'))
    X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
    y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
    y_val = np.load(os.path.join(data_dir, 'y_val.npy'))
    y_test = np.load(os.path.join(data_dir, 'y_test.npy'))
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Image shape: {X_train[0].shape}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_model(model, X_train, y_train, X_val, y_val, epochs=EPOCHS, batch_size=BATCH_SIZE):
    """
    Train the CNN model.
    
    Args:
        model: Keras model to train
        X_train, y_train: Training data
        X_val, y_val: Validation data
        epochs: Number of training epochs
        batch_size: Batch size
    
    Returns:
        Training history
    """
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            'best_model.keras',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Data augmentation - create augmented training dataset
    # Note: In production, use tf.keras.preprocessing.image.ImageDataGenerator
    # or add augmentation as the first layers in the model for better performance
    print("\nNote: Data augmentation can be enabled by adding it as model layers")
    print("or using ImageDataGenerator for the training data.")
    
    # Train the model
    print("\nStarting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    return history


def evaluate_model(model, X_test, y_test):
    """Evaluate the model on test data."""
    print("\nEvaluating model on test data...")
    
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=1)
    
    print(f"\nTest Results:")
    print(f"  Loss: {test_loss:.4f}")
    print(f"  Accuracy: {test_accuracy:.4f}")
    
    return test_loss, test_accuracy


def plot_training_history(history):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy plot
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    
    # Loss plot
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=150)
    plt.show()
    print("Training history plot saved to training_history.png")


def save_model_h5(model, output_path=MODEL_OUTPUT_PATH):
    """Save the model as .h5 file."""
    model.save(output_path)
    print(f"\nModel saved to: {output_path}")
    return output_path


def main():
    """Main training pipeline."""
    print("="*60)
    print("COW DISEASE CLASSIFICATION MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load preprocessed data
    X_train, X_val, X_test, y_train, y_val, y_test = load_preprocessed_data()
    
    # Build model
    print("\nBuilding CNN model...")
    model = build_cnn_model(
        input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS),
        num_classes=NUM_CLASSES
    )
    model.summary()
    
    # Train model
    history = train_model(model, X_train, y_train, X_val, y_val)
    
    # Plot training history
    plot_training_history(history)
    
    # Evaluate on test set
    test_loss, test_accuracy = evaluate_model(model, X_test, y_test)
    
    # Save final model as .h5
    model_path = save_model_h5(model)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Model saved to: {model_path}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    return model, history


if __name__ == "__main__":
    model, history = main()
