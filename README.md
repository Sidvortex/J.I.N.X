```markdown
<div align="center">

# ⚡ J.I.N.X. ⚡
### **Judgmental Intelligence with Neural eXecution**

![Version](https://img.shields.io/badge/version-2.0.77-cyan?style=for-the-badge)
![Status](https://img.shields.io/badge/status-ACTIVE-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python)
![ESP32](https://img.shields.io/badge/ESP32-WROOM--32-red?style=for-the-badge)

<br>

*An autonomous AI-powered robotic assistant with real-time computer vision, 
voice interaction, environmental awareness, and adaptive personality — 
built from electronic waste.*

<br>

**B.Tech Final Year Project — Data Science (2023-2027)**

<br>

[Features](#-features) · 
[Architecture](#-system-architecture) · 
[Hardware](#-hardware) · 
[ML Models](#-ml-models) · 
[Installation](#-installation) · 
[Usage](#-usage) · 
[Demo](#-demo-day) · 
[License](#-license)

</div>

---

## 📌 About

**J.I.N.X.** is a multi-modal AI robotic assistant that sees, hears, 
speaks, moves, and judges — all built from recycled electronic 
components, a spare smartphone, a dead laptop, and low-cost 
microcontrollers within a budget of ₹4,000.

It combines **10 machine learning models** spanning computer vision, 
audio processing, natural language understanding, network security, 
and multi-modal sensor fusion into a single autonomous mobile platform 
with a cyberpunk aesthetic and a sarcastic personality.

> *"JINX was born from a dead ThinkPad T61. A laptop from 2007 that 
> couldn't even turn on anymore. Its metal chassis became JINX's body. 
> Its screws hold JINX together. A spare phone that couldn't make calls 
> became JINX's eyes, ears, and voice. Total hardware cost: ₹4,000. 
> This project proves that AI isn't about expensive hardware — it's 
> about intelligence."*

---

## 🎯 Problem Statement

Current AI and robotics projects in academic settings typically require 
expensive hardware such as GPUs, dedicated AI development boards, and 
premium sensors, making them inaccessible to students with limited 
budgets. Additionally, most existing systems focus on single-modal 
intelligence (vision-only or voice-only), lacking the multi-sensory 
integration needed for truly autonomous and interactive robotic behavior.

**JINX** addresses both challenges by developing a fully functional AI 
robotic assistant using recycled electronics, low-cost microcontrollers, 
and open-source ML frameworks — achieving multi-modal intelligence 
(vision + audio + language + IoT) at a total hardware cost under ₹4,000.

---

## 🎯 Objectives

1. To develop a multi-modal AI robotic system capable of real-time face 
   detection, recognition, and classification of known, unknown, and 
   flagged individuals using computer vision techniques.

2. To implement pose estimation and gesture recognition for intuitive 
   human-robot interaction and device control.

3. To build and train a Convolutional Neural Network (CNN) for real-time 
   environmental audio classification and anomaly detection.

4. To integrate Natural Language Processing (NLP) for voice-command-based 
   control, conversational AI interaction, and context-aware humor 
   generation using Large Language Models.

5. To design an IoT-based sensor fusion system combining visual, auditory, 
   and proximity sensor data for intelligent decision-making and 
   autonomous navigation.

6. To develop a cyberpunk-themed real-time monitoring dashboard for 
   centralized data visualization, alert logging, and system management.

7. To implement autonomous power management with battery monitoring and 
   self-docking behavior.

8. To demonstrate sustainable engineering practices by constructing the 
   system primarily from recycled and repurposed electronic components 
   within a constrained budget.

---

## ✨ Features

### 🤖 Core Capabilities

| Feature | Description |
|---|---|
| 👁️ **Face Detection & Recognition** | Detects faces in real-time, recognizes known individuals, flags unknown and threat-marked persons with color-coded bounding boxes (🟢 Known Safe, 🔵 Unknown, 🔴 Threat) |
| 🦴 **Pose Estimation** | 33-keypoint body skeleton tracking with neon glow overlay in real-time |
| 🖐️ **Gesture Control** | Hand gesture recognition (21 keypoints per hand) to control LED lights and robot behavior |
| 🎭 **468-Point Face Mesh** | Real-time facial landmark mesh for dramatic scanning visual effects |
| 🔊 **Audio Classification** | CNN-based environmental sound detection — glass breaking, screams, sirens, dog barking, gunshots, normal speech |
| 🗣️ **Voice Commands** | Wake-word activated voice control — "Hey JINX, [command]" |
| 💬 **Conversational AI** | Gemini Pro LLM-powered conversations with context-aware sarcastic personality |
| 🔥 **Roast Mode** | AI-generated personalized comedic roasts using face recognition + LLM |
| 🎵 **Music Playback** | Voice-activated music search and playback |
| 💡 **Light Control** | IoT-based LED strip control via voice commands and gestures |
| 🛡️ **Network Monitoring** | Real-time network device detection and traffic anomaly analysis |
| 🚨 **Surveillance Mode** | Autonomous patrol with face/object/sound threat detection and alert logging |

### 🎨 Physical Features

| Feature | Description |
|---|---|
| 👀 **Animated Eyes** | 2.4" TFT display showing 11 emotional eye states (happy, angry, sleepy, love, scanning, threat, roast, music, thinking, surprised, neutral) |
| 🔄 **Head Tracking** | Pan-tilt servo mechanism — JINX physically turns its head to follow detected faces |
| 👁️ **Pupil Tracking** | Digital eye pupils follow face position on screen synchronized with head movement |
| 🏗️ **Metal Tank Chassis** | All-metal tracked platform for stable indoor navigation |
| 🔋 **Battery Management** | 7.4V 18650 Li-ion pack with BMS, voltage monitoring, and low-battery dock-seeking behavior |
| 📦 **Storage Unit** | Physical compartment for storing HDDs and USB drives |
| 🔌 **Charging Dock** | Self-navigating dock return with "charge me please" personality behavior |
| 🌈 **Reactive LED System** | WS2812B addressable LED strip that changes color/pattern based on JINX's mood, alerts, and modes |
| 🔊 **Built-in Speaker** | DFPlayer Mini + 3W speaker for voice output and sound effects from JINX's body |
| ♻️ **Recycled Body** | Chassis decorated with ThinkPad keyboard keys, RAM sticks, HDD platters, vent grills with LED backlighting |

### 🧠 Operating Modes

```
MODE 1: BUDDY MODE (Default)
├── Friendly personality, responds to commands
├── Plays music, controls lights, answers questions
├── Eyes follow people, head tracks faces
├── Wanders slowly when idle
└── Returns to dock when battery low

MODE 2: SENTINEL MODE (Surveillance)
├── Active patrol and scanning
├── Color-coded face/object detection
│   ├── 🟢 GREEN = Known + Safe
│   ├── 🔵 BLUE = Unknown (not in database)
│   └── 🔴 RED = Known + Flagged as Threat
├── Audio anomaly detection (glass break, screams)
├── Network intrusion monitoring
├── All events logged with timestamps + screenshots
└── LED strips react to threat level

MODE 3: ROAST MODE
├── Scans person's face
├── Identifies them from database
├── Generates personalized comedic roast via Gemini LLM
├── Delivers roast through built-in speaker
├── Eyes show smug expression
└── LED strips flash party mode

MODE 4: DOCK MODE (Auto-Charging)
├── Battery level drops below 10%
├── Eyes become sleepy
├── JINX says "charge me please"
├── Follows line to charging dock
├── Waits for user to plug in cable
├── Eyes slowly brighten as charging progresses
└── Announces "I'M BACK!" when fully charged
```

---

## 🏗️ System Architecture

```
                    ┌──────────────────────────────┐
                    │     LAPTOP (Main Server)      │
                    │                              │
                    │  🧠 ML Models:               │
                    │  ├── YOLOv5-nano             │
                    │  ├── MediaPipe (Face/Pose/Hand)│
                    │  ├── Face Recognition (dlib)  │
                    │  ├── Audio CNN               │
                    │  ├── Network Anomaly Det.     │
                    │  ├── Vosk STT                │
                    │  ├── Gemini Pro LLM          │
                    │  └── Sensor Fusion Engine    │
                    │                              │
                    │  🌐 Server:                   │
                    │  ├── Flask / FastAPI          │
                    │  ├── MQTT Broker (Mosquitto)  │
                    │  ├── SQLite Database          │
                    │  └── WebSocket Server         │
                    └──────────┬───────────────────┘
                               │
                          WiFi ROUTER
                     (Private Network)
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
     ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
     │   J.I.N.X.  │   │   TABLET    │   │   PHONE     │
     │   ROBOT     │   │  DASHBOARD  │   │  (Remote    │
     │             │   │             │   │   Control)  │
     │ ┌─────────┐ │   │  Cyberpunk  │   └─────────────┘
     │ │ ESP32   │ │   │  Command    │
     │ │-Motors  │ │   │  Center     │
     │ │-Servos  │ │   │             │
     │ │-Display │ │   │ -Camera Feed│
     │ │-LEDs    │ │   │ -Face Scan  │
     │ │-Sensors │ │   │ -Pose View  │
     │ │-Speaker │ │   │ -Audio Viz  │
     │ └─────────┘ │   │ -Network    │
     │ ┌─────────┐ │   │ -Alerts     │
     │ │ REDMI   │ │   │ -Battery    │
     │ │ NOTE 12 │ │   └─────────────┘
     │ │-Camera  │ │
     │ │-Mic     │ │
     │ │-Speaker │ │
     │ │-Display │ │
     │ └─────────┘ │
     └─────────────┘
```

### Data Flow

```
VISION PIPELINE:
Phone Camera → WiFi Stream → Laptop Server → 
ML Processing (YOLO + MediaPipe + face_recognition) → 
Processed Frame → Tablet Dashboard + MQTT Commands → 
ESP32 (eyes + LEDs + head servos)

VOICE PIPELINE:
Bluetooth Mic → Laptop Server → Vosk STT → 
Intent Classification → Command Execution / 
Gemini API → TTS Response → Phone Speaker + 
DFPlayer Sound Effects

AUDIO PIPELINE:
Wired Mic → Laptop Server → MFCC/Mel Spectrogram → 
Audio CNN → Classification → Alert System → 
ESP32 (LEDs + buzzer + eyes)

SENSOR PIPELINE:
Ultrasonic + IR Sensors → ESP32 → MQTT → 
Laptop Server → Navigation Decisions → 
MQTT → ESP32 (motors)

NETWORK PIPELINE:
WiFi Router Traffic → Laptop (scapy) → 
Feature Extraction → Anomaly Detection Model → 
Dashboard + Alerts
```

### Communication Protocol

```
MQTT TOPICS:
├── jinx/eyes          Server → ESP32    Eye state commands
├── jinx/head_track    Server → ESP32    Face position for head servos
├── jinx/eye_track     Server → ESP32    Face position for pupil tracking
├── jinx/motor         Server → ESP32    Movement commands
├── jinx/led           Server → ESP32    LED pattern commands
├── jinx/sound         Server → ESP32    Sound effect triggers
├── jinx/buzzer        Server → ESP32    Buzzer commands
├── jinx/sensors       ESP32 → Server    Ultrasonic + IR data
├── jinx/battery       ESP32 → Server    Battery voltage + percentage
├── jinx/status        ESP32 → Server    System status
├── jinx/frame         Server → Tablet   Processed camera frames
├── jinx/audio         Server → Tablet   Audio classification results
├── jinx/alerts        Server → Tablet   Alert notifications
├── jinx/mode          Server → ESP32    Mode switching
└── jinx/command       Server → ESP32    General commands
```

---

## 🔧 Hardware

### Components Purchased

| # | Component | Specification | Qty | Purpose |
|---|---|---|---|---|
| 1 | All Metal Tank Chassis Kit | Aluminum, 2× DC geared motors, rubber treads, sprockets | 1 | Mobility platform |
| 2 | ESP32-WROOM-32 DevKit V1 | 30-pin, WiFi + BT, CP2102/CH340 USB | 1 | Robot microcontroller |
| 3 | 2.4" TFT LCD Display | ILI9341, SPI, 240×320, 65K color | 1 | Animated eye display |
| 4 | SG90 Micro Servo Motor | 180°, 1.8 kg-cm torque, 4.8-6V | 2 | Head pan + tilt |
| 5 | L298N Motor Driver Module | Dual H-Bridge, 5-35V input | 1 | DC motor control |
| 6 | HC-SR04 Ultrasonic Sensor | 2-400cm range, 5V | 2 | Obstacle avoidance |
| 7 | IR Obstacle Sensor Module | Digital output, adjustable | 2 | Line following / dock navigation |
| 8 | Active Buzzer Module | 5V, active type | 1 | Alert sounds |
| 9 | 18650 Li-ion Battery Cell | 3.7V, 2600mAh, flat-top | 4 | Power source (2S2P = 7.4V) |
| 10 | 2S BMS Protection Board | 7.4V, 10-20A | 1 | Battery safety |
| 11 | 18650 Battery Holder | 4-slot, 2S2P | 1 | Battery housing |
| 12 | TP4056 Charging Module | 5V Micro-USB, 1A, with protection | 2 | Battery charging |
| 13 | 10kΩ Resistor | 1/4W carbon film | 2 | Voltage divider (battery monitor) |
| 14 | Mini Rocker Switch | SPST ON/OFF | 1 | Main power switch |
| 15 | DFPlayer Mini | MP3, UART, Micro SD | 1 | Sound effects playback |
| 16 | Mini Speaker | 3W, 4Ω, 40mm | 1 | Audio output |
| 17 | WS2812B LED Strip | 30 LEDs, 5V, addressable | 1 | Reactive mood lighting |
| 18 | Jumper Wires M-M | 20cm, 40pc | 1 | Wiring |
| 19 | Jumper Wires M-F | 20cm, 40pc | 1 | Wiring |
| 20 | Solderless Breadboard | 840 tie points | 1 | Prototyping |

### Recycled / Pre-owned Components

| # | Component | Source | Purpose |
|---|---|---|---|
| 21 | Metal chassis parts, screws, hinges, fan, speaker, keyboard keys, RAM sticks, HDD platters | Lenovo ThinkPad T61 (non-functional) | Robot body structure + cyberpunk decoration |
| 22 | Camera, microphone, speaker, display, WiFi, sensors | Xiaomi Redmi Note 12 (spare) | Primary sensor array |
| 23 | WiFi Router | Pre-owned | Private local network |
| 24 | Tablet | UP Government issued | Dashboard display |
| 25 | Bluetooth Microphone | Pre-owned | Voice command input |
| 26 | Wired Microphone | Pre-owned | Audio classification input |
| 27 | LED Strips | Pre-owned | Room ambiance lighting |
| 28 | USB-C Chargers + Adapters | Pre-owned | Charging dock |
| 29 | Vibration motor, magnets, copper wire | Non-functional Oppo phone + earphones | Harvested components |
| 30 | Power Bank | Pre-owned | User phone charging (stored on robot) |
| 31 | Micro SD Card | Pre-owned | DFPlayer sound storage |

### GPIO Pin Mapping

```
ESP32 GPIO ALLOCATION:

TFT DISPLAY (ILI9341):          MOTORS (via L298N):
├── GPIO 18 → SCK                ├── GPIO 25 → IN1
├── GPIO 23 → MOSI               ├── GPIO 26 → IN2
├── GPIO 15 → CS                 ├── GPIO 27 → IN3
├── GPIO  2 → DC                 ├── GPIO 14 → IN4
├── GPIO  4 → RST                ├── GPIO 32 → ENA (PWM)
└── 3.3V   → VCC + LED           └── GPIO 33 → ENB (PWM)

SERVOS (Pan-Tilt Head):          SENSORS:
├── GPIO 19 → Pan Servo           ├── GPIO  5 → US1 TRIG
└── GPIO 21 → Tilt Servo          ├── GPIO 34 → US1 ECHO
                                  ├── GPIO  0 → US2 TRIG
LED STRIP (WS2812B):              ├── GPIO 35 → US2 ECHO
└── GPIO 13 → DATA                ├── GPIO 36 → IR Left
                                  └── GPIO 39 → IR Right
BUZZER:
└── GPIO 12 → Signal             BATTERY MONITOR:
                                  └── GPIO 39 → ADC (Voltage Divider)
DFPLAYER MINI:
├── GPIO 17 → TX (ESP→DF)        POWER:
└── GPIO 16 → RX (DF→ESP)        ├── VIN ← 5V (from L298N regulator)
                                  └── GND ← Common Ground
```

### Power System

```
18650 Battery Pack (2S2P):
7.4V, ~5000mAh
│
├── Rocker Switch (ON/OFF)
│
├── 2S BMS (overcharge/discharge protection)
│
├──► L298N Motor Driver (7.4V input)
│    ├── Motors (get ~6V after driver drop)
│    └── 5V Regulator Output
│         ├── ESP32 (via VIN)
│         ├── Servos
│         ├── LED Strip
│         ├── DFPlayer
│         ├── Sensors
│         └── Buzzer
│
├──► Voltage Divider (10kΩ + 10kΩ)
│    └── ESP32 ADC (battery monitoring)
│
└──► TP4056 Modules (for charging)
     └── Micro-USB input from wall charger

Estimated Runtime: 3-4 hours (typical use)
Charging Time: ~2-3 hours
```

---

## 🧠 ML Models

| # | Model | Task | Type | Dataset | Key Metric |
|---|---|---|---|---|---|
| 1 | YOLOv5-nano | Object Detection | Pre-trained + fine-tuned | COCO | mAP |
| 2 | MediaPipe Face Mesh | 468-point Face Landmarks | Pre-trained | Google | Detection Accuracy |
| 3 | MediaPipe Pose | 33-point Body Pose Estimation | Pre-trained | Google | Keypoint Confidence |
| 4 | MediaPipe Hands + Custom Classifier | Hand Gesture Recognition | Pre-trained + Custom | Google + Custom | Gesture Accuracy |
| 5 | dlib ResNet / FaceNet | Face Recognition (128-d embeddings) | Pre-trained + Custom DB | LFW + Custom | FAR / FRR |
| 6 | Custom CNN (2D Conv) | Audio Event Classification | Trained from scratch | UrbanSound8K / ESC-50 | F1-Score, Accuracy |
| 7 | Vosk / Google Speech API | Speech-to-Text | Pre-trained | — | WER |
| 8 | Gemini Pro (LLM) | NLU + Conversation + Humor | Pre-trained API | Google | Response Relevance |
| 9 | Random Forest / XGBoost / Autoencoder | Network Anomaly Detection | Trained | NSL-KDD / CICIDS2017 | ROC-AUC, Precision |
| 10 | Weighted Ensemble | Multi-modal Sensor Fusion | Custom Designed | — | Detection Accuracy, FAR |

### Model Details

#### 1. Object Detection (YOLOv5-nano)
```
Architecture: YOLOv5-nano (1.9M parameters)
Input: 640×640 RGB frame
Output: Bounding boxes + class labels + confidence
Classes: 80 COCO classes (person, car, dog, etc.)
Speed: ~30ms per frame on CPU
Use: Detecting people, vehicles, animals in surveillance mode
```

#### 2-4. MediaPipe Suite
```
Face Mesh: 468 3D facial landmarks, real-time
Pose: 33 body keypoints, full skeleton
Hands: 21 keypoints per hand, up to 2 hands
All run on CPU, no GPU required
Use: Visual effects, gesture control, scanning animations
```

#### 5. Face Recognition
```
Method: 128-dimensional face embedding comparison
Encoding: dlib's ResNet face encoder
Matching: Cosine similarity / Euclidean distance
Threshold: 0.5 (adjustable)
Database: Local SQLite with known face encodings
Classification: Safe (green) / Unknown (blue) / Threat (red)
```

#### 6. Audio Classification CNN
```
Architecture:
├── Input: 128×128 Mel Spectrogram (1 channel)
├── Conv2D(32, 3×3) → ReLU → MaxPool(2×2)
├── Conv2D(64, 3×3) → ReLU → MaxPool(2×2)
├── Conv2D(64, 3×3) → ReLU → MaxPool(2×2)
├── Flatten
├── Dense(128) → ReLU → Dropout(0.3)
└── Dense(10) → Softmax

Features: Mel Spectrogram + MFCC
Classes: air_conditioner, car_horn, children_playing,
         dog_bark, drilling, engine_idling, gun_shot,
         jackhammer, siren, street_music
Dataset: UrbanSound8K (8,732 samples)
Training: 80/20 split, 50 epochs, Adam optimizer
```

#### 9. Network Anomaly Detection
```
Models tested: Random Forest, XGBoost, Autoencoder
Best: XGBoost (highest ROC-AUC)
Features: Packet size, protocol, flags, duration, 
          byte count, port numbers
Dataset: NSL-KDD (125,973 training samples)
Classes: Normal vs Anomalous traffic
```

#### 10. Sensor Fusion
```
Inputs:
├── Visual threat score (0-1) from face recognition
├── Audio threat score (0-1) from sound classification
├── Network threat score (0-1) from anomaly detection
├── Proximity alert (0/1) from ultrasonic sensors

Fusion Method: Weighted average with learned weights
Output: Combined threat score (0-1)
Threshold: > 0.7 = ALERT
```

---

## 🛠️ Tech Stack

### Software

```
LANGUAGE          │ PURPOSE
──────────────────┼─────────────────────────
Python 3.10+      │ Main server, ML models
C++ (Arduino)     │ ESP32 firmware
HTML/CSS/JS       │ Dashboard styling
SQL               │ Database queries

FRAMEWORK/LIBRARY │ PURPOSE
──────────────────┼─────────────────────────
Flask / FastAPI    │ Backend API server
OpenCV             │ Image processing
MediaPipe          │ Face mesh, pose, hands
face_recognition   │ Face detection + recognition
dlib               │ Face encoding (ResNet)
Ultralytics        │ YOLOv5 object detection
TensorFlow/Keras   │ Audio classification CNN
librosa            │ Audio feature extraction
scikit-learn       │ Network anomaly models
Vosk               │ Offline speech recognition
pyttsx3            │ Text-to-speech engine
Google Generative AI│ Gemini Pro LLM API
paho-mqtt          │ MQTT communication
Streamlit          │ Cyberpunk dashboard
Plotly             │ Data visualization
pandas             │ Data processing
SQLite3            │ Event/alert database
scapy              │ Network packet analysis
yt-dlp             │ Music search/download
pygame             │ Audio playback

ARDUINO LIBRARIES  │ PURPOSE
──────────────────┼─────────────────────────
TFT_eSPI           │ TFT display (eye animations)
Adafruit NeoPixel  │ WS2812B LED strip control
PubSubClient       │ MQTT client
ArduinoJson        │ JSON parsing
ESP32Servo         │ Servo motor control
DFRobotDFPlayerMini│ MP3 sound effects
NewPing            │ Ultrasonic sensor reading
```

### Hardware Architecture

```
SERVER LAYER:     Personal Laptop (Python + ML)
NETWORK LAYER:    WiFi Router (MQTT + HTTP)
CONTROLLER LAYER: ESP32-WROOM-32 (Motor + Sensor + Display)
SENSOR LAYER:     Redmi Note 12 (Camera + Mic)
DISPLAY LAYER:    UP Govt Tablet (Dashboard) + TFT (Eyes)
ACTUATOR LAYER:   Motors + Servos + LEDs + Speaker + Buzzer
POWER LAYER:      18650 2S2P Pack (7.4V) + BMS + TP4056
```

---

## 📁 Project Structure

```
JINX/
├── server/
│   ├── main.py                  # Main entry point — starts all systems
│   ├── vision.py                # Computer vision pipeline
│   ├── voice.py                 # Voice commands + TTS + Gemini
│   ├── audio_classifier.py      # Audio event classification
│   ├── network_monitor.py       # Network anomaly detection
│   ├── mqtt_handler.py          # MQTT communication manager
│   ├── database.py              # SQLite event/alert logging
│   ├── sensor_fusion.py         # Multi-modal threat scoring
│   └── personality.py           # Personality lines + responses
│
├── dashboard/
│   ├── app.py                   # Streamlit cyberpunk dashboard
│   ├── styles.css               # Neon/cyberpunk CSS theme
│   └── assets/
│       ├── fonts/               # Orbitron, Share Tech Mono
│       └── icons/               # Dashboard icons
│
├── arduino/
│   └── jinx_esp32/
│       ├── jinx_esp32.ino       # Main ESP32 firmware
│       ├── eyes.h               # Eye animation functions
│       ├── motors.h             # Motor control functions
│       ├── leds.h               # LED pattern functions
│       ├── sensors.h            # Sensor reading functions
│       ├── servos.h             # Head pan-tilt functions
│       └── config.h             # Pin definitions + WiFi config
│
├── models/
│   ├── audio_classifier.h5      # Trained audio CNN model
│   ├── network_anomaly.pkl      # Trained network model
│   ├── vosk-model/              # Offline speech recognition model
│   └── yolov5n.pt               # YOLOv5-nano weights
│
├── data/
│   ├── known_faces/             # Registered face images
│   │   ├── admin.jpg
│   │   └── ...
│   ├── alerts/                  # Alert screenshots
│   ├── urbansound8k/            # Audio training dataset
│   ├── nsl-kdd/                 # Network training dataset
│   └── jinx_database.db         # SQLite database
│
├── training/
│   ├── train_audio_cnn.py       # Audio model training script
│   ├── train_network_model.py   # Network model training script
│   └── evaluate_models.py       # Model evaluation + metrics
│
├── assets/
│   ├── personality.json         # Personality lines database
│   └── sounds/                  # MP3 sound effects for DFPlayer
│       ├── 001_boot.mp3
│       ├── 002_alert.mp3
│       ├── 003_happy.mp3
│       ├── 004_threat.mp3
│       ├── 005_sleepy.mp3
│       └── 006_ambient.mp3
│
├── docs/
│   ├── report.pdf               # Final project report
│   ├── presentation.pptx        # Demo presentation
│   ├── wiring_diagram.png       # Hardware wiring diagram
│   ├── architecture_diagram.png # System architecture
│   └── demo_video.mp4           # Recorded demo backup
│
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore rules
```

---

## ⚡ Installation

### Prerequisites

```
- Personal Laptop (Windows/Linux/Mac)
- Python 3.10 or higher
- Arduino IDE 2.x
- Git
- Assembled JINX robot hardware
- WiFi Router configured
- Redmi Note 12 with IP Webcam app
- UP Govt Tablet with browser
```

### Step 1: Clone Repository

```bash
git clone https://github.com/sidvortex/JINX.git
cd JINX
```

### Step 2: Python Environment Setup

```bash
# Create virtual environment
python -m venv jinx_env

# Activate
# Windows:
jinx_env\Scripts\activate
# Linux/Mac:
source jinx_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Download ML Models

```bash
# YOLOv5 (auto-downloads on first run)
python -c "from ultralytics import YOLO; YOLO('yolov5n.pt')"

# Vosk speech model
# Download from: https://alphacephei.com/vosk/models
# Extract to: models/vosk-model/

# Audio model (train or use pre-trained)
python training/train_audio_cnn.py
```

### Step 4: Configure API Keys

```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Get free API key from:
# https://aistudio.google.com/
```

### Step 5: Configure Network

```bash
# Edit server/config.py
LAPTOP_IP = "192.168.1.10"
PHONE_IP = "192.168.1.11"
TABLET_IP = "192.168.1.12"
ESP32_IP = "192.168.1.20"
MQTT_PORT = 1883
CAMERA_URL = "http://192.168.1.11:8080/video"
```

### Step 6: Flash ESP32

```
1. Open Arduino IDE
2. Open arduino/jinx_esp32/jinx_esp32.ino
3. Install required libraries (TFT_eSPI, NeoPixel, 
   PubSubClient, ArduinoJson, ESP32Servo, DFPlayer)
4. Configure TFT_eSPI User_Setup.h for ILI9341
5. Select Board: ESP32 Dev Module
6. Select Port: COMx / /dev/ttyUSBx
7. Upload
```

### Step 7: Setup Phone

```
1. Install "IP Webcam" from Play Store
2. Connect to WiFi router (static IP: 192.168.1.11)
3. Open IP Webcam → Start Server
4. Verify: http://192.168.1.11:8080/video in browser
```

### Step 8: Register Faces

```bash
# Add face images to data/known_faces/
# Filename = person's name
# Example: data/known_faces/admin.jpg
#          data/known_faces/amit_friend.jpg
#          data/known_faces/threat_person.jpg

# Update labels in server/config.py
FACE_LABELS = {
    "admin": "safe",
    "amit_friend": "safe",
    "threat_person": "threat"
}
```

---

## 🚀 Usage

### Starting JINX

```bash
# Terminal 1: Start MQTT Broker
mosquitto -v

# Terminal 2: Start JINX Core Server
cd JINX
source jinx_env/bin/activate
python server/main.py

# Terminal 3: Start Dashboard
streamlit run dashboard/app.py --server.port 8501

# On Tablet: Open browser → http://192.168.1.10:8501
# On Phone: Start IP Webcam
# On Robot: Power ON (rocker switch)
```

### Boot Sequence

```
╔═══════════════════════════════════════════╗
║     ██╗██╗███╗   ██╗██╗  ██╗             ║
║     ██║██║████╗  ██║╚██╗██╔╝             ║
║     ██║██║██╔██╗ ██║ ╚███╔╝              ║
║██   ██║██║██║╚██╗██║ ██╔██╗              ║
║╚█████╔╝██║██║ ╚████║██╔╝ ██╗            ║
║ ╚════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝            ║
║                                           ║
║  JUDGMENTAL INTELLIGENCE WITH              ║
║  NEURAL EXECUTION v2.0.77                 ║
╚═══════════════════════════════════════════╝

[INIT] Loading MQTT Broker........... ✓
[INIT] Loading Neural Engine......... ✓
[INIT] Loading Optic Pipeline........ ✓
[INIT] Loading Echo Scanner.......... ✓
[INIT] Loading Voice Core............ ✓
[INIT] Loading Personality Matrix.... ✓
[INIT] Loading Motor Controller...... ✓
[INIT] Loading Dashboard Server...... ✓

⚡ JINX NEURAL CORE ONLINE ⚡
```

### Voice Commands

```
"Hey JINX, wake up"              → System activation
"Hey JINX, guard mode"           → Sentinel surveillance mode
"Hey JINX, roast [name]"         → AI-generated roast
"Hey JINX, play music"           → Music playback
"Hey JINX, lights [color]"       → LED control (red/blue/green/purple/party)
"Hey JINX, come here"            → Move forward
"Hey JINX, go back"              → Move backward
"Hey JINX, search [topic]"       → Web search + summarize
"Hey JINX, what's the weather?"  → Weather information
"Hey JINX, goodnight"            → Sleep mode
```

---

## 🎬 Demo Day

### Room Setup

```
┌──────────────────────────────────────────────┐
│  ░░░░░░ LED STRIPS (PURPLE BREATHING) ░░░░░ │
│                                              │
│   ┌─────────┐  ┌──────────────┐              │
│   │ LAPTOP  │  │   TABLET     │              │
│   │ Terminal │  │  DASHBOARD   │              │
│   │ (Matrix) │  │  (Cyberpunk) │              │
│   └─────────┘  └──────────────┘              │
│                                              │
│          ┌──────────┐                        │
│          │ J.I.N.X. │  ← The Star            │
│          │   🤖     │                        │
│          └──────────┘                        │
│                           ┌────────┐         │
│                           │CHARGING│         │
│                           │ DOCK   │         │
│                           └────────┘         │
│                                              │
│  ░░░░░░ LED STRIPS (PURPLE BREATHING) ░░░░░ │
│                                              │
│       👥 AUDIENCE 👥                         │
│                                              │
└──────────────────────────────────────────────┘
```

### Demo Script

```
1. Room is dark. LED strips breathing purple.
2. "Hey JINX, wake up."
   → Boot animation, eyes open, LEDs flash cyan
3. Step in front → face recognized → green box → "Hey boss!"
4. Friend steps in → unknown → blue box → scanned and logged
5. "Hey JINX, roast [friend]" → AI roast delivered
6. "Hey JINX, guard mode" → scanning eyes, surveillance active
7. Play glass breaking sound → threat detected → red alert
8. "Hey JINX, play music" → music + LED light show
9. "Hey JINX, lights purple" → room changes color
10. "Hey JINX, goodnight" → sleepy eyes → system standby
```

---

## 🔋 Power Specifications

```
Battery: 4× 18650 Li-ion (2S2P)
Voltage: 7.4V nominal (8.4V full, 6.0V cutoff)
Capacity: ~5000mAh
Runtime: 3-4 hours (typical)
Charging: TP4056 via Micro-USB (5V 1A)
Charge Time: 2-3 hours
Protection: 2S BMS (overcharge, over-discharge, short circuit)
Monitoring: ESP32 ADC via voltage divider
```

---

## 💰 Budget

| Category | Cost (₹) |
|---|---|
| Metal Tank Chassis Kit | 900 |
| ESP32 + Display | 800 |
| Servos + Motor Driver | 290 |
| Sensors + Buzzer | 225 |
| Battery + BMS + Charger + Switch | 565 |
| DFPlayer + Speaker | 160 |
| LED Strip | 250 |
| Wiring + Breadboard | 230 |
| Build Materials | 330 |
| **Total** | **~₹3,750** |

> Recycled components from ThinkPad T61, spare phone, existing 
> peripherals saved an estimated ₹15,000+ in equivalent hardware costs.

---

## 📊 Results & Metrics

| Model | Metric | Score |
|---|---|---|
| YOLOv5-nano | mAP@0.5 | 28.0% (COCO) |
| Face Recognition | Accuracy | ~95%+ |
| Face Recognition | False Acceptance Rate | <2% |
| Pose Estimation | Keypoint Confidence | ~90%+ |
| Audio CNN | F1-Score | ~85%+ |
| Audio CNN | Accuracy | ~88%+ |
| Network Anomaly | ROC-AUC | ~92%+ |
| Voice Recognition | Word Error Rate | ~10-15% |
| Sensor Fusion | Overall Detection Accuracy | ~90%+ |

> *Metrics to be updated after final training and evaluation.*

---

## 🔮 Future Scope

```
├── Spider leg mechanism (servo-based hexapod conversion)
├── SLAM-based room mapping and path planning
├── Raspberry Pi 4 integration for on-robot ML processing
├── Robotic arm attachment for object manipulation
├── Multi-robot swarm communication
├── Cloud dashboard for remote monitoring
├── Mobile app for remote control
├── Emotion detection from facial expressions
├── Multi-language voice support (Hindi + English)
├── Integration with smart home ecosystems (Google Home, Alexa)
└── 3D-printed custom chassis upgrade
```

---

## 👨‍💻 Author

```
[Your Name]
B.Tech Data Science (2023-2027)
[Your College Name]
[Your University]

Email: [your.email@example.com]
GitHub: github.com/yourusername
LinkedIn: linkedin.com/in/yourprofile
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

```
├── Google MediaPipe team (vision models)
├── Ultralytics (YOLOv5)
├── dlib / face_recognition library
├── Google Gemini AI
├── DFRobot (DFPlayer Mini)
├── Espressif Systems (ESP32)
├── The dead ThinkPad T61 that gave its body for science
├── Open-source community
└── [Your Professor's Name] (Project Guide)
```

---

<div align="center">

**Built with ♥, sarcasm, and ₹3,750 worth of components.**

**JINX doesn't just think. It judges.**

⚡🤖⚡

</div>
