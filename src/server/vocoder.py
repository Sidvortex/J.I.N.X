"""
VOCODER.PY — VOICE SYSTEM
Handles: Wake word detection, STT (Vosk offline / Google online),
         TTS (edge-TTS for human-like voice, ElevenLabs for ultra-real),
         Gemini LLM conversations, voice commands, roast mode, music.

Human voice via edge-TTS (Microsoft Neural TTS — free, sounds real)
or ElevenLabs (paid, even more realistic). Never pyttsx3 again.
"""

import os
import re
import json
import queue
import time
import asyncio
import threading
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import sounddevice as sd
import numpy as np
import speech_recognition as sr

import dna
from blackbox import Blackbox
from synapse  import Synapse
from psyche   import Psyche

# Optional imports (graceful degradation)
try:
    import google.generativeai as genai
    genai.configure(api_key=dna.GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-2.0-flash")
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False
    print("  [VOCODER] Gemini not available")

try:
    from vosk import Model as VoskModel, KaldiRecognizer
    VOSK_MODEL_PATH = "models/vosk-model"
    if Path(VOSK_MODEL_PATH).exists():
        _vosk_model = VoskModel(VOSK_MODEL_PATH)
        VOSK_AVAILABLE = True
    else:
        VOSK_AVAILABLE = False
        print("  [VOCODER] Vosk model not found at models/vosk-model/")
except ImportError:
    VOSK_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("  [VOCODER] edge-tts not installed: pip install edge-tts")

try:
    import requests as http_requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Vocoder:
    def __init__(self, synapse: Synapse, blackbox: Blackbox, psyche: Psyche, optic=None):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.psyche    = psyche
        self.optic     = optic
        self.running   = False
        self.mode      = dna.DEFAULT_MODE

        # Conversation history for context
        self.conversation_history = []
        self.is_speaking   = False
        self.is_listening  = False
        self.awake         = False
        self.awake_until   = 0

        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        # Music state
        self.music_process = None

        # Subscribe to MQTT
        synapse.subscribe(dna.TOPIC["mode"],        self._on_mode)
        synapse.subscribe(dna.TOPIC["web_command"], self._on_web_command)

        print("  [VOCODER] Voice system initialized")
        if EDGE_TTS_AVAILABLE:
            print(f"  [VOCODER] TTS: edge-TTS ({dna.EDGE_TTS_VOICE})")
        if dna.ELEVENLABS_API_KEY:
            print("  [VOCODER] TTS: ElevenLabs (premium)")
        if VOSK_AVAILABLE:
            print("  [VOCODER] STT: Vosk (offline)")

    def _on_mode(self, payload: str):
        self.mode = payload.strip()

    def _on_web_command(self, payload: str):
        try:
            cmd = json.loads(payload)
            if cmd.get("action") == "speak":
                self.speak(cmd.get("text", ""))
            elif cmd.get("action") == "roast":
                self.roast_mode(cmd.get("name"))
            elif cmd.get("action") == "command":
                self._execute_command(cmd.get("text", ""))
        except Exception:
            pass

    # ── TTS: Text to Speech ────────────────────────────────────────────────

    def speak(self, text: str, emotion: str = "neutral"):
        """Speak text using best available TTS engine."""
        if not text:
            return
        self.is_speaking = True
        self.synapse.publish(dna.TOPIC["eyes"], "talking")

        try:
            if dna.ELEVENLABS_API_KEY and REQUESTS_AVAILABLE:
                self._speak_elevenlabs(text)
            elif EDGE_TTS_AVAILABLE:
                self._speak_edge_tts(text)
            else:
                self._speak_espeak(text)

            self.blackbox.log_event("SPEECH", {"text": text[:100]})
        except Exception as e:
            print(f"  [VOCODER] TTS error: {e}")
            self._speak_espeak(text)
        finally:
            self.is_speaking = False
            if self.mode != dna.Mode.SENTINEL:
                self.synapse.publish(dna.TOPIC["eyes"], "neutral")

    def _speak_edge_tts(self, text: str):
        """edge-TTS: Microsoft Neural voice — sounds very human, fully free."""
        async def _tts():
            communicate = edge_tts.Communicate(text, dna.EDGE_TTS_VOICE)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            await communicate.save(tmp)
            return tmp

        loop    = asyncio.new_event_loop()
        tmp     = loop.run_until_complete(_tts())
        loop.close()

        # Play via mpv or pygame
        try:
            subprocess.run(["mpv", "--no-terminal", tmp],
                           capture_output=True, timeout=30)
        except Exception:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        finally:
            os.unlink(tmp)

    def _speak_elevenlabs(self, text: str):
        """ElevenLabs API — ultra-realistic voice."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{dna.ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": dna.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        body = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        resp = http_requests.post(url, headers=headers, json=body, timeout=10)
        if resp.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(resp.content)
                tmp = f.name
            subprocess.run(["mpv", "--no-terminal", tmp], capture_output=True)
            os.unlink(tmp)
        else:
            raise RuntimeError(f"ElevenLabs error {resp.status_code}")

    def _speak_espeak(self, text: str):
        """Fallback: espeak (robotic but always works)."""
        subprocess.run(["espeak", "-v", "en", "-s", "150", text], capture_output=True)

    # ── STT: Speech to Text ────────────────────────────────────────────────

    def listen(self, timeout: int = 5) -> str:
        """Listen for speech and return transcribed text."""
        self.is_listening = True
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            if dna.USE_OFFLINE_STT and VOSK_AVAILABLE:
                return self._transcribe_vosk(audio)
            else:
                return self._transcribe_google(audio)
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"  [VOCODER] Listen error: {e}")
            return ""
        finally:
            self.is_listening = False

    def _transcribe_google(self, audio) -> str:
        try:
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            # Fallback to Vosk
            if VOSK_AVAILABLE:
                return self._transcribe_vosk(audio)
            return ""

    def _transcribe_vosk(self, audio) -> str:
        if not VOSK_AVAILABLE:
            return ""
        rec = KaldiRecognizer(_vosk_model, 16000)
        wav = audio.get_wav_data(convert_rate=16000)
        if rec.AcceptWaveform(wav):
            result = json.loads(rec.Result())
            return result.get("text", "").lower()
        return ""

    # ── Wake Word Detection ────────────────────────────────────────────────

    def _listen_for_wake_word(self):
        """Continuous background listening for wake word."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"  [VOCODER] Listening for wake word: '{dna.WAKE_WORD}'")
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)
                    text  = self._transcribe_google(audio) if not dna.USE_OFFLINE_STT \
                            else self._transcribe_vosk(audio)
                    if text and dna.WAKE_WORD in text:
                        self._on_wake()
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    time.sleep(1)

    def _on_wake(self):
        """Triggered when wake word is detected."""
        if self.is_speaking:
            return
        print("  [VOCODER] Wake word detected!")
        self.awake      = True
        self.awake_until = time.time() + dna.VOICE_TIMEOUT + 30

        self.synapse.publish(dna.TOPIC["eyes"], "happy")
        self.synapse.publish(dna.TOPIC["led"],  "wake")
        self.synapse.publish(dna.TOPIC["sound"], "wake")

        # Listen for command
        self.speak(self.psyche.get_ack())  # "Yes?", "What?", "Ugh, what now?"
        command = self.listen(timeout=dna.VOICE_TIMEOUT)
        if command:
            self._execute_command(command)
        else:
            self.speak("I heard nothing. Classic.")
        self.awake = False

    # ── Command Parsing ────────────────────────────────────────────────────

    def _execute_command(self, text: str):
        """Parse and execute a voice command."""
        text = text.lower().strip()
        print(f"  [VOCODER] Command: '{text}'")
        self.blackbox.log_event("COMMAND", {"text": text})

        # Mode switching
        if any(w in text for w in ["guard mode", "sentinel", "surveillance"]):
            self.synapse.publish(dna.TOPIC["mode"], dna.Mode.SENTINEL)
            self.speak("Switching to sentinel mode. I'm watching everyone.")

        elif any(w in text for w in ["buddy mode", "normal mode", "relax"]):
            self.synapse.publish(dna.TOPIC["mode"], dna.Mode.BUDDY)
            self.speak("Back to buddy mode. I'll try to be nice. No promises.")

        elif any(w in text for w in ["sleep", "goodnight", "shut up", "stop"]):
            self.synapse.publish(dna.TOPIC["eyes"], "sleep")
            self.speak("Finally. Peace and quiet.")
            self.synapse.publish(dna.TOPIC["mode"], dna.Mode.SLEEP)

        # Roast mode
        elif "roast" in text:
            name = self._extract_name(text)
            self.roast_mode(name)

        # Music
        elif any(w in text for w in ["play music", "play song", "play"]):
            query = re.sub(r"(play music|play song|play|hey jinx)", "", text).strip()
            self.play_music(query or "chill music")

        elif any(w in text for w in ["stop music", "pause music", "mute"]):
            self.stop_music()

        # Lights / LEDs
        elif "lights" in text or "led" in text:
            color = self._extract_color(text)
            self.synapse.publish(dna.TOPIC["led"], f"color:{color}")
            self.speak(f"Lights set to {color}.")

        # Movement
        elif any(w in text for w in ["come here", "forward", "move forward"]):
            self.synapse.publish(dna.TOPIC["motor"], "forward")
            self.speak("Moving forward.")

        elif any(w in text for w in ["go back", "backward", "retreat"]):
            self.synapse.publish(dna.TOPIC["motor"], "backward")
            self.speak("Backing up.")

        elif any(w in text for w in ["stop moving", "halt"]):
            self.synapse.publish(dna.TOPIC["motor"], "stop")
            self.speak("Stopping.")

        # Status
        elif any(w in text for w in ["status", "how are you", "battery"]):
            self._report_status()

        # Face registration
        elif "register" in text or "learn my face" in text:
            name = self._extract_name(text) or "unknown_person"
            if self.optic and self.optic.register_face(name):
                self.speak(f"Got it. I'll remember you as {name}. Lucky you.")
            else:
                self.speak("I couldn't see a face clearly. Try again.")

        # Agent mode — document question or code review
        elif any(w in text for w in ["read", "summarize", "explain", "what does", "review code"]):
            self.synapse.publish(dna.TOPIC["command"],
                                 json.dumps({"type": "agent_query", "query": text}))
            self.speak("Let me check that for you.")

        # Skeleton show-off
        elif any(w in text for w in ["skeleton", "show skeleton", "dance mode"]):
            self.speak("Show me your moves. I'll judge.")
            self.synapse.publish(dna.TOPIC["mode"], dna.Mode.BUDDY)

        # Fallback — Gemini conversation
        else:
            response = self.ask_gemini(text)
            self.speak(response)

    def _extract_name(self, text: str) -> str:
        match = re.search(r"(?:roast|register|learn)\s+(\w+)", text)
        return match.group(1).capitalize() if match else ""

    def _extract_color(self, text: str) -> str:
        colors = ["red", "blue", "green", "purple", "cyan", "yellow", "white", "orange", "pink", "rainbow"]
        for c in colors:
            if c in text:
                return c
        return "white"

    def _report_status(self):
        # Battery comes from MQTT state in hivemind
        msg = f"All systems online. Running in {self.mode} mode. " \
              f"I've seen {len(self.optic.known_names) if self.optic else 0} faces in my database."
        self.speak(msg)

    # ── Gemini LLM ────────────────────────────────────────────────────────

    def ask_gemini(self, user_input: str) -> str:
        """Send message to Gemini with personality context."""
        if not GEMINI_AVAILABLE:
            return "My brain module is offline. Check the API key."

        # Build personality system prompt
        system_prompt = self.psyche.get_system_prompt()

        # Add to conversation history (keep last 10 turns)
        self.conversation_history.append({"role": "user", "parts": [user_input]})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        try:
            chat = GEMINI_MODEL.start_chat(history=self.conversation_history[:-1])
            response = chat.send_message(
                f"{system_prompt}\n\nUser said: {user_input}\n"
                "Reply in 1-3 sentences. Be clever and sarcastic but helpful. "
                "No markdown formatting in your reply."
            )
            reply = response.text.strip()
            self.conversation_history.append({"role": "model", "parts": [reply]})
            return reply
        except Exception as e:
            print(f"  [VOCODER] Gemini error: {e}")
            return "My thoughts are buffering. Try again."

    # ── Roast Mode ────────────────────────────────────────────────────────

    def roast_mode(self, name: str = None):
        """Generate and deliver a personalized AI roast."""
        if not GEMINI_AVAILABLE:
            self.speak("I'd roast you, but my creativity module is offline.")
            return

        self.synapse.publish(dna.TOPIC["eyes"], "roast")
        self.synapse.publish(dna.TOPIC["led"],  "roast")
        self.synapse.publish(dna.TOPIC["sound"], "roast")

        context = f"Target: {name}" if name else "Unknown person standing in front of me"
        intensity_map = {
            "light":  "mild, friendly roast — like a friend teasing",
            "medium": "funny, sharp roast — definitely embarrassing",
            "savage": "absolutely savage roast — hold nothing back"
        }
        style = intensity_map.get(dna.ROAST_INTENSITY, "funny, sharp roast")

        prompt = (
            f"You are JINX, a sarcastic AI deskbot with attitude. "
            f"Deliver a {style} about: {context}. "
            "Keep it to 2-3 sentences. Be creative. Reference the situation if possible. "
            "End with a smug one-liner."
        )
        try:
            response = GEMINI_MODEL.generate_content(prompt)
            roast    = response.text.strip()
        except Exception:
            roast = "I was going to roast you, but I see you're already well-done."

        self.speak(roast)

    # ── Music ─────────────────────────────────────────────────────────────

    def play_music(self, query: str):
        """Search and play music via yt-dlp."""
        self.speak(f"Looking up {query}...")
        self.synapse.publish(dna.TOPIC["eyes"], "music")
        self.synapse.publish(dna.TOPIC["led"],  "music")

        def _play():
            try:
                # Get audio URL via yt-dlp (no download)
                result = subprocess.run(
                    ["yt-dlp", "-f", "bestaudio", "--get-url",
                     f"ytsearch1:{query}"],
                    capture_output=True, text=True, timeout=15
                )
                url = result.stdout.strip().split("\n")[0]
                if url:
                    self.stop_music()
                    self.music_process = subprocess.Popen(
                        ["mpv", "--no-terminal", url],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                else:
                    self.speak("Couldn't find that. Your taste in music must be too obscure.")
            except Exception as e:
                self.speak("Music playback failed. Check yt-dlp and mpv are installed.")

        threading.Thread(target=_play, daemon=True).start()

    def stop_music(self):
        if self.music_process:
            self.music_process.terminate()
            self.music_process = None
            self.synapse.publish(dna.TOPIC["eyes"], "neutral")
            self.synapse.publish(dna.TOPIC["led"],  "normal")

    # ── Main Loop ─────────────────────────────────────────────────────────

    def run(self):
        """Start voice system — runs wake word detection loop."""
        self.running = True
        print("  [VOCODER] Voice system running")
        self._listen_for_wake_word()

    def stop(self):
        self.running = False
        self.stop_music()
