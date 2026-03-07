# Google Colab Training Pipeline
# Usage:
# 1. In Colab choose Runtime > Change runtime type > GPU
# 2. Upload your dataset to Colab or mount Google Drive and set `DATA_DIR`
# 3. Run this script cell-by-cell or as a .py file

# Sections:
# 1) Imports & GPU check
# 2) Data loading & preprocessing helpers
# 3) Model builder (flexible: MLP for tabular, small CNN for images)
# 4) 5-fold cross-validation training loop
# 5) Final training on full data + saving

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# ----------------------
# 1) GPU check
# ----------------------

def check_gpu():
    gpus = tf.config.list_physical_devices('GPU')
    print('GPUs found:', gpus)
    if gpus:
        try:
            for g in gpus:
                tf.config.experimental.set_memory_growth(g, True)
            print('GPU available and memory growth set')
        except Exception as e:
            print('Error setting memory growth:', e)
    else:
        print('No GPU available; training will use CPU')

check_gpu()

# ----------------------
# 2) Data loading & preprocessing
# ----------------------

def load_data_from_npy(data_dir):
    # Tries to load common numpy preprocessed files if available
    paths = {
        'X_train': os.path.join(data_dir, 'X_train.npy'),
        'y_train': os.path.join(data_dir, 'y_train.npy'),
        'X_val': os.path.join(data_dir, 'X_val.npy'),
        'y_val': os.path.join(data_dir, 'y_val.npy'),
        'X_test': os.path.join(data_dir, 'X_test.npy'),
        'y_test': os.path.join(data_dir, 'y_test.npy')
    }
    data = {}
    for k,p in paths.items():
        if os.path.exists(p):
            data[k] = np.load(p)
            print(f'Loaded {k} from {p} with shape {data[k].shape}')
        else:
            data[k] = None
    return data


def load_csv(data_path, features=None, target_col=None):
    df = pd.read_csv(data_path)
    if target_col is None:
        raise ValueError('target_col must be provided for CSV loading')
    if features is None:
        X = df.drop(columns=[target_col]).values
    else:
        X = df[features].values
    y = df[target_col].values
    print('Loaded CSV', data_path, 'X shape', X.shape, 'y shape', y.shape)
    return X, y


def detect_problem_type(y):
    # Heuristic: integer classes with small number of unique values -> classification
    if y is None:
        return None
    if np.issubdtype(y.dtype, np.integer) or np.issubdtype(y.dtype, np.bool_):
        n_classes = len(np.unique(y))
        if n_classes <= 50:
            return 'classification'
    # else if floats -> regression
    if np.issubdtype(y.dtype, np.floating):
        return 'regression'
    # fallback to classification
    return 'classification'

# Preprocessing that fits scaler on training fold only (no leakage)

def get_preprocessing_fn(X_train, X_val=None):
    if X_train.ndim == 4:
        # images: scale to [0,1]
        def preprocess_train(x):
            return x.astype('float32') / 255.0
        return preprocess_train, preprocess_train
    else:
        # tabular features: standard scaler
        scaler = StandardScaler()
        scaler.fit(X_train.reshape((X_train.shape[0], -1)))
        def preprocess_train(x):
            shp = x.shape
            flat = x.reshape((shp[0], -1))
            scaled = scaler.transform(flat)
            return scaled.reshape(shp)
        def preprocess_infer(x):
            shp = x.shape
            flat = x.reshape((shp[0], -1))
            scaled = scaler.transform(flat)
            return scaled.reshape(shp)
        return preprocess_train, preprocess_infer

# Utility to build tf.data.Dataset

def make_dataset(X, y=None, batch_size=32, shuffle=False):
    if y is None:
        ds = tf.data.Dataset.from_tensor_slices(X)
    else:
        ds = tf.data.Dataset.from_tensor_slices((X, y))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(X))
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

# ----------------------
# 3) Model builder
# ----------------------

def build_model(input_shape, problem_type='classification', n_classes=None, hidden_units=[128,64], dropout=0.3):
    inputs = keras.Input(shape=input_shape)
    x = inputs
    if len(input_shape) == 1:
        # MLP for tabular
        for units in hidden_units:
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(dropout)(x)
        if problem_type == 'classification':
            if n_classes is None or n_classes <= 2:
                outputs = layers.Dense(1, activation='sigmoid')(x)
            else:
                outputs = layers.Dense(n_classes, activation='softmax')(x)
        else:
            outputs = layers.Dense(1, activation='linear')(x)
    elif len(input_shape) == 3:
        # simple CNN for image-like inputs (H,W,C)
        x = layers.Conv2D(32, 3, activation='relu', padding='same')(x)
        x = layers.MaxPool2D()(x)
        x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
        x = layers.MaxPool2D()(x)
        x = layers.Flatten()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(dropout)(x)
        if problem_type == 'classification':
            if n_classes is None or n_classes <= 2:
                outputs = layers.Dense(1, activation='sigmoid')(x)
            else:
                outputs = layers.Dense(n_classes, activation='softmax')(x)
        else:
            outputs = layers.Dense(1, activation='linear')(x)
    else:
        # fallback MLP: flatten then dense
        x = layers.Flatten()(x)
        for units in hidden_units:
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(dropout)(x)
        if problem_type == 'classification':
            if n_classes is None or n_classes <= 2:
                outputs = layers.Dense(1, activation='sigmoid')(x)
            else:
                outputs = layers.Dense(n_classes, activation='softmax')(x)
        else:
            outputs = layers.Dense(1, activation='linear')(x)

    model = keras.Model(inputs, outputs)

    # compile
    if problem_type == 'classification':
        if n_classes is None or n_classes <= 2:
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']
    else:
        loss = 'mse'
        metrics = ['mae']

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=1e-3), loss=loss, metrics=metrics)
    return model

# ----------------------
# 4) 5-fold CV training loop
# ----------------------

def run_k_fold_cv(X, y, problem_type=None, n_splits=5, batch_size=64, epochs=50, model_builder=build_model, save_dir='/content/drive/MyDrive/models'):
    os.makedirs(save_dir, exist_ok=True)
    if problem_type is None:
        problem_type = detect_problem_type(y)
    print('Detected problem type:', problem_type)

    if problem_type == 'classification':
        n_classes = len(np.unique(y))
    else:
        n_classes = None

    # choose StratifiedKFold for classification if possible
    if problem_type == 'classification' and len(np.unique(y)) > 1:
        kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        splits = kf.split(X, y)
    else:
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        splits = kf.split(X)

    fold_metrics = []

    for fold, (train_idx, val_idx) in enumerate(splits, 1):
        print(f'\n===== Fold {fold}/{n_splits} =====')
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        preprocess_train, preprocess_infer = get_preprocessing_fn(X_train)
        X_train_pre = preprocess_train(X_train)
        X_val_pre = preprocess_infer(X_val)

        # Adjust input shapes for model builder
        if X_train_pre.ndim > 2 and X_train_pre.shape[-1] in (1,3):
            input_shape = X_train_pre.shape[1:]
        elif X_train_pre.ndim == 2:
            input_shape = (X_train_pre.shape[1],)
        else:
            input_shape = X_train_pre.shape[1:]

        model = model_builder(input_shape=input_shape, problem_type=problem_type, n_classes=n_classes)
        model.summary()

        # callbacks
        cb = [
            keras.callbacks.EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
        ]

        train_ds = make_dataset(X_train_pre, y_train, batch_size=batch_size, shuffle=True)
        val_ds = make_dataset(X_val_pre, y_val, batch_size=batch_size, shuffle=False)

        history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=cb, verbose=2)

        # evaluate predictions and compute metrics
        y_pred_prob = model.predict(val_ds)
        if problem_type == 'classification':
            if n_classes is None or n_classes <= 2:
                y_pred = (y_pred_prob.ravel() > 0.5).astype(int)
            else:
                y_pred = np.argmax(y_pred_prob, axis=1)

            acc = accuracy_score(y_val, y_pred)
            prec = precision_score(y_val, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_val, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_val, y_pred, average='weighted', zero_division=0)
            metrics = {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}
        else:
            y_pred = y_pred_prob.ravel()
            mse = mean_squared_error(y_val, y_pred)
            mae = mean_absolute_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            metrics = {'mse': mse, 'mae': mae, 'r2': r2}

        print(f'Fold {fold} metrics:', metrics)
        fold_metrics.append(metrics)

        # save fold model
        model_path = os.path.join(save_dir, f'model_fold_{fold}.h5')
        model.save(model_path)
        print('Saved fold model to', model_path)

        # Save scaler if tabular
        if X_train.ndim != 4:
            # We saved scaler inside get_preprocessing_fn via closure only; better to export StandardScaler object
            try:
                # try to rebuild scaler for entire training fold and save
                scaler = StandardScaler()
                flat = X_train.reshape((X_train.shape[0], -1))
                scaler.fit(flat)
                scaler_path = os.path.join(save_dir, f'scaler_fold_{fold}.pkl')
                joblib.dump(scaler, scaler_path)
                print('Saved scaler to', scaler_path)
            except Exception as e:
                print('Could not save scaler:', e)

    # compute average metrics across folds
    avg_metrics = {}
    keys = fold_metrics[0].keys()
    for k in keys:
        vals = [fm[k] for fm in fold_metrics]
        avg_metrics[k] = float(np.mean(vals))
    print('\n===== Cross-validation summary =====')
    print('Per-fold metrics:', fold_metrics)
    print('Average metrics:', avg_metrics)

    # Save summary
    summary_path = os.path.join(save_dir, 'cv_summary.npy')
    np.save(summary_path, {'fold_metrics': fold_metrics, 'avg_metrics': avg_metrics})
    print('Saved CV summary to', summary_path)

    return fold_metrics, avg_metrics

# ----------------------
# 5) Final training on full set and saving
# ----------------------

def train_final_and_save(X, y, problem_type=None, batch_size=64, epochs=50, save_path='/content/drive/MyDrive/models/final_model.h5'):
    if problem_type is None:
        problem_type = detect_problem_type(y)
    print('Training final model, problem type:', problem_type)

    preprocess_train, preprocess_infer = get_preprocessing_fn(X)
    X_pre = preprocess_train(X)

    if X_pre.ndim == 2:
        input_shape = (X_pre.shape[1],)
    else:
        input_shape = X_pre.shape[1:]

    if problem_type == 'classification':
        n_classes = len(np.unique(y))
    else:
        n_classes = None

    model = build_model(input_shape=input_shape, problem_type=problem_type, n_classes=n_classes)

    ds = make_dataset(X_pre, y, batch_size=batch_size, shuffle=True)

    cb = [keras.callbacks.EarlyStopping(monitor='loss', patience=6, restore_best_weights=True),]

    model.fit(ds, epochs=epochs, callbacks=cb, verbose=2)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print('Saved final model to', save_path)
    return save_path

# ----------------------
# Example quick-run helper for Colab
# ----------------------

if __name__ == '__main__':
    # Typical Colab usage: mount drive or set DATA_DIR to uploaded folder
    # from google.colab import drive
    # drive.mount('/content/drive')

    # Set your data directory here (example uses AI-Models/Data/preprocessed if repo is present in Colab)
    DATA_DIR = '/content/AI-Models/Data/preprocessed'  # change if using Drive or uploads

    # Try load npy files if present
    data = load_data_from_npy(DATA_DIR)

    # Prefer (X_train, y_train) if full training arrays are available, else fall back to loading CSV
    if data['X_train'] is not None and data['y_train'] is not None:
        X = data['X_train']
        y = data['y_train']
        print('Using X_train/y_train from preprocessed folder')
    elif data['X_train'] is None and os.path.exists(os.path.join(DATA_DIR, 'dataset.csv')):
        X, y = load_csv(os.path.join(DATA_DIR, 'dataset.csv'), target_col='target')
    else:
        raise RuntimeError('Data not found. Upload files to Colab or mount Drive and set DATA_DIR.')

    # Run 5-fold CV
    fold_metrics, avg_metrics = run_k_fold_cv(X, y, n_splits=5, batch_size=64, epochs=25, save_dir='/content/drive/MyDrive/skyacre_models')

    # Train final model on all data and save
    final_path = train_final_and_save(X, y, batch_size=64, epochs=25, save_path='/content/drive/MyDrive/skyacre_models/final_model.h5')

    print('Done. Models and summaries saved to Google Drive (if mounted).')
