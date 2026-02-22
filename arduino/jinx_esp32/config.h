// ============================================================
//  CONFIG.H — PIN DEFINITIONS + WIFI + MQTT
// ============================================================
#pragma once
#include <Arduino.h>

// ── WiFi ──────────────────────────────────────────────────────
#define WIFI_SSID    "YOUR_WIFI_SSID"
#define WIFI_PASS    "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER  "192.168.1.100"   // Your laptop IP
#define MQTT_PORT    1883

// ── MQTT Topics ────────────────────────────────────────────────
#define TOPIC_EYES         "jinx/eyes"
#define TOPIC_HEAD_TRACK   "jinx/head_track"
#define TOPIC_EYE_TRACK    "jinx/eye_track"
#define TOPIC_MOTOR        "jinx/motor"
#define TOPIC_LED          "jinx/led"
#define TOPIC_SOUND        "jinx/sound"
#define TOPIC_BUZZER       "jinx/buzzer"
#define TOPIC_SENSORS      "jinx/sensors"
#define TOPIC_BATTERY      "jinx/battery"
#define TOPIC_STATUS       "jinx/status"
#define TOPIC_MODE         "jinx/mode"
#define TOPIC_COMMAND      "jinx/command"

// ── TFT Display (ILI9341) ──────────────────────────────────────
#define PIN_TFT_CS    15
#define PIN_TFT_DC     2
#define PIN_TFT_RST    4
#define PIN_TFT_MOSI  23
#define PIN_TFT_SCLK  18

// ── Servos ────────────────────────────────────────────────────
#define PIN_SERVO_PAN  19
#define PIN_SERVO_TILT 11   // Changed from 22 to avoid I2C conflict

// ── Motors (L298N) ─────────────────────────────────────────────
#define PIN_MOTOR_IN1  25
#define PIN_MOTOR_IN2  26
#define PIN_MOTOR_IN3  27
#define PIN_MOTOR_IN4  14
#define PIN_MOTOR_ENA  32
#define PIN_MOTOR_ENB  33

// ── Ultrasonic Sensors ─────────────────────────────────────────
#define PIN_US1_TRIG   5
#define PIN_US1_ECHO  34
#define PIN_US2_TRIG   0
#define PIN_US2_ECHO  35

// ── IR Sensors (table edge detection) ─────────────────────────
#define PIN_IR_LEFT   36
#define PIN_IR_RIGHT  39

// ── VL53L0X ToF Sensors (I2C) ──────────────────────────────────
#define PIN_SDA       21
#define PIN_SCL       22
#define PIN_TOF1_XSHUT 13   // Down-facing sensor (table edge)
#define PIN_TOF2_XSHUT 12   // Forward-facing sensor (obstacle)
#define TOF1_ADDRESS  0x30  // Custom I2C address for sensor 1
#define TOF2_ADDRESS  0x31  // Custom I2C address for sensor 2

// ── LED Strip (WS2812B) ─────────────────────────────────────────
#define PIN_LED        13   // NOTE: Same as TOF1_XSHUT—adjust if conflict
#define NUM_LEDS       30

// !! WARNING: If PIN_LED conflicts with PIN_TOF1_XSHUT (both GPIO 13),
//    change PIN_LED to another free GPIO like GPIO 15 (after freeing from TFT)
//    or use GPIO 3 (not recommended) or choose differently.
//    Better: PIN_LED = GPIO 16 (free if DFPlayer moved to SW serial)
// For this build: use GPIO 16 for LED data, GPIO 17/18 for DFPlayer

// ── DFPlayer Mini ─────────────────────────────────────────────
#define PIN_DFP_TX    17
#define PIN_DFP_RX    16

// ── Buzzer ─────────────────────────────────────────────────────
#define PIN_BUZZER    12

// ── Battery Monitor ────────────────────────────────────────────
#define PIN_BATTERY_ADC  34  // Shares with US1_ECHO — use separate ADC pin
// Better: use GPIO 35 or 32 for ADC if 34 is taken by ultrasonic
// Adjust in your actual wiring!

// ── Sound IDs (DFPlayer SD card tracks) ───────────────────────
#define SOUND_BOOT      1
#define SOUND_ALERT     2
#define SOUND_HAPPY     3
#define SOUND_THREAT    4
#define SOUND_SLEEPY    5
#define SOUND_AMBIENT   6
#define SOUND_WAKE      7
#define SOUND_ROAST     8
