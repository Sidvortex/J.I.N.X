# vocoder.py - jinx's ears and mouth
# handles wake word detection, voice commands, tts, 
# gemini integration for roasts and conversation
# 
# the speech recognition is kinda finicky sometimes
# if it keeps failing try adjusting the ambient noise duration
# or just speak louder lol

import speech_recognition as sr
import pyttsx3
import json
import paho.mqtt.client as mqtt
import threading
import subprocess
import time
import random
import os

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    print("[VOCODER] gemini not installed, roasts wont work")
    GEMINI_AVAILABLE = False

from dna import *
from blackbox import JinxDB
from psyche import say, roast_prompt, chat_prompt


class Vocoder:
    def __init__(self):
        print("[VOCODER] warming up voice systems...")
        
        # mqtt
        self.syn = mqtt.Client()
        self.syn.connect(LAPTOP_IP, MQTT_PORT)
        
        # database
        self.db = JinxDB(DB_PATH)
        
        # speech recognition
        self.ear = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # adjust for ambient noise on startup
        # this takes a couple seconds but makes recognition way better
        print("[VOCODER] calibrating mic... stay quiet for 2 sec")
        with self.mic as source:
            self.ear.adjust_for_ambient_noise(source, duration=2)
        print("[VOCODER] mic calibrated")
        
        # text to speech
        self.mouth = pyttsx3.init()
        
        # try to find a decent voice
        voices = self.mouth.getProperty('voices')
        for v in voices:
            if 'english' in v.name.lower():
                self.mouth.setProperty('voice', v.id)
                break
        
        self.mouth.setProperty('rate', 155)  # slightly slower than default
        # 150 = calm jinx, 170 = excited jinx, 200 = panicking jinx
        
        # gemini for the fun stuff
        if GEMINI_AVAILABLE and GEMINI_API_KEY != "PASTE_YOUR_KEY_HERE":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.brain = genai.GenerativeModel('gemini-pro')
                print("[VOCODER] gemini connected - roasts are GO")
            except Exception as e:
                print(f"[VOCODER] gemini failed: {e}")
                self.brain = None
        else:
            self.brain = None
            print("[VOCODER] no gemini key, using offline responses only")
        
        # state
        self.wake_word = "jinx"
        self.alive = True  # controls the listen loop
        self.is_speaking = False  # dont listen while talking lol
        self.current_mode = "buddy"
        
        # last person detected (updated by optic.py via mqtt)
        self.last_detected_person = None
        
        # subscribe to relevant mqtt topics
        self.syn.on_message = self._on_mqtt_message
        self.syn.subscribe("jinx/detected_person")
        self.syn.loop_start()
        
        self.db.add_syslog("VOCODER", "voice system ready")
        print("[VOCODER] ready to talk")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """receive info from other modules"""
        try:
            data = json.loads(msg.payload.decode())
            if msg.topic == "jinx/detected_person":
                self.last_detected_person = data.get("name", None)
        except:
            pass
    
    # ============================================
    # MOUTH - speaking
    # ============================================
    
    def vocalize(self, text):
        """make jinx speak
        also triggers talking eye animation on esp32"""
        if not text:
            return
        
        self.is_speaking = True
        print(f"[JINX SAYS] {text}")
        
        # tell esp32 to show talking eyes
        self.syn.publish(TOPICS["eyes"], json.dumps({"state": "talking"}))
        
        # speak
        try:
            self.mouth.say(text)
            self.mouth.runAndWait()
        except Exception as e:
            # pyttsx3 sometimes crashes if called too fast
            # just print and move on, not worth crashing the whole system
            print(f"[VOCODER] tts error: {e}")
        
        # back to normal eyes
        self.syn.publish(TOPICS["eyes"], json.dumps({"state": "happy"}))
        self.is_speaking = False
    
    def vocalize_async(self, text):
        """speak without blocking the main thread
        useful when we need to keep listening"""
        t = threading.Thread(target=self.vocalize, args=(text,), daemon=True)
        t.start()
    
    # ============================================
    # BRAIN - gemini integration
    # ============================================
    
    def incinerate(self, person_name="someone", extra_info=""):
        """generate a roast using gemini
        this is the crowd favorite feature lol"""
        
        if not self.brain:
            # fallback roasts if gemini isnt available
            fallbacks = [
                f"I was gonna roast you {person_name} but my AI brain is offline. Consider yourself lucky.",
                f"Hey {person_name}, I cant connect to my roast engine. That's the nicest thing that'll happen to you today.",
                f"My roast module crashed looking at you {person_name}. Even my AI gave up.",
                f"{person_name}, I dont need AI to tell you that your fashion sense is a threat to my sensors.",
            ]
            return random.choice(fallbacks)
        
        prompt = roast_prompt(person_name, extra_info)
        
        try:
            response = self.brain.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[VOCODER] gemini error: {e}")
            return f"I tried to roast you {person_name} but even Google's AI crashed. That says something."
    
    def mind_meld(self, user_input):
        """general conversation using gemini
        for when people just wanna chat with jinx"""
        
        if not self.brain:
            # basic offline responses
            simple_responses = {
                "how are you": "Im a robot running on 3750 rupees worth of parts. How do you think?",
                "what are you": "Im JINX. Judgmental Intelligence with Neural eXecution. Basically a sarcastic robot.",
                "who made you": "A sleep deprived BTech student with more ambition than budget.",
                "what can you do": "I can see faces, hear sounds, roast people, play music, and judge everyone. So basically everything important.",
                "hello": "Hey! Whats up?",
                "hi": "Hi! Need something or just checking if Im alive?",
                "thank you": "Youre welcome. I accept compliments and electricity as payment.",
                "thanks": "No problem. Tell your friends about me.",
            }
            
            # check if any key matches
            lower_input = user_input.lower()
            for key, response in simple_responses.items():
                if key in lower_input:
                    return response
            
            return "My AI brain is offline right now. Try again later or ask something simpler."
        
        prompt = chat_prompt(user_input)
        
        try:
            response = self.brain.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[VOCODER] gemini chat error: {e}")
            return "My neural network is buffering. Happens to the best of us."
    
    # ============================================
    # COMMAND PROCESSING
    # ============================================
    
    def parse_order(self, text):
        """figure out what the user wants and do it
        this is basically a big if/elif chain
        not the most elegant but it works and its readable"""
        
        text = text.lower().strip()
        print(f"[COMMAND] processing: '{text}'")
        self.db.add_syslog("VOCODER", f"command: {text}")
        
        # --- WAKE UP ---
        if any(w in text for w in ["wake up", "good morning", "hello", "hey"]):
            self.vocalize(say("wake_up"))
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "happy"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "cyan_pulse"}))
            # play boot sound effect
            self.syn.publish(TOPICS["sound"], json.dumps({"sfx": 1}))
        
        # --- SENTINEL MODE ---
        elif any(w in text for w in ["guard", "sentinel", "security", "watch", "patrol"]):
            self.current_mode = "sentinel"
            self.vocalize(say("sentinel_on"))
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "scanning"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "blue_pulse"}))
            self.syn.publish(TOPICS["mode"], json.dumps({"mode": "sentinel"}))
            self.syn.publish(TOPICS["sound"], json.dumps({"sfx": 2}))  # alert sound
        
        # --- BUDDY MODE ---
        elif any(w in text for w in ["buddy", "normal", "chill", "relax", "friend"]):
            self.current_mode = "buddy"
            self.vocalize("Back to buddy mode. Missed being chill.")
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "happy"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "purple_breathe"}))
            self.syn.publish(TOPICS["mode"], json.dumps({"mode": "buddy"}))
        
        # --- ROAST ---
        elif "roast" in text:
            # try to extract a name from the command
            # "roast amit" -> name = "amit"
            name = text.replace("roast", "").replace("him", "").replace("her", "").strip()
            
            if not name and self.last_detected_person:
                name = self.last_detected_person
            if not name:
                name = "this person"
            
            # dramatic buildup
            self.vocalize(say("roast_prefix"))
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "roast"}))
            
            # small pause for dramatic effect
            time.sleep(0.5)
            
            # the actual roast
            roast = self.incinerate(name)
            self.vocalize(roast)
            
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "party"}))
            self.syn.publish(TOPICS["sound"], json.dumps({"sfx": 3}))  # happy sound
            self.db.add_syslog("VOCODER", f"roasted: {name}")
        
        # --- PLAY MUSIC ---
        elif any(w in text for w in ["play music", "play song", "play some"]):
            search = text
            for word in ["play", "music", "song", "some", "jinx"]:
                search = search.replace(word, "")
            search = search.strip()
            
            if not search:
                search = "cyberpunk ambient music"
            
            self.vocalize(say("music"))
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "music"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "rainbow"}))
            
            self.summon_music(search)
        
        # --- STOP MUSIC ---
        elif any(w in text for w in ["stop music", "quiet", "shut up", "silence"]):
            self.vocalize("Fine. Silence it is.")
            # TODO: implement music stop via pygame
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "neutral"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "purple_breathe"}))
        
        # --- LED CONTROL ---
        elif any(w in text for w in ["light", "led", "color", "colour"]):
            color_map = {
                "red": "solid_red",
                "blue": "solid_blue",
                "green": "solid_green",
                "purple": "purple_breathe",
                "pink": "solid_pink",
                "white": "solid_white",
                "off": "off",
                "party": "party",
                "rainbow": "rainbow",
                "cyan": "solid_cyan",
            }
            
            matched = False
            for color_name, mode in color_map.items():
                if color_name in text:
                    self.syn.publish(TOPICS["led"], json.dumps({"mode": mode}))
                    responses = [
                        f"{color_name.title()}. Good choice.",
                        f"Setting {color_name}. Very aesthetic.",
                        f"{color_name.title()} it is. I approve.",
                    ]
                    self.vocalize(random.choice(responses))
                    matched = True
                    break
            
            if not matched:
                self.vocalize("What color? I know red, blue, green, purple, cyan, rainbow, and party.")
        
        # --- MOVEMENT ---
        elif any(w in text for w in ["come here", "forward", "come", "approach"]):
            self.vocalize("On my way!")
            self.syn.publish(TOPICS["motor"], json.dumps({
                "action": "forward", "duration": 2000, "speed": 180
            }))
        
        elif any(w in text for w in ["go back", "back", "reverse", "retreat"]):
            self.vocalize("Backing up. Beep beep.")
            self.syn.publish(TOPICS["motor"], json.dumps({
                "action": "backward", "duration": 2000, "speed": 150
            }))
        
        elif any(w in text for w in ["turn left", "left"]):
            self.syn.publish(TOPICS["motor"], json.dumps({
                "action": "left", "duration": 1000, "speed": 150
            }))
        
        elif any(w in text for w in ["turn right", "right"]):
            self.syn.publish(TOPICS["motor"], json.dumps({
                "action": "right", "duration": 1000, "speed": 150
            }))
        
        elif any(w in text for w in ["stop", "halt", "freeze"]):
            self.vocalize("Stopping.")
            self.syn.publish(TOPICS["motor"], json.dumps({"action": "stop"}))
        
        # --- REGISTER FACE ---
        elif "register" in text or "remember" in text:
            # "register amit" or "remember this face as amit"
            name = text
            for word in ["register", "remember", "this", "face", "as", "jinx"]:
                name = name.replace(word, "")
            name = name.strip()
            
            if name:
                self.vocalize(f"Alright, saving face as {name}. Look at my camera.")
                self.syn.publish(TOPICS["command"], json.dumps({
                    "action": "register_face", "name": name, "label": "safe"
                }))
                time.sleep(2)  # give camera time to capture
                self.vocalize(f"Got it. I'll remember you, {name}. Probably.")
            else:
                self.vocalize("Register who? Give me a name.")
        
        # --- STATUS ---
        elif any(w in text for w in ["status", "how are you", "battery", "health"]):
            self.vocalize("All systems nominal. I think. Let me check.")
            # request battery info from esp32
            # the response comes via mqtt, dashboard shows it
            self.syn.publish(TOPICS["command"], json.dumps({"action": "status_report"}))
        
        # --- GOODNIGHT ---
        elif any(w in text for w in ["goodnight", "good night", "sleep", "shutdown", "bye"]):
            self.vocalize(say("goodnight"))
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "sleepy"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "fade_out"}))
            self.syn.publish(TOPICS["sound"], json.dumps({"sfx": 5}))  # sleepy sound
            # dont actually kill the system, just go to sleep mode
            # can still be woken up with wake word
        
        # --- GENERAL CHAT (fallback) ---
        else:
            response = self.mind_meld(text)
            self.vocalize(response)
    
    # ============================================
    # MUSIC
    # ============================================
    
    def summon_music(self, query):
        """search and play music using yt-dlp
        runs in background so it doesnt block everything"""
        
        def _play(q):
            try:
                print(f"[VOCODER] searching for: {q}")
                
                # download audio only
                result = subprocess.run([
                    "yt-dlp",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "5",  # lower quality = faster
                    "-o", "/tmp/jinx_music.mp3",
                    "--no-playlist",
                    "--default-search", "ytsearch1",
                    q
                ], capture_output=True, text=True, timeout=30)
                
                if os.path.exists("/tmp/jinx_music.mp3"):
                    # play with pygame or mpv or whatever works
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load("/tmp/jinx_music.mp3")
                        pygame.mixer.music.play()
                        print("[VOCODER] music playing")
                    except:
                        # fallback to system player
                        subprocess.Popen(["mpv", "--no-video", "/tmp/jinx_music.mp3"])
                        print("[VOCODER] playing via mpv")
                else:
                    print("[VOCODER] download failed")
                    self.vocalize_async("Couldnt find that song. My taste is better anyway.")
                    
            except subprocess.TimeoutExpired:
                print("[VOCODER] music search timed out")
                self.vocalize_async("Taking too long to find that. Try something else?")
            except Exception as e:
                print(f"[VOCODER] music error: {e}")
                self.vocalize_async("Music system broke. I blame the internet.")
        
        # run in background thread
        t = threading.Thread(target=_play, args=(query,), daemon=True)
        t.start()
    
    # ============================================
    # EARS - listening
    # ============================================
    
    def eavesdrop(self):
        """main listening loop
        waits for wake word 'jinx' then processes command
        
        flow:
        1. listen for any speech
        2. check if 'jinx' is in it
        3. if yes, extract the command part
        4. if command is empty, ask 'yes?' and listen again
        5. process the command
        6. go back to step 1
        """
        
        print(f"[VOCODER] listening for wake word: '{self.wake_word}'")
        print("[VOCODER] say 'jinx <command>' to interact")
        
        while self.alive:
            # dont listen while speaking (would hear ourselves)
            if self.is_speaking:
                time.sleep(0.1)
                continue
            
            try:
                with self.mic as source:
                    # timeout=5 means give up after 5 seconds of silence
                    # phrase_time_limit=10 means max 10 seconds of speech
                    audio = self.ear.listen(source, timeout=5, phrase_time_limit=10)
                
                # try to recognize what was said
                # using google's free api (needs internet)
                text = self.ear.recognize_google(audio).lower()
                print(f"[HEARD] {text}")
                
                # check for wake word
                if self.wake_word not in text:
                    continue  # not talking to us, ignore
                
                # extract command (everything after 'jinx')
                parts = text.split(self.wake_word, 1)
                command = parts[1].strip() if len(parts) > 1 else ""
                
                if command:
                    # got a command, process it
                    self.parse_order(command)
                else:
                    # just said "jinx" with nothing after
                    # ask whats up and listen for follow up
                    responses = [
                        "Yes?", "Im listening.", "What do you need?",
                        "You called?", "Whats up?",
                    ]
                    self.vocalize(random.choice(responses))
                    self.syn.publish(TOPICS["eyes"], json.dumps({"state": "neutral"}))
                    
                    # listen for follow up command
                    try:
                        with self.mic as source:
                            followup = self.ear.listen(source, timeout=5, phrase_time_limit=10)
                        followup_text = self.ear.recognize_google(followup).lower()
                        print(f"[FOLLOW UP] {followup_text}")
                        self.parse_order(followup_text)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        self.vocalize("Nothing? Okay then.")
                        self.syn.publish(TOPICS["eyes"], json.dumps({"state": "happy"}))
                    except Exception as e:
                        print(f"[VOCODER] followup error: {e}")
            
            except sr.WaitTimeoutError:
                # nobody said anything for 5 seconds, thats fine
                pass
            
            except sr.UnknownValueError:
                # heard something but couldnt understand it
                # happens a lot, dont worry about it
                pass
            
            except sr.RequestError as e:
                # google api failed (probably no internet)
                print(f"[VOCODER] google STT error: {e}")
                print("[VOCODER] check internet connection")
                time.sleep(5)  # wait before retrying
            
            except Exception as e:
                # something unexpected
                print(f"[VOCODER] error: {e}")
                time.sleep(1)
        
        print("[VOCODER] stopped listening")
    
    def eavesdrop_offline(self):
        """offline version using vosk instead of google
        doesnt need internet but less accurate
        use this as backup if wifi dies during demo"""
        
        try:
            from vosk import Model, KaldiRecognizer
        except:
            print("[VOCODER] vosk not installed, cant do offline recognition")
            return
        
        if not os.path.exists(VOSK_MODEL_PATH):
            print(f"[VOCODER] vosk model not found at {VOSK_MODEL_PATH}")
            print("[VOCODER] download from: https://alphacephei.com/vosk/models")
            return
        
        import pyaudio
        
        model = Model(VOSK_MODEL_PATH)
        rec = KaldiRecognizer(model, 16000)
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )
        
        print("[VOCODER] offline mode active (vosk)")
        
        while self.alive:
            if self.is_speaking:
                time.sleep(0.1)
                continue
            
            data = stream.read(4096, exception_on_overflow=False)
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                
                if text and self.wake_word in text:
                    parts = text.split(self.wake_word, 1)
                    command = parts[1].strip() if len(parts) > 1 else ""
                    
                    if command:
                        self.parse_order(command)
                    else:
                        self.vocalize("Yes?")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    # ============================================
    # LIFECYCLE
    # ============================================
    
    def flatline(self):
        """shutdown voice system"""
        self.alive = False
        self.syn.loop_stop()
        self.db.close()
        print("[VOCODER] voice system offline")


# test standalone
if __name__ == "__main__":
    v = Vocoder()
    
    # test tts
    print("\n--- testing voice output ---")
    v.vocalize(say("wake_up"))
    
    # test gemini
    if v.brain:
        print("\n--- testing roast ---")
        roast = v.incinerate("test person")
        print(f"roast: {roast}")
        v.vocalize(roast)
        
        print("\n--- testing chat ---")
        response = v.mind_meld("what can you do")
        print(f"chat: {response}")
    
    # test listening
    print("\n--- testing listening ---")
    print("say 'jinx hello' or 'jinx roast me'")
    print("press ctrl+c to stop")
    
    try:
        v.eavesdrop()
    except KeyboardInterrupt:
        print("\nstopped")
    
    v.flatline()