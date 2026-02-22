"""
ECHO HUNTER.PY — AUDIO CLASSIFICATION
CNN-based environmental sound detection.
Detects: gunshots, screams, sirens, glass breaking, and more.
"""

import json
import time
import threading
import numpy as np
import dna
from blackbox import Blackbox
from synapse  import Synapse

try:
    import sounddevice as sd
    import librosa
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class EchoHunter:
    def __init__(self, synapse: Synapse, blackbox: Blackbox):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.running   = False
        self.model     = None
        self.mode      = dna.DEFAULT_MODE

        if TF_AVAILABLE:
            self._load_model()
        else:
            print("  [ECHO] TensorFlow not available — audio CNN disabled")

        synapse.subscribe(dna.TOPIC["mode"], lambda p: setattr(self, "mode", p.strip()))

    def _load_model(self):
        import os
        model_path = "models/audio_classifier.h5"
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            print(f"  [ECHO] Audio CNN loaded: {model_path}")
        else:
            print("  [ECHO] Audio model not found. Run training/train_audio_cnn.py first.")

    def _record_chunk(self, duration: float = None) -> np.ndarray:
        """Record a chunk of audio."""
        dur = duration or dna.AUDIO_CHUNK_DURATION
        return sd.rec(
            int(dur * dna.AUDIO_SAMPLE_RATE),
            samplerate=dna.AUDIO_SAMPLE_RATE,
            channels=1, dtype="float32", blocking=True
        ).flatten()

    def _audio_to_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """Convert audio to mel spectrogram for CNN input."""
        mel = librosa.feature.melspectrogram(
            y=audio, sr=dna.AUDIO_SAMPLE_RATE,
            n_mels=128, fmax=8000
        )
        mel_db = librosa.power_to_db(mel, ref=np.max)
        # Resize to 128x128
        mel_resized = librosa.util.fix_length(mel_db, size=128, axis=1)
        mel_resized = mel_resized[:128, :128]
        return mel_resized.reshape(1, 128, 128, 1).astype(np.float32)

    def freq_hunt(self, audio: np.ndarray) -> dict:
        """Run audio through CNN and return classification result."""
        if self.model is None:
            return {"label": "unknown", "confidence": 0.0}

        try:
            spectrogram = self._audio_to_spectrogram(audio)
            predictions = self.model.predict(spectrogram, verbose=0)[0]
            best_idx    = int(np.argmax(predictions))
            label       = dna.AUDIO_CLASSES[best_idx]
            confidence  = float(predictions[best_idx])
            return {"label": label, "confidence": confidence}
        except Exception as e:
            return {"label": "error", "confidence": 0.0}

    def run(self):
        """Continuous audio monitoring loop."""
        if not SD_AVAILABLE or not TF_AVAILABLE or self.model is None:
            print("  [ECHO] Audio monitoring disabled (missing dependencies or model)")
            return

        self.running = True
        print("  [ECHO] Audio monitoring started")

        while self.running:
            try:
                audio  = self._record_chunk()
                result = self.freq_hunt(audio)

                # Only publish if confident
                if result["confidence"] > 0.70:
                    self.synapse.publish(dna.TOPIC["audio"], json.dumps(result))

                    label = result["label"]
                    conf  = result["confidence"]
                    print(f"  [ECHO] Detected: {label} ({conf:.0%})")

                    # Trigger alerts for threat sounds
                    if label in dna.AUDIO_THREAT_CLASSES:
                        self.synapse.publish(dna.TOPIC["led"],    "threat")
                        self.synapse.publish(dna.TOPIC["eyes"],   "threat")
                        self.synapse.publish(dna.TOPIC["buzzer"], "on")
                        self.synapse.publish(dna.TOPIC["alerts"],
                                            f"AUDIO THREAT: {label} ({conf:.0%})")
                        self.blackbox.log_event("AUDIO_THREAT",
                                               {"label": label, "confidence": conf})

            except Exception as e:
                print(f"  [ECHO] Error: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False
