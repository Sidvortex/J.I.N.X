#ifndef BATTERY_H
#define BATTERY_H

// ═══════════════════════════════════════════════════════════════════════════
//  battery.h — Battery Monitor for JINX
//
//  Reads 2S LiPo voltage via resistor voltage divider on ADC pin.
//  Voltage divider: Vbatt → 10kΩ → GPIO35 → 10kΩ → GND
//  This halves the voltage: ADC sees Vbatt/2 (max ~4.2V for 8.4V pack)
//
//  Publishes to MQTT "jinx/battery" every BATTERY_INTERVAL ms.
//  Triggers:
//    • LED_BATTERY_LOW + EYE_SLEEPY when < BATTERY_CRIT_PCT (10%)
//    • MQTT alert when < BATTERY_WARN_PCT (20%)
//    • Motor emergency stop when < 5% (protect battery)
//
//  Functions:
//    batteryInit()          — call in setup()
//    batteryTick()          — call in loop(), returns true when published
//    batteryGetVoltage()    — returns float voltage
//    batteryGetPercent()    — returns 0–100
//    batteryBuildJson()     — returns JSON string for MQTT
// ═══════════════════════════════════════════════════════════════════════════

#include "config.h"
#include "LED.h"
#include "eyes.h"
#include "motors.h"

// ── Smoothing buffer ───────────────────────────────────────────────────────
#define BATT_SAMPLES     16    // ADC readings to average
static int     _battRawBuf[BATT_SAMPLES];
static uint8_t _battBufIdx   = 0;
static bool    _battBufFull  = false;
static float   _battVoltage  = 0.0f;
static int     _battPercent  = 100;
static uint32_t _battLastMs  = 0;
static bool    _warnSent     = false;
static bool    _critSent     = false;

// ── Discharge curve (2S LiPo: 6.0V–8.4V) ─────────────────────────────────
// Maps voltage to percentage via lookup table for more accuracy than linear
// [voltage × 10, percent]
static const int _battCurve[][2] = {
  {84, 100}, {82, 95}, {80, 90}, {79, 80},
  {78, 70},  {77, 60}, {76, 50}, {75, 40},
  {74, 30},  {73, 20}, {72, 15}, {71, 10},
  {70, 5},   {68, 2},  {60, 0}
};
#define BATT_CURVE_LEN (sizeof(_battCurve) / sizeof(_battCurve[0]))

// ── Init ──────────────────────────────────────────────────────────────────
void batteryInit() {
  analogSetAttenuation(ADC_11db);   // full range 0–3.3V
  analogSetWidth(12);               // 12-bit = 0–4095
  pinMode(BATTERY_PIN, INPUT);

  // Pre-fill buffer with a few readings
  for (int i = 0; i < BATT_SAMPLES; i++) {
    _battRawBuf[i] = analogRead(BATTERY_PIN);
    delay(2);
  }
  _battBufFull = true;

  // Initial reading
  _battVoltage = batteryGetVoltage();
  _battPercent = batteryGetPercent();

  DBGF("[BATT] Init: %.2fV → %d%%\n", _battVoltage, _battPercent);
}

// ── Raw ADC read with averaging ────────────────────────────────────────────
float _battReadSmoothed() {
  // Add new sample to circular buffer
  _battRawBuf[_battBufIdx] = analogRead(BATTERY_PIN);
  _battBufIdx = (_battBufIdx + 1) % BATT_SAMPLES;

  // Average all samples
  long sum = 0;
  for (int i = 0; i < BATT_SAMPLES; i++) sum += _battRawBuf[i];
  float avg = sum / (float)BATT_SAMPLES;

  // Convert ADC → actual voltage
  float adcVoltage  = (avg / 4095.0f) * 3.3f;
  float battVoltage = adcVoltage * 2.0f;   // voltage divider factor

  // Optional calibration offset (measure with multimeter and adjust)
  battVoltage += 0.0f;   // e.g. +0.15f if reading low

  return battVoltage;
}

// ── Voltage lookup → percentage ───────────────────────────────────────────
int _voltageToPercent(float v) {
  int vx10 = (int)(v * 10);   // e.g. 7.8V → 78

  // Past top of curve
  if (vx10 >= _battCurve[0][0]) return 100;
  // Past bottom of curve
  if (vx10 <= _battCurve[BATT_CURVE_LEN-1][0]) return 0;

  // Find segment and interpolate
  for (int i = 0; i < BATT_CURVE_LEN - 1; i++) {
    if (vx10 <= _battCurve[i][0] && vx10 >= _battCurve[i+1][0]) {
      int v1 = _battCurve[i][0],   p1 = _battCurve[i][1];
      int v2 = _battCurve[i+1][0], p2 = _battCurve[i+1][1];
      // Linear interpolation between two curve points
      float pct = p2 + (float)(vx10 - v2) / (v1 - v2) * (p1 - p2);
      return (int)constrain(pct, 0, 100);
    }
  }
  return 0;
}

// ── Public getters ────────────────────────────────────────────────────────
float batteryGetVoltage() {
  _battVoltage = _battReadSmoothed();
  return _battVoltage;
}

int batteryGetPercent() {
  _battPercent = _voltageToPercent(_battVoltage);
  return _battPercent;
}

// ── Build MQTT JSON ────────────────────────────────────────────────────────
String batteryBuildJson() {
  char buf[100];
  const char* status =
    (_battPercent <= BATTERY_CRIT_PCT) ? "critical" :
    (_battPercent <= BATTERY_WARN_PCT) ? "low"      : "ok";

  snprintf(buf, sizeof(buf),
    "{\"level\":%d,\"voltage\":%.2f,\"status\":\"%s\"}",
    _battPercent, _battVoltage, status);
  return String(buf);
}

// ── batteryTick() — call every loop() ─────────────────────────────────────
// Returns true when a new reading was published (for caller to send MQTT)
bool batteryTick() {
  uint32_t now = millis();
  if (now - _battLastMs < BATTERY_INTERVAL) return false;
  _battLastMs = now;

  // Update readings
  batteryGetVoltage();
  batteryGetPercent();

  DBGF("[BATT] %.2fV → %d%%\n", _battVoltage, _battPercent);

  // ── Warning threshold (20%) ──────────────────────────────────────────
  if (_battPercent <= BATTERY_WARN_PCT && !_warnSent) {
    _warnSent = true;
    DBGLN("[BATT] WARNING: battery low");
    // Caller (main .ino) will publish to TOPIC_ALERTS
  }

  // ── Critical threshold (10%) ──────────────────────────────────────────
  if (_battPercent <= BATTERY_CRIT_PCT && !_critSent) {
    _critSent = true;
    DBGLN("[BATT] CRITICAL: battery critical");
    ledSetMode(LED_BATTERY_LOW);
    eyeSetState(EYE_SLEEPY);
  }

  // ── Emergency: stop motors at 5% to protect cells ─────────────────────
  if (_battPercent <= 5 && !motorIsEmergency()) {
    DBGLN("[BATT] EMERGENCY: shutting down motors to protect battery");
    motorEmergencyStop();
  }

  // Reset warning flags if battery somehow recovers (charging)
  if (_battPercent > BATTERY_WARN_PCT + 5) {
    _warnSent = false;
    _critSent = false;
  }

  return true;  // new data ready — caller should publish
}

// ── Is battery warning active? (for main .ino to handle MQTT alert) ───────
bool batteryIsWarn()  { return _battPercent <= BATTERY_WARN_PCT; }
bool batteryIsCrit()  { return _battPercent <= BATTERY_CRIT_PCT; }

#endif // BATTERY_H
