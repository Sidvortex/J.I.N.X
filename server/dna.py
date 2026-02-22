# dna.py - jinx configuration
# dont touch this unless you know what ur doing lol

# -- network stuff --
LAPTOP_IP = "127.0.0.1"  # localhost for testing, change to 192.168.1.10 when router is set up
PHONE_IP = "192.168.1.11"
TABLET_IP = "192.168.1.12"
ESP32_IP = "192.168.1.20"
MQTT_PORT = 1883
CAMERA_URL = f"http://{PHONE_IP}:8080/video"
DASHBOARD_PORT = 8501

# gemini api key (dont push this to github bruh)
GEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"  # TODO: move to .env later

# paths
KNOWN_FACES_DIR = "data/known_faces/"
ALERTS_DIR = "data/alerts/"
DB_PATH = "data/jinx_database.db"
AUDIO_MODEL_PATH = "models/audio_classifier.h5"
VOSK_MODEL_PATH = "models/vosk-model/"
SOUNDS_DIR = "assets/sounds/"

# face labels - add more people here
# "safe" = green box, "threat" = red box
FACE_LABELS = {
    "admin": "safe",
    # "amit": "safe",
    # "random_guy": "threat",  # lmao
}

# mqtt topics
# i know this is a lot but each one does something different trust me
TOPICS = {
    "eyes": "jinx/eyes",
    "head_track": "jinx/head_track",
    "eye_track": "jinx/eye_track",
    "motor": "jinx/motor",
    "led": "jinx/led",
    "sound": "jinx/sound",
    "buzzer": "jinx/buzzer",
    "sensors": "jinx/sensors",
    "battery": "jinx/battery",
    "status": "jinx/status",
    "frame": "jinx/frame",
    "audio": "jinx/audio",
    "alerts": "jinx/alerts",
    "mode": "jinx/mode",
    "command": "jinx/command",
    "voice": "jinx/voice",
}

# detection thresholds - tweaked these a LOT to get them right
FACE_RECOGNITION_TOLERANCE = 0.5  # lower = stricter matching
FACE_DETECTION_CONFIDENCE = 0.5
POSE_DETECTION_CONFIDENCE = 0.5
AUDIO_CONFIDENCE_THRESHOLD = 0.7  # was 0.6 but too many false positives
THREAT_SCORE_THRESHOLD = 0.7

# audio classes (from urbansound8k dataset)
AUDIO_CLASSES = [
    'air_conditioner', 'car_horn', 'children_playing',
    'dog_bark', 'drilling', 'engine_idling',
    'gun_shot', 'jackhammer', 'siren', 'street_music'
]
THREAT_SOUNDS = ['gun_shot', 'siren', 'car_horn']

# colors in BGR (opencv uses BGR not RGB, this confused me for 2 hours)
NEON_CYAN = (255, 255, 0)
NEON_GREEN = (0, 255, 0)
NEON_MAGENTA = (255, 0, 255)
NEON_RED = (0, 0, 255)
NEON_BLUE = (255, 100, 0)
NEON_YELLOW = (0, 255, 255)
NEON_PURPLE = (255, 0, 128)