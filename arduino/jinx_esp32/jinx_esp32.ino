// ============================================================
//  DESKBOT_ESP32.INO — ESP32 MAIN FIRMWARE
//  Handles: Eyes, Motors, Servos, LEDs, Sensors, Battery, Speaker
//  Communication: WiFi + MQTT
// ============================================================
// REQUIRED LIBRARIES:
//   TFT_eSPI, Adafruit_NeoPixel, PubSubClient,
//   ArduinoJson, ESP32Servo, DFRobotDFPlayerMini,
//   VL53L0X (Pololu)
// ============================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "eyes.h"
#include "motors.h"
#include "leds.h"
#include "sensors.h"
#include "servos.h"

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastSensorPublish = 0;
unsigned long lastBatteryCheck  = 0;
const long    SENSOR_INTERVAL   = 100;   // ms
const long    BATTERY_INTERVAL  = 5000;  // ms

// ── Setup ──────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n[DESKBOT] Booting...");

  // Init subsystems
  initMotors();
  initServos();
  initLEDs();
  initSensors();
  initEyes();

  // Play boot animation
  setEyeState(EYE_BOOT);
  ledEffect(LED_BOOT);

  // Connect WiFi
  connectWiFi();

  // Connect MQTT
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setBufferSize(4096);  // Larger buffer for frame data
  connectMQTT();

  // Boot sound
  playSound(SOUND_BOOT);
  setEyeState(EYE_NEUTRAL);
  ledEffect(LED_NORMAL);

  Serial.println("[DESKBOT] Online!");
  mqtt.publish(TOPIC_STATUS, "{\"status\":\"online\"}");
}

// ── Main Loop ─────────────────────────────────────────────────────────────

void loop() {
  if (!mqtt.connected()) connectMQTT();
  mqtt.loop();

  unsigned long now = millis();

  // Publish sensor data
  if (now - lastSensorPublish > SENSOR_INTERVAL) {
    lastSensorPublish = now;
    publishSensors();
  }

  // Battery check
  if (now - lastBatteryCheck > BATTERY_INTERVAL) {
    lastBatteryCheck = now;
    publishBattery();
  }

  // Update LED animations
  updateLEDs();

  // Update servo smooth movement
  updateServos();
}

// ── WiFi ──────────────────────────────────────────────────────────────────

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("[WIFI] Connecting");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WIFI] Connected: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WIFI] Failed! Running in offline mode.");
  }
}

// ── MQTT ──────────────────────────────────────────────────────────────────

void connectMQTT() {
  int retries = 0;
  while (!mqtt.connected() && retries < 5) {
    Serial.print("[MQTT] Connecting...");
    if (mqtt.connect("deskbot_esp32")) {
      Serial.println(" OK");
      // Subscribe to all command topics
      mqtt.subscribe(TOPIC_EYES);
      mqtt.subscribe(TOPIC_HEAD_TRACK);
      mqtt.subscribe(TOPIC_EYE_TRACK);
      mqtt.subscribe(TOPIC_MOTOR);
      mqtt.subscribe(TOPIC_LED);
      mqtt.subscribe(TOPIC_SOUND);
      mqtt.subscribe(TOPIC_BUZZER);
      mqtt.subscribe(TOPIC_MODE);
      mqtt.subscribe(TOPIC_COMMAND);
    } else {
      Serial.printf(" Failed rc=%d, retrying...\n", mqtt.state());
      delay(2000);
    }
    retries++;
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';
  String msg   = String((char*)payload);
  String topic_str = String(topic);

  // ── Eyes ────────────────────────────────────────────────
  if (topic_str == TOPIC_EYES) {
    if (msg == "neutral")    setEyeState(EYE_NEUTRAL);
    else if (msg == "happy")     setEyeState(EYE_HAPPY);
    else if (msg == "angry")     setEyeState(EYE_ANGRY);
    else if (msg == "sleepy")    setEyeState(EYE_SLEEPY);
    else if (msg == "love")      setEyeState(EYE_LOVE);
    else if (msg == "scanning")  setEyeState(EYE_SCANNING);
    else if (msg == "threat")    setEyeState(EYE_THREAT);
    else if (msg == "roast")     setEyeState(EYE_ROAST);
    else if (msg == "music")     setEyeState(EYE_MUSIC);
    else if (msg == "thinking")  setEyeState(EYE_THINKING);
    else if (msg == "talking")   setEyeState(EYE_TALKING);
    else if (msg == "boot")      setEyeState(EYE_BOOT);
  }

  // ── Head Tracking (Pan/Tilt) ────────────────────────────
  else if (topic_str == TOPIC_HEAD_TRACK) {
    StaticJsonDocument<64> doc;
    if (!deserializeJson(doc, msg)) {
      float nx = doc["x"] | 0.5f;  // Normalized 0-1
      float ny = doc["y"] | 0.5f;
      // Convert to servo angles: center=90°, full range=60°
      int pan  = 90 + (int)((0.5f - nx) * 60);   // Left/right
      int tilt = 90 + (int)((ny - 0.5f) * 40);   // Up/down
      pan  = constrain(pan,  60, 120);
      tilt = constrain(tilt, 70, 110);
      setServoPan(pan);
      setServoTilt(tilt);
    }
  }

  // ── Eye pupil tracking ────────────────────────────────────
  else if (topic_str == TOPIC_EYE_TRACK) {
    StaticJsonDocument<64> doc;
    if (!deserializeJson(doc, msg)) {
      float nx = doc["x"] | 0.5f;
      float ny = doc["y"] | 0.5f;
      movePupils(nx, ny);  // Implemented in eyes.h
    }
  }

  // ── Motors ───────────────────────────────────────────────
  else if (topic_str == TOPIC_MOTOR) {
    if (msg == "forward")  motorSurge(200);
    else if (msg == "backward") motorRetreat(200);
    else if (msg == "left")     motorLeft(180);
    else if (msg == "right")    motorRight(180);
    else if (msg == "stop")     motorHalt();
  }

  // ── LEDs ─────────────────────────────────────────────────
  else if (topic_str == TOPIC_LED) {
    if (msg == "off")        ledOff();
    else if (msg == "normal")    ledEffect(LED_NORMAL);
    else if (msg == "boot")      ledEffect(LED_BOOT);
    else if (msg == "wake")      ledEffect(LED_WAKE);
    else if (msg == "threat")    ledEffect(LED_THREAT);
    else if (msg == "scan")      ledEffect(LED_SCAN);
    else if (msg == "music")     ledEffect(LED_MUSIC);
    else if (msg == "roast")     ledEffect(LED_ROAST);
    else if (msg == "alert")     ledEffect(LED_ALERT);
    else if (msg == "party")     ledEffect(LED_PARTY);
    else if (msg == "battery_low") ledEffect(LED_BATTERY_LOW);
    else if (msg.startsWith("color:")) {
      String color = msg.substring(6);
      setLEDColor(color);
    }
  }

  // ── Sound Effects ─────────────────────────────────────────
  else if (topic_str == TOPIC_SOUND) {
    if (msg == "wake")       playSound(SOUND_WAKE);
    else if (msg == "boot")  playSound(SOUND_BOOT);
    else if (msg == "alert") playSound(SOUND_ALERT);
    else if (msg == "roast") playSound(SOUND_ROAST);
    else if (msg == "battery_low") playSound(SOUND_SLEEPY);
  }

  // ── Buzzer ────────────────────────────────────────────────
  else if (topic_str == TOPIC_BUZZER) {
    if (msg == "on") {
      tone(PIN_BUZZER, 880, 300);
      delay(100);
      tone(PIN_BUZZER, 660, 300);
    } else if (msg == "off") {
      noTone(PIN_BUZZER);
    }
  }

  // ── Mode ──────────────────────────────────────────────────
  else if (topic_str == TOPIC_MODE) {
    if (msg == "sentinel")   ledEffect(LED_SCAN);
    else if (msg == "sleep") { setEyeState(EYE_SLEEPY); ledEffect(LED_NORMAL); }
    else if (msg == "buddy") { setEyeState(EYE_NEUTRAL); ledEffect(LED_NORMAL); }
  }
}

// ── Sensor Publishing ─────────────────────────────────────────────────────

void publishSensors() {
  SensorData data = readSensors();
  StaticJsonDocument<256> doc;
  doc["us1_cm"]     = data.us1_cm;
  doc["us2_cm"]     = data.us2_cm;
  doc["ir_left"]    = data.ir_left;
  doc["ir_right"]   = data.ir_right;
  doc["tof_down_mm"]= data.tof_down_mm;
  doc["tof_fwd_mm"] = data.tof_fwd_mm;

  char buf[256];
  serializeJson(doc, buf);
  mqtt.publish(TOPIC_SENSORS, buf);
}

void publishBattery() {
  float voltage = readBatteryVoltage();
  float pct     = batteryPercent(voltage);
  StaticJsonDocument<64> doc;
  doc["voltage"] = voltage;
  doc["percent"] = (int)pct;
  char buf[64];
  serializeJson(doc, buf);
  mqtt.publish(TOPIC_BATTERY, buf);
}
