"""
TRAIN_AUDIO_CNN.PY — Train environmental sound classifier CNN
Dataset: UrbanSound8K
Download from: https://urbansounddataset.weebly.com/urbansound8k.html
Place in: data/urbansound8k/

Run: python training/train_audio_cnn.py
Output: models/audio_classifier.h5
"""

import os
import sys
import numpy as np
import librosa
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
import dna

DATA_DIR   = Path("data/urbansound8k")
MODEL_PATH = "models/audio_classifier.h5"
N_MELS     = 128
MAX_LEN    = 128

def extract_mel(file_path: str) -> np.ndarray | None:
    try:
        audio, sr = librosa.load(file_path, sr=dna.AUDIO_SAMPLE_RATE, duration=4.0)
        mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS, fmax=8000)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        mel_fixed = librosa.util.fix_length(mel_db, size=MAX_LEN, axis=1)
        return mel_fixed[:N_MELS, :MAX_LEN]
    except Exception as e:
        print(f"  Error loading {file_path}: {e}")
        return None

def load_dataset():
    print("[TRAIN] Loading UrbanSound8K dataset...")
    X, y = [], []
    label_map = {}  # Maps class folder name to index

    # UrbanSound8K structure: audio/fold1/classname/files
    audio_dir = DATA_DIR / "audio"
    if not audio_dir.exists():
        print(f"[TRAIN] ERROR: Dataset not found at {audio_dir}")
        print("  Download from: https://urbansounddataset.weebly.com/")
        sys.exit(1)

    # Build label map from class names
    class_dirs = sorted([d for d in audio_dir.rglob("*") if d.is_dir()])
    classes    = sorted(set(d.name for d in audio_dir.glob("fold*/") for d in d.iterdir() if d.is_dir()))

    # Use dna.AUDIO_CLASSES order
    for cls in dna.AUDIO_CLASSES:
        label_map[cls] = dna.AUDIO_CLASSES.index(cls)

    count = 0
    for wav_file in audio_dir.rglob("*.wav"):
        class_name = wav_file.parent.name
        if class_name not in label_map:
            continue
        mel = extract_mel(str(wav_file))
        if mel is not None:
            X.append(mel)
            y.append(label_map[class_name])
            count += 1
            if count % 100 == 0:
                print(f"  Loaded {count} files...")

    X = np.array(X).reshape(-1, N_MELS, MAX_LEN, 1).astype(np.float32)
    y = np.array(y)

    # Normalize
    X = (X - X.mean()) / (X.std() + 1e-8)

    print(f"[TRAIN] Loaded {len(X)} samples across {len(set(y))} classes")
    return X, y

def build_model(num_classes: int):
    import tensorflow as tf
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(N_MELS, MAX_LEN, 1)),

        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.GlobalAveragePooling2D(),

        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(num_classes, activation='softmax'),
    ])
    return model

def train():
    import tensorflow as tf
    from sklearn.model_selection import train_test_split

    X, y = load_dataset()
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    num_classes = len(dna.AUDIO_CLASSES)
    model = build_model(num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5),
        tf.keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]

    print(f"\n[TRAIN] Training on {len(X_train)} samples...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=40,
        batch_size=32,
        callbacks=callbacks,
    )

    # Final evaluation
    val_loss, val_acc = model.evaluate(X_val, y_val)
    print(f"\n[TRAIN] Validation Accuracy: {val_acc:.2%}")
    print(f"[TRAIN] Model saved to: {MODEL_PATH}")

    # Per-class metrics
    from sklearn.metrics import classification_report
    y_pred = np.argmax(model.predict(X_val), axis=1)
    print("\n[TRAIN] Classification Report:")
    print(classification_report(y_val, y_pred, target_names=dna.AUDIO_CLASSES))

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train()
