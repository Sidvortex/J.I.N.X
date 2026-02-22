// ============================================================
//  LEDS.H — WS2812B ADDRESSABLE LED STRIP CONTROL
// ============================================================
#pragma once
#include <Adafruit_NeoPixel.h>
#include "config.h"

Adafruit_NeoPixel strip(NUM_LEDS, PIN_LED, NEO_GRB + NEO_KHZ800);

enum LEDEffect {
  LED_OFF, LED_NORMAL, LED_BOOT, LED_WAKE, LED_THREAT,
  LED_SCAN, LED_MUSIC, LED_ROAST, LED_ALERT, LED_PARTY,
  LED_BATTERY_LOW
};

LEDEffect currentLED = LED_NORMAL;
unsigned long lastLEDUpdate = 0;
int ledStep = 0;

void initLEDs() {
  strip.begin();
  strip.show();
  strip.setBrightness(180);
}

uint32_t colorFromName(String name) {
  name.toLowerCase();
  if (name == "red")    return strip.Color(255, 0, 0);
  if (name == "cyan")   return strip.Color(0, 255, 255);
  if (name == "green")  return strip.Color(0, 255, 100);
  if (name == "blue")   return strip.Color(0, 0, 255);
  if (name == "purple") return strip.Color(100, 0, 255);
  if (name == "yellow") return strip.Color(255, 200, 0);
  if (name == "orange") return strip.Color(255, 100, 0);
  if (name == "pink")   return strip.Color(255, 20, 100);
  return strip.Color(255, 255, 255);  // white default
}

void setLEDColor(String colorName) {
  uint32_t c = colorFromName(colorName);
  for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, c);
  strip.show();
  currentLED = LED_NORMAL;
}

void ledOff() {
  strip.clear(); strip.show();
  currentLED = LED_OFF;
}

void ledEffect(LEDEffect eff) { currentLED = eff; ledStep = 0; }

void updateLEDs() {
  if (millis() - lastLEDUpdate < 30) return;
  lastLEDUpdate = millis();
  ledStep++;

  switch (currentLED) {
    case LED_OFF: break;

    case LED_NORMAL:
      // Slow purple breathing
      { float b = (sin(ledStep * 0.05f) + 1.0f) * 0.5f;
        uint32_t c = strip.Color((int)(50*b), 0, (int)(180*b));
        for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, c);
        strip.show(); break; }

    case LED_BOOT:
      // Cyan wipe from center outward
      { int center = NUM_LEDS / 2;
        int progress = ledStep % (center + 5);
        strip.clear();
        if (progress < center) {
          strip.setPixelColor(center + progress, strip.Color(0, 255, 255));
          strip.setPixelColor(center - progress, strip.Color(0, 255, 255));
        }
        strip.show(); break; }

    case LED_WAKE:
      // Cyan flash
      { bool on = (ledStep % 10) < 5;
        for (int i = 0; i < NUM_LEDS; i++)
          strip.setPixelColor(i, on ? strip.Color(0, 200, 255) : 0);
        strip.show(); break; }

    case LED_THREAT:
      // Red fast strobe
      { bool on = (ledStep % 6) < 3;
        for (int i = 0; i < NUM_LEDS; i++)
          strip.setPixelColor(i, on ? strip.Color(255, 0, 0) : 0);
        strip.show(); break; }

    case LED_SCAN:
      // Cyan chase
      { int pos = ledStep % NUM_LEDS;
        strip.clear();
        for (int i = 0; i < 5; i++) {
          int p = (pos + i) % NUM_LEDS;
          strip.setPixelColor(p, strip.Color(0, (int)(255 * (i / 5.0f)), 255));
        }
        strip.show(); break; }

    case LED_MUSIC:
      // Rainbow rotate
      { for (int i = 0; i < NUM_LEDS; i++) {
          int hue = (int)((i * 65536L / NUM_LEDS) + (ledStep * 500)) % 65536;
          strip.setPixelColor(i, strip.ColorHSV(hue, 255, 200));
        }
        strip.show(); break; }

    case LED_ROAST:
      // Orange/yellow party flash
      { bool tog = (ledStep % 8) < 4;
        for (int i = 0; i < NUM_LEDS; i++) {
          strip.setPixelColor(i, (i % 2 == (tog ? 0 : 1)) ?
            strip.Color(255, 100, 0) : strip.Color(200, 200, 0));
        }
        strip.show(); break; }

    case LED_ALERT:
      // Red + white alternating
      { bool tog = (ledStep % 10) < 5;
        for (int i = 0; i < NUM_LEDS; i++) {
          if (i % 2 == 0) strip.setPixelColor(i, tog ? strip.Color(255,0,0) : 0);
          else            strip.setPixelColor(i, tog ? 0 : strip.Color(200,200,200));
        }
        strip.show(); break; }

    case LED_PARTY:
      // Full rainbow fast spin
      { for (int i = 0; i < NUM_LEDS; i++) {
          int hue = (int)((i * 65536L / NUM_LEDS) + (ledStep * 1500)) % 65536;
          strip.setPixelColor(i, strip.ColorHSV(hue, 255, 255));
        }
        strip.show(); break; }

    case LED_BATTERY_LOW:
      // Yellow slow pulse
      { float b = (sin(ledStep * 0.03f) + 1.0f) * 0.5f;
        for (int i = 0; i < NUM_LEDS; i++)
          strip.setPixelColor(i, strip.Color((int)(255*b), (int)(150*b), 0));
        strip.show(); break; }
  }
}


// ============================================================
//  SENSORS.H — ULTRASONIC + IR + VL53L0X ToF + BATTERY
// ============================================================
#pragma once
#include <Wire.h>
#include <VL53L0X.h>
#include "config.h"

VL53L0X tof1, tof2;  // Down-facing, Forward-facing

struct SensorData {
  float us1_cm, us2_cm;
  bool  ir_left, ir_right;
  int   tof_down_mm, tof_fwd_mm;
};

void initSensors() {
  // Ultrasonic
  pinMode(PIN_US1_TRIG, OUTPUT); pinMode(PIN_US1_ECHO, INPUT);
  pinMode(PIN_US2_TRIG, OUTPUT); pinMode(PIN_US2_ECHO, INPUT);

  // IR
  pinMode(PIN_IR_LEFT,  INPUT);
  pinMode(PIN_IR_RIGHT, INPUT);

  // VL53L0X — Init with different I2C addresses
  Wire.begin(PIN_SDA, PIN_SCL);

  // Disable both, enable one at a time to set address
  pinMode(PIN_TOF1_XSHUT, OUTPUT);
  pinMode(PIN_TOF2_XSHUT, OUTPUT);
  digitalWrite(PIN_TOF1_XSHUT, LOW);
  digitalWrite(PIN_TOF2_XSHUT, LOW);
  delay(10);

  // Init TOF1 (down-facing)
  digitalWrite(PIN_TOF1_XSHUT, HIGH);
  delay(10);
  tof1.init();
  tof1.setAddress(TOF1_ADDRESS);
  tof1.startContinuous();

  // Init TOF2 (forward-facing)
  digitalWrite(PIN_TOF2_XSHUT, HIGH);
  delay(10);
  tof2.init();
  tof2.setAddress(TOF2_ADDRESS);
  tof2.startContinuous();

  // Battery ADC
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);  // 0-3.9V range

  Serial.println("[SENSORS] Initialized");
}

float _readUltrasonic(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long dur = pulseIn(echoPin, HIGH, 30000);  // 30ms timeout
  return (dur == 0) ? 999.0f : dur * 0.0343f / 2.0f;
}

SensorData readSensors() {
  SensorData d;
  d.us1_cm    = _readUltrasonic(PIN_US1_TRIG, PIN_US1_ECHO);
  d.us2_cm    = _readUltrasonic(PIN_US2_TRIG, PIN_US2_ECHO);
  d.ir_left   = digitalRead(PIN_IR_LEFT) == LOW;   // Active LOW
  d.ir_right  = digitalRead(PIN_IR_RIGHT) == LOW;
  d.tof_down_mm = tof1.readRangeContinuousMillimeters();
  d.tof_fwd_mm  = tof2.readRangeContinuousMillimeters();
  return d;
}

float readBatteryVoltage() {
  int raw = analogRead(PIN_BATTERY_ADC);
  // 12-bit ADC, 3.9V full scale, times voltage divider ratio
  float adc_v  = (raw / 4095.0f) * 3.9f;
  float bat_v  = adc_v * 2.0f;  // Voltage divider (R1=R2=10k → ratio=2)
  return bat_v;
}

float batteryPercent(float voltage) {
  // 2S Li-ion: 8.4V = 100%, 6.0V = 0%
  float pct = (voltage - 6.0f) / (8.4f - 6.0f) * 100.0f;
  return constrain(pct, 0.0f, 100.0f);
}


// ============================================================
//  SERVOS.H — PAN/TILT HEAD SERVO CONTROL (SMOOTH)
// ============================================================
#pragma once
#include <ESP32Servo.h>
#include "config.h"

Servo servoPan, servoTilt;

int currentPan  = 90;
int currentTilt = 90;
int targetPan   = 90;
int targetTilt  = 90;
unsigned long lastServoUpdate = 0;
const int SERVO_STEP_MS = 15;  // Update interval
const int SERVO_STEP_DEG = 3;  // Degrees per step (smooth movement)

void initServos() {
  servoPan.attach(PIN_SERVO_PAN, 500, 2400);
  servoTilt.attach(PIN_SERVO_TILT, 500, 2400);
  servoPan.write(90);
  servoTilt.write(90);
  delay(500);
}

void setServoPan(int angle) {
  targetPan = constrain(angle, 45, 135);
}

void setServoTilt(int angle) {
  targetTilt = constrain(angle, 70, 110);
}

void centerServos() {
  targetPan  = 90;
  targetTilt = 90;
}

void updateServos() {
  if (millis() - lastServoUpdate < SERVO_STEP_MS) return;
  lastServoUpdate = millis();

  // Smooth interpolation
  if (currentPan < targetPan)       currentPan  = min(currentPan + SERVO_STEP_DEG, targetPan);
  else if (currentPan > targetPan)  currentPan  = max(currentPan - SERVO_STEP_DEG, targetPan);

  if (currentTilt < targetTilt)     currentTilt = min(currentTilt + SERVO_STEP_DEG, targetTilt);
  else if (currentTilt > targetTilt)currentTilt = max(currentTilt - SERVO_STEP_DEG, targetTilt);

  servoPan.write(currentPan);
  servoTilt.write(currentTilt);
}


// ============================================================
//  DFPLAYER.H — MP3 SOUND EFFECTS VIA DFPLAYER MINI
// ============================================================
#pragma once
#include <HardwareSerial.h>
#include <DFRobotDFPlayerMini.h>
#include "config.h"

HardwareSerial dfSerial(2);   // UART2: GPIO 16 (RX), 17 (TX)
DFRobotDFPlayerMini dfPlayer;
bool dfAvailable = false;

// Call this once in setup(), AFTER Serial.begin()
void initDFPlayer() {
  dfSerial.begin(9600, SERIAL_8N1, PIN_DFP_RX, PIN_DFP_TX);
  if (dfPlayer.begin(dfSerial)) {
    dfPlayer.volume(20);  // 0-30
    dfAvailable = true;
    Serial.println("[DFPlayer] Ready");
  } else {
    Serial.println("[DFPlayer] Not found — check wiring");
  }
}

void playSound(int track) {
  if (dfAvailable) dfPlayer.play(track);
}

void stopSound() {
  if (dfAvailable) dfPlayer.stop();
}

void setVolume(int vol) {
  if (dfAvailable) dfPlayer.volume(constrain(vol, 0, 30));
}
