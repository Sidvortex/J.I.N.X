#ifndef MOTORS_H
#define MOTORS_H

// ═══════════════════════════════════════════════════════════════════════════
//  motors.h — L298N Dual Motor Driver
//  Controls left and right track motors via IN1–IN4 + ENA/ENB PWM.
//  Commands: forward, backward, left, right, stop, surge, retreat
//  Speed: 0–255 via motorSetSpeed()
//  Safety: auto-stop if obstacle/edge detected (called from sensors.h)
// ═══════════════════════════════════════════════════════════════════════════

#include "config.h"

// ── PWM channels (ESP32 LEDC) ─────────────────────────────────────────────
#define PWM_CH_A  0    // ENA — left motor
#define PWM_CH_B  1    // ENB — right motor

// ── Motor state ───────────────────────────────────────────────────────────
static uint8_t  _motorSpeed    = MOTOR_DEFAULT_SPEED;
static String   _motorCmd      = "stop";
static bool     _motorStopped  = false;   // emergency stop flag

// ── Init ──────────────────────────────────────────────────────────────────
void initMotors() {
  // Direction pins
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_IN3, OUTPUT);
  pinMode(MOTOR_IN4, OUTPUT);

  // PWM setup (ESP32 LEDC)
  ledcSetup(PWM_CH_A, MOTOR_PWM_FREQ, MOTOR_PWM_RES);
  ledcSetup(PWM_CH_B, MOTOR_PWM_FREQ, MOTOR_PWM_RES);
  ledcAttachPin(MOTOR_ENA, PWM_CH_A);
  ledcAttachPin(MOTOR_ENB, PWM_CH_B);

  // Start stopped
  motorHalt();
  DBGLN("[MOTORS] Initialized");
}

// ── Internal: set raw direction ────────────────────────────────────────────
void _motorLeft(bool fwd) {
  digitalWrite(MOTOR_IN1, fwd ? HIGH : LOW);
  digitalWrite(MOTOR_IN2, fwd ? LOW  : HIGH);
}
void _motorRight(bool fwd) {
  digitalWrite(MOTOR_IN3, fwd ? HIGH : LOW);
  digitalWrite(MOTOR_IN4, fwd ? LOW  : HIGH);
}
void _motorSetPWM(uint8_t speedA, uint8_t speedB) {
  ledcWrite(PWM_CH_A, speedA);
  ledcWrite(PWM_CH_B, speedB);
}

// ── Public motor commands ──────────────────────────────────────────────────

void motorHalt() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
  digitalWrite(MOTOR_IN3, LOW);
  digitalWrite(MOTOR_IN4, LOW);
  _motorSetPWM(0, 0);
  _motorCmd = "stop";
}

void motorForward() {
  if (_motorStopped) return;
  _motorLeft(true);
  _motorRight(true);
  _motorSetPWM(_motorSpeed, _motorSpeed);
  _motorCmd = "forward";
}

void motorBackward() {
  if (_motorStopped) return;
  _motorLeft(false);
  _motorRight(false);
  _motorSetPWM(_motorSpeed, _motorSpeed);
  _motorCmd = "backward";
}

void motorTurnLeft() {
  if (_motorStopped) return;
  // Tank turn: left track backward, right track forward
  _motorLeft(false);
  _motorRight(true);
  _motorSetPWM(_motorSpeed, _motorSpeed);
  _motorCmd = "left";
}

void motorTurnRight() {
  if (_motorStopped) return;
  _motorLeft(true);
  _motorRight(false);
  _motorSetPWM(_motorSpeed, _motorSpeed);
  _motorCmd = "right";
}

// Surge = emergency full-speed forward burst (for demo)
void motorSurge() {
  if (_motorStopped) return;
  _motorLeft(true);
  _motorRight(true);
  _motorSetPWM(255, 255);
  _motorCmd = "surge";
}

// Retreat = emergency full-speed backward burst
void motorRetreat() {
  _motorLeft(false);
  _motorRight(false);
  _motorSetPWM(255, 255);
  _motorCmd = "retreat";
}

// ── Speed control ─────────────────────────────────────────────────────────
void motorSetSpeed(uint8_t speed) {
  _motorSpeed = speed;
  // If currently moving, update speed live
  if (_motorCmd == "forward")  motorForward();
  if (_motorCmd == "backward") motorBackward();
  if (_motorCmd == "left")     motorTurnLeft();
  if (_motorCmd == "right")    motorTurnRight();
}

// ── Emergency stop (called by sensors when edge/obstacle detected) ─────────
void motorEmergencyStop() {
  motorHalt();
  _motorStopped = true;
  DBGLN("[MOTORS] EMERGENCY STOP");
}

void motorClearEmergency() {
  _motorStopped = false;
  DBGLN("[MOTORS] Emergency cleared");
}

bool motorIsEmergency() { return _motorStopped; }

// ── Handle MQTT command string ─────────────────────────────────────────────
// Called from mqttCallback with payload from TOPIC_MOTOR
// Expected JSON: {"direction":"forward"} or {"direction":"stop","speed":200}
void motorHandleCommand(String direction, int speed = -1) {
  if (speed > 0) motorSetSpeed((uint8_t)constrain(speed, 0, 255));

  direction.toLowerCase();
  if      (direction == "forward")  motorForward();
  else if (direction == "backward") motorBackward();
  else if (direction == "left")     motorTurnLeft();
  else if (direction == "right")    motorTurnRight();
  else if (direction == "stop")     motorHalt();
  else if (direction == "surge")    motorSurge();
  else if (direction == "retreat")  motorRetreat();
  else                              motorHalt();

  DBGF("[MOTORS] Command: %s @ speed %d\n", direction.c_str(), _motorSpeed);
}

// ── Get current command (for status reporting) ─────────────────────────────
String motorGetCmd() { return _motorCmd; }
uint8_t motorGetSpeed() { return _motorSpeed; }

#endif // MOTORS_H
