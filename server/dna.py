# ============================================================
#  DNA.PY — DESKBOT CONFIGURATION
#  All settings, IPs, thresholds, and API keys live here.
#  Copy this to dna.py and fill in your values.
# ============================================================

# ── Network ─────────────────────────────────────────────────
LAPTOP_IP    = "192.168.1.100"   # Your laptop's local IP
PHONE_IP     = "192.168.1.101"   # Redmi Note 12 static IP
TABLET_IP    = "192.168.1.102"   # Tablet static IP
MQTT_BROKER  = LAPTOP_IP
MQTT_PORT    = 1883

CAMERA_URL   = f"http://{PHONE_IP}:4747/video"   # DroidCam stream URL
DASHBOARD_PORT = 8501
WEB_PORT       = 5000

# ── API Keys ─────────────────────────────────────────────────
GEMINI_API_KEY      = "YOUR_GEMINI_API_KEY_HERE"        # aistudio.google.com
ELEVENLABS_API_KEY  = ""   # Optional — leave blank to use edge-TTS (free)
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # "Adam" — change as you like
OPENWEATHER_API_KEY = ""   # Optional — for weather queries

# ── Face Recognition ─────────────────────────────────────────
FACE_TOLERANCE    = 0.50        # Lower = stricter (0.4–0.6 range)
KNOWN_FACES_DIR   = "data/known_faces"
FACE_LABELS = {
    # "filename_without_ext": "safe" | "threat"
    "admin":  "safe",
    # Add more:
    # "friend": "safe",
    # "intruder": "threat",
}

# ── Vision ───────────────────────────────────────────────────
VISION_FPS           = 20       # Target FPS for camera processing
YOLO_CONFIDENCE      = 0.5
POSE_CONFIDENCE      = 0.7
HEAD_TRACK_ENABLED   = True     # Enable head servo tracking

# ── Audio ─────────────────────────────────────────────────────
AUDIO_SAMPLE_RATE    = 22050
AUDIO_CHUNK_DURATION = 2.0      # Seconds per audio classification window
AUDIO_CLASSES = [
    "air_conditioner", "car_horn", "children_playing",
    "dog_bark", "drilling", "engine_idling",
    "gun_shot", "jackhammer", "siren", "street_music"
]
AUDIO_THREAT_CLASSES = {"gun_shot", "siren", "glass_break"}

# ── Sensors / Safety ──────────────────────────────────────────
OBSTACLE_DANGER_CM       = 20   # Ultrasonic: stop if closer than this
DEPTH_DANGER_MM          = 80   # VL53L0X facing down: table edge threshold
FORWARD_OBSTACLE_MM      = 150  # VL53L0X facing forward: obstacle threshold

# ── Battery ───────────────────────────────────────────────────
BATTERY_LOW_PERCENT      = 15   # Alert threshold
BATTERY_CRITICAL_PERCENT = 8    # Shutdown warning threshold
BATTERY_FULL_VOLTAGE     = 8.4  # 2S Li-ion full charge
BATTERY_EMPTY_VOLTAGE    = 6.0  # 2S Li-ion cutoff
VOLTAGE_DIVIDER_RATIO    = 2.0  # R1=R2=10kΩ so ratio=2

# ── Voice ─────────────────────────────────────────────────────
WAKE_WORD          = "hey jinx"
VOICE_TIMEOUT      = 5          # Seconds to wait for command after wake word
USE_OFFLINE_STT    = True       # Vosk (offline) or Google (online, more accurate)
VOICE_GENDER       = "male"     # edge-TTS voice gender if ElevenLabs not set
# Edge-TTS voice options: "en-US-GuyNeural", "en-US-JasonNeural", "en-IN-PrabhatNeural"
EDGE_TTS_VOICE     = "en-US-GuyNeural"

# ── AI Agent ──────────────────────────────────────────────────
DOCUMENTS_DIR      = "data/documents"    # Upload PDFs/docs here for Q&A
WATCH_CODE_DIR     = ""                  # Set to your project folder for code review
MAX_CONTEXT_TOKENS = 32000

# ── Network Monitoring ────────────────────────────────────────
NETWORK_SCAN_INTERVAL = 60      # Seconds between network scans
TRUSTED_MACS = [
    # "AA:BB:CC:DD:EE:FF",   # Add trusted device MACs
]

# ── Personality ───────────────────────────────────────────────
ROAST_INTENSITY  = "medium"     # "light" | "medium" | "savage"
HUMOR_FREQUENCY  = 0.3          # 0.0–1.0: how often to make unprompted jokes
BOT_NAME         = "JINX"

# ── Sensor Fusion Weights ────────────────────────────────────
FUSION_WEIGHTS = {
    "visual":    0.35,
    "audio":     0.30,
    "network":   0.20,
    "proximity": 0.15,
}
DOOM_ALERT_THRESHOLD = 0.70

# ── MQTT Topics ───────────────────────────────────────────────
TOPIC = {
    "eyes":          "jinx/eyes",
    "head_track":    "jinx/head_track",
    "eye_track":     "jinx/eye_track",
    "motor":         "jinx/motor",
    "led":           "jinx/led",
    "sound":         "jinx/sound",
    "buzzer":        "jinx/buzzer",
    "sensors":       "jinx/sensors",
    "battery":       "jinx/battery",
    "status":        "jinx/status",
    "frame":         "jinx/frame",
    "audio":         "jinx/audio",
    "alerts":        "jinx/alerts",
    "mode":          "jinx/mode",
    "command":       "jinx/command",
    "doom_level":    "jinx/doom_level",
    "network_stats": "jinx/network_stats",
    "depth":         "jinx/depth",
    "web_command":   "jinx/web_command",
}

# ── Operating Modes ────────────────────────────────────────────
class Mode:
    BUDDY      = "buddy"
    SENTINEL   = "sentinel"
    ROAST      = "roast"
    DOCK       = "dock"
    SLEEP      = "sleep"
    AGENT      = "agent"

DEFAULT_MODE = Mode.BUDDY
