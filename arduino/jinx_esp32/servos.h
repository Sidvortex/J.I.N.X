#ifndef SERVOS_H
#define SERVOS_H

// ═══════════════════════════════════════════════════════════════════════════
//  servos.h — Pan/Tilt Servo Head Control
//  Two SG90 servos: pan (left/right) and tilt (up/down).
//  Features:
//    • Smooth interpolation (3° per step, 15ms interval)
//    • Face tracking via normalized (x,y) from OPTIC module
//    • Manual positioning
//    • Centering / reset
// ═══════════════════════════════════════════════════════════════════════════

#include <ESP32Servo.h>
#include "config.h"

// ── Servo objects ─────────────────────────────────────────────────────────
Servo servoPan;
Servo servoTilt;

// ── Current and target positions ──────────────────────────────────────────
static float _panCurrent  = PAN_CENTER;
static float _tiltCurrent = TILT_CENTER;
static float _panTarget   = PAN_CENTER;
static float _tiltTarget  = TILT_CENTER;
static uint32_t _servoLastMs = 0;

// ── Init ──────────────────────────────────────────────────────────────────
void initServos() {
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  servoPan.setPeriodHertz(50);
  servoTilt.setPeriodHertz(50);

  servoPan.attach(SERVO_PAN_PIN,  500, 2400);
  servoTilt.attach(SERVO_TILT_PIN, 500, 2400);

  servoPan.write(PAN_CENTER);
  servoTilt.write(TILT_CENTER);

  _panCurrent  = PAN_CENTER;
  _tiltCurrent = TILT_CENTER;
  _panTarget   = PAN_CENTER;
  _tiltTarget  = TILT_CENTER;

  DBGLN("[SERVOS] Initialized — centered");
}

// ── Set target position (servos will interpolate smoothly) ────────────────
void servoSetPan(float deg) {
  _panTarget = constrain(deg, PAN_MIN, PAN_MAX);
}

void servoSetTilt(float deg) {
  _tiltTarget = constrain(deg, TILT_MIN, TILT_MAX);
}

void servoCenter() {
  _panTarget  = PAN_CENTER;
  _tiltTarget = TILT_CENTER;
}

// ── Face tracking: receive normalized (0.0–1.0) face center from OPTIC ────
// nx=0.0 → face at left edge → pan right (increase angle)
// nx=1.0 → face at right edge → pan left (decrease angle)
// ny=0.0 → face at top → tilt up (increase angle)
// ny=1.0 → face at bottom → tilt down (decrease angle)
void servoTrackFace(float nx, float ny) {
  // Map normalized position to servo range
  // Invert X so robot turns toward face
  float panDeg  = map(nx * 100, 0, 100, PAN_MAX, PAN_MIN);
  float tiltDeg = map(ny * 100, 0, 100, TILT_MIN, TILT_MAX);

  // Dead zone: only move if face is significantly off-center
  float panDeadZone  = 5.0f;
  float tiltDeadZone = 4.0f;

  if (abs(panDeg  - _panCurrent)  > panDeadZone)  servoSetPan(panDeg);
  if (abs(tiltDeg - _tiltCurrent) > tiltDeadZone) servoSetTilt(tiltDeg);
}

// ── servos.h map() helper (float version) ─────────────────────────────────
float mapf(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// ── servoTick() — call every loop() ──────────────────────────────────────
// Moves current position toward target by SERVO_STEP degrees every SERVO_INTERVAL ms
void servoTick() {
  uint32_t now = millis();
  if (now - _servoLastMs < SERVO_INTERVAL) return;
  _servoLastMs = now;

  bool moved = false;

  // Pan interpolation
  if (abs(_panTarget - _panCurrent) > 0.5f) {
    if (_panTarget > _panCurrent)
      _panCurrent = min(_panCurrent + SERVO_STEP, _panTarget);
    else
      _panCurrent = max(_panCurrent - SERVO_STEP, _panTarget);
    servoPan.write((int)_panCurrent);
    moved = true;
  }

  // Tilt interpolation
  if (abs(_tiltTarget - _tiltCurrent) > 0.5f) {
    if (_tiltTarget > _tiltCurrent)
      _tiltCurrent = min(_tiltCurrent + SERVO_STEP, _tiltTarget);
    else
      _tiltCurrent = max(_tiltCurrent - SERVO_STEP, _tiltTarget);
    servoTilt.write((int)_tiltCurrent);
    moved = true;
  }
}

// ── Getters ───────────────────────────────────────────────────────────────
float servoGetPan()  { return _panCurrent;  }
float servoGetTilt() { return _tiltCurrent; }

// ── Nod: quick tilt down+up (acknowledgement gesture) ────────────────────
void servoNod() {
  float savedTilt = _tiltTarget;
  servoSetTilt(_tiltCurrent + 15);
  delay(250);
  servoSetTilt(savedTilt);
}

// ── Shake: quick pan left+right (disagreement gesture) ────────────────────
void servoShake() {
  float savedPan = _panTarget;
  servoSetPan(_panCurrent - 20);
  delay(200);
  servoSetPan(_panCurrent + 20);
  delay(200);
  servoSetPan(savedPan);
}

#endif // SERVOS_H
