#ifndef LED_H
#define LED_H

// ─── LED.h ────────────────────────────────────────────────────────────────
// WS2812B NeoPixel LED controller for JINX
// Pin: GPIO16  |  Count: 12 LEDs (ring around robot head)
// Uses: Adafruit NeoPixel library
//
// 11 Modes:
//   OFF, NORMAL, BOOT, SCAN, ALERT, THREAT,
//   MUSIC, PARTY, RAINBOW, BATTERY_LOW, COLOR
//
// Non-blocking — all animations use millis() timing.
// Call ledTick() in your main loop() every iteration.
// ─────────────────────────────────────────────────────────────────────────

#include <Adafruit_NeoPixel.h>

// ── Configuration ─────────────────────────────────────────────────────────
#define LED_PIN        16
#define LED_COUNT      12
#define LED_BRIGHTNESS 200    // 0–255 default brightness

// ── LED effect names ───────────────────────────────────────────────────────
#define LED_OFF         0
#define LED_NORMAL      1
#define LED_BOOT        2
#define LED_SCAN        3
#define LED_ALERT       4
#define LED_THREAT      5
#define LED_MUSIC       6
#define LED_PARTY       7
#define LED_RAINBOW     8
#define LED_BATTERY_LOW 9
#define LED_COLOR       10   // solid custom color

// ── Pixel object ──────────────────────────────────────────────────────────
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// ── Internal state ────────────────────────────────────────────────────────
static uint8_t  _ledMode        = LED_OFF;
static uint32_t _ledColor       = 0x00F5FF;  // default cyan
static uint8_t  _ledBrightness  = LED_BRIGHTNESS;
static uint32_t _ledLastMs      = 0;
static uint8_t  _ledStep        = 0;
static bool     _ledAlertState  = false;
static uint16_t _rainbowHue     = 0;

// ── Color helpers ──────────────────────────────────────────────────────────
#define C_CYAN    strip.Color(0,   245, 255)
#define C_GREEN   strip.Color(0,   255, 136)
#define C_RED     strip.Color(255, 0,   0)
#define C_ORANGE  strip.Color(255, 100, 0)
#define C_BLUE    strip.Color(0,   100, 255)
#define C_PURPLE  strip.Color(170, 0,   255)
#define C_WHITE   strip.Color(255, 255, 255)
#define C_YELLOW  strip.Color(255, 220, 0)
#define C_OFF     strip.Color(0,   0,   0)

// ── Scale color brightness ─────────────────────────────────────────────────
uint32_t scaleColor(uint32_t color, uint8_t scale) {
  uint8_t r = (uint8_t)((color >> 16) & 0xFF);
  uint8_t g = (uint8_t)((color >> 8)  & 0xFF);
  uint8_t b = (uint8_t)((color)       & 0xFF);
  r = (r * scale) / 255;
  g = (g * scale) / 255;
  b = (b * scale) / 255;
  return strip.Color(r, g, b);
}

// ── Set all pixels to one color ────────────────────────────────────────────
void ledFill(uint32_t color) {
  for (int i = 0; i < LED_COUNT; i++) strip.setPixelColor(i, color);
  strip.show();
}

// ── Init ──────────────────────────────────────────────────────────────────
void ledInit() {
  strip.begin();
  strip.setBrightness(_ledBrightness);
  ledFill(C_OFF);
  _ledMode = LED_OFF;
}

// ── Set mode (call from MQTT callback) ────────────────────────────────────
void ledSetMode(uint8_t mode) {
  _ledMode  = mode;
  _ledStep  = 0;
  _ledLastMs = 0;
  if (mode == LED_OFF) ledFill(C_OFF);
}

void ledSetBrightness(uint8_t b) {
  _ledBrightness = b;
  strip.setBrightness(b);
}

// Set a custom solid color by R,G,B
void ledSetColor(uint8_t r, uint8_t g, uint8_t b) {
  _ledColor = strip.Color(r, g, b);
  _ledMode  = LED_COLOR;
  ledFill(_ledColor);
}

// Set color by name (from MQTT payload)
void ledSetColorByName(String name) {
  name.toLowerCase();
  if      (name == "red")    ledSetColor(255, 0,   0);
  else if (name == "green")  ledSetColor(0,   255, 0);
  else if (name == "blue")   ledSetColor(0,   0,   255);
  else if (name == "cyan")   ledSetColor(0,   245, 255);
  else if (name == "yellow") ledSetColor(255, 220, 0);
  else if (name == "orange") ledSetColor(255, 100, 0);
  else if (name == "purple") ledSetColor(170, 0,   255);
  else if (name == "pink")   ledSetColor(255, 0,   255);
  else if (name == "white")  ledSetColor(255, 255, 255);
  else                       ledSetColor(0,   245, 255);  // default cyan
}

// Set mode by MQTT string (called from mqttCallback)
void ledSetByString(String pattern) {
  pattern.toLowerCase();
  if      (pattern == "off")         ledSetMode(LED_OFF);
  else if (pattern == "normal")      ledSetMode(LED_NORMAL);
  else if (pattern == "boot")        ledSetMode(LED_BOOT);
  else if (pattern == "scan")        ledSetMode(LED_SCAN);
  else if (pattern == "alert")       ledSetMode(LED_ALERT);
  else if (pattern == "threat")      ledSetMode(LED_THREAT);
  else if (pattern == "music")       ledSetMode(LED_MUSIC);
  else if (pattern == "party")       ledSetMode(LED_PARTY);
  else if (pattern == "rainbow")     ledSetMode(LED_RAINBOW);
  else if (pattern == "battery_low") ledSetMode(LED_BATTERY_LOW);
  else if (pattern.startsWith("color:")) {
    String colorName = pattern.substring(6);
    ledSetColorByName(colorName);
  }
}

// ─────────────────────────────────────────────────────────────────────────
// ledTick() — CALL THIS EVERY loop() ITERATION
// All animations are non-blocking (millis-based).
// ─────────────────────────────────────────────────────────────────────────
void ledTick() {
  uint32_t now = millis();

  switch (_ledMode) {

    // ── OFF ──────────────────────────────────────────────────────────────
    case LED_OFF:
      // Nothing — already cleared on mode set
      break;

    // ── NORMAL — slow gentle cyan breathe ────────────────────────────────
    case LED_NORMAL:
      if (now - _ledLastMs >= 20) {
        _ledLastMs = now;
        // Sine-wave breathing: step 0→255→0 over ~5 seconds
        float angle = (_ledStep / 255.0f) * 2.0f * PI;
        uint8_t bright = (uint8_t)(128 + 127 * sin(angle));
        uint32_t col = scaleColor(C_CYAN, bright);
        ledFill(col);
        _ledStep++;
      }
      break;

    // ── BOOT — fill up LEDs one by one, then hold ─────────────────────────
    case LED_BOOT:
      if (now - _ledLastMs >= 80) {
        _ledLastMs = now;
        if (_ledStep < LED_COUNT) {
          strip.setPixelColor(_ledStep, C_CYAN);
          strip.show();
          _ledStep++;
        }
        // Once filled, switch to NORMAL
        if (_ledStep >= LED_COUNT) {
          _ledMode = LED_NORMAL;
          _ledStep = 0;
        }
      }
      break;

    // ── SCAN — single cyan pixel chasing the ring ─────────────────────────
    case LED_SCAN:
      if (now - _ledLastMs >= 50) {
        _ledLastMs = now;
        ledFill(C_OFF);
        // Bright head pixel + fading tail
        for (int i = 0; i < 4; i++) {
          int idx = (_ledStep - i + LED_COUNT) % LED_COUNT;
          uint8_t bright = 255 - (i * 60);
          strip.setPixelColor(idx, scaleColor(C_CYAN, bright));
        }
        strip.show();
        _ledStep = (_ledStep + 1) % LED_COUNT;
      }
      break;

    // ── ALERT — fast red/off strobe ───────────────────────────────────────
    case LED_ALERT:
      if (now - _ledLastMs >= 150) {
        _ledLastMs = now;
        _ledAlertState = !_ledAlertState;
        ledFill(_ledAlertState ? C_RED : C_OFF);
      }
      break;

    // ── THREAT — red pulse (slower than alert, more eerie) ───────────────
    case LED_THREAT:
      if (now - _ledLastMs >= 20) {
        _ledLastMs = now;
        float angle = (_ledStep / 128.0f) * PI;
        uint8_t bright = (uint8_t)(255 * sin(angle));
        ledFill(scaleColor(C_RED, bright));
        _ledStep = (_ledStep + 2) % 128;
      }
      break;

    // ── MUSIC — bouncing purple pixels synced to beat feel ────────────────
    case LED_MUSIC:
      if (now - _ledLastMs >= 60) {
        _ledLastMs = now;
        ledFill(C_OFF);
        // Two "beats" running opposite directions
        int p1 = _ledStep % LED_COUNT;
        int p2 = (LED_COUNT - 1) - ((_ledStep + LED_COUNT/2) % LED_COUNT);
        strip.setPixelColor(p1, C_PURPLE);
        strip.setPixelColor(p2, scaleColor(C_PURPLE, 120));
        // Neighbor glow
        strip.setPixelColor((p1+1) % LED_COUNT, scaleColor(C_PURPLE, 60));
        strip.setPixelColor((p1-1+LED_COUNT) % LED_COUNT, scaleColor(C_PURPLE, 60));
        strip.show();
        _ledStep++;
      }
      break;

    // ── PARTY — random color splashes ────────────────────────────────────
    case LED_PARTY:
      if (now - _ledLastMs >= 80) {
        _ledLastMs = now;
        for (int i = 0; i < LED_COUNT; i++) {
          uint8_t r = random(0, 256);
          uint8_t g = random(0, 256);
          uint8_t b = random(0, 256);
          strip.setPixelColor(i, strip.Color(r, g, b));
        }
        strip.show();
      }
      break;

    // ── RAINBOW — smooth hue rotation around ring ─────────────────────────
    case LED_RAINBOW:
      if (now - _ledLastMs >= 15) {
        _ledLastMs = now;
        for (int i = 0; i < LED_COUNT; i++) {
          uint16_t hue = _rainbowHue + (i * 65536L / LED_COUNT);
          strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(hue)));
        }
        strip.show();
        _rainbowHue += 256;   // speed of rotation
      }
      break;

    // ── BATTERY LOW — slow orange pulse ───────────────────────────────────
    case LED_BATTERY_LOW:
      if (now - _ledLastMs >= 25) {
        _ledLastMs = now;
        float angle = (_ledStep / 100.0f) * PI;
        uint8_t bright = (uint8_t)(255 * sin(angle));
        ledFill(scaleColor(C_ORANGE, bright));
        _ledStep = (_ledStep + 1) % 100;
      }
      break;

    // ── COLOR — solid custom color, no animation ──────────────────────────
    case LED_COLOR:
      // Already set in ledSetColor(), nothing to update
      break;
  }
}

// ── Convenience: flash white once (for acknowledgement) ───────────────────
void ledFlashAck() {
  uint8_t savedMode = _ledMode;
  ledFill(C_WHITE);
  delay(80);
  ledFill(C_OFF);
  delay(40);
  ledFill(C_WHITE);
  delay(80);
  ledSetMode(savedMode);
}

// ── Boot sequence shortcut ────────────────────────────────────────────────
void ledBoot() {
  ledSetMode(LED_BOOT);
}

#endif // LED_H
