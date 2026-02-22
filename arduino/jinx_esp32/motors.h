// ============================================================
//  MOTORS.H — DC MOTOR CONTROL VIA L298N
// ============================================================
#pragma once
#include "config.h"

void initMotors() {
  pinMode(PIN_MOTOR_IN1, OUTPUT); pinMode(PIN_MOTOR_IN2, OUTPUT);
  pinMode(PIN_MOTOR_IN3, OUTPUT); pinMode(PIN_MOTOR_IN4, OUTPUT);
  pinMode(PIN_MOTOR_ENA, OUTPUT); pinMode(PIN_MOTOR_ENB, OUTPUT);
  motorHalt();
}

void _setMotorSpeed(int speed) {
  analogWrite(PIN_MOTOR_ENA, speed);
  analogWrite(PIN_MOTOR_ENB, speed);
}

void motorSurge(int speed = 200) {
  digitalWrite(PIN_MOTOR_IN1, HIGH); digitalWrite(PIN_MOTOR_IN2, LOW);
  digitalWrite(PIN_MOTOR_IN3, HIGH); digitalWrite(PIN_MOTOR_IN4, LOW);
  _setMotorSpeed(speed);
}

void motorRetreat(int speed = 200) {
  digitalWrite(PIN_MOTOR_IN1, LOW); digitalWrite(PIN_MOTOR_IN2, HIGH);
  digitalWrite(PIN_MOTOR_IN3, LOW); digitalWrite(PIN_MOTOR_IN4, HIGH);
  _setMotorSpeed(speed);
}

void motorLeft(int speed = 180) {
  digitalWrite(PIN_MOTOR_IN1, LOW); digitalWrite(PIN_MOTOR_IN2, HIGH);
  digitalWrite(PIN_MOTOR_IN3, HIGH); digitalWrite(PIN_MOTOR_IN4, LOW);
  _setMotorSpeed(speed);
}

void motorRight(int speed = 180) {
  digitalWrite(PIN_MOTOR_IN1, HIGH); digitalWrite(PIN_MOTOR_IN2, LOW);
  digitalWrite(PIN_MOTOR_IN3, LOW); digitalWrite(PIN_MOTOR_IN4, HIGH);
  _setMotorSpeed(speed);
}

void motorHalt() {
  digitalWrite(PIN_MOTOR_IN1, LOW); digitalWrite(PIN_MOTOR_IN2, LOW);
  digitalWrite(PIN_MOTOR_IN3, LOW); digitalWrite(PIN_MOTOR_IN4, LOW);
  _setMotorSpeed(0);
}
