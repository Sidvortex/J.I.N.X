# 🧠 J.I.N.X. Codex — Cyberpunk Naming Convention

All functions, variables, and modules in JINX use cyberpunk-inspired codenames.

## Module Codenames

| Module | Codename | Purpose | Key Functions |
|---|---|---|---|
| `genesis.py` | **GENESIS** | System initialization and startup | `boot()`, `shutdown()` |
| `dna.py` | **DNA** | Configuration, settings, constants | `load_config()` |
| `blackbox.py` | **BLACKBOX** | SQLite database logging | `log_event()`, `fetch_events()` |
| `psyche.py` | **PSYCHE** | Personality, dialogue, emotional prompts | `generate_roast()`, `get_emotion_prompt()` |
| `optic.py` | **OPTIC** | Vision pipeline — detection, recognition, mesh | `cortex_scan()`, `phantom_trace()`, `wireframe()` |
| `vocoder.py` | **VOCODER** | Voice — STT, TTS, Gemini LLM, commands | `parse_order()`, `vocalize()` |
| `echo_hunter.py` | **ECHO HUNTER** | Audio classification, sound detection | `freq_hunt()` |
| `ice_wall.py` | **ICE WALL** | Network scanning, anomaly detection | `scan_network()` |
| `synapse.py` | **SYNAPSE** | MQTT message routing, state management | `broadcast()`, `subscribe()` |
| `hivemind.py` | **HIVEMIND** | Sensor fusion, threat scoring | `_recalculate()`, `doom_score()` |
| `nexus.py` | **NEXUS** | Streamlit dashboard, UI | `run_dashboard()` |

## Function Codenames

### OPTIC (Vision)
- `cortex_scan()` — Main vision pipeline combining all detection methods
- `phantom_trace()` — Face recognition and threat classification
- `wireframe()` — Face mesh and skeleton overlay
- `bone_rip()` — Pose estimation
- `gesture_lock()` — Hand gesture recognition
- `threat_halo()` — Bounding box drawing with threat coloring

### VOCODER (Voice)
- `parse_order()` — Speech-to-text command parsing
- `vocalize()` — Text-to-speech output
- `roast_generator()` — Gemini API roast generation
- `command_execute()` — Voice command routing

### ECHO HUNTER (Audio)
- `freq_hunt()` — Audio classification CNN inference
- `spectrogram_gen()` — Mel-spectrogram generation
- `anomaly_alert()` — Threat sound detection

### ICE WALL (Network)
- `scan_network()` — ARP network device discovery
- `anomaly_detect()` — ML-based intrusion detection
- `threat_assess()` — Network traffic analysis

### HIVEMIND (Fusion)
- `_recalculate()` — Recalculate doom_level
- `doom_score()` — Combined threat calculation
- `threat_broadcast()` — Send alerts via MQTT

## Variable Codenames

| Variable | Meaning |
|---|---|
| `doom_level` | Combined threat score (0.0 - 1.0) |
| `phantom_list` | Known faces database |
| `threat_vector` | Current threat classification (SAFE / UNKNOWN / THREAT) |
| `neon_frame` | Processed frame with HUD overlays |
| `cortex` | Main AI processing context |
| `synapse_state` | Current system state tracking |

## MQTT Topic Codenames

| Topic | Direction | Content |
|---|---|---|
| `jinx/eyes` | Server → ESP32 | Eye state + emotion |
| `jinx/head_track` | Server → ESP32 | Face position for servos |
| `jinx/motor` | Server → ESP32 | Movement commands |
| `jinx/led` | Server → ESP32 | LED patterns |
| `jinx/buzzer` | Server → ESP32 | Alert sounds |
| `jinx/sensors` | ESP32 → Server | Sensor readings |
| `jinx/battery` | ESP32 → Server | Battery voltage/percentage |
| `jinx/doom_level` | Server → Tablet | Threat score |
| `jinx/alerts` | Server → Tablet | Alert notifications |

## Eye Animation States

| State | Codename | Trigger |
|---|---|---|
| Neutral | `NEUTRAL` | Default |
| Happy | `HAPPY` | Friendly interaction |
| Angry | `ANGRY` | Threat detected |
| Sleepy | `SLEEPY` | Low battery |
| Love | `LOVE` | Roast mode / flirting |
| Scanning | `SCANNING` | Active patrol |
| Threat | `THREAT` | Red alert |
| Roast | `ROAST` | Roast mode active |
| Music | `MUSIC` | Music playback |
| Thinking | `THINKING` | Processing |
| Surprised | `SURPRISED` | Unexpected event |

## Mode Codenames

| Mode | Status | Behavior |
|---|---|---|
| `BUDDY` | Default | Friendly, responsive, wandering |
| `SENTINEL` | Surveillance | Active patrol, threat detection |
| `ROAST` | Humor | Face-based comedic generation |
| `DOCK` | Charging | Battery low, seeking dock |

---

**All new code should follow this naming convention for consistency and immersion in the J.I.N.X. universe.**
