// ============================================================
//  EYES.H — TFT ANIMATED EYE STATES
//  11 emotional states rendered on 2.4" ILI9341 TFT display
// ============================================================
#pragma once
#include <TFT_eSPI.h>
#include "config.h"

TFT_eSPI tft = TFT_eSPI();

// Eye state enum
enum EyeState {
  EYE_NEUTRAL, EYE_HAPPY, EYE_ANGRY, EYE_SLEEPY, EYE_LOVE,
  EYE_SCANNING, EYE_THREAT, EYE_ROAST, EYE_MUSIC,
  EYE_THINKING, EYE_TALKING, EYE_BOOT
};

// Colors
#define TFT_NEON_CYAN   0x07FF
#define TFT_NEON_GREEN  0x07E0
#define TFT_NEON_RED    0xF800
#define TFT_NEON_PURPLE 0x780F
#define TFT_NEON_YELLOW 0xFFE0
#define TFT_NEON_ORANGE 0xFC60
#define TFT_BG          TFT_BLACK

EyeState currentEye = EYE_NEUTRAL;
float    pupilX = 0.5f, pupilY = 0.5f;   // Normalized pupil position
int      scanAngle = 0;   // For scanning animation
bool     blinkState = false;
unsigned long lastBlink = 0;
unsigned long lastAnim  = 0;

void initEyes() {
  tft.init();
  tft.setRotation(1);   // Landscape
  tft.fillScreen(TFT_BG);
  tft.setTextColor(TFT_NEON_CYAN, TFT_BG);
  tft.setTextSize(2);
  tft.setCursor(50, 100);
  tft.print("INITIALIZING...");
  delay(1000);
}

void _drawEyePupil(int cx, int cy, int r, uint16_t color, float nx, float ny) {
  // Pupil offset based on gaze direction
  int px = cx + (int)((nx - 0.5f) * r * 0.6f);
  int py = cy + (int)((ny - 0.5f) * r * 0.6f);
  // Iris
  tft.fillCircle(cx, cy, r, color);
  tft.drawCircle(cx, cy, r, TFT_WHITE);
  // Pupil
  tft.fillCircle(px, py, r / 3, TFT_BLACK);
  // Highlight
  tft.fillCircle(px - r/5, py - r/5, r/7, TFT_WHITE);
}

void drawEyeNeutral() {
  tft.fillScreen(TFT_BG);
  // Left eye
  _drawEyePupil(80, 120, 45, TFT_NEON_CYAN, pupilX, pupilY);
  // Right eye
  _drawEyePupil(240, 120, 45, TFT_NEON_CYAN, pupilX, pupilY);
}

void drawEyeHappy() {
  tft.fillScreen(TFT_BG);
  // Upward arched eyes (^-^)
  for (int i = -45; i <= 45; i++) {
    float rad = i * 0.0174f;
    int lx = 80 + (int)(45 * sin(rad));
    int ly = 120 - (int)(45 * abs(cos(rad))) + 15;
    tft.fillCircle(lx, ly, 4, TFT_NEON_GREEN);

    int rx = 240 + (int)(45 * sin(rad));
    int ry = 120 - (int)(45 * abs(cos(rad))) + 15;
    tft.fillCircle(rx, ry, 4, TFT_NEON_GREEN);
  }
}

void drawEyeAngry() {
  tft.fillScreen(TFT_BG);
  // Red eyes with angry eyebrows
  _drawEyePupil(80, 120, 40, TFT_NEON_RED, 0.5f, 0.6f);
  _drawEyePupil(240, 120, 40, TFT_NEON_RED, 0.5f, 0.6f);
  // Angry brows (diagonal lines)
  tft.drawLine(40, 60, 120, 80, TFT_NEON_RED);
  tft.drawLine(41, 60, 121, 80, TFT_NEON_RED);
  tft.drawLine(200, 80, 280, 60, TFT_NEON_RED);
  tft.drawLine(200, 81, 280, 61, TFT_NEON_RED);
}

void drawEyeSleepy() {
  tft.fillScreen(TFT_BG);
  // Half-closed eyes
  _drawEyePupil(80, 130, 40, TFT_NEON_CYAN, 0.5f, 0.7f);
  _drawEyePupil(240, 130, 40, TFT_NEON_CYAN, 0.5f, 0.7f);
  // Heavy eyelids (cover top half)
  tft.fillRect(35, 80, 90, 55, TFT_BG);
  tft.fillRect(195, 80, 90, 55, TFT_BG);
  // Zzz text
  tft.setTextColor(TFT_NEON_CYAN, TFT_BG);
  tft.setTextSize(1);
  tft.setCursor(150, 50);
  tft.print("z z z");
}

void drawEyeScanning() {
  tft.fillScreen(TFT_BG);
  // Scanning animation — rotating arc
  for (int i = 0; i < 360; i += 10) {
    float rad = (i + scanAngle) * 0.0174f;
    int x = 160 + (int)(100 * cos(rad));
    int y = 120 + (int)(100 * sin(rad));
    uint16_t brightness = (i < 180) ? TFT_NEON_CYAN : TFT_NEON_GREEN;
    tft.drawPixel(x, y, brightness);
  }
  // Center reticle
  tft.drawCircle(160, 120, 10, TFT_NEON_CYAN);
  tft.drawLine(150, 120, 170, 120, TFT_NEON_GREEN);
  tft.drawLine(160, 110, 160, 130, TFT_NEON_GREEN);
  // Text
  tft.setTextColor(TFT_NEON_GREEN, TFT_BG);
  tft.setTextSize(1);
  tft.setCursor(100, 200);
  tft.print("SCANNING...");
  scanAngle = (scanAngle + 5) % 360;
}

void drawEyeThreat() {
  tft.fillScreen(TFT_BG);
  // Red alert eyes
  _drawEyePupil(80, 120, 45, TFT_NEON_RED, pupilX, pupilY);
  _drawEyePupil(240, 120, 45, TFT_NEON_RED, pupilX, pupilY);
  // Alert border
  tft.drawRect(0, 0, 320, 240, TFT_NEON_RED);
  tft.drawRect(2, 2, 316, 236, TFT_NEON_RED);
  tft.setTextColor(TFT_NEON_RED, TFT_BG);
  tft.setTextSize(1);
  tft.setCursor(105, 205);
  tft.print("[ THREAT ]");
}

void drawEyeRoast() {
  tft.fillScreen(TFT_BG);
  // Smug eyes (one raised "eyebrow")
  _drawEyePupil(80, 120, 40, TFT_NEON_ORANGE, 0.6f, 0.5f);
  _drawEyePupil(240, 120, 45, TFT_NEON_ORANGE, 0.6f, 0.5f);
  // Smirk line
  tft.drawLine(120, 190, 200, 185, TFT_NEON_ORANGE);
  tft.drawLine(200, 185, 210, 175, TFT_NEON_ORANGE);
  tft.setTextColor(TFT_NEON_ORANGE, TFT_BG);
  tft.setTextSize(1);
  tft.setCursor(100, 205);
  tft.print("ROAST MODE");
}

void drawEyeMusic() {
  tft.fillScreen(TFT_BG);
  // Musical notes bouncing
  _drawEyePupil(80, 120, 40, TFT_NEON_PURPLE, pupilX, pupilY);
  _drawEyePupil(240, 120, 40, TFT_NEON_PURPLE, pupilX, pupilY);
  tft.setTextColor(TFT_NEON_PURPLE, TFT_BG);
  tft.setTextSize(2);
  int noteX = 130 + (int)(20 * sin(millis() / 300.0f));
  tft.setCursor(noteX, 190);
  tft.print("^");
  tft.setCursor(noteX + 40, 195);
  tft.print("~");
}

void drawEyeThinking() {
  tft.fillScreen(TFT_BG);
  // One eye looking up-right
  _drawEyePupil(80, 120, 40, TFT_NEON_CYAN, 0.7f, 0.3f);
  _drawEyePupil(240, 120, 40, TFT_NEON_CYAN, 0.7f, 0.3f);
  // Thinking dots
  tft.setTextColor(TFT_NEON_CYAN, TFT_BG);
  tft.setTextSize(2);
  int dotCount = (millis() / 500) % 4;
  String dots = "";
  for (int i = 0; i < dotCount; i++) dots += ".";
  tft.setCursor(130, 200);
  tft.print(dots + "   ");
}

void drawEyeTalking() {
  tft.fillScreen(TFT_BG);
  _drawEyePupil(80, 120, 40, TFT_NEON_CYAN, pupilX, pupilY);
  _drawEyePupil(240, 120, 40, TFT_NEON_CYAN, pupilX, pupilY);
  // Animated mouth
  int mouthW = 40 + (int)(20 * sin(millis() / 150.0f));
  int mouthH = 5 + (int)(8 * abs(sin(millis() / 150.0f)));
  tft.fillRoundRect(160 - mouthW/2, 190, mouthW, mouthH, 3, TFT_NEON_CYAN);
}

void drawEyeBoot() {
  tft.fillScreen(TFT_BG);
  // Boot sequence: loading bar
  tft.setTextColor(TFT_NEON_CYAN, TFT_BG);
  tft.setTextSize(1);
  tft.setCursor(70, 80);
  tft.print("DESKBOT INITIALIZING");
  int progress = (millis() / 30) % 101;
  tft.fillRect(60, 110, (int)(2 * progress), 10, TFT_NEON_CYAN);
  tft.drawRect(60, 110, 200, 10, TFT_NEON_CYAN);
  tft.setCursor(145, 130);
  tft.print(String(progress) + "%");
}

void drawEyeLove() {
  tft.fillScreen(TFT_BG);
  // Heart-shaped eyes
  // Simple heart approximation
  for (int x = -20; x <= 20; x++) {
    for (int y = -20; y <= 20; y++) {
      if ((x*x + y*y - 400) * (x*x + y*y - 400) - 4*x*x * y*y * y < 0) {
        tft.drawPixel(80 + x, 120 + y, TFT_NEON_RED);
        tft.drawPixel(240 + x, 120 + y, TFT_NEON_RED);
      }
    }
  }
}

// Auto-blink
void autoUpdate() {
  unsigned long now = millis();
  if (now - lastBlink > 3000 + random(2000)) {
    lastBlink = now;
    // Quick blink
    tft.fillRect(35, 90, 90, 70, TFT_BG);
    tft.fillRect(195, 90, 90, 70, TFT_BG);
    delay(80);
    setEyeState(currentEye);
  }
}

void movePupils(float nx, float ny) {
  pupilX = nx;
  pupilY = ny;
  // Redraw if neutral/happy to update pupil position
  if (currentEye == EYE_NEUTRAL || currentEye == EYE_THREAT) {
    setEyeState(currentEye);
  }
}

void setEyeState(EyeState state) {
  currentEye = state;
  switch (state) {
    case EYE_NEUTRAL:  drawEyeNeutral();  break;
    case EYE_HAPPY:    drawEyeHappy();    break;
    case EYE_ANGRY:    drawEyeAngry();    break;
    case EYE_SLEEPY:   drawEyeSleepy();   break;
    case EYE_LOVE:     drawEyeLove();     break;
    case EYE_SCANNING: drawEyeScanning(); break;
    case EYE_THREAT:   drawEyeThreat();   break;
    case EYE_ROAST:    drawEyeRoast();    break;
    case EYE_MUSIC:    drawEyeMusic();    break;
    case EYE_THINKING: drawEyeThinking(); break;
    case EYE_TALKING:  drawEyeTalking();  break;
    case EYE_BOOT:     drawEyeBoot();     break;
  }
}
