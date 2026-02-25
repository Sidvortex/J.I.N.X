#ifndef SENSORS_H
#define SENSORS_H

// ═══════════════════════════════════════════════════════════════════════════
//  sensors.h — All Sensor Reads for JINX
//
//  1. VL53L0X ToF ×2  — downward (edge detection) + forward (obstacle)
//  2. HC-SR04 ×2       — front-left and front-right ultrasonic
//  3. IR ×2            — left and right line/edge sensors (digital)
//
//  Non-blocking: all reads happen in sensorTick() every SENSOR_INTERVAL ms.
//  Publishes to MQTT "jinx/sensors" as JSON.
//  Auto-triggers motorEmergencyStop() on edge or obstacle.
// ═══════════════════════════════════════════════════════════════════════════

#include <Wire.h>
#include <VL53L0X.h>
#include <PubSubClient.h>
#include "config.h"
#include "motors.h"

// ── VL53L0X sensor objects ─────────────────────────────────────────────────
VL53L0X tofDown;   // points downward — detects table edge
VL53L0X tofFwd;    // points forward  — detects obstacles

// ── Sensor data (latest readings) ─────────────────────────────────────────
static uint16_t _tofDownMm  = 9999;
static uint16_t _tofFwdMm   = 9999;
static float    _us1Cm      = 999.0f;
static float    _us2Cm      = 999.0f;
static bool     _irLeft     = false;
static bool     _irRight    = false;

static uint32_t _sensorLastMs  = 0;
static bool     _sensorsOk     = false;

// ── ToF init: stagger XSHUT to assign unique I2C addresses ────────────────
bool initToF() {
  Wire.begin(I2C_SDA, I2C_SCL);

  // Both sensors off
  pinMode(TOF_DOWN_XSHUT, OUTPUT);
  pinMode(TOF_FWD_XSHUT,  OUTPUT);
  digitalWrite(TOF_DOWN_XSHUT, LOW);
  digitalWrite(TOF_FWD_XSHUT,  LOW);
  delay(10);

  // Init downward sensor first
  digitalWrite(TOF_DOWN_XSHUT, HIGH);
  delay(10);
  tofDown.init();
  tofDown.setAddress(TOF_DOWN_ADDR);
  tofDown.startContinuous(50);
  DBGLN("[SENSORS] ToF DOWN init OK");

  // Then forward sensor
  digitalWrite(TOF_FWD_XSHUT, HIGH);
  delay(10);
  tofFwd.init();
  tofFwd.setAddress(TOF_FWD_ADDR);
  tofFwd.startContinuous(50);
  DBGLN("[SENSORS] ToF FWD init OK");

  return true;
}

// ── HC-SR04 single pulse read (blocking ~30ms max) ────────────────────────
float readUltrasonic(uint8_t trigPin, uint8_t echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 25000);  // 25ms timeout = ~4m max
  if (duration == 0) return 999.0f;               // timeout = no echo
  return (duration * 0.0343f) / 2.0f;             // cm
}

// ── All sensor init ────────────────────────────────────────────────────────
void initSensors() {
  // HC-SR04
  pinMode(HCSR04_1_TRIG, OUTPUT);
  pinMode(HCSR04_1_ECHO, INPUT);
  pinMode(HCSR04_2_TRIG, OUTPUT);
  pinMode(HCSR04_2_ECHO, INPUT);

  // IR sensors
  pinMode(IR_LEFT_PIN,  INPUT);
  pinMode(IR_RIGHT_PIN, INPUT);

  // ToF
  _sensorsOk = initToF();

  if (!_sensorsOk) {
    DBGLN("[SENSORS] WARNING: ToF init failed — running without ToF");
  }
  DBGLN("[SENSORS] All sensors initialized");
}

// ── sensorTick() — call every loop() ──────────────────────────────────────
// Reads all sensors every SENSOR_INTERVAL ms.
// Returns true when new data is ready (publish on this tick).
bool sensorTick() {
  uint32_t now = millis();
  if (now - _sensorLastMs < SENSOR_INTERVAL) return false;
  _sensorLastMs = now;

  // ── Read ToF ────────────────────────────────────────────────────────────
  if (_sensorsOk) {
    uint16_t d = tofDown.readRangeContinuousMillimeters();
    if (!tofDown.timeoutOccurred()) _tofDownMm = d;

    uint16_t f = tofFwd.readRangeContinuousMillimeters();
    if (!tofFwd.timeoutOccurred()) _tofFwdMm = f;
  }

  // ── Read HC-SR04 ─────────────────────────────────────────────────────────
  _us1Cm = readUltrasonic(HCSR04_1_TRIG, HCSR04_1_ECHO);
  _us2Cm = readUltrasonic(HCSR04_2_TRIG, HCSR04_2_ECHO);

  // ── Read IR ──────────────────────────────────────────────────────────────
  // Most IR modules: LOW = surface detected, HIGH = edge/no surface
  _irLeft  = (digitalRead(IR_LEFT_PIN)  == HIGH);
  _irRight = (digitalRead(IR_RIGHT_PIN) == HIGH);

  // ── Safety checks ────────────────────────────────────────────────────────

  // Edge detection via ToF (table edge = sudden increase in distance)
  bool edgeDetected = (_tofDownMm > EDGE_THRESHOLD_MM);
  // IR backup
  bool irEdge = (_irLeft || _irRight);

  if (edgeDetected || irEdge) {
    if (!motorIsEmergency()) {
      DBGF("[SENSORS] EDGE DETECTED! ToF=%dmm IR_L=%d IR_R=%d\n",
           _tofDownMm, _irLeft, _irRight);
      motorEmergencyStop();
    }
  } else {
    // Clear emergency if edge no longer detected
    if (motorIsEmergency()) {
      motorClearEmergency();
    }
  }

  // Forward obstacle via ToF
  if (_tofFwdMm < OBSTACLE_THRESHOLD_MM) {
    if (!motorIsEmergency()) {
      DBGF("[SENSORS] OBSTACLE! ToF_fwd=%dmm\n", _tofFwdMm);
      motorEmergencyStop();
    }
  }

  // Ultrasonic obstacle
  float minUs = min(_us1Cm, _us2Cm);
  if (minUs < ULTRASONIC_STOP_CM && minUs > 0) {
    if (!motorIsEmergency()) {
      DBGF("[SENSORS] US OBSTACLE! %.1fcm\n", minUs);
      motorEmergencyStop();
    }
  }

  return true;  // new data ready
}

// ── Build sensor JSON payload for MQTT ────────────────────────────────────
String sensorBuildJson() {
  char buf[200];
  snprintf(buf, sizeof(buf),
    "{\"tof_down_mm\":%u,\"tof_fwd_mm\":%u,"
    "\"us1_cm\":%.1f,\"us2_cm\":%.1f,"
    "\"ir_left\":%s,\"ir_right\":%s,"
    "\"edge\":%s,\"obstacle\":%s}",
    _tofDownMm, _tofFwdMm,
    _us1Cm, _us2Cm,
    _irLeft  ? "true" : "false",
    _irRight ? "true" : "false",
    (_tofDownMm > EDGE_THRESHOLD_MM || _irLeft || _irRight) ? "true" : "false",
    (_tofFwdMm  < OBSTACLE_THRESHOLD_MM ||
     min(_us1Cm,_us2Cm) < ULTRASONIC_STOP_CM) ? "true" : "false"
  );
  return String(buf);
}

// ── Getters ───────────────────────────────────────────────────────────────
uint16_t sensorGetTofDown() { return _tofDownMm; }
uint16_t sensorGetTofFwd()  { return _tofFwdMm;  }
float    sensorGetUs1()     { return _us1Cm;      }
float    sensorGetUs2()     { return _us2Cm;      }
bool     sensorGetIrLeft()  { return _irLeft;     }
bool     sensorGetIrRight() { return _irRight;    }
bool     sensorEdgeDetected() {
  return (_tofDownMm > EDGE_THRESHOLD_MM || _irLeft || _irRight);
}

#endif // SENSORS_H
