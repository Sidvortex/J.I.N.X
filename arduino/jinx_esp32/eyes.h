#ifndef EYES_H
#define EYES_H

// ═══════════════════════════════════════════════════════════════════════════
//  eyes.h — ILI9341 TFT Animated Eye Display (240×320)
//
//  12 eye states matching the Android EyesView exactly:
//    NEUTRAL, HAPPY, ANGRY, SLEEPY, SCANNING, THREAT,
//    ROAST, MUSIC, TALKING, THINKING, BOOT, LOVE
//
//  Features:
//    • Pupil tracking via normalized (x,y) from OPTIC
//    • Auto-blink every ~4 seconds
//    • All drawing uses Adafruit GFX — no images needed
//    • eyeTick() is non-blocking (millis-based)
// ═══════════════════════════════════════════════════════════════════════════

#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include "config.h"

// ── TFT Object ────────────────────────────────────────────────────────────
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

// ── Color palette ─────────────────────────────────────────────────────────
#define COL_BG       0x0000   // Black
#define COL_CYAN     0x07FF   // #00F5FF approx
#define COL_GREEN    0x07E0   // #00FF00
#define COL_RED      0xF800
#define COL_ORANGE   0xFD20   // #FF8800 approx
#define COL_PURPLE   0x801F   // #880088 approx
#define COL_WHITE    0xFFFF
#define COL_YELLOW   0xFFE0
#define COL_DKGRAY   0x2104
#define COL_LTGRAY   0x8410

// ── Eye state enum ────────────────────────────────────────────────────────
enum EyeStateESP {
  EYE_NEUTRAL  = 0,
  EYE_HAPPY    = 1,
  EYE_ANGRY    = 2,
  EYE_SLEEPY   = 3,
  EYE_SCANNING = 4,
  EYE_THREAT   = 5,
  EYE_ROAST    = 6,
  EYE_MUSIC    = 7,
  EYE_TALKING  = 8,
  EYE_THINKING = 9,
  EYE_BOOT     = 10,
  EYE_LOVE     = 11
};

// ── Display constants (240×320) ────────────────────────────────────────────
#define TFT_W    240
#define TFT_H    320

// Eye positions (two eyes side by side)
#define EYE_L_CX   75    // left eye center X
#define EYE_R_CX  165    // right eye center X
#define EYE_CY    160    // eye center Y
#define EYE_RX     48    // eye horizontal radius
#define EYE_RY     55    // eye vertical radius
#define PUPIL_R    18    // pupil radius
#define GLINT_R     6    // white glint radius

// ── Internal state ────────────────────────────────────────────────────────
static EyeStateESP _eyeState    = EYE_NEUTRAL;
static EyeStateESP _lastDrawn   = (EyeStateESP)255;
static float       _pupilNx     = 0.5f;
static float       _pupilNy     = 0.5f;
static bool        _blinkState  = false;
static uint32_t    _blinkLastMs = 0;
static uint32_t    _animLastMs  = 0;
static uint8_t     _animStep    = 0;
static uint16_t    _scanAngle   = 0;
static bool        _needRedraw  = true;
static uint8_t     _bootPct     = 0;

// ── Init ──────────────────────────────────────────────────────────────────
void initEyes() {
  tft.begin();
  tft.setRotation(2);    // portrait, USB at bottom
  tft.fillScreen(COL_BG);
  _eyeState  = EYE_BOOT;
  _needRedraw = true;
  DBGLN("[EYES] TFT initialized");
}

// ── Set state ─────────────────────────────────────────────────────────────
void eyeSetState(EyeStateESP state) {
  if (_eyeState == state) return;
  _eyeState   = state;
  _animStep   = 0;
  _needRedraw = true;
  tft.fillScreen(COL_BG);
}

void eyeSetStateByName(String name) {
  name.toLowerCase();
  if      (name == "neutral")  eyeSetState(EYE_NEUTRAL);
  else if (name == "happy")    eyeSetState(EYE_HAPPY);
  else if (name == "angry")    eyeSetState(EYE_ANGRY);
  else if (name == "sleepy")   eyeSetState(EYE_SLEEPY);
  else if (name == "scanning") eyeSetState(EYE_SCANNING);
  else if (name == "threat")   eyeSetState(EYE_THREAT);
  else if (name == "roast")    eyeSetState(EYE_ROAST);
  else if (name == "music")    eyeSetState(EYE_MUSIC);
  else if (name == "talking")  eyeSetState(EYE_TALKING);
  else if (name == "thinking") eyeSetState(EYE_THINKING);
  else if (name == "boot")     eyeSetState(EYE_BOOT);
  else if (name == "love")     eyeSetState(EYE_LOVE);
  else                         eyeSetState(EYE_NEUTRAL);
}

// ── Pupil tracking from face center ───────────────────────────────────────
void eyeTrackPupil(float nx, float ny) {
  _pupilNx = constrain(nx, 0.0f, 1.0f);
  _pupilNy = constrain(ny, 0.0f, 1.0f);
  if (_eyeState == EYE_NEUTRAL || _eyeState == EYE_TALKING) {
    _needRedraw = true;
  }
}

// ── Helper: draw one eye (oval + pupil + glint) ────────────────────────────
void _drawEye(int cx, int cy, int rx, int ry,
              uint16_t irisCol, float nx, float ny,
              bool blink = false) {
  if (blink) {
    // Blink: draw flat horizontal line
    tft.drawLine(cx - rx, cy, cx + rx, cy, irisCol);
    return;
  }
  tft.fillEllipse(cx, cy, rx, ry, irisCol);

  // Pupil offset based on face position
  int px = cx + (int)((nx - 0.5f) * rx * 0.5f);
  int py = cy + (int)((ny - 0.5f) * ry * 0.5f);
  tft.fillCircle(px, py, PUPIL_R, COL_BG);

  // White glint (top-left of iris)
  tft.fillCircle(cx - rx/3, cy - ry/3, GLINT_R, COL_WHITE);
}

// ── Border glow ────────────────────────────────────────────────────────────
void _drawBorder(uint16_t col) {
  tft.drawRect(0, 0, TFT_W, TFT_H, col);
  tft.drawRect(1, 1, TFT_W-2, TFT_H-2, col);
}

// ── Draw NEUTRAL / TALKING ─────────────────────────────────────────────────
void _drawNeutral(bool talking) {
  _drawBorder(COL_CYAN);
  _drawEye(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, COL_CYAN, _pupilNx, _pupilNy, _blinkState);
  _drawEye(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, COL_CYAN, _pupilNx, _pupilNy, _blinkState);

  if (talking) {
    // Animated mouth bar
    int mouthW = 60 + (_animStep % 20) * 2;
    int mouthH = 8 + (_animStep % 10);
    tft.fillRoundRect(TFT_W/2 - mouthW/2, EYE_CY + 80, mouthW, mouthH, 4, COL_CYAN);
  }
}

// ── Draw HAPPY ─────────────────────────────────────────────────────────────
void _drawHappy() {
  _drawBorder(COL_GREEN);
  // ^ ^ arcs
  for (int i = -EYE_RX; i <= EYE_RX; i++) {
    float y = -(float)(EYE_RY) * (1.0f - ((float)(i*i)) / (EYE_RX * EYE_RX));
    tft.drawPixel(EYE_L_CX + i, EYE_CY + (int)y, COL_GREEN);
    tft.drawPixel(EYE_R_CX + i, EYE_CY + (int)y, COL_GREEN);
  }
  tft.setTextColor(COL_GREEN); tft.setTextSize(2);
  tft.setCursor(TFT_W/2 - 20, EYE_CY + 80);
  tft.print("^_^");
}

// ── Draw ANGRY ─────────────────────────────────────────────────────────────
void _drawAngry() {
  _drawBorder(COL_RED);
  _drawEye(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, COL_RED, _pupilNx, _pupilNy);
  _drawEye(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, COL_RED, _pupilNx, _pupilNy);
  // Diagonal angry brows
  tft.drawLine(EYE_L_CX - EYE_RX, EYE_CY - EYE_RY - 10,
               EYE_L_CX + EYE_RX, EYE_CY - EYE_RY + 15, COL_RED);
  tft.drawLine(EYE_R_CX + EYE_RX, EYE_CY - EYE_RY - 10,
               EYE_R_CX - EYE_RX, EYE_CY - EYE_RY + 15, COL_RED);
}

// ── Draw SLEEPY ────────────────────────────────────────────────────────────
void _drawSleepy() {
  _drawBorder(0x421F);  // dim purple
  // Half-closed: top half of iris covered by lid
  tft.fillEllipse(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, 0x421F);
  tft.fillEllipse(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, 0x421F);
  // Black lid covers top half
  tft.fillRect(EYE_L_CX - EYE_RX, EYE_CY - EYE_RY, EYE_RX*2, EYE_RY, COL_BG);
  tft.fillRect(EYE_R_CX - EYE_RX, EYE_CY - EYE_RY, EYE_RX*2, EYE_RY, COL_BG);
  // Zzz text
  tft.setTextColor(0x421F); tft.setTextSize(2);
  tft.setCursor(EYE_R_CX + EYE_RX + 5, EYE_CY - 20);
  tft.print("zzz");
}

// ── Draw SCANNING ──────────────────────────────────────────────────────────
void _drawScanning() {
  // Rotating arc + crosshair
  _drawBorder(COL_CYAN);
  int cx = TFT_W/2; int cy = EYE_CY;
  int r = 70;
  // Draw arc segments (approximate with lines)
  float a = (_scanAngle / 57.3f);  // radians
  for (int i = 0; i < 200; i++) {
    float ang = a + i * 0.015f;
    int x = cx + (int)(r * cos(ang));
    int y = cy + (int)(r * sin(ang));
    tft.drawPixel(x, y, COL_CYAN);
  }
  // Crosshair
  tft.drawLine(cx - 15, cy, cx + 15, cy, COL_CYAN);
  tft.drawLine(cx, cy - 15, cx, cy + 15, COL_CYAN);
  tft.drawCircle(cx, cy, 5, COL_CYAN);
  // SCAN label
  tft.setTextColor(COL_CYAN); tft.setTextSize(1);
  tft.setCursor(cx - 14, cy + r + 10);
  tft.print("SCANNING");
}

// ── Draw THREAT ────────────────────────────────────────────────────────────
void _drawThreat() {
  // Red border, red pupils
  tft.drawRect(0, 0, TFT_W, TFT_H, COL_RED);
  tft.drawRect(2, 2, TFT_W-4, TFT_H-4, COL_RED);
  tft.drawRect(4, 4, TFT_W-8, TFT_H-8, COL_RED);
  _drawEye(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, COL_RED, _pupilNx, _pupilNy);
  _drawEye(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, COL_RED, _pupilNx, _pupilNy);
  tft.setTextColor(COL_RED); tft.setTextSize(2);
  tft.setCursor(TFT_W/2 - 36, EYE_CY + 85);
  tft.print("THREAT");
}

// ── Draw ROAST ─────────────────────────────────────────────────────────────
void _drawRoast() {
  _drawBorder(COL_ORANGE);
  // Narrow smug eyes
  tft.fillRect(EYE_L_CX - EYE_RX, EYE_CY - 5, EYE_RX*2, 10, COL_ORANGE);
  tft.fillRect(EYE_R_CX - EYE_RX, EYE_CY - 5, EYE_RX*2, 10, COL_ORANGE);
  // Smirk
  int mx = TFT_W/2; int my = EYE_CY + 75;
  tft.drawLine(mx - 30, my, mx + 10, my + 15, COL_ORANGE);
  tft.drawLine(mx + 10, my + 15, mx + 35, my - 5, COL_ORANGE);
}

// ── Draw MUSIC ─────────────────────────────────────────────────────────────
void _drawMusic() {
  _drawBorder(COL_PURPLE);
  _drawEye(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, COL_PURPLE, 0.5f, 0.5f);
  _drawEye(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, COL_PURPLE, 0.5f, 0.5f);
  // Animated notes
  int noteY = EYE_CY - 80 - (_animStep % 20);
  tft.setTextColor(COL_PURPLE); tft.setTextSize(3);
  tft.setCursor(30,  noteY);
  tft.print("J");
  tft.setCursor(170, noteY + 15 - (_animStep % 15));
  tft.print("J");
}

// ── Draw THINKING ──────────────────────────────────────────────────────────
void _drawThinking() {
  _drawBorder(COL_CYAN);
  // Eyes looking up-right
  _drawEye(EYE_L_CX, EYE_CY, EYE_RX, EYE_RY, COL_CYAN, 0.7f, 0.3f);
  _drawEye(EYE_R_CX, EYE_CY, EYE_RX, EYE_RY, COL_CYAN, 0.7f, 0.3f);
  // Dots ...
  int dotX = TFT_W/2 - 20;
  for (int i = 0; i < 3; i++) {
    uint16_t col = (i == (_animStep % 3)) ? COL_WHITE : COL_DKGRAY;
    tft.fillCircle(dotX + i*20, EYE_CY + 85, 6, col);
  }
}

// ── Draw BOOT ──────────────────────────────────────────────────────────────
void _drawBoot() {
  _drawBorder(COL_CYAN);
  tft.setTextColor(COL_WHITE); tft.setTextSize(2);
  tft.setCursor(TFT_W/2 - 40, EYE_CY - 60);
  tft.print("JINX v2.1");
  tft.setTextSize(1); tft.setTextColor(COL_CYAN);
  tft.setCursor(TFT_W/2 - 52, EYE_CY - 30);
  tft.print("INITIALIZING...");

  // Progress bar
  int barX = 20; int barY = EYE_CY + 20;
  int barW = TFT_W - 40; int barH = 14;
  tft.drawRect(barX, barY, barW, barH, COL_CYAN);
  int fill = (int)((barW - 2) * (_bootPct / 100.0f));
  tft.fillRect(barX + 1, barY + 1, fill, barH - 2, COL_CYAN);

  char pct[8]; snprintf(pct, sizeof(pct), "%d%%", _bootPct);
  tft.setTextColor(COL_WHITE); tft.setTextSize(1);
  tft.setCursor(TFT_W/2 - 10, barY + barH + 5);
  tft.print(pct);

  if (_bootPct < 100) _bootPct += 3;
  else eyeSetState(EYE_NEUTRAL);
}

// ── Draw LOVE ──────────────────────────────────────────────────────────────
void _drawLove() {
  _drawBorder(COL_RED);
  // Heart shapes for eyes (approximate with circles)
  tft.fillCircle(EYE_L_CX - 15, EYE_CY - 10, 22, COL_RED);
  tft.fillCircle(EYE_L_CX + 15, EYE_CY - 10, 22, COL_RED);
  tft.fillTriangle(EYE_L_CX - 35, EYE_CY,
                   EYE_L_CX + 35, EYE_CY,
                   EYE_L_CX,      EYE_CY + 30, COL_RED);

  tft.fillCircle(EYE_R_CX - 15, EYE_CY - 10, 22, COL_RED);
  tft.fillCircle(EYE_R_CX + 15, EYE_CY - 10, 22, COL_RED);
  tft.fillTriangle(EYE_R_CX - 35, EYE_CY,
                   EYE_R_CX + 35, EYE_CY,
                   EYE_R_CX,      EYE_CY + 30, COL_RED);
}

// ── eyeTick() — call every loop() ─────────────────────────────────────────
void eyeTick() {
  uint32_t now = millis();

  // Auto-blink every ~4 seconds (only in neutral/talking states)
  if (_eyeState == EYE_NEUTRAL || _eyeState == EYE_TALKING) {
    if (!_blinkState && now - _blinkLastMs > 4000) {
      _blinkState  = true;
      _blinkLastMs = now;
      _needRedraw  = true;
    }
    if (_blinkState && now - _blinkLastMs > 120) {
      _blinkState  = false;
      _blinkLastMs = now;
      _needRedraw  = true;
    }
  }

  // Animation tick (for scanning, music, thinking, etc.)
  if (now - _animLastMs > 60) {
    _animLastMs = now;
    _animStep++;
    _scanAngle = (_scanAngle + 8) % 360;
    // These states need continuous redraw
    if (_eyeState == EYE_SCANNING || _eyeState == EYE_MUSIC  ||
        _eyeState == EYE_THINKING || _eyeState == EYE_TALKING ||
        _eyeState == EYE_BOOT) {
      _needRedraw = true;
    }
  }

  if (!_needRedraw) return;
  _needRedraw = false;

  // Clear screen only for static states (continuous states clear their own area)
  if (_eyeState != EYE_SCANNING && _eyeState != EYE_BOOT) {
    tft.fillScreen(COL_BG);
  }

  switch (_eyeState) {
    case EYE_NEUTRAL:  _drawNeutral(false); break;
    case EYE_HAPPY:    _drawHappy();        break;
    case EYE_ANGRY:    _drawAngry();        break;
    case EYE_SLEEPY:   _drawSleepy();       break;
    case EYE_SCANNING: _drawScanning();     break;
    case EYE_THREAT:   _drawThreat();       break;
    case EYE_ROAST:    _drawRoast();        break;
    case EYE_MUSIC:    _drawMusic();        break;
    case EYE_TALKING:  _drawNeutral(true);  break;
    case EYE_THINKING: _drawThinking();     break;
    case EYE_BOOT:     _drawBoot();         break;
    case EYE_LOVE:     _drawLove();         break;
  }
}

// ── Set boot progress (0–100) ─────────────────────────────────────────────
void eyeSetBootProgress(uint8_t pct) {
  _bootPct    = pct;
  _needRedraw = true;
}

#endif // EYES_H
