# echo_hunter.py - jinx's sound detection system
# uses a CNN trained on mel spectrograms to classify ambient sounds
# can detect glass breaking, gunshots, sirens, dog barks etc
# 
# the mel spectrogram thing was confusing at first but basically
# its a visual representation of sound that a CNN can understand
# like turning audio into an image and then doing image classification
# pretty clever ngl

import numpy as np
import json
import os
import time
import threading
import paho.mqtt.client as mqtt
import sounddevice as sd

try:
    import librosa
    LIBROSA_OK = True
except:
    print("[ECHO] librosa not installed")
    LIBROSA_OK = False

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
    from tensorflow.keras.utils import to_categorical
    TF_OK = True
except:
    print("[ECHO] tensorflow not installed, audio classification wont work")
    TF_OK = False

import sys
sys.path.insert(0, os.path.dirname(__file__))

from dna import *
from blackbox import JinxDB


class EchoHunter:
    def __init__(self):
        print("[ECHO] initializing sound detection...")

        # mqtt
        self.syn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.syn.connect(LAPTOP_IP, MQTT_PORT)

        # database
        self.db = JinxDB(DB_PATH)

        # audio settings
        self.sample_rate = 22050
        self.chunk_duration = 2  # seconds per chunk
        self.n_mels = 128  # mel bands
        self.target_shape = (128, 128)  # input shape for CNN

        # model
        self.model = None
        self.alive = True

        # try loading pretrained model
        if TF_OK and os.path.exists(AUDIO_MODEL_PATH):
            try:
                self.model = load_model(AUDIO_MODEL_PATH)
                print(f"[ECHO] loaded model from {AUDIO_MODEL_PATH}")
            except Exception as e:
                print(f"[ECHO] couldnt load model: {e}")
                print("[ECHO] youll need to train one first (run with --train)")
        else:
            if TF_OK:
                print("[ECHO] no trained model found")
                print(f"[ECHO] expected at: {AUDIO_MODEL_PATH}")
                print("[ECHO] run: python echo_hunter.py --train")

        self.db.add_syslog("ECHO", "sound detection ready")
        print("[ECHO] ready")

    def extract_features(self, audio, sr=22050):
        """turn audio into a mel spectrogram image
        basically converts sound waves into a picture
        that our CNN can classify"""

        if not LIBROSA_OK:
            return None

        try:
            # compute mel spectrogram
            mel = librosa.feature.melspectrogram(
                y=audio, sr=sr, n_mels=self.n_mels
            )
            mel_db = librosa.power_to_db(mel, ref=np.max)

            # resize to target shape
            # pad if too short, crop if too long
            if mel_db.shape[1] < self.target_shape[1]:
                pad_width = self.target_shape[1] - mel_db.shape[1]
                mel_db = np.pad(mel_db, ((0, 0), (0, pad_width)), mode='constant')
            mel_db = mel_db[:self.target_shape[0], :self.target_shape[1]]

            # reshape for CNN (add channel dimension)
            return mel_db.reshape(self.target_shape[0], self.target_shape[1], 1)

        except Exception as e:
            print(f"[ECHO] feature extraction error: {e}")
            return None

    def build_model(self):
        """build the CNN architecture
        pretty standard conv net, nothing fancy
        3 conv layers -> flatten -> dense -> output"""

        if not TF_OK:
            print("[ECHO] cant build model without tensorflow")
            return None

        model = Sequential([
            Conv2D(32, (3, 3), activation='relu',
                   input_shape=(self.target_shape[0], self.target_shape[1], 1)),
            MaxPooling2D((2, 2)),

            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),

            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),

            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.3),  # helps prevent overfitting
            Dense(len(AUDIO_CLASSES), activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        model.summary()
        self.model = model
        return model

    def train(self, data_dir="data/urbansound8k/"):
        """train the model on urbansound8k or esc-50 dataset
        this takes a while depending on your machine
        
        expected folder structure:
        data/urbansound8k/
        ├── fold1/
        │   ├── sound1.wav
        │   ├── sound2.wav
        ├── fold2/
        │   ├── ...
        └── metadata/
            └── UrbanSound8K.csv"""

        if not TF_OK or not LIBROSA_OK:
            print("[ECHO] need tensorflow and librosa to train")
            return

        print("[ECHO] starting training...")
        print(f"[ECHO] looking for data in: {data_dir}")

        if not os.path.exists(data_dir):
            print(f"[ECHO] data directory not found: {data_dir}")
            print("[ECHO] download UrbanSound8K from:")
            print("       https://urbansounddataset.weebly.com/urbansound8k.html")
            return

        import pandas as pd

        # load metadata
        meta_path = os.path.join(data_dir, "metadata", "UrbanSound8K.csv")
        if not os.path.exists(meta_path):
            print(f"[ECHO] metadata not found: {meta_path}")
            return

        meta = pd.read_csv(meta_path)
        print(f"[ECHO] found {len(meta)} audio samples")

        features = []
        labels = []
        errors = 0

        for idx, row in meta.iterrows():
            fold = f"fold{row['fold']}"
            filename = row['slice_file_name']
            classID = row['classID']
            filepath = os.path.join(data_dir, fold, filename)

            if not os.path.exists(filepath):
                errors += 1
                continue

            try:
                audio, sr = librosa.load(filepath, sr=self.sample_rate, duration=2.0)
                feat = self.extract_features(audio, sr)

                if feat is not None:
                    features.append(feat)
                    labels.append(classID)

                if idx % 500 == 0:
                    print(f"[ECHO] processed {idx}/{len(meta)} files...")

            except Exception as e:
                errors += 1
                continue

        print(f"[ECHO] processed {len(features)} files, {errors} errors")

        if len(features) == 0:
            print("[ECHO] no features extracted, something is wrong")
            return

        X = np.array(features)
        y = to_categorical(np.array(labels), num_classes=len(AUDIO_CLASSES))

        # split 80/20
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        print(f"[ECHO] training: {len(X_train)} samples")
        print(f"[ECHO] testing: {len(X_test)} samples")

        # build and train
        self.build_model()
        history = self.model.fit(
            X_train, y_train,
            epochs=30,
            batch_size=32,
            validation_data=(X_test, y_test),
            verbose=1
        )

        # evaluate
        loss, acc = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\n[ECHO] test accuracy: {acc:.2%}")
        print(f"[ECHO] test loss: {loss:.4f}")

        # save
        os.makedirs(os.path.dirname(AUDIO_MODEL_PATH), exist_ok=True)
        self.model.save(AUDIO_MODEL_PATH)
        print(f"[ECHO] model saved to {AUDIO_MODEL_PATH}")

        self.db.add_syslog("ECHO", f"model trained, accuracy: {acc:.2%}")

    def freq_hunt(self, audio):
        """classify a single audio chunk
        returns (class_name, confidence) or None"""

        if self.model is None:
            return None

        features = self.extract_features(audio, self.sample_rate)
        if features is None:
            return None

        # add batch dimension
        features = np.expand_dims(features, 0)

        # predict
        prediction = self.model.predict(features, verbose=0)
        class_idx = np.argmax(prediction)
        confidence = float(prediction[0][class_idx])
        class_name = AUDIO_CLASSES[class_idx]

        return class_name, confidence

    def patrol(self):
        """main loop - continuously listens and classifies sounds
        sends alerts when it hears something threatening"""

        if self.model is None:
            print("[ECHO] no model loaded, cant patrol")
            print("[ECHO] run with --train first")
            return

        print("[ECHO] patrol mode active, listening...")

        while self.alive:
            try:
                # record a chunk of audio
                audio = sd.rec(
                    int(self.chunk_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()  # wait until recording is done
                audio = audio.flatten()

                # classify it
                result = self.freq_hunt(audio)

                if result is None:
                    continue

                class_name, confidence = result

                # only act on confident predictions
                if confidence < AUDIO_CONFIDENCE_THRESHOLD:
                    continue

                is_threat = class_name in THREAT_SOUNDS

                # log to database
                self.db.add_audio(class_name, confidence, is_threat)

                # send to dashboard
                self.syn.publish(TOPICS["audio"], json.dumps({
                    "class": class_name,
                    "confidence": confidence,
                    "is_threat": is_threat,
                    "time": time.strftime("%H:%M:%S")
                }))

                if is_threat:
                    print(f"[ECHO] ⚠️ THREAT: {class_name} ({confidence:.0%})")
                    self.syn.publish(TOPICS["eyes"], json.dumps({"state": "threat"}))
                    self.syn.publish(TOPICS["led"], json.dumps({"mode": "red_strobe"}))
                    self.syn.publish(TOPICS["buzzer"], json.dumps({"beeps": 3}))
                    self.db.add_alert("AUDIO_THREAT", class_name, confidence)
                else:
                    # just log it, no alert
                    print(f"[ECHO] heard: {class_name} ({confidence:.0%})")

            except Exception as e:
                print(f"[ECHO] error: {e}")
                time.sleep(1)

    def flatline(self):
        """shutdown"""
        self.alive = False
        self.syn.disconnect()
        self.db.close()
        print("[ECHO] sound detection offline")


# standalone usage
if __name__ == "__main__":
    import sys as _sys

    eh = EchoHunter()

    if "--train" in _sys.argv:
        # python echo_hunter.py --train
        eh.train()
    elif "--test" in _sys.argv:
        # python echo_hunter.py --test
        # quick test: record 2 seconds and classify
        print("recording 2 seconds...")
        audio = sd.rec(
            int(2 * eh.sample_rate),
            samplerate=eh.sample_rate,
            channels=1, dtype='float32'
        )
        sd.wait()
        audio = audio.flatten()

        result = eh.freq_hunt(audio)
        if result:
            print(f"detected: {result[0]} ({result[1]:.0%})")
        else:
            print("couldnt classify (model not loaded?)")
    else:
        # python echo_hunter.py
        # normal mode - continuous listening
        try:
            eh.patrol()
        except KeyboardInterrupt:
            print("\nstopped")

    eh.flatline()