// ═══════════════════════════════════════════════════════════════════════════
//  jinx_esp32.ino — JINX Robot Main Firmware
//
//  Hardware: ESP32-WROOM-32
//  Author:   Sidvortex
//  Version:  2.1.0
//
//  Includes:
//    config.h   — all pins, topics, thresholds
//    LED.h      — WS2812B NeoPixel (12 LEDs, 11 modes)
//    eyes.h     — ILI9341 TFT animated eyes (12 states)
//    motors.h   — L298N dual motor driver
//    servos.h   — SG90 pan/tilt head tracking
//    sensors.h  — VL53L0X ToF + HC-SR04 + IR sensors
//
//  MQTT Topics handled:
//    jinx/eyes        → eye state name ("neutral","threat",...)
//    jinx/head_track  → {"x":0.5,"y":0.5}  (face center normalized)
//    jinx/eye_track   → {"x":0.5,"y":0.5}  (pupil target)
//    jinx/motor       → {"direction":"forward","speed":180}
//    jinx/led         → "scan" / "alert" / "color:red" / ...
//    jinx/sound       → {"track":3}  (DFPlayer track number)
//    jinx/command     → {"type":"reboot"} / {"type":"center"} / ...
//    jinx/mode        → "BUDDY" / "SENTINEL" / "ROAST" / "SLEEP"
//
//  Publishes:
//    jinx/sensors  → sensor JSON every 100ms
//    jinx/battery  → {"level":85,"voltage":7.8} every 5s
//    jinx/status   → {"online":true,"mode":"BUDDY",...} on connect
// ═══════════════════════════════════════════════════════════════════════════

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ── Project headers (order matters) ──────────────────────────────────────
#include "config.h"
#include "LED.h"
#include "eyes.h"
#include "motors.h"
#include "servos.h"
#include "sensors.h"
#include "sound.h"
#include "battery.h"

// ── MQTT & WiFi clients ───────────────────────────────────────────────────
WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

// ── Global state ──────────────────────────────────────────────────────────
String  currentMode    = "BUDDY";
bool    wifiConnected  = false;
bool    mqttConnected  = false;
uint32_t lastMqttRetry = 0;
uint32_t lastWifiRetry = 0;

// Battery publishing handled via battery.h — see batteryTick() and batteryBuildJson()
void publishBattery() {
  String json = batteryBuildJson();
  mqtt.publish(TOPIC_BATTERY, json.c_str(), true);  // retained

  // If warning level, also send an alert
  if (batteryIsWarn()) {
    String alertMsg = "{\"type\":\"battery_low\",\"level\":" +
                      String(batteryGetPercent()) + "}";
    mqtt.publish(TOPIC_ALERTS, alertMsg.c_str());
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  MQTT CALLBACK
// ═══════════════════════════════════════════════════════════════════════════
void mqttCallback(char* topic, byte* payload, unsigned int len) {
  // Null-terminate payload
  char msg[MQTT_BUFFER_SIZE];
  len = min(len, (unsigned int)(MQTT_BUFFER_SIZE - 1));
  memcpy(msg, payload, len);
  msg[len] = '\0';

  String topicStr(topic);
  String msgStr(msg);

  DBGF("[MQTT] ← %s : %s\n", topic, msg);

  // ── jinx/eyes ────────────────────────────────────────────────────────────
  if (topicStr == TOPIC_EYES) {
    eyeSetStateByName(msgStr);
    return;
  }

  // ── jinx/led ─────────────────────────────────────────────────────────────
  if (topicStr == TOPIC_LED) {
    // Check for brightness: "brightness:180"
    if (msgStr.startsWith("brightness:")) {
      int b = msgStr.substring(11).toInt();
      ledSetBrightness(constrain(b, 0, 255));
    } else {
      ledSetByString(msgStr);
    }
    return;
  }

  // ── jinx/head_track  {"x":0.5,"y":0.4} ───────────────────────────────────
  if (topicStr == TOPIC_HEAD_TRACK) {
    StaticJsonDocument<64> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      float nx = doc["x"] | 0.5f;
      float ny = doc["y"] | 0.5f;
      servoTrackFace(nx, ny);
    }
    return;
  }

  // ── jinx/eye_track  {"x":0.5,"y":0.4} ────────────────────────────────────
  if (topicStr == TOPIC_EYE_TRACK) {
    StaticJsonDocument<64> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      float nx = doc["x"] | 0.5f;
      float ny = doc["y"] | 0.5f;
      eyeTrackPupil(nx, ny);
    }
    return;
  }

  // ── jinx/motor  {"direction":"forward","speed":180} ───────────────────────
  if (topicStr == TOPIC_MOTOR) {
    StaticJsonDocument<128> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      String dir = doc["direction"] | "stop";
      int    spd = doc["speed"]     | -1;
      motorHandleCommand(dir, spd);
    }
    return;
  }

  // ── jinx/sound  {"track":3} or {"name":"boot"} or "stop" ────────────────
  if (topicStr == TOPIC_SOUND) {
    soundHandleMqtt(msgStr);
    return;
  }

  // ── jinx/mode  "BUDDY" / "SENTINEL" / "ROAST" / "SLEEP" ─────────────────
  if (topicStr == TOPIC_MODE) {
    currentMode = msgStr;
    currentMode.toUpperCase();
    onModeChange(currentMode);
    return;
  }

  // ── jinx/command  {"type":"reboot"} ──────────────────────────────────────
  if (topicStr == TOPIC_COMMAND) {
    StaticJsonDocument<256> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      String type = doc["type"] | "";
      handleCommand(type, doc);
    }
    return;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  MODE CHANGES
// ═══════════════════════════════════════════════════════════════════════════
void onModeChange(String mode) {
  DBGF("[MODE] → %s\n", mode.c_str());

  if (mode == "BUDDY") {
    eyeSetState(EYE_NEUTRAL);
    ledSetMode(LED_NORMAL);
  } else if (mode == "SENTINEL") {
    eyeSetState(EYE_SCANNING);
    ledSetMode(LED_SCAN);
  } else if (mode == "ROAST") {
    eyeSetState(EYE_ROAST);
    ledSetMode(LED_PARTY);
  } else if (mode == "AGENT") {
    eyeSetState(EYE_THINKING);
    ledSetMode(LED_NORMAL);
  } else if (mode == "SLEEP") {
    eyeSetState(EYE_SLEEPY);
    ledSetMode(LED_OFF);
    motorHalt();
    servoCenter();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  COMMAND HANDLER
// ═══════════════════════════════════════════════════════════════════════════
void handleCommand(String type, JsonDocument& doc) {
  if (type == "reboot_esp") {
    DBGLN("[CMD] Rebooting...");
    delay(200);
    ESP.restart();
  }
  else if (type == "center_servos") {
    servoCenter();
    DBGLN("[CMD] Servos centered");
  }
  else if (type == "nod") {
    servoNod();
  }
  else if (type == "shake") {
    servoShake();
  }
  else if (type == "ack") {
    ledFlashAck();
  }
  else if (type == "brightness") {
    int b = doc["value"] | LED_DEFAULT_BRIGHT;
    ledSetBrightness(b);
  }
  else if (type == "emergency_stop") {
    motorEmergencyStop();
    eyeSetState(EYE_THREAT);
    ledSetMode(LED_ALERT);
    DBGLN("[CMD] Emergency stop");
  }
  else if (type == "clear_stop") {
    motorClearEmergency();
    eyeSetState(EYE_NEUTRAL);
    ledSetMode(LED_NORMAL);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  WiFi
// ═══════════════════════════════════════════════════════════════════════════
void connectWiFi() {
  DBGF("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    DBG(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    DBGF("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    wifiConnected = false;
    DBGLN("\n[WiFi] Failed — will retry");
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  MQTT
// ═══════════════════════════════════════════════════════════════════════════
void connectMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;

  DBGF("[MQTT] Connecting to %s:%d\n", MQTT_BROKER, MQTT_PORT);
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setBufferSize(MQTT_BUFFER_SIZE);

  bool ok = (strlen(MQTT_USER) > 0)
    ? mqtt.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS,
                   TOPIC_STATUS, 0, true, "{\"online\":false}")
    : mqtt.connect(MQTT_CLIENT_ID, NULL, NULL,
                   TOPIC_STATUS, 0, true, "{\"online\":false}");

  if (ok) {
    mqttConnected = true;
    DBGLN("[MQTT] Connected!");

    // Subscribe to all command topics
    mqtt.subscribe(TOPIC_EYES);
    mqtt.subscribe(TOPIC_HEAD_TRACK);
    mqtt.subscribe(TOPIC_EYE_TRACK);
    mqtt.subscribe(TOPIC_MOTOR);
    mqtt.subscribe(TOPIC_LED);
    mqtt.subscribe(TOPIC_SOUND);
    mqtt.subscribe(TOPIC_MODE);
    mqtt.subscribe(TOPIC_COMMAND);

    // Announce online
    char status[120];
    snprintf(status, sizeof(status),
      "{\"online\":true,\"mode\":\"%s\",\"ip\":\"%s\",\"firmware\":\"2.1.0\"}",
      currentMode.c_str(), WiFi.localIP().toString().c_str());
    mqtt.publish(TOPIC_STATUS, status, true);

    // Boot complete LED + eyes
    ledSetMode(LED_NORMAL);
    eyeSetState(EYE_NEUTRAL);
    soundPlay(SOUND_BOOT);   // plays /01/001.mp3

  } else {
    mqttConnected = false;
    DBGF("[MQTT] Failed, rc=%d\n", mqtt.state());
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//  SETUP
// ═══════════════════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  DBGLN("\n\n[JINX] Booting v2.1.0...");

  // ── Boot sequence: eyes + LED first (no WiFi needed) ──────────────────
  initEyes();
  eyeSetState(EYE_BOOT);
  ledInit();
  ledBoot();
  eyeSetBootProgress(10);

  // ── Motors and servos ─────────────────────────────────────────────────
  initMotors();
  eyeSetBootProgress(25);

  initServos();
  eyeSetBootProgress(40);

  // ── Sensors ───────────────────────────────────────────────────────────
  initSensors();
  eyeSetBootProgress(55);

  // ── Sound ──────────────────────────────────────────────────────────────
  soundInit();
  eyeSetBootProgress(65);

  // ── WiFi ──────────────────────────────────────────────────────────────
  batteryInit();
  connectWiFi();
  eyeSetBootProgress(80);

  // ── MQTT ──────────────────────────────────────────────────────────────
  if (wifiConnected) {
    connectMQTT();
  }
  eyeSetBootProgress(100);

  DBGLN("[JINX] Boot complete");
}

// ═══════════════════════════════════════════════════════════════════════════
//  LOOP
// ═══════════════════════════════════════════════════════════════════════════
void loop() {
  uint32_t now = millis();

  // ── WiFi watchdog ─────────────────────────────────────────────────────
  if (WiFi.status() != WL_CONNECTED) {
    if (now - lastWifiRetry > WIFI_RECONNECT_MS) {
      lastWifiRetry = now;
      wifiConnected = false;
      mqttConnected = false;
      DBGLN("[WiFi] Reconnecting...");
      WiFi.reconnect();
    }
  }

  // ── MQTT watchdog ─────────────────────────────────────────────────────
  if (wifiConnected && !mqtt.connected()) {
    if (now - lastMqttRetry > MQTT_RECONNECT_MS) {
      lastMqttRetry = now;
      DBGLN("[MQTT] Reconnecting...");
      connectMQTT();
    }
  }

  // ── MQTT loop (process incoming messages) ─────────────────────────────
  if (mqtt.connected()) {
    mqtt.loop();
  }

  // ── Sensors (reads + safety checks + MQTT publish) ───────────────────
  if (sensorTick() && mqtt.connected()) {
    String sensorJson = sensorBuildJson();
    mqtt.publish(TOPIC_SENSORS, sensorJson.c_str());
  }

  // ── Battery tick + publish ─────────────────────────────────────────────
  if (batteryTick() && mqtt.connected()) {
    publishBattery();
  }

  // ── Non-blocking animations ───────────────────────────────────────────
  ledTick();      // LED effects
  eyeTick();      // TFT eye animations
  servoTick();    // smooth servo interpolation
}
