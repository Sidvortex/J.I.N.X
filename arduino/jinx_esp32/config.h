#ifndef CONFIG_H
#define CONFIG_H

// ═══════════════════════════════════════════════════════════════════════════
//  config.h — JINX ESP32 Central Configuration
//  Edit this file only. All other headers read from here.
// ═══════════════════════════════════════════════════════════════════════════

// ── WiFi ──────────────────────────────────────────────────────────────────
#define WIFI_SSID        "YourWiFiName"
#define WIFI_PASSWORD    "YourWiFiPassword"

// ── MQTT Broker (your laptop's IP on the LAN) ─────────────────────────────
#define MQTT_BROKER      "192.168.1.100"
#define MQTT_PORT        1883
#define MQTT_CLIENT_ID   "JINX_ESP32"
#define MQTT_USER        ""          // leave blank if no auth
#define MQTT_PASS        ""

// ── MQTT Topics ───────────────────────────────────────────────────────────
#define TOPIC_EYES        "jinx/eyes"
#define TOPIC_HEAD_TRACK  "jinx/head_track"
#define TOPIC_EYE_TRACK   "jinx/eye_track"
#define TOPIC_MOTOR       "jinx/motor"
#define TOPIC_LED         "jinx/led"
#define TOPIC_SOUND       "jinx/sound"
#define TOPIC_SENSORS     "jinx/sensors"
#define TOPIC_BATTERY     "jinx/battery"
#define TOPIC_ALERTS      "jinx/alerts"
#define TOPIC_MODE        "jinx/mode"
#define TOPIC_COMMAND     "jinx/command"
#define TOPIC_STATUS      "jinx/status"

// ── TFT Display (ILI9341) SPI ─────────────────────────────────────────────
#define TFT_CS    15
#define TFT_DC    2
#define TFT_RST   4
#define TFT_MOSI  23
#define TFT_CLK   18
#define TFT_MISO  19    // not used for display but needed by SPI bus

// ── Servos ────────────────────────────────────────────────────────────────
#define SERVO_PAN_PIN    13    // horizontal (left/right)
#define SERVO_TILT_PIN   12    // vertical   (up/down)

#define PAN_MIN          60    // degrees
#define PAN_MAX          120
#define PAN_CENTER       90

#define TILT_MIN         70
#define TILT_MAX         110
#define TILT_CENTER      90

#define SERVO_STEP       3     // degrees per move
#define SERVO_INTERVAL   15    // ms between steps (smoothing)

// ── L298N Motor Driver ────────────────────────────────────────────────────
#define MOTOR_IN1  25
#define MOTOR_IN2  26
#define MOTOR_IN3  27
#define MOTOR_IN4  14
#define MOTOR_ENA  32    // PWM channel A
#define MOTOR_ENB  33    // PWM channel B

#define MOTOR_DEFAULT_SPEED  180   // 0–255
#define MOTOR_PWM_FREQ       1000
#define MOTOR_PWM_RES        8     // bits

// ── WS2812B NeoPixel ─────────────────────────────────────────────────────
#define LED_PIN_NUM      16
#define LED_NUM_PIXELS   12
#define LED_DEFAULT_BRIGHT 200

// ── VL53L0X ToF Sensors (I2C) ─────────────────────────────────────────────
#define I2C_SDA          21
#define I2C_SCL          22

#define TOF_DOWN_XSHUT   5     // GPIO to XSHUT of downward sensor
#define TOF_FWD_XSHUT    17    // GPIO to XSHUT of forward sensor

#define TOF_DOWN_ADDR    0x30  // custom I2C address after init
#define TOF_FWD_ADDR     0x31

// Edge detection threshold: if downward sensor reads > this → edge/drop
#define EDGE_THRESHOLD_MM   80
// Forward obstacle: if forward sensor reads < this → too close
#define OBSTACLE_THRESHOLD_MM 150

// ── HC-SR04 Ultrasonic Sensors ────────────────────────────────────────────
#define HCSR04_1_TRIG    5
#define HCSR04_1_ECHO    34
#define HCSR04_2_TRIG    0
#define HCSR04_2_ECHO    35

#define ULTRASONIC_STOP_CM  20   // stop motors if obstacle within this distance

// ── IR Sensors ────────────────────────────────────────────────────────────
#define IR_LEFT_PIN      36
#define IR_RIGHT_PIN     39

// ── DFPlayer Mini (UART) ──────────────────────────────────────────────────
#define DFPLAYER_RX      16    // ESP32 RX ← DFPlayer TX
#define DFPLAYER_TX      17    // ESP32 TX → DFPlayer RX
// Note: LED_PIN_NUM is also 16 — if using DFPlayer, move LED to another pin
// Recommended: move LED to GPIO 4 and update LED_PIN_NUM to 4

// ── Buzzer ────────────────────────────────────────────────────────────────
#define BUZZER_PIN       12    // shares with SERVO_TILT — use only if no tilt servo
// Better: use GPIO 4 for buzzer if TFT_RST is freed up

// ── Battery ADC ───────────────────────────────────────────────────────────
#define BATTERY_PIN      35    // voltage divider: 10k+10k → GPIO35
#define BATTERY_FULL_V   8.4f
#define BATTERY_EMPTY_V  6.0f
#define BATTERY_WARN_PCT 20    // send warning below this %
#define BATTERY_CRIT_PCT 10    // trigger battery_low LED below this %

// ── Timing Intervals (ms) ─────────────────────────────────────────────────
#define SENSOR_INTERVAL    100    // read all sensors every 100ms
#define BATTERY_INTERVAL  5000    // read battery every 5s
#define MQTT_RECONNECT_MS 3000    // retry MQTT connection every 3s
#define WIFI_RECONNECT_MS 5000    // retry WiFi every 5s

// ── MQTT Buffer ────────────────────────────────────────────────────────────
#define MQTT_BUFFER_SIZE  4096    // increase from default 256

// ── Debug Serial ──────────────────────────────────────────────────────────
#define DEBUG_SERIAL      1       // set to 0 to disable Serial.print
#if DEBUG_SERIAL
  #define DBG(x)    Serial.print(x)
  #define DBGLN(x)  Serial.println(x)
  #define DBGF(...) Serial.printf(__VA_ARGS__)
#else
  #define DBG(x)
  #define DBGLN(x)
  #define DBGF(...)
#endif

#endif // CONFIG_H
