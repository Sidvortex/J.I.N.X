<div align="center">

# 🤖 J.I.N.X
### **Judgmental AI Desk Companion**

![Version](https://img.shields.io/badge/version-2.1.0-cyan?style=for-the-badge)
![Status](https://img.shields.io/badge/status-ACTIVE-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python)
![ESP32](https://img.shields.io/badge/ESP32-WROOM--32-red?style=for-the-badge)
![Budget](https://img.shields.io/badge/budget-₹4%2C550-yellow?style=for-the-badge)

<br>

*An autonomous AI desk robot with real-time computer vision, human-like voice,
face recognition, skeleton tracking, document Q&A, live code review,
home automation, and a sarcastic personality — built from electronic waste.*

<br>

**B.Tech Final Year Project — Data Science (2023–2027)**

<br>

[Features](#-features) ·
[Architecture](#-system-architecture) ·
[Hardware](#-hardware) ·
[ML Models](#-ml-models) ·
[Installation](#-installation) ·
[Usage](#-usage) ·
[Codex](#-codex) ·
[Demo](#-demo-setup) ·
[License](#-license)

</div>

---

## 📌 About

**J.I.N.X** is a multi-modal AI robotic desk companion that sees, hears, speaks, judges, and even reviews your code — all built from recycled electronics, a spare smartphone, a dead ThinkPad, and low-cost microcontrollers within a budget of ₹4,550.

It combines **10 machine learning models** spanning computer vision, audio classification, natural language understanding, network security, and sensor fusion into a single desk-mounted platform with a cyberpunk aesthetic and an attitude problem.

> *"Born from a dead ThinkPad T61 that couldn't even turn on anymore. Its metal chassis became J.I.N.X's body. A spare phone that couldn't make calls became its eyes, ears, and voice. Total hardware cost: ₹4,550. This project proves that AI isn't about expensive hardware — it's about intelligence."*

---

## 🎯 Problem Statement

AI robotics projects in academic settings typically require expensive GPUs, dedicated AI boards, and premium sensors — inaccessible to students on tight budgets. Most systems also focus on a single modality (vision-only or voice-only), lacking the multi-sensory integration needed for truly autonomous and useful robotic behavior.

**J.I.N.X** addresses both challenges: a fully multi-modal AI companion using recycled electronics, low-cost microcontrollers, and open-source ML frameworks at under ₹4,600 total.

---

## 🎯 Objectives

1. Develop a multi-modal AI system capable of real-time face detection, recognition, and classification (safe / unknown / threat) using computer vision.
2. Implement pose estimation and gesture recognition for human-robot interaction and device control.
3. Build and train a CNN for environmental audio classification and anomaly detection.
4. Integrate NLP for voice-command control and conversational AI using Gemini LLM with a human-sounding neural TTS voice.
5. Build an AI agent capable of answering questions from uploaded documents and reviewing live code.
6. Design an IoT sensor fusion system combining visual, audio, proximity, and depth sensor data for intelligent decision-making.
7. Implement depth-aware safety (table edge detection using VL53L0X ToF sensors) and autonomous battery management.
8. Demonstrate sustainable engineering by constructing the system primarily from recycled components under a constrained budget.

---

## ✨ Features

### 🧠 AI & Intelligence

| Feature | Description |
|---|---|
| 👁️ **Face Detection & Recognition** | Detects and recognizes faces in real-time. Color-coded bounding boxes: 🟢 Known Safe, 🔵 Unknown, 🔴 Flagged Threat |
| 🦴 **Skeleton / Pose Estimation** | 33-keypoint full body skeleton overlay — use it to analyze posture, show off during a dance, or detect falls |
| 🖐️ **Gesture Control** | 21-keypoint hand gesture recognition — control LEDs, change modes, trigger actions without touching anything |
| 🎭 **Face Mesh** | 468-point real-time facial landmark mesh — dramatic scanning visual effect |
| 🔊 **Audio Classification** | CNN-trained on UrbanSound8K — detects gunshots, sirens, glass breaking, screams, dog barks in real-time |
| 🗣️ **Wake Word + Voice Commands** | "Hey JINX, [command]" — offline wake word detection, full voice control |
| 💬 **Conversational AI** | Gemini 2.0 Flash-powered conversations with context memory and sarcastic personality |
| 🎙️ **Human Voice (edge-TTS)** | Microsoft Neural TTS — sounds like a real human, not a robot. Free. No API key needed |
| 📄 **Document Q&A** | Upload PDFs, books, notes to `data/documents/` — ask J.I.N.X questions about them by voice or web |
| 💻 **Code Review Agent** | Point it at your project folder — auto-reviews changed files on save, flags bugs, security issues, style problems |
| 🔥 **Roast Mode** | Scans your face, identifies you, generates a personalized AI roast via Gemini, delivers it through the speaker |
| 🎵 **Music Playback** | Voice-activated music search and streaming via yt-dlp + mpv |
| 💡 **Home Automation** | IoT LED strip + smart device control via voice and gesture |
| 🛡️ **Network Monitor** | Detects all devices on WiFi, flags unknown/new devices, traffic anomaly detection |

### 🤖 Physical & Mechanical

| Feature | Description |
|---|---|
| 👀 **Animated Eyes** | 2.4" TFT display with 12 emotional states: neutral, happy, angry, sleepy, love, scanning, threat, roast, music, thinking, talking, boot |
| 🔄 **Head Tracking** | Pan-tilt servo mechanism — J.I.N.X physically turns its head to follow detected faces |
| 👁️ **Pupil Tracking** | Digital eye pupils follow face position on the TFT display, synchronized with servo movement |
| 📏 **Table Edge Detection** | VL53L0X ToF sensor facing downward — detects desk edges with millimeter accuracy, stops motors instantly |
| 🚧 **Obstacle Avoidance** | Dual HC-SR04 ultrasonic + forward VL53L0X — stops before hitting anything |
| 🔋 **Battery Management** | 7.4V 18650 2S2P pack, BMS protection, voltage monitoring via ESP32 ADC |
| 🔔 **Low Battery Alert** | At <15%: eyes go sleepy, LEDs pulse yellow, J.I.N.X says *"I'm running on spite"* |
| 🌈 **Reactive LED System** | WS2812B strip with 11 animated modes — reacts to mood, threats, music, and battery level |
| 🔊 **Built-in Speaker** | DFPlayer Mini + 3W speaker for sound effects. Neural TTS plays through phone speaker |
| ♻️ **Recycled Body** | ThinkPad T61 chassis, keyboard keys, RAM sticks, HDD platters as decoration |

### 🌐 Control & Interface

| Feature | Description |
|---|---|
| 📱 **Web Control Panel** | Phone/tablet browser UI at `http://LAPTOP_IP:5000` — live feed, mode switching, LED colors, movement, document upload, code paste |
| 🖥️ **Streamlit Dashboard** | Cyberpunk command center at port 8501 — camera feed, skeleton view, network map, audio viz, alert log |
| 📲 **Remote Control** | Any device on the same WiFi can control J.I.N.X from a browser — no app needed |

---

### 🔀 Operating Modes

```
MODE 1: BUDDY (Default)
├── Friendly personality, responds to voice commands
├── Answers questions, plays music, controls lights
├── Eyes follow people, head tracks faces
├── Skeleton overlay shows your movements in real-time
└── Returns low-battery warning when needed

MODE 2: SENTINEL (Surveillance)
├── Active scanning — color-coded face + object detection
│   ├── 🟢 GREEN  = Known + Safe
│   ├── 🔵 BLUE   = Unknown (not in database)
│   └── 🔴 RED    = Known + Flagged as Threat
├── Audio anomaly detection (glass break, screams, gunshots)
├── Network device monitoring — flags unknown WiFi devices
├── All events logged with timestamps + screenshots
└── LED strips react to threat level in real-time

MODE 3: ROAST
├── Scans person's face → identifies from database
├── Generates personalized comedic roast via Gemini
├── Delivers roast through speaker in human voice
├── Eyes show smug expression, LEDs flash orange party mode
└── Adjustable intensity: light / medium / savage

MODE 4: AGENT
├── Document Q&A — ask questions about uploaded PDFs/books
├── Code review — watches your project folder, reviews on save
├── Image search — "what does a golden retriever look like?"
├── Research assistant — searches web for answers
└── Read document aloud — summarizes books by voice command

MODE 5: SLEEP
├── Eyes close, LEDs dim
├── Wake word still active
└── "I was in the middle of something."
```

---

## 🏗️ System Architecture

```
                ┌──────────────────────────────────┐
                │       LAPTOP (Main Server)        │
                │                                  │
                │  🧠 ML Models:                   │
                │  ├── YOLOv5-nano (object detect)  │
                │  ├── MediaPipe (Face/Pose/Hands)   │
                │  ├── face_recognition (dlib)      │
                │  ├── Audio CNN (UrbanSound8K)     │
                │  ├── Vosk STT (offline)           │
                │  ├── edge-TTS (neural voice)      │
                │  ├── Gemini 2.0 Flash (LLM)       │
                │  ├── Network Anomaly (RF)         │
                │  └── Sensor Fusion (Hivemind)     │
                │                                  │
                │  🌐 Services:                     │
                │  ├── Python Backend               │
                │  ├── MQTT Broker (Mosquitto)      │
                │  ├── Flask Web Control (:5000)    │
                │  ├── Streamlit Dashboard (:8501)  │
                │  └── SQLite Database              │
                └───────────────┬──────────────────┘
                                │
                           WiFi Router
                      (Private Local Network)
                                │
          ┌─────────────────────┼──────────────────────┐
          │                     │                      │
   ┌──────▼──────┐      ┌──────▼──────┐       ┌──────▼──────┐
   │  J.I.N.X    │      │   TABLET    │        │   PHONE     │
   │  ROBOT      │      │  DASHBOARD  │        │  (Control   │
   │             │      │             │        │   Panel)    │
   │ ┌─────────┐ │      │  ─ Camera   │        │             │
   │ │  ESP32  │ │      │  ─ Skeleton │        │ http://     │
   │ │─Motors  │ │      │  ─ Network  │        │ LAPTOP:5000 │
   │ │─Servos  │ │      │  ─ Alerts   │        └─────────────┘
   │ │─TFT Eyes│ │      │  ─ Audio    │
   │ │─LEDs    │ │      │  ─ Battery  │
   │ │─Sensors │ │      └─────────────┘
   │ │─Speaker │ │
   │ └─────────┘ │
   │ ┌─────────┐ │
   │ │Redmi 12 │ │
   │ │─Camera  │ │
   │ │─Mic     │ │
   │ │─Speaker │ │  ← Neural TTS voice plays here
   │ └─────────┘ │
   └─────────────┘
```

### Data Flow Pipelines

```
VISION:   Phone Camera → WiFi → Laptop → YOLO + MediaPipe + face_recognition
          → Annotated Frame → Tablet Dashboard + MQTT → ESP32 (eyes/LEDs/servos)

VOICE:    Microphone → Laptop → Vosk STT → Command Parser / Gemini LLM
          → edge-TTS → Phone Speaker + DFPlayer Sound Effects

AUDIO:    Mic → Laptop → Mel Spectrogram → CNN → Alert System
          → ESP32 (LEDs/buzzer/eyes)

DEPTH:    VL53L0X (down) → ESP32 → MQTT → Laptop → Stop motor if edge detected
          VL53L0X (fwd)  → ESP32 → MQTT → Laptop → Stop if obstacle < 15cm

NETWORK:  WiFi Router → scapy → Device Scanner → Anomaly Model
          → Dashboard + Alerts

FUSION:   Visual + Audio + Network + Proximity scores → Weighted average
          → doom_level (0–1) → LED color + eye state + alert log
```

---

## 🔧 Hardware

### Purchased Components (~₹3,750 from original JINX build + ~₹800 additions)

| # | Component | Spec | Purpose |
|---|---|---|---|
| 1 | ESP32-WROOM-32 DevKit | WiFi+BT, 30-pin | Robot brain |
| 2 | 2.4" TFT ILI9341 | 240×320, SPI | Animated eyes |
| 3 | SG90 Servo (×2) | 180°, 1.8kg-cm | Head pan + tilt |
| 4 | L298N Motor Driver | Dual H-Bridge | DC motor control |
| 5 | HC-SR04 Ultrasonic (×2) | 2-400cm | Obstacle detection |
| 6 | **VL53L0X ToF Sensor (×2)** | 2m, ±1mm, I2C | Table edge + precise obstacle depth |
| 7 | IR Sensor (×2) | Digital output | Secondary edge detection |
| 8 | WS2812B LED Strip | 30 LEDs, 5V | Mood reactive lighting |
| 9 | DFPlayer Mini + 3W Speaker | UART, MP3 | Sound effects |
| 10 | 18650 Battery (×4) | 3.7V 2600mAh | 2S2P = 7.4V ~5000mAh |
| 11 | 2S BMS Board | 7.4V 10A | Battery protection |
| 12 | TP4056 Modules (×2) | 5V 1A | Charging |
| 13 | Active Buzzer | 5V | Alerts |
| 14 | 10kΩ Resistors (×4) | 1/4W | Voltage divider |
| 15 | Jumper Wires + Breadboard | — | Wiring |

> **Why VL53L0X over IR for depth?** IR sensors only give "object yes/no". The VL53L0X gives exact distance in millimeters via I2C — so J.I.N.X knows it's 5mm from a table edge vs 50mm, and can react proportionally.

### Recycled / Pre-owned

| Component | Source | Purpose |
|---|---|---|
| Metal parts, keyboard keys, RAM, HDD platters, fan | Lenovo ThinkPad T61 | Body structure + decoration |
| Camera, mic, speaker, display, WiFi | Xiaomi Redmi Note 12 | Primary sensor array + neural TTS speaker |
| Tablet | UP Govt issued | Dashboard display |
| WiFi Router | Pre-owned | Private local network |
| Bluetooth Mic | Pre-owned | Voice input |

**Total hardware cost: ~₹4,550**
Recycled components saved an estimated ₹15,000+ in equivalent hardware costs.

### GPIO Pin Mapping

```
TFT DISPLAY (ILI9341):        I2C BUS (VL53L0X):
├── GPIO 18 → SCK             ├── GPIO 21 → SDA
├── GPIO 23 → MOSI            └── GPIO 22 → SCL
├── GPIO 15 → CS              (TOF1 XSHUT → GPIO 13)
├── GPIO 2  → DC              (TOF2 XSHUT → GPIO 12)
└── GPIO 4  → RST

SERVOS (Pan-Tilt):            MOTORS (L298N):
├── GPIO 19 → Pan             ├── GPIO 25 → IN1
└── GPIO 11 → Tilt            ├── GPIO 26 → IN2
                              ├── GPIO 27 → IN3
LED STRIP (WS2812B):          ├── GPIO 14 → IN4
└── GPIO 16 → DATA            ├── GPIO 32 → ENA (PWM)
                              └── GPIO 33 → ENB (PWM)
ULTRASONIC:
├── GPIO 5/34 → US1 TRIG/ECHO BATTERY ADC:
└── GPIO 0/35 → US2 TRIG/ECHO └── GPIO 35 → ADC (voltage divider)

DFPLAYER: GPIO 16(RX), 17(TX)
BUZZER:   GPIO 12
IR:       GPIO 36, 39
```

---

## 🧠 ML Models

| # | Model | Task | Type | Dataset |
|---|---|---|---|---|
| 1 | YOLOv5-nano | Object Detection | Pre-trained | COCO (80 classes) |
| 2 | MediaPipe Face Mesh | 468-point Landmarks | Pre-trained | Google |
| 3 | MediaPipe Pose | 33-point Skeleton | Pre-trained | Google |
| 4 | MediaPipe Hands + Classifier | Gesture Recognition | Pre-trained + Custom | Google + Custom |
| 5 | dlib ResNet / face_recognition | Face Recognition (128-d embeddings) | Pre-trained + Custom DB | LFW + Your faces |
| 6 | Custom CNN (2D Conv) | Audio Classification | Trained from scratch | UrbanSound8K |
| 7 | Vosk / Google STT | Speech-to-Text | Pre-trained | — |
| 8 | Gemini 2.0 Flash | NLU + Conversation + Agent | API | Google |
| 9 | Random Forest | Network Anomaly Detection | Trained | NSL-KDD |
| 10 | Weighted Ensemble | Sensor Fusion | Custom | — |

### Audio CNN Architecture

```
Input: 128×128 Mel Spectrogram
  │
  ├── Conv2D(32, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
  ├── Conv2D(64, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
  ├── Conv2D(128, 3×3) → BatchNorm → ReLU → MaxPool(2×2)
  ├── Conv2D(64, 3×3) → GlobalAveragePooling
  ├── Dense(256) → ReLU → Dropout(0.4)
  ├── Dense(128) → ReLU → Dropout(0.3)
  └── Dense(10) → Softmax

Classes: air_conditioner, car_horn, children_playing, dog_bark,
         drilling, engine_idling, gun_shot, jackhammer, siren, street_music
Dataset: UrbanSound8K (8,732 samples)
```

### Sensor Fusion (Hivemind)

```
Visual Score  (0–1) × 0.35  ←  face_recognition threat level
Audio Score   (0–1) × 0.30  ←  CNN threat-class confidence
Network Score (0–1) × 0.20  ←  anomaly model prediction
Proximity     (0–1) × 0.15  ←  ultrasonic + ToF distances
                    ↓
              doom_level (0–1)
              > 0.70 → ALERT → LED + eyes + buzzer + log
```

---

## 📖 Codex

All modules use cyberpunk-inspired codenames.

| File | Codename | Purpose |
|---|---|---|
| `genesis.py` | GENESIS | Main startup — launches everything |
| `dna.py` | DNA | All configuration and settings |
| `blackbox.py` | BLACKBOX | SQLite event logging |
| `psyche.py` | PSYCHE | Personality, jokes, roast prompts |
| `optic.py` | OPTIC | Vision — camera, faces, pose, mesh, gestures |
| `vocoder.py` | VOCODER | Voice — STT, neural TTS, Gemini, commands, music |
| `echo_hunter.py` | ECHO HUNTER | Audio — CNN sound classification |
| `ice_wall.py` | ICE WALL | Network — device scan, anomaly detection |
| `synapse.py` | SYNAPSE | MQTT — all inter-module messaging |
| `hivemind.py` | HIVEMIND | Sensor fusion — doom level scoring |
| `agent.py` | AGENT | AI Agent — document Q&A + code review |
| `nexus.py` | NEXUS | Streamlit cyberpunk dashboard |
| `web_control/app.py` | NEXUS-WEB | Flask phone control panel |

---

## 📁 Project Structure

```
J.I.N.X/
│
├── server/
│   ├── genesis.py          # Main startup + module orchestration
│   ├── dna.py              # All config (IPs, API keys, thresholds)
│   ├── blackbox.py         # SQLite logging
│   ├── psyche.py           # Personality + humor system
│   ├── optic.py            # Vision pipeline
│   ├── vocoder.py          # Voice system (STT + neural TTS + Gemini)
│   ├── echo_hunter.py      # Audio CNN
│   ├── ice_wall.py         # Network monitoring
│   ├── synapse.py          # MQTT hub
│   ├── hivemind.py         # Sensor fusion
│   └── agent.py            # Document Q&A + code review agent
│
├── dashboard/
│   └── nexus.py            # Streamlit cyberpunk dashboard (:8501)
│
├── web_control/
│   ├── app.py              # Flask control server (:5000)
│   └── templates/
│       └── index.html      # Phone/browser UI
│
├── arduino/
│   └── jinx_esp32/
│       ├── jinx_esp32.ino  # Main firmware
│       ├── config.h           # Pin definitions + WiFi + MQTT topics
│       ├── eyes.h             # TFT animated eye states (12 modes)
│       ├── motors.h           # L298N DC motor control
│       ├── sensors.h          # Ultrasonic + VL53L0X + IR + Battery + DFPlayer
│       └── servos.h           # Pan-tilt head servo (smooth interpolation)
│
├── training/
│   └── train_audio_cnn.py     # CNN training on UrbanSound8K
│
├── scripts/
│   └── register_face.py       # Add faces to database (file or live camera)
│
├── models/
│   ├── audio_classifier.h5    # Trained audio CNN (generated)
│   ├── network_anomaly.pkl    # Trained network model (generated)
│   └── vosk-model/            # Offline STT model (downloaded)
│
├── data/
│   ├── known_faces/           # Face images — filename = person name
│   ├── documents/             # Upload PDFs/books here for agent Q&A
│   ├── alerts/                # Auto-saved alert screenshots
│   └── jinx_database.db       # SQLite database (auto-generated)
│
├── assets/sounds/             # MP3 files for DFPlayer
├── BUILD_GUIDE.md             # Full hardware assembly guide
├── requirements.txt
└── README.md
```

---

## ⚡ Installation

### Prerequisites

```
Personal laptop (Linux recommended, Windows/Mac also work)
Python 3.10+
Arduino IDE 2.x
Assembled J.I.N.X hardware
WiFi router (private network)
Redmi Note 12 with DroidCam installed
Mosquitto MQTT broker
cmake (for face_recognition/dlib)
mpv (for audio/music playback)
```

### Step 1 — Clone

```bash
git clone https://github.com/Sidvortex/J.I.N.X.git
cd J.I.N.X
```

### Step 2 — Install Dependencies

```bash
# Ubuntu/Debian
sudo apt install mosquitto cmake libcmake-data espeak-ng mpv yt-dlp \
                 portaudio19-dev python3-pip

# Arch/EndeavourOS
sudo pacman -S mosquitto cmake espeak-ng mpv yt-dlp portaudio python-pip

# Python packages
pip install -r requirements.txt

# Start MQTT broker
sudo systemctl enable --now mosquitto
```

### Step 3 — Configure

```bash
cp server/dna.py server/dna.py.example
nano server/dna.py

# Set:
LAPTOP_IP       = "your.laptop.ip"
PHONE_IP        = "redmi.note.ip"
GEMINI_API_KEY  = "get from aistudio.google.com"
FACE_LABELS     = {"yourname": "safe"}
```

### Step 4 — Download ML Models

```bash
# Vosk offline STT model
mkdir -p models/vosk-model
# Download from: https://alphacephei.com/vosk/models
# Use: vosk-model-small-en-us-0.15 (~40MB)
# Extract contents into models/vosk-model/

# YOLOv5 (auto-downloads on first run)
python -c "from ultralytics import YOLO; YOLO('yolov5n.pt')"
```

### Step 5 — Train Audio Model (Optional)

```bash
# Download UrbanSound8K from:
# https://urbansounddataset.weebly.com/urbansound8k.html
# Extract to: data/urbansound8k/

python training/train_audio_cnn.py
# Takes ~30 minutes, saves to models/audio_classifier.h5
```

### Step 6 — Register Your Face

```bash
# From a photo file
python scripts/register_face.py --name yourname --file photo.jpg --label safe

# Or live from camera
python scripts/register_face.py --name yourname --live --label safe

# Then add to dna.py:
FACE_LABELS = {"yourname": "safe"}
```

### Step 7 — Flash ESP32

```
1. Open Arduino IDE 2.x
2. Open arduino/jinx_esp32/jinx_esp32.ino
3. Install libraries via Library Manager:
   TFT_eSPI, Adafruit NeoPixel, PubSubClient,
   ArduinoJson, ESP32Servo, DFRobotDFPlayerMini, VL53L0X
4. Edit arduino/jinx_esp32/config.h:
   - Set WIFI_SSID, WIFI_PASS, MQTT_BROKER
5. Configure TFT_eSPI: edit User_Setup.h in its library folder
   (see BUILD_GUIDE.md for exact settings)
6. Board: ESP32 Dev Module
7. Upload
```

### Step 8 — Setup Phone

```
1. Install DroidCam on Redmi Note 12
2. Connect to same WiFi network
3. Set static IP in router settings
4. Update PHONE_IP in server/dna.py
5. Open DroidCam → Start Server
6. Test: http://PHONE_IP:4747/video in browser
```

---

## 🚀 Usage

### Starting J.I.N.X

```bash
# Normal startup
python server/genesis.py

# Start in Sentinel mode
python server/genesis.py --sentinel

# Start in Agent mode (document/code focus)
python server/genesis.py --agent-mode

# Skip modules for faster startup
python server/genesis.py --no-audio --no-network

# Individual module testing
python server/optic.py          # Vision only
python server/vocoder.py        # Voice only
python server/echo_hunter.py    # Audio only
```

### Startup Output

```
     ██████╗ ███████╗███████╗██╗  ██╗██████╗  ██████╗ ████████╗
     ██╔══██╗██╔════╝██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
     ██║  ██║█████╗  ███████╗█████╔╝ ██████╔╝██║   ██║   ██║
     ██║  ██║██╔══╝  ╚════██║██╔═██╗ ██╔══██╗██║   ██║   ██║
     ██████╔╝███████╗███████║██║  ██╗██████╔╝╚██████╔╝   ██║
     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝

  [INIT] Loading SYNAPSE (MQTT Bridge)............. ✓
  [INIT] Loading BLACKBOX (Database)............... ✓
  [INIT] Loading PSYCHE (Personality Matrix)....... ✓
  [INIT] Loading OPTIC (Visual Cortex)............. ✓
  [INIT] Loading VOCODER (Voice System)............ ✓
  [INIT] Loading ECHO HUNTER (Sound Detection)..... ✓
  [INIT] Loading ICE WALL (Network Defense)........ ✓
  [INIT] Loading HIVEMIND (Sensor Fusion).......... ✓
  [INIT] Loading AGENT (AI Code/Doc Agent)......... ✓

  ⚡ J.I.N.X NEURAL CORE ONLINE ⚡
```

### Voice Commands

```
"Hey JINX, wake up"              → System activation
"Hey JINX, guard mode"           → Sentinel surveillance mode
"Hey JINX, buddy mode"           → Switch to buddy mode
"Hey JINX, agent mode"           → Document Q&A / code review mode
"Hey JINX, roast [name]"         → AI-generated personalized roast
"Hey JINX, what is [topic]"      → Gemini answers + shows image
"Hey JINX, play [song/genre]"    → Music search and playback
"Hey JINX, lights [color]"       → LED color change
"Hey JINX, come here"            → Move forward
"Hey JINX, go back"              → Move backward
"Hey JINX, status"               → System health report
"Hey JINX, register [name]"      → Save current face to database
"Hey JINX, read [document name]" → Summarizes uploaded document
"Hey JINX, review my code"       → Code review of watched folder
"Hey JINX, what does X look like"→ Image search shown on tablet
"Hey JINX, goodnight"            → Sleep mode
"Hey JINX, stop music"           → Stop playback
```

### Document Q&A (Agent Mode)

```bash
# Drop any PDF, text, or code file into data/documents/
cp my_textbook.pdf data/documents/
cp lecture_notes.txt data/documents/

# Then ask by voice:
"Hey JINX, what does chapter 3 say about neural networks?"
"Hey JINX, summarize the lecture notes"

# Or via web panel at http://LAPTOP_IP:5000 → AI Agent tab
```

### Code Review (Agent Mode)

```bash
# In dna.py, set:
WATCH_CODE_DIR = "/path/to/your/project"

# J.I.N.X will automatically review any Python/JS/Java file
# you save in that directory and publish the review to the dashboard.

# Or paste code in the web panel → Code Review tab
```

---

## 📊 Results & Metrics

| Model | Metric | Target |
|---|---|---|
| YOLOv5-nano | mAP@0.5 | 28% COCO baseline |
| Face Recognition | Accuracy | ~95%+ |
| Face Recognition | False Acceptance Rate | <2% |
| Pose Estimation | Keypoint Confidence | ~90%+ |
| Audio CNN | F1-Score | ~85%+ |
| Audio CNN | Accuracy | ~88%+ |
| Network Anomaly | ROC-AUC | ~92%+ |
| Voice Recognition | Word Error Rate | ~10-15% |
| Sensor Fusion | Detection Accuracy | ~90%+ |
| Table Edge Detection | Accuracy | ~99% (VL53L0X) |

*Metrics updated after final training and evaluation.*

---

## 💰 Budget

| Category | Cost |
|---|---|
| Metal Tank Chassis Kit | ₹900 |
| ESP32 + TFT Display | ₹800 |
| Servos + Motor Driver | ₹290 |
| Ultrasonic + IR Sensors | ₹225 |
| VL53L0X ToF Sensors (×2) | ₹300 |
| Battery + BMS + Charger | ₹565 |
| DFPlayer + Speaker | ₹160 |
| LED Strip | ₹250 |
| Wiring + Breadboard | ₹230 |
| Build Materials + Misc | ₹330 |
| **Total** | **~₹4,550** |

Recycled components (ThinkPad T61, Redmi Note 12, tablet) saved an estimated ₹15,000+ in equivalent hardware.

---

## 🖥️ Demo Setup

```
┌──────────────────────────────────────────────────┐
│   ░░░░░░ LED STRIPS (PURPLE BREATHING) ░░░░░░░  │
│                                                  │
│   ┌──────────┐   ┌────────────────┐             │
│   │  LAPTOP  │   │    TABLET      │             │
│   │ genesis  │   │   NEXUS DASH   │             │
│   │ terminal │   │                │             │
│   └──────────┘   │ Camera Feed    │             │
│                  │ Skeleton View  │             │
│                  │ Network Map    │             │
│   ┌──────────┐   │ Alert Log      │             │
│   │ J.I.N.X  │   └────────────────┘             │
│   │   🤖     │                                  │
│   │  Eyes    │                                  │
│   │  LEDs    │                                  │
│   └──────────┘                                  │
│                                                  │
│   ░░░░░░ LED STRIPS (PURPLE BREATHING) ░░░░░░░  │
│                                                  │
│              👥 AUDIENCE 👥                      │
└──────────────────────────────────────────────────┘
```

### Demo Script

```
1.  Room lights off. LED strips breathing purple.
2.  "Hey JINX, wake up."
    → Boot animation on TFT, eyes open, LEDs flash cyan.
3.  Step in front → face recognized → green box → "Oh, it's you again."
4.  Friend steps in → unknown → blue box → "New face detected. I'm watching you."
5.  "Hey JINX, show skeleton" → pose estimation + skeleton overlay on tablet.
6.  Dance in front → real-time skeleton follows your movements.
7.  "Hey JINX, guard mode" → scanning eyes, face colors update, network scan.
8.  Play glass breaking sound near mic → audio CNN triggers red alert.
9.  "Hey JINX, roast [friend]" → Gemini-generated personalized roast delivered.
10. "Hey JINX, what does a black hole look like?" → image shown on tablet.
11. "Hey JINX, play chill music" → music starts, LEDs go rainbow.
12. "Hey JINX, lights purple" → LEDs change color on voice command.
13. "Hey JINX, review my code" → pulls latest file from watched folder, reviews it.
14. "Hey JINX, goodnight" → sleepy eyes, LED dim → system standby.
```

---

## 🔮 Future Scope

```
├── SLAM-based room mapping and path planning
├── Raspberry Pi 4 integration for on-robot ML (remove laptop dependency)
├── Robotic arm for object manipulation
├── Emotion detection from facial expressions
├── Multi-language voice (Hindi + English)
├── Smart home ecosystem integration (Google Home, Alexa)
├── 3D-printed custom chassis upgrade
├── Mobile app (React Native) for remote control
├── Cloud dashboard for remote monitoring outside local network
├── Multi-robot swarm communication
└── Hexapod leg conversion (servo-based spider legs)
```

---

## 🛠️ Tech Stack

```
LANGUAGE          PURPOSE
Python 3.10+    │ Main server, ML models, web backend
C++ (Arduino)   │ ESP32 firmware
HTML/CSS/JS     │ Web control panel UI
SQL             │ Database queries

LIBRARY               PURPOSE
OpenCV              │ Image processing + display
MediaPipe           │ Face mesh, pose estimation, hands
face_recognition    │ Face detection + recognition
dlib                │ Face encoding (ResNet backbone)
Ultralytics         │ YOLOv5 object detection
TensorFlow/Keras    │ Audio CNN
librosa             │ Audio feature extraction (mel spectrogram)
scikit-learn        │ Network anomaly Random Forest
Vosk                │ Offline STT
edge-tts            │ Microsoft Neural TTS (human voice, free)
google-generativeai │ Gemini 2.0 Flash LLM
paho-mqtt           │ MQTT broker communication
Flask               │ Web control server
Streamlit           │ Cyberpunk dashboard
scapy               │ Network packet analysis
yt-dlp + mpv        │ Music streaming
PyPDF2 / pypdf      │ PDF text extraction
python-docx         │ Word document reading
SQLite3             │ Event and alert logging

ARDUINO LIBRARY       PURPOSE
TFT_eSPI            │ TFT display (ILI9341) — eye animations
Adafruit NeoPixel   │ WS2812B LED strip
PubSubClient        │ MQTT client
ArduinoJson         │ JSON parsing
ESP32Servo          │ Servo motor control
DFRobotDFPlayerMini │ MP3 sound effects via DFPlayer Mini
VL53L0X (Pololu)    │ Time-of-Flight depth sensors
```

---

## 👨‍💻 Author

**Sidvortex**
B.Tech Data Science (2023–2027)

GitHub: [github.com/Sidvortex](https://github.com/Sidvortex)

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

```
├── Google MediaPipe team (vision models)
├── Ultralytics (YOLOv5)
├── Adam Geitgey (face_recognition library)
├── Microsoft (edge-TTS Neural voices)
├── Google Gemini AI
├── Vosk / Alpha Cephei (offline STT)
├── DFRobot (DFPlayer Mini)
├── Espressif Systems (ESP32)
├── Pololu (VL53L0X library)
├── The dead ThinkPad T61 that gave its body for science
├── The open-source community
└── [Your Professor's Name] — Project Guide
```

---

<div align="center">

Built with ♥, sarcasm, and ₹4,550 worth of components.

*J.I.N.X doesn't just think. It judges.*

⚡ 🤖 ⚡

</div>
