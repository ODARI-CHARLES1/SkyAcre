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
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

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


def evaluate_comprehensive(model, X_test, y_test, class_labels=CLASS_LABELS):
    """
    Comprehensive evaluation with multiple metrics to detect overfitting/underfitting.
    
    Args:
        model: Trained Keras model
        X_test: Test features
        y_test: Test labels
        class_labels: Dictionary mapping class indices to labels
    
    Returns:
        Dictionary containing all evaluation metrics
    """
    print("\n" + "="*60)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("="*60)
    
    # Get predictions
    y_pred_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    results = {}
    
    # 1. Basic Metrics
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    results['test_loss'] = test_loss
    results['test_accuracy'] = test_accuracy
    print(f"\n1. BASIC METRICS:")
    print(f"   Test Loss: {test_loss:.4f}")
    print(f"   Test Accuracy: {test_accuracy:.4f}")
    
    # 2. Precision, Recall, F1-Score (per-class and weighted)
    precision_per_class = precision_score(y_test, y_pred, average=None)
    recall_per_class = recall_score(y_test, y_pred, average=None)
    f1_per_class = f1_score(y_test, y_pred, average=None)
    
    precision_weighted = precision_score(y_test, y_pred, average='weighted')
    recall_weighted = recall_score(y_test, y_pred, average='weighted')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    results['precision_per_class'] = precision_per_class
    results['recall_per_class'] = recall_per_class
    results['f1_per_class'] = f1_per_class
    results['precision_weighted'] = precision_weighted
    results['recall_weighted'] = recall_weighted
    results['f1_weighted'] = f1_weighted
    
    print(f"\n2. PRECISION, RECALL, F1-SCORE (Per-Class):")
    print(f"   {'Class':<20} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
    print(f"   {'-'*50}")
    for i, label in class_labels.items():
        print(f"   {label:<20} {precision_per_class[i]:>10.4f} {recall_per_class[i]:>10.4f} {f1_per_class[i]:>10.4f}")
    
    print(f"\n   Weighted Average:")
    print(f"   Precision: {precision_weighted:.4f}")
    print(f"   Recall: {recall_weighted:.4f}")
    print(f"   F1-Score: {f1_weighted:.4f}")
    
    # 3. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    results['confusion_matrix'] = cm
    
    print(f"\n3. CONFUSION MATRIX:")
    print(f"   Predicted ->  {'foot-and-mouth':>14} {'lumpy':>14} {'healthy':>14}")
    for i, label in class_labels.items():
        print(f"   Actual {label:<14} {cm[i, 0]:>14} {cm[i, 1]:>14} {cm[i, 2]:>14}")
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=list(class_labels.values()),
                yticklabels=list(class_labels.values()))
    plt.title('Confusion Matrix', fontsize=14)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150)
    plt.show()
    print("   Confusion matrix saved to confusion_matrix.png")
    
    # 4. ROC-AUC (One-vs-Rest)
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
            # Create binary labels for this class
            y_test_binary = (y_test == i).astype(int)
            roc_auc_class = roc_auc_score(y_test_binary, y_pred_proba[:, i])
            print(f"   {label}: {roc_auc_class:.4f}")
            
        # Plot ROC curves
        plot_roc_curves(y_test, y_pred_proba, class_labels)
        
    except Exception as e:
        print(f"   Error computing ROC-AUC: {e}")
        results['roc_auc_ovr'] = None
        results['roc_auc_ovo'] = None
    
    # 5. Full Classification Report
    print(f"\n5. FULL CLASSIFICATION REPORT:")
    report = classification_report(y_test, y_pred, target_names=list(class_labels.values()))
    print(report)
    results['classification_report'] = report
    
    return results


def plot_roc_curves(y_true, y_pred_proba, class_labels):
    """Plot ROC curves for each class (One-vs-Rest)."""
    plt.figure(figsize=(10, 8))
    
    for i, label in class_labels.items():
        # Binary labels
        y_test_binary = (y_true == i).astype(int)
        fpr, tpr, _ = roc_curve(y_test_binary, y_pred_proba[:, i])
        roc_auc = roc_auc_score(y_test_binary, y_pred_proba[:, i])
        plt.plot(fpr, tpr, label=f'{label} (AUC = {roc_auc:.4f})', linewidth=2)
    
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves (One-vs-Rest)', fontsize=14)
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('roc_curves.png', dpi=150)
    plt.show()
    print("   ROC curves saved to roc_curves.png")


def detect_overfitting(history):
    """
    Detect overfitting/underfitting by analyzing training history.
    
    Args:
        history: Keras training history
    
    Returns:
        Dictionary with overfitting analysis results
    """
    print("\n" + "="*60)
    print("OVERFITTING/UNDERFITTING DETECTION")
    print("="*60)
    
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
    
    # Gap analysis (key indicator of overfitting)
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
    
    # Diagnosis
    print(f"\nDiagnosis:")
    
    if acc_gap > 0.15 and loss_gap > 0.1:
        print("   ⚠️  OVERFITTING DETECTED!")
        print("   The model is memorizing training data but not generalizing well.")
        print("   Suggestions:")
        print("   - Increase dropout rate")
        print("   - Add more regularization (L1/L2)")
        print("   - Use data augmentation")
        print("   - Reduce model complexity")
        print("   - Collect more training data")
        results['diagnosis'] = 'overfitting'
    elif acc_gap < -0.1:
        print("   ⚠️  UNDERFITTING DETECTED!")
        print("   The model is not learning the training data well.")
        print("   Suggestions:")
        print("   - Increase model complexity")
        print("   - Train for more epochs")
        print("   - Reduce regularization")
        print("   - Check data quality")
        results['diagnosis'] = 'underfitting'
    else:
        print("   ✅ MODEL APPEARS WELL-FITTED!")
        print("   Training and validation metrics are reasonably close.")
        results['diagnosis'] = 'good_fit'
    
    # Plot overfitting detection
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy plot
    ax1.plot(train_acc, label='Training Accuracy', linewidth=2)
    ax1.plot(val_acc, label='Validation Accuracy', linewidth=2)
    ax1.fill_between(range(len(train_acc)), train_acc, val_acc, alpha=0.3, color='red' if acc_gap > 0.15 else 'green')
    ax1.set_title('Accuracy: Overfitting Detection', fontsize=12)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Loss plot
    ax2.plot(train_loss, label='Training Loss', linewidth=2)
    ax2.plot(val_loss, label='Validation Loss', linewidth=2)
    ax2.fill_between(range(len(train_loss)), train_loss, val_loss, alpha=0.3, color='red' if loss_gap > 0.1 else 'green')
    ax2.set_title('Loss: Overfitting Detection', fontsize=12)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('overfitting_detection.png', dpi=150)
    plt.show()
    print("\n   Overfitting detection plot saved to overfitting_detection.png")
    
    return results


def cross_validate_model(X_train, y_train, n_splits=5):
    """
    Perform k-fold cross-validation to get more robust performance estimates.
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_splits: Number of folds (default: 5)
    
    Returns:
        Dictionary with cross-validation results
    """
    print("\n" + "="*60)
    print(f"{n_splits}-FOLD CROSS-VALIDATION")
    print("="*60)
    
    # Prepare data
    X = X_train.astype('float32')
    y = y_train
    
    # Store results
    fold_results = []
    
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        print(f"\nFold {fold}/{n_splits}:")
        
        X_fold_train, X_fold_val = X[train_idx], X[val_idx]
        y_fold_train, y_fold_val = y[train_idx], y[val_idx]
        
        # Build fresh model for each fold
        model = build_cnn_model()
        
        # Train
        model.fit(
            X_fold_train, y_fold_train,
            validation_data=(X_fold_val, y_fold_val),
            epochs=10,  # Reduced for cross-validation speed
            batch_size=BATCH_SIZE,
            verbose=0
        )
        
        # Evaluate
        val_loss, val_acc = model.evaluate(X_fold_val, y_fold_val, verbose=0)
        
        # Get predictions for additional metrics
        y_pred = np.argmax(model.predict(X_fold_val, verbose=0), axis=1)
        
        precision = precision_score(y_fold_val, y_pred, average='weighted')
        recall = recall_score(y_fold_val, y_pred, average='weighted')
        f1 = f1_score(y_fold_val, y_pred, average='weighted')
        
        fold_results.append({
            'fold': fold,
            'val_loss': val_loss,
            'val_accuracy': val_acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        })
        
        print(f"   Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        print(f"   Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Clear memory
        del model
        tf.keras.backend.clear_session()
    
    # Calculate mean and std
    mean_acc = np.mean([r['val_accuracy'] for r in fold_results])
    std_acc = np.std([r['val_accuracy'] for r in fold_results])
    mean_loss = np.mean([r['val_loss'] for r in fold_results])
    std_loss = np.std([r['val_loss'] for r in fold_results])
    mean_f1 = np.mean([r['f1_score'] for r in fold_results])
    std_f1 = np.std([r['f1_score'] for r in fold_results])
    
    print(f"\nCross-Validation Summary:")
    print(f"   Mean Val Accuracy: {mean_acc:.4f} (+/- {std_acc:.4f})")
    print(f"   Mean Val Loss: {mean_loss:.4f} (+/- {std_loss:.4f})")
    print(f"   Mean F1-Score: {mean_f1:.4f} (+/- {std_f1:.4f})")
    
    return {
        'fold_results': fold_results,
        'mean_accuracy': mean_acc,
        'std_accuracy': std_acc,
        'mean_loss': mean_loss,
        'std_loss': std_loss,
        'mean_f1': mean_f1,
        'std_f1': std_f1
    }


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


def main(enable_cross_validation=False, n_folds=5):
    """Main training pipeline.
    
    Args:
        enable_cross_validation: Whether to run k-fold cross-validation
        n_folds: Number of folds for cross-validation
    """
    print("="*60)
    print("COW DISEASE CLASSIFICATION MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load preprocessed data
    X_train, X_val, X_test, y_train, y_val, y_test = load_preprocessed_data()
    
    # Optional: Run cross-validation
    if enable_cross_validation:
        cv_results = cross_validate_model(X_train, y_train, n_splits=n_folds)
    
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
    
    # Evaluate on test set (basic)
    test_loss, test_accuracy = evaluate_model(model, X_test, y_test)
    
    # Comprehensive evaluation with all metrics
    eval_results = evaluate_comprehensive(model, X_test, y_test)
    
    # Detect overfitting/underfitting
    overfitting_results = detect_overfitting(history)
    
    # Save final model as .h5
    model_path = save_model_h5(model)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Model saved to: {model_path}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Weighted F1-Score: {eval_results['f1_weighted']:.4f}")
    print(f"ROC-AUC (OvR): {eval_results['roc_auc_ovr']:.4f}")
    print(f"Overfitting Diagnosis: {overfitting_results['diagnosis']}")
    
    return model, history, eval_results, overfitting_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Cow Disease Classification Model')
    parser.add_argument('--cv', action='store_true', help='Enable k-fold cross-validation')
    parser.add_argument('--folds', type=int, default=5, help='Number of folds for cross-validation')
    args = parser.parse_args()
    
    model, history, eval_results, overfitting_results = main(
        enable_cross_validation=args.cv,
        n_folds=args.folds
    )
