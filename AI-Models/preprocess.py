"""
Data Preprocessing Pipeline for Cow Disease Classification

This pipeline processes images of cows for the CNN model to classify
whether a cow has foot-and-mouth disease or is healthy.

Usage:
    python preprocess.py
"""

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import shutil
import warnings
warnings.filterwarnings('ignore')

# Configuration
CONFIG = {
    # Image settings
    'img_height': 224,
    'img_width': 224,
    'color_mode': 'rgb',  # 'rgb' or 'grayscale'
    
    # Data paths
    'data_dir': 'Data/archive (3)/Cows datasets',
    'output_dir': 'Data/preprocessed',
    
    # Class labels
    'classes': {
        'foot-and-mouth': 0,  # Diseased
        'lumpy': 1,          # Lumpy Skin Disease
        'healthy': 2         # Healthy
    },
    
    # Split ratios
    'train_ratio': 0.7,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    
    # Data augmentation settings (for training only)
    'augmentation': {
        'rotation_range': 20,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.15,
        'zoom_range': 0.2,
        'horizontal_flip': True,
        'fill_mode': 'nearest'
    },
    
    # Normalization
    'normalize': True,
    'normalization_factor': 255.0  # Scale to [0, 1]
}


class ImagePreprocessor:
    """Class for preprocessing images for CNN training."""
    
    def __init__(self, config=CONFIG):
        self.config = config
        self.images = []
        self.labels = []
        self.filenames = []
        
    def load_image(self, image_path):
        """Load and preprocess a single image."""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if self.config['color_mode'] == 'rgb':
                img = img.convert('RGB')
            else:
                img = img.convert('L')
            
            # Resize to target dimensions
            img = img.resize((self.config['img_width'], self.config['img_height']))
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Normalize if enabled
            if self.config['normalize']:
                img_array = img_array / self.config['normalization_factor']
            
            return img_array
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None
    
    def load_dataset(self):
        """Load all images from the dataset directory."""
        data_dir = self.config['data_dir']
        
        for class_name, class_label in self.config['classes'].items():
            class_dir = os.path.join(data_dir, class_name)
            
            if not os.path.exists(class_dir):
                print(f"Warning: Directory not found: {class_dir}")
                continue
            
            # Get all image files in the class directory
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
            image_files = [f for f in os.listdir(class_dir) 
                          if f.lower().endswith(image_extensions)]
            
            print(f"Loading {len(image_files)} images from '{class_name}' class...")
            
            for img_file in image_files:
                img_path = os.path.join(class_dir, img_file)
                img_array = self.load_image(img_path)
                
                if img_array is not None:
                    self.images.append(img_array)
                    self.labels.append(class_label)
                    self.filenames.append(img_file)
        
        # Convert to numpy arrays
        self.images = np.array(self.images)
        self.labels = np.array(self.labels)
        
        print(f"\nDataset loaded successfully!")
        print(f"Total images: {len(self.images)}")
        print(f"Image shape: {self.images[0].shape}")
        print(f"Classes: {self.config['classes']}")
        
        # Print class distribution
        unique, counts = np.unique(self.labels, return_counts=True)
        print("\nClass distribution:")
        for label, count in zip(unique, counts):
            class_name = [k for k, v in self.config['classes'].items() if v == label][0]
            print(f"  {class_name}: {count} images")
        
        return self.images, self.labels
    
    def split_dataset(self, images=None, labels=None):
        """Split dataset into train, validation, and test sets."""
        if images is None:
            images = self.images
        if labels is None:
            labels = self.labels
        
        # First split: train + (validation + test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            images, labels,
            test_size=(self.config['val_ratio'] + self.config['test_ratio']),
            random_state=42,
            stratify=labels
        )
        
        # Second split: validation + test
        val_size = self.config['test_ratio'] / (self.config['val_ratio'] + self.config['test_ratio'])
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=val_size,
            random_state=42,
            stratify=y_temp
        )
        
        print(f"\nDataset split:")
        print(f"  Training set: {len(X_train)} images ({len(X_train)/len(images)*100:.1f}%)")
        print(f"  Validation set: {len(X_val)} images ({len(X_val)/len(images)*100:.1f}%)")
        print(f"  Test set: {len(X_test)} images ({len(X_test)/len(images)*100:.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def augment_image(self, img_array):
        """Apply data augmentation to a single image."""
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        
        aug_config = self.config['augmentation']
        
        # Create datagen for single image
        datagen = ImageDataGenerator(
            rotation_range=aug_config['rotation_range'],
            width_shift_range=aug_config['width_shift_range'],
            height_shift_range=aug_config['height_shift_range'],
            shear_range=aug_config['shear_range'],
            zoom_range=aug_config['zoom_range'],
            horizontal_flip=aug_config['horizontal_flip'],
            fill_mode=aug_config['fill_mode']
        )
        
        # Reshape for ImageDataGenerator (batch_size, height, width, channels)
        if len(img_array.shape) == 2:
            img_array = np.expand_dims(img_array, axis=(0, -1))
        else:
            img_array = np.expand_dims(img_array, axis=0)
        
        # Generate augmented images
        augmented_images = []
        for batch in datagen.flow(img_array, batch_size=1):
            augmented_images.append(batch[0])
            if len(augmented_images) >= 1:  # Generate 1 augmented version
                break
        
        return augmented_images[0]
    
    def create_augmented_dataset(self, X_train, y_train, augment_factor=3):
        """Create augmented training dataset."""
        print(f"\nCreating augmented dataset (factor: {augment_factor})...")
        
        X_augmented = list(X_train)
        y_augmented = list(y_train)
        
        for i in range(len(X_train)):
            for _ in range(augment_factor - 1):
                aug_img = self.augment_image(X_train[i])
                X_augmented.append(aug_img)
                y_augmented.append(y_train[i])
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(X_train)} images...")
        
        X_augmented = np.array(X_augmented)
        y_augmented = np.array(y_augmented)
        
        print(f"  Augmented dataset size: {len(X_augmented)} images")
        
        return X_augmented, y_augmented
    
    def save_preprocessed_data(self, X_train, X_val, X_test, y_train, y_val, y_test):
        """Save preprocessed data to disk."""
        output_dir = self.config['output_dir']
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as numpy arrays
        np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
        np.save(os.path.join(output_dir, 'X_val.npy'), X_val)
        np.save(os.path.join(output_dir, 'X_test.npy'), X_test)
        np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
        np.save(os.path.join(output_dir, 'y_val.npy'), y_val)
        np.save(os.path.join(output_dir, 'y_test.npy'), y_test)
        
        # Save configuration
        import json
        config_path = os.path.join(output_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"\nPreprocessed data saved to: {output_dir}")
        print(f"  X_train.npy: {X_train.shape}")
        print(f"  X_val.npy: {X_val.shape}")
        print(f"  X_test.npy: {X_test.shape}")
        
    def visualize_samples(self, num_samples=4):
        """Visualize sample images from each class."""
        fig, axes = plt.subplots(2, num_samples, figsize=(15, 6))
        
        for class_idx, (class_name, class_label) in enumerate(self.config['classes'].items()):
            # Get images for this class
            class_indices = np.where(self.labels == class_label)[0][:num_samples]
            
            for i, idx in enumerate(class_indices):
                img = self.images[idx]
                
                # Denormalize for visualization
                if self.config['normalize']:
                    img = img * self.config['normalization_factor']
                    img = img.astype(np.uint8)
                
                axes[class_idx, i].imshow(img)
                axes[class_idx, i].set_title(f"{class_name}\n{self.filenames[idx][:20]}")
                axes[class_idx, i].axis('off')
        
        plt.suptitle('Sample Images from Each Class', fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.config['output_dir'], 'sample_images.png'), dpi=150)
        plt.show()
        print(f"\nSample visualization saved to: {self.config['output_dir']}/sample_images.png")


class DataGenerator:
    """Keras-compatible data generator for training."""
    
    def __init__(self, X, y, batch_size=32, shuffle=True, augmentation=False):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.augmentation = augmentation
        self.indices = np.arange(len(self.X))
        
        if self.shuffle:
            np.random.shuffle(self.indices)
    
    def __len__(self):
        return int(np.ceil(len(self.X) / self.batch_size))
    
    def __getitem__(self, idx):
        batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        
        batch_x = self.X[batch_indices]
        batch_y = self.y[batch_indices]
        
        # Apply augmentation if enabled
        if self.augmentation:
            from tensorflow.keras.preprocessing.image import ImageDataGenerator
            
            datagen = ImageDataGenerator(
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.15,
                zoom_range=0.2,
                horizontal_flip=True
            )
            
            augmented = []
            for img in batch_x:
                img_expanded = np.expand_dims(img, axis=0)
                for aug_img in datagen.flow(img_expanded, batch_size=1):
                    augmented.append(aug_img[0])
                    break
            
            batch_x = np.array(augmented)
        
        return batch_x, batch_y
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)


def load_preprocessed_data(data_dir='Data/preprocessed'):
    """Load preprocessed data from disk."""
    X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
    X_val = np.load(os.path.join(data_dir, 'X_val.npy'))
    X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
    y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
    y_val = np.load(os.path.join(data_dir, 'y_val.npy'))
    y_test = np.load(os.path.join(data_dir, 'y_test.npy'))
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def verify_data_integrity(X, y, class_names):
    """Verify data integrity and print statistics."""
    print("\n" + "="*50)
    print("DATA INTEGRITY VERIFICATION")
    print("="*50)
    
    print(f"Image shape: {X[0].shape}")
    print(f"Data type: {X.dtype}")
    print(f"Value range: [{X.min():.4f}, {X.max():.4f}]")
    
    unique, counts = np.unique(y, return_counts=True)
    print("\nClass distribution:")
    for label, count in zip(unique, counts):
        class_name = [k for k, v in class_names.items() if v == label][0]
        print(f"  {class_name} ({label}): {count} samples ({count/len(y)*100:.1f}%)")
    
    print("="*50 + "\n")


def main():
    """Main preprocessing pipeline."""
    print("="*50)
    print("COW DISEASE IMAGE PREPROCESSING PIPELINE")
    print("="*50 + "\n")
    
    # Initialize preprocessor
    preprocessor = ImagePreprocessor(CONFIG)
    
    # Load dataset
    images, labels = preprocessor.load_dataset()
    
    # Verify data
    verify_data_integrity(images, labels, CONFIG['classes'])
    
    # Split dataset
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split_dataset(images, labels)
    
    # Optionally create augmented dataset (uncomment if needed)
    # X_train, y_train = preprocessor.create_augmented_dataset(X_train, y_train, augment_factor=3)
    
    # Save preprocessed data
    preprocessor.save_preprocessed_data(X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Visualize samples
    preprocessor.visualize_samples(num_samples=4)
    
    print("\nPreprocessing complete!")
    print("\nNext steps:")
    print("1. Use load_preprocessed_data() to load the processed data")
    print("2. Build your CNN model using TensorFlow/Keras")
    print("3. Train the model with the preprocessed data")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


if __name__ == "__main__":
    X_train, X_val, X_test, y_train, y_val, y_test = main()
