<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=13&pause=1000&color=5E81AC&center=true&vCenter=true&width=600&lines=Judgmental+Intelligence+with+Neural+eXecution;Born+from+a+dead+ThinkPad+%26+%E2%82%B94%2C550+of+recycled+dreams.;It+doesn't+just+think.+It+judges." alt="Typing SVG" />
</p>

<h1 align="center">
  <img src="https://img.shields.io/badge/J.I.N.X-NEURAL%20CORE%20ONLINE-5e81ac?style=for-the-badge&logo=probot&logoColor=white" alt="JINX">
</h1>

<h3 align="center"><i>Innocence fades in circuits — judgment is all that remains.</i></h3>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.0-5e81ac?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/status-ACTIVE-88c0d0?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/budget-%E2%82%B98%2C000-ebcb8b?style=for-the-badge" alt="Budget">
  <img src="https://img.shields.io/badge/license-MIT-bf616a?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/ESP32-WROOM--32-red?style=for-the-badge" alt="ESP32">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Sidvortex/J.I.N.X?style=for-the-badge&label=Stars&color=bf616a&logo=github" alt="Stars">
  <img src="https://img.shields.io/github/forks/Sidvortex/J.I.N.X?style=for-the-badge&label=Forks&color=5e81ac&logo=github" alt="Forks">
  <img src="https://img.shields.io/github/last-commit/Sidvortex/J.I.N.X?style=for-the-badge&color=a3be8c&logo=github" alt="Last Commit">
</p>

---

<p align="center">
  An autonomous AI desk robot with real-time computer vision, human-like voice, face recognition,<br>
  skeleton tracking, document Q&A, live code review, home automation —<br>
  and a <strong>sarcastic personality</strong>. Built from electronic waste for ₹8,000.
</p>

<p align="center">
  <strong>B.Tech Final Year Project — Data Science (2023–2027)</strong>
</p>

<p align="center">
  <a href="#-about">About</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-system-architecture">Architecture</a> ·
  <a href="#-hardware">Hardware</a> ·
  <a href="#-ml-models">ML Models</a> ·
  <a href="#-installation">Installation</a> ·
  <a href="#-usage">Usage</a> ·
  <a href="#-codex">Codex</a> ·
  <a href="#-demo-setup">Demo</a>
</p>

---

## 📌 About

**J.I.N.X** is a multi-modal AI robotic desk companion that sees, hears, speaks, judges, and even reviews your code — all built from recycled electronics, a spare smartphone, a dead ThinkPad, and low-cost microcontrollers.

It combines **10 machine learning models** spanning computer vision, audio classification, natural language understanding, network security, and sensor fusion into a single desk-mounted platform with a cyberpunk aesthetic and an attitude problem.

> *"Born from a dead ThinkPad T61 that couldn't even turn on anymore. Its metal chassis became J.I.N.X's body. A spare phone that couldn't make calls became its eyes, ears, and voice. Total hardware cost: ₹8,000. This project proves that AI isn't about expensive hardware — it's about intelligence."*

---

## ✨ Features

### 🧠 AI & Intelligence

```
    ✧ Real-time face detection + recognition (green = safe / blue = unknown / red = threat)
    ✧ 33-keypoint full body skeleton + pose estimation overlay
    ✧ 21-keypoint hand gesture recognition — control everything without touching anything
    ✧ 468-point face mesh with dramatic scanning visual effect
    ✧ CNN-trained audio classification (gunshots, sirens, glass breaks, screams)
    ✧ Offline wake word + full voice command system
    ✧ Gemini 2.0 Flash conversations with context memory and sarcastic personality
    ✧ Microsoft Neural TTS — sounds like a real human, not a robot. Free. No API key.
    ✧ Document Q&A — ask questions about uploaded PDFs by voice or web panel
    ✧ Code review agent — auto-reviews changed files on save, flags bugs and style issues
    ✧ Roast mode — scans your face, generates a personalized AI roast, delivers it live
    ✧ Voice-activated music search and streaming via yt-dlp + mpv
    ✧ IoT home automation — LED strip + smart device control by voice and gesture
    ✧ WiFi network monitor — flags unknown devices, detects traffic anomalies
```

### 🤖 Physical & Mechanical

```
    ✧ Animated eyes on 2.4" TFT with 12 emotional states (neutral / angry / scanning / roast / boot...)
    ✧ Pan-tilt servo head — physically turns to follow detected faces
    ✧ Digital pupils that track face position, synced with servo movement
    ✧ VL53L0X ToF sensor (downward) — detects desk edges with millimeter accuracy
    ✧ Dual HC-SR04 ultrasonic + forward VL53L0X obstacle avoidance
    ✧ 7.4V 18650 2S2P battery pack with BMS protection and voltage monitoring
    ✧ At <15% battery: eyes go sleepy, LEDs pulse yellow, J.I.N.X says "I'm running on spite"
    ✧ WS2812B LED strip with 11 animated modes — reacts to mood, threats, music, battery
    ✧ DFPlayer Mini + 3W speaker for sound effects. Neural TTS plays through phone speaker
    ✧ Body made from ThinkPad T61 chassis, keyboard keys, RAM sticks, HDD platters
```

### 🌐 Control & Interface

```
    ✧ Web control panel at http://LAPTOP_IP:5000 — live feed, modes, LEDs, movement, uploads
    ✧ Streamlit cyberpunk dashboard at port 8501 — camera, skeleton, network map, alerts
    ✧ Any device on the same WiFi can control J.I.N.X from a browser — no app needed
```

---

## 🔀 Operating Modes

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
                │  ├── Flask Web Control (:5000)    │
                │  ├── Streamlit Dashboard (:8501)  │
                │  ├── MQTT Broker (Mosquitto)      │
                │  └── SQLite Database              │
                └───────────────┬──────────────────┘
                                │ WiFi (Private Local Network)
          ┌─────────────────────┼──────────────────────┐
          │                     │                      │
   ┌──────▼──────┐      ┌──────▼──────┐       ┌──────▼──────┐
   │  J.I.N.X    │      │   TABLET    │        │   PHONE     │
   │  ROBOT      │      │  NEXUS DASH │        │  (Control)  │
   │             │      │             │        │             │
   │ ┌─────────┐ │      │ ─ Camera    │        │ :5000       │
   │ │  ESP32  │ │      │ ─ Skeleton  │        └─────────────┘
   │ │─Motors  │ │      │ ─ Network   │
   │ │─Servos  │ │      │ ─ Alerts    │
   │ │─TFT Eyes│ │      │ ─ Audio     │
   │ │─LEDs    │ │      └─────────────┘
   │ │─Sensors │ │
   │ │─Speaker │ │
   │ └─────────┘ │
   │ ┌─────────┐ │
   │ │Redmi 12 │ │  ← Neural TTS voice plays here
   │ │─Camera  │ │
   │ │─Mic/Spk │ │
   │ └─────────┘ │
   └─────────────┘
```

---

## 🔧 Hardware

### Purchased Components (~₹8,000 total)

| # | Component | Spec | Purpose |
|---|-----------|------|---------|
| 1 | ESP32-WROOM-32 DevKit | WiFi+BT, 30-pin | Robot brain |
| 2 | 2.4" TFT ILI9341 | 240×320, SPI | Animated eyes |
| 3 | SG90 Servo ×2 | 180°, 1.8kg-cm | Head pan + tilt |
| 4 | L298N Motor Driver | Dual H-Bridge | DC motor control |
| 5 | HC-SR04 Ultrasonic ×2 | 2–400cm | Obstacle detection |
| 6 | VL53L0X ToF Sensor ×2 | 2m, ±1mm, I2C | Table edge + precise depth |
| 7 | WS2812B LED Strip | 30 LEDs, 5V | Mood reactive lighting |
| 8 | DFPlayer Mini + 3W Speaker | UART, MP3 | Sound effects |
| 9 | 18650 Battery ×4 | 3.7V 2600mAh | 2S2P = 7.4V ~5000mAh |
| 10 | 2S BMS Board | 7.4V 10A | Battery protection |
| 11 | Servo Pan/Tilt Platform | Vertical & Horizontal Axis Movement | Clean Build |

### Recycled / Pre-owned

| Component | Source | Purpose |
|-----------|--------|---------|
| Metal parts, keyboard keys, RAM, HDD platters | Lenovo ThinkPad T61 | Body structure + decoration |
| Camera, mic, speaker, WiFi | Xiaomi Redmi Note 12 | Primary sensor array + TTS speaker |
| Tablet | UP Govt issued | Dashboard display |

> Recycled components saved an estimated **₹15,000+** in equivalent hardware costs.

---

## 🧠 ML Models

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,tensorflow,pytorch,opencv" alt="ML Stack" />
</p>

| # | Model | Task | Type | Dataset |
|---|-------|------|------|---------|
| 1 | YOLOv5-nano | Object Detection | Pre-trained | COCO (80 classes) |
| 2 | MediaPipe Face Mesh | 468-point Landmarks | Pre-trained | Google |
| 3 | MediaPipe Pose | 33-point Skeleton | Pre-trained | Google |
| 4 | MediaPipe Hands + Classifier | Gesture Recognition | Pre-trained + Custom | Google + Custom |
| 5 | dlib ResNet / face_recognition | Face Recognition (128-d) | Pre-trained + Custom | LFW + Your faces |
| 6 | Custom CNN (2D Conv) | Audio Classification | Trained from scratch | UrbanSound8K |
| 7 | Vosk / Google STT | Speech-to-Text | Pre-trained | — |
| 8 | Gemini 2.0 Flash | NLU + Conversation + Agent | API | Google |
| 9 | Random Forest | Network Anomaly Detection | Trained | NSL-KDD |
| 10 | Weighted Ensemble | Sensor Fusion | Custom | — |

### Audio CNN Architecture

```
Input: 128×128 Mel Spectrogram
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

| File | Codename | Purpose |
|------|----------|---------|
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

## ⚡ Installation

### Prerequisites

```
Personal laptop (Linux recommended, Windows/Mac also work)
Python 3.10+ · Arduino IDE 2.x · Assembled J.I.N.X hardware
WiFi router · Redmi Note 12 with DroidCam · Mosquitto MQTT
cmake (for face_recognition/dlib) · mpv (for music playback)
```

### Step 1 — Clone

```bash
git clone https://github.com/Sidvortex/J.I.N.X.git
cd J.I.N.X
```

### Step 2 — Install Dependencies

```bash
# Arch / EndeavourOS
sudo pacman -S mosquitto cmake espeak-ng mpv yt-dlp portaudio python-pip

# Ubuntu / Debian
sudo apt install mosquitto cmake libcmake-data espeak-ng mpv yt-dlp \
                 portaudio19-dev python3-pip

pip install -r requirements.txt
sudo systemctl enable --now mosquitto
```

### Step 3 — Configure

```bash
nano server/dna.py

# Set:
LAPTOP_IP       = "your.laptop.ip"
PHONE_IP        = "redmi.note.ip"
GEMINI_API_KEY  = "get from aistudio.google.com"
FACE_LABELS     = {"yourname": "safe"}
```

### Step 4 — Download ML Models

```bash
# Vosk offline STT (~40MB)
mkdir -p models/vosk-model
# Download: https://alphacephei.com/vosk/models → vosk-model-small-en-us-0.15
# Extract into models/vosk-model/

# YOLOv5 (auto-downloads on first run)
python -c "from ultralytics import YOLO; YOLO('yolov5n.pt')"
```

### Step 5 — Register Your Face

```bash
python scripts/register_face.py --name yourname --file photo.jpg --label safe
# or live:
python scripts/register_face.py --name yourname --live --label safe
```

### Step 6 — Flash ESP32

```
1. Open Arduino IDE 2.x → arduino/jinx_esp32/jinx_esp32.ino
2. Install via Library Manager:
   TFT_eSPI · Adafruit NeoPixel · PubSubClient
   ArduinoJson · ESP32Servo · DFRobotDFPlayerMini · VL53L0X
3. Edit config.h → set WIFI_SSID, WIFI_PASS, MQTT_BROKER
4. Board: ESP32 Dev Module → Upload
```

### Step 7 — Setup Phone

```
1. Install DroidCam on Redmi Note 12
2. Connect to same WiFi → set static IP in router
3. Update PHONE_IP in server/dna.py
4. Open DroidCam → Start Server
5. Test: http://PHONE_IP:4747/video
```

---

## 🚀 Usage

### Start J.I.N.X

```bash
python server/genesis.py              # Normal startup
python server/genesis.py --sentinel   # Start in Sentinel mode
python server/genesis.py --agent-mode # Document/code focus
python server/genesis.py --no-audio --no-network  # Faster startup
```

### Voice Commands

```
    ✧ "Hey JINX, wake up"              → System activation
    ✧ "Hey JINX, guard mode"           → Sentinel surveillance
    ✧ "Hey JINX, roast [name]"         → AI-generated personalized roast
    ✧ "Hey JINX, what is [topic]"      → Gemini answers + shows image
    ✧ "Hey JINX, play [song/genre]"    → Music search and playback
    ✧ "Hey JINX, lights [color]"       → LED color change
    ✧ "Hey JINX, review my code"       → Code review of watched folder
    ✧ "Hey JINX, read [document name]" → Summarizes uploaded document
    ✧ "Hey JINX, status"               → System health report
    ✧ "Hey JINX, goodnight"            → Sleep mode
```

---

## 📊 Results & Metrics

| Model | Metric | Score |
|-------|--------|-------|
| Face Recognition | Accuracy | ~95%+ |
| Face Recognition | False Acceptance Rate | <2% |
| Audio CNN | F1-Score | ~85%+ |
| Audio CNN | Accuracy | ~88%+ |
| Network Anomaly | ROC-AUC | ~92%+ |
| Voice Recognition | Word Error Rate | ~10–15% |
| Sensor Fusion | Detection Accuracy | ~90%+ |
| Table Edge Detection | Accuracy | ~99% (VL53L0X) |

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,cpp,js,html,css" alt="Languages" />
  <br>
  <img src="https://skillicons.dev/icons?i=tensorflow,pytorch,opencv,flask,sqlite" alt="ML & Backend" />
  <br>
  <img src="https://skillicons.dev/icons?i=arduino,linux,bash,git,github" alt="Hardware & Dev Tools" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenCV-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe">
  <img src="https://img.shields.io/badge/Gemini%202.0-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Flask-%23000000.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=eclipse-mosquitto&logoColor=white" alt="MQTT">
  <img src="https://img.shields.io/badge/SQLite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

---

## 🔮 Future Scope

```
    ✧ SLAM-based room mapping and path planning
    ✧ Raspberry Pi 4 integration — remove laptop dependency
    ✧ Robotic arm for object manipulation
    ✧ Emotion detection from facial expressions
    ✧ Multi-language voice (Hindi + English)
    ✧ Smart home ecosystem integration (Google Home, Alexa)
    ✧ Mobile app (React Native) for remote control
    ✧ Cloud dashboard for remote monitoring outside local network
    ✧ Multi-robot swarm communication
    ✧ Hexapod leg conversion (servo-based spider legs)
```

---

## 🙏 Acknowledgments

```
    ✧ Google MediaPipe team (vision models)
    ✧ Ultralytics (YOLOv5)
    ✧ Adam Geitgey (face_recognition library)
    ✧ Microsoft (edge-TTS Neural voices)
    ✧ Google Gemini AI
    ✧ Vosk / Alpha Cephei (offline STT)
    ✧ The dead ThinkPad T61 that gave its body for science
    ✧ The open-source community
```

---

## 🎬 Demo

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- PHOTO GALLERY — replace the src URLs with your actual images  -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<p align="center">
  <img src="YOUR_PHOTO_1_URL_HERE" width="30%" alt="J.I.N.X Front View">
  &nbsp;
  <img src="YOUR_PHOTO_2_URL_HERE" width="30%" alt="J.I.N.X Side View">
  &nbsp;
  <img src="YOUR_PHOTO_3_URL_HERE" width="30%" alt="J.I.N.X in Action">
</p>

<p align="center">
  <img src="YOUR_PHOTO_4_URL_HERE" width="46%" alt="Dashboard Screenshot">
  &nbsp;
  <img src="YOUR_PHOTO_5_URL_HERE" width="46%" alt="Web Control Panel">
</p>

<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- YOUTUBE VIDEO — replace with your actual YouTube video link   -->
<!-- Format: https://www.youtube.com/watch?v=YOUR_VIDEO_ID        -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<p align="center">
  <a href="YOUR_YOUTUBE_VIDEO_URL_HERE">
    <img src="https://img.shields.io/badge/▶%20Watch%20Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch Demo on YouTube">
  </a>
</p>

> 📸 *This is a unfinished project right now, as soon as we get funds we will be desiging its body, we would not let it stay nude like a 3yr-old child roaming around the house !!*

> 🎥 *we hope you like the video on our channel and support us. Stay Tuned for such crazy projects we will be delivering them with a craze on !!*

---

## 👥 Team

<p align="center">

  <!-- ─────────────────── SIDDHARTH ─────────────────── -->
  <table align="center">
  <tr>

  <td align="center" width="220">

  <!-- Replace with Siddharth's photo URL -->
  <img src="sid.png" width="100" height="100" style="border-radius:50%" alt="Siddharth Ravada"><br><br>
  <strong>Ravada Siddharth</strong><br>
  <sub>Lead Developer · AI/ML · Hardware · IoT · Backend</sub><br><br>
  <a href="https://github.com/Sidvortex"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://www.linkedin.com/in/siddharth-ravada-a032b52a2/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/crisisbysid"><img src="https://img.shields.io/badge/X-000000?style=flat-square&logo=x&logoColor=white" alt="X"></a>
  <a href="mailto:ravadasiddharth@gmail.com"><img src="https://img.shields.io/badge/Gmail-D14836?style=flat-square&logo=gmail&logoColor=white" alt="Gmail"></a>

  </td>

  <!-- ─────────────────── AYUSH ─────────────────── -->
  <td align="center" width="220">

  <!-- Replace with Ayush's photo URL -->
  <img src="ayush.jpeg" width="100" height="100" style="border-radius:50%" alt="Ayush Mishra"><br><br>
  <strong>Kanak Sharma</strong><br>
  <sub>Developer · Backend · Integration · AI/ML</sub><br><br>
  <a href="https://github.com/bhavya132006"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>

  </td>

  <!-- ─────────────────── VINAYAK ─────────────────── -->
  <td align="center" width="220">

  <!-- Replace with Vinayak's photo URL -->
  <img src="vinayak.jpeg" width="100" height="100" style="border-radius:50%" alt="Vinayak Kapoor"><br><br>
  <strong>Arpit Kumar</strong><br>
  <sub>Developer · Frontend · App_Development · AI/ML</sub><br><br>
  <a href="https://github.com/arpitkumar1275hacker"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>

  </td>

  </tr>
  </table>
  

</p>

<p align="center">
  <strong>B.Tech Data Science (2023–2027)</strong>
</p>

---

<p align="center">
  <img src="https://www.animatedimages.org/data/media/562/animated-line-image-0184.gif" alt="Divider">
</p>

<p align="center">
  Built with dark magic acquired from the pitch black caves of West Bengal<br>
  <strong><a href="https://github.com/Sidvortex">@sidvortex</a></strong>
</p>

<p align="center">
  <i>J.I.N.X doesn't just think. It judges.</i>
</p>
