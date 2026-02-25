#ifndef SOUND_H
#define SOUND_H

// ═══════════════════════════════════════════════════════════════════════════
//  sound.h — DFPlayer Mini Audio Controller
//
//  Connected via UART2 (Serial2) on ESP32
//  RX: DFPLAYER_RX (GPIO16)  TX: DFPLAYER_TX (GPIO17)
//
//  SD Card folder structure expected:
//    /01/001.mp3  — boot sound
//    /01/002.mp3  — alert
//    /01/003.mp3  — threat detected
//    /01/004.mp3  — roast intro
//    /01/005.mp3  — buddy greeting
//    /01/006.mp3  — scan start
//    /01/007.mp3  — acknowledged
//    /01/008.mp3  — error / warning
//    /01/009.mp3  — music mode
//    /01/010.mp3  — sleep sound
//
//  Functions:
//    soundInit()           — call in setup()
//    soundPlay(track)      — play by track number
//    soundPlayNamed(name)  — play by name string (from MQTT)
//    soundSetVolume(0-30)  — volume level
//    soundStop()           — stop current track
//    soundNext()           — next track
// ═══════════════════════════════════════════════════════════════════════════

#include "config.h"

// ── Named track map ───────────────────────────────────────────────────────
#define SOUND_BOOT      1
#define SOUND_ALERT     2
#define SOUND_THREAT    3
#define SOUND_ROAST     4
#define SOUND_GREET     5
#define SOUND_SCAN      6
#define SOUND_ACK       7
#define SOUND_ERROR     8
#define SOUND_MUSIC     9
#define SOUND_SLEEP     10

// ── DFPlayer command bytes ─────────────────────────────────────────────────
#define DF_START   0x7E
#define DF_VER     0xFF
#define DF_LEN     0x06
#define DF_END     0xEF
#define DF_FB      0x00   // no feedback

// ── Internal state ─────────────────────────────────────────────────────────
static HardwareSerial _dfSerial(2);
static uint8_t  _soundVolume  = 25;   // 0–30
static bool     _soundReady   = false;
static uint32_t _soundLastCmd = 0;
#define SOUND_CMD_DELAY_MS 30    // min delay between DFPlayer commands

// ── Build and send DFPlayer command ───────────────────────────────────────
void _dfSend(uint8_t cmd, uint8_t paramHi, uint8_t paramLo) {
  // Enforce minimum delay between commands
  uint32_t now = millis();
  if (now - _soundLastCmd < SOUND_CMD_DELAY_MS) {
    delay(SOUND_CMD_DELAY_MS - (now - _soundLastCmd));
  }
  _soundLastCmd = millis();

  // Checksum = 0 - (VER + LEN + CMD + FB + ParamHi + ParamLo)
  uint16_t checksum = -(DF_VER + DF_LEN + cmd + DF_FB + paramHi + paramLo);

  uint8_t packet[10] = {
    DF_START,
    DF_VER,
    DF_LEN,
    cmd,
    DF_FB,
    paramHi,
    paramLo,
    (uint8_t)(checksum >> 8),
    (uint8_t)(checksum & 0xFF),
    DF_END
  };
  _dfSerial.write(packet, sizeof(packet));
  DBGF("[SOUND] CMD 0x%02X %02X %02X\n", cmd, paramHi, paramLo);
}

// ── Init ──────────────────────────────────────────────────────────────────
void soundInit() {
  _dfSerial.begin(9600, SERIAL_8N1, DFPLAYER_RX, DFPLAYER_TX);
  delay(600);   // DFPlayer needs time after power-on

  // Reset
  _dfSend(0x0C, 0x00, 0x00);
  delay(500);

  // Set volume
  _dfSend(0x06, 0x00, _soundVolume);
  delay(100);

  // Select TF card as source
  _dfSend(0x09, 0x00, 0x02);
  delay(200);

  _soundReady = true;
  DBGLN("[SOUND] DFPlayer initialized");
}

// ── Play track by number ───────────────────────────────────────────────────
void soundPlay(int track) {
  if (!_soundReady) return;
  if (track < 1) track = 1;
  // Command 0x03 = specify track number
  _dfSend(0x03, (track >> 8) & 0xFF, track & 0xFF);
  DBGF("[SOUND] Play track %d\n", track);
}

// ── Play track by name (from MQTT payload) ────────────────────────────────
void soundPlayNamed(String name) {
  name.toLowerCase();
  if      (name == "boot")    soundPlay(SOUND_BOOT);
  else if (name == "alert")   soundPlay(SOUND_ALERT);
  else if (name == "threat")  soundPlay(SOUND_THREAT);
  else if (name == "roast")   soundPlay(SOUND_ROAST);
  else if (name == "greet")   soundPlay(SOUND_GREET);
  else if (name == "scan")    soundPlay(SOUND_SCAN);
  else if (name == "ack")     soundPlay(SOUND_ACK);
  else if (name == "error")   soundPlay(SOUND_ERROR);
  else if (name == "music")   soundPlay(SOUND_MUSIC);
  else if (name == "sleep")   soundPlay(SOUND_SLEEP);
  else {
    // Try parsing as number
    int n = name.toInt();
    if (n > 0) soundPlay(n);
  }
}

// ── Volume (0–30) ──────────────────────────────────────────────────────────
void soundSetVolume(uint8_t vol) {
  _soundVolume = constrain(vol, 0, 30);
  _dfSend(0x06, 0x00, _soundVolume);
  DBGF("[SOUND] Volume %d\n", _soundVolume);
}

// ── Stop ──────────────────────────────────────────────────────────────────
void soundStop() {
  _dfSend(0x16, 0x00, 0x00);
  DBGLN("[SOUND] Stop");
}

// ── Pause / Resume ────────────────────────────────────────────────────────
void soundPause()  { _dfSend(0x0E, 0x00, 0x00); }
void soundResume() { _dfSend(0x0D, 0x00, 0x00); }

// ── Next / Previous ───────────────────────────────────────────────────────
void soundNext() { _dfSend(0x01, 0x00, 0x00); }
void soundPrev() { _dfSend(0x02, 0x00, 0x00); }

// ── Loop single track ─────────────────────────────────────────────────────
void soundLoop(int track) {
  soundPlay(track);
  delay(50);
  _dfSend(0x19, 0x00, 0x00);  // loop current track
}

// ── Handle MQTT sound payload ──────────────────────────────────────────────
// Accepts JSON: {"name":"boot"} or {"track":3} or {"volume":20}
// or plain string: "boot" / "3" / "stop"
void soundHandleMqtt(String msg) {
  msg.trim();

  // Check for plain "stop"
  if (msg == "stop")  { soundStop();  return; }
  if (msg == "pause") { soundPause(); return; }
  if (msg == "next")  { soundNext();  return; }

  // Try JSON parse
  if (msg.startsWith("{")) {
    StaticJsonDocument<128> doc;
    if (deserializeJson(doc, msg) == DeserializationError::Ok) {
      if (doc.containsKey("volume")) {
        soundSetVolume(doc["volume"]);
        return;
      }
      if (doc.containsKey("name")) {
        soundPlayNamed(doc["name"].as<String>());
        return;
      }
      if (doc.containsKey("track")) {
        soundPlay(doc["track"]);
        return;
      }
    }
  }

  // Plain name or number
  soundPlayNamed(msg);
}

// ── Is DFPlayer ready? ────────────────────────────────────────────────────
bool soundIsReady() { return _soundReady; }

#endif // SOUND_H
