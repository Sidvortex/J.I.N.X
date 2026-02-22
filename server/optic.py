# optic.py - jinx's eyes and visual cortex
# this is the big one, handles everything camera related
# face detection, recognition, pose, mesh, object detection
# took me forever to get the glow effect right ngl

import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import json
import os
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# using relative imports would be "proper" but this works fine
from dna import *
from blackbox import JinxDB
from psyche import say

class OpticNerve:
    def __init__(self):
        print("[OPTIC] waking up the eye...")
        
        # mqtt for talking to esp32
        self.syn = mqtt.Client()
        self.syn.connect(LAPTOP_IP, MQTT_PORT)
        
        # database
        self.db = JinxDB(DB_PATH)
        
        # mediapipe stuff
        # face mesh - the 468 point thing that looks insane
        self.mp_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_mesh.FaceMesh(
            max_num_faces=5,
            min_detection_confidence=FACE_DETECTION_CONFIDENCE
        )
        
        # pose - skeleton tracking
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=POSE_DETECTION_CONFIDENCE,
            min_tracking_confidence=0.5
        )
        
        # hands - for gesture control
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        
        # face recognition - who are you
        self.memory_bank = {}   # name -> face encoding
        self.labels = {}        # name -> safe/threat
        self._load_faces()
        
        # yolo - object detection
        # importing here cuz its heavy and i dont want it 
        # slowing down startup if something fails
        try:
            from ultralytics import YOLO
            self.yolo = YOLO('yolov5n.pt')
            print("[OPTIC] yolo loaded")
        except Exception as e:
            print(f"[OPTIC] yolo failed to load: {e}")
            self.yolo = None
        
        # camera
        self.feed = None
        self.state = "buddy"  # current mode
        self.phantoms = []    # detected faces this frame
        self.incident_log = []
        
        # tracking
        self.last_face_pos = (50, 50)  # normalized x,y for head tracking
        self.frames_without_face = 0
        
        print("[OPTIC] eye is ready")
    
    def _load_faces(self):
        """load all known faces from the folder"""
        os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
        
        for f in os.listdir(KNOWN_FACES_DIR):
            if not f.endswith(('.jpg', '.png', '.jpeg')):
                continue
            
            name = f.rsplit('.', 1)[0]  # filename without extension
            path = os.path.join(KNOWN_FACES_DIR, f)
            
            try:
                img = face_recognition.load_image_file(path)
                encs = face_recognition.face_encodings(img)
                if encs:
                    self.memory_bank[name] = encs[0]
                    self.labels[name] = FACE_LABELS.get(name, "safe")
                    print(f"[OPTIC] loaded face: {name} ({self.labels[name]})")
                else:
                    print(f"[OPTIC] no face found in {f}, skipping")
            except Exception as e:
                print(f"[OPTIC] error loading {f}: {e}")
        
        print(f"[OPTIC] {len(self.memory_bank)} faces in memory bank")
    
    def register_face(self, frame, name, label="safe"):
        """add a new face to the database"""
        encs = face_recognition.face_encodings(frame)
        if not encs:
            print(f"[OPTIC] cant find face to register")
            return False
        
        self.memory_bank[name] = encs[0]
        self.labels[name] = label
        
        # save the image
        path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
        cv2.imwrite(path, frame)
        
        self.db.add_face(name, label, 1.0, "registered")
        print(f"[OPTIC] registered: {name} as {label}")
        return True
    
    def connect_camera(self, source=None):
        """connect to camera feed"""
        src = source or CAMERA_URL
        print(f"[OPTIC] connecting to camera: {src}")
        
        self.feed = cv2.VideoCapture(src)
        
        if not self.feed.isOpened():
            print("[OPTIC] camera failed! trying laptop webcam...")
            self.feed = cv2.VideoCapture(0)
        
        if self.feed.isOpened():
            print("[OPTIC] camera connected")
            return True
        else:
            print("[OPTIC] no camera available :(")
            return False
    
    def void_filter(self, frame):
        """darken the frame for that cyberpunk look"""
        # this one line took me embarrassingly long to figure out
        return cv2.addWeighted(frame, 0.35, np.zeros_like(frame), 0.65, 0)
    
    def plasma_bleed(self, layer, frame):
        """add glow effect to a layer and merge with frame
        basically blur the bright stuff and add it back
        makes everything look like tron"""
        glow = cv2.GaussianBlur(layer, (15, 15), 0)
        result = cv2.add(frame, glow)
        result = cv2.add(result, layer)
        return result
    
    def wireframe(self, frame, rgb):
        """draw 468 point face mesh - looks absolutely insane
        this is what makes people go 'woah' at demos"""
        results = self.mesh.process(rgb)
        
        if not results.multi_face_landmarks:
            return frame
        
        for face_lm in results.multi_face_landmarks:
            for lm in face_lm.landmark:
                x = int(lm.x * frame.shape[1])
                y = int(lm.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, NEON_CYAN, -1)
        
        return frame
    
    def bone_rip(self, frame, rgb):
        """draw pose skeleton with neon glow
        33 keypoints connected with glowing lines
        looks like that one scene from every sci fi movie"""
        results = self.pose.process(rgb)
        
        if not results.pose_landmarks:
            return frame
        
        h, w = frame.shape[:2]
        lms = results.pose_landmarks
        
        # make a separate layer for the glow trick
        skel_layer = np.zeros_like(frame)
        
        # draw connections
        for conn in self.mp_pose.POSE_CONNECTIONS:
            p1 = lms.landmark[conn[0]]
            p2 = lms.landmark[conn[1]]
            x1, y1 = int(p1.x * w), int(p1.y * h)
            x2, y2 = int(p2.x * w), int(p2.y * h)
            cv2.line(skel_layer, (x1, y1), (x2, y2), NEON_MAGENTA, 3)
        
        # draw joints
        for lm in lms.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(skel_layer, (x, y), 4, NEON_CYAN, -1)
        
        # apply the glow
        frame = self.plasma_bleed(skel_layer, frame)
        
        return frame
    
    def phantom_trace(self, frame, rgb):
        """detect and recognize faces
        color coding: green=safe, blue=unknown, red=threat
        also sends position to esp32 for head tracking"""
        
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)
        
        detected = []
        
        for (top, right, bottom, left), enc in zip(locations, encodings):
            # try to match against known faces
            name = "???"
            color = NEON_BLUE  # unknown = blue
            label = "unknown"
            conf = 0.0
            
            if self.memory_bank:
                matches = face_recognition.compare_faces(
                    list(self.memory_bank.values()), enc,
                    tolerance=FACE_RECOGNITION_TOLERANCE
                )
                dists = face_recognition.face_distance(
                    list(self.memory_bank.values()), enc
                )
                
                if True in matches:
                    best = np.argmin(dists)
                    name = list(self.memory_bank.keys())[best]
                    conf = 1.0 - dists[best]
                    label = self.labels.get(name, "safe")
                    
                    if label == "safe":
                        color = NEON_GREEN
                    elif label == "threat":
                        color = NEON_RED
            
            # draw the box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # name tag background
            cv2.rectangle(frame, (left, bottom), (right, bottom + 25), color, -1)
            cv2.putText(frame, f"{name} {conf:.0%}", (left + 4, bottom + 18),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)
            
            # send eye/led commands based on who we see
            if label == "safe" and name != "???":
                self.syn.publish(TOPICS["eyes"], json.dumps({"state": "love"}))
                self.syn.publish(TOPICS["led"], json.dumps({"mode": "green_flash"}))
            elif label == "threat":
                self.syn.publish(TOPICS["eyes"], json.dumps({"state": "threat"}))
                self.syn.publish(TOPICS["led"], json.dumps({"mode": "red_strobe"}))
                self.syn.publish(TOPICS["buzzer"], json.dumps({"beeps": 3}))
                self.havoc_ping("THREAT", name, conf)
            elif name == "???":
                self.syn.publish(TOPICS["eyes"], json.dumps({"state": "scanning"}))
                self.havoc_ping("UNKNOWN_FACE", "unidentified", conf)
            
            # head tracking - send face position to esp32
            cx = (left + right) / 2
            cy = (top + bottom) / 2
            nx = int(cx / frame.shape[1] * 100)  # normalize to 0-100
            ny = int(cy / frame.shape[0] * 100)
            self.last_face_pos = (nx, ny)
            self.frames_without_face = 0
            
            # physical head + digital eye tracking
            self.syn.publish(TOPICS["head_track"], json.dumps({"x": nx, "y": ny}))
            self.syn.publish(TOPICS["eye_track"], json.dumps({"x": nx, "y": ny}))
            
            # log it
            self.db.add_face(name, label, conf)
            detected.append({"name": name, "label": label, "conf": conf})
        
        # no faces? count frames and reset head to center eventually
        if not locations:
            self.frames_without_face += 1
            if self.frames_without_face > 30:  # about 1 second
                self.syn.publish(TOPICS["head_track"], json.dumps({"x": 50, "y": 50}))
                self.syn.publish(TOPICS["eyes"], json.dumps({"state": "neutral"}))
        
        self.phantoms = detected
        return frame
    
    def detect_objects(self, frame):
        """yolo object detection - only in sentinel mode
        draws blue boxes around everything it finds"""
        if not self.yolo:
            return frame
        
        results = self.yolo(frame, verbose=False, conf=0.4)
        
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.yolo.names[cls]
                
                # skip 'person' since face detection handles that
                if label == "person":
                    continue
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), NEON_BLUE, 2)
                cv2.putText(frame, f"{label} {conf:.0%}", (x1, y1 - 8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_BLUE, 1)
        
        return frame
    
    def burn_hud(self, frame, face_count):
        """overlay the cyberpunk HUD on the frame
        adds top bar, bottom bar, corner brackets
        the little details that make it look pro"""
        h, w = frame.shape[:2]
        
        # top bar
        cv2.rectangle(frame, (0, 0), (w, 28), (15, 15, 15), -1)
        mode_text = f"JINX // {self.state.upper()} MODE"
        cv2.putText(frame, mode_text, (10, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_CYAN, 1)
        
        # timestamp
        ts = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, ts, (w - 90, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_GREEN, 1)
        
        # bottom bar
        cv2.rectangle(frame, (0, h - 28), (w, h), (15, 15, 15), -1)
        cv2.putText(frame, f"FACES: {face_count}", (10, h - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_GREEN, 1)
        cv2.putText(frame, f"PHANTOMS: {len(self.phantoms)}", (150, h - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_CYAN, 1)
        
        # corner brackets - these small things make it look 10x better
        blen = 25
        # top left
        cv2.line(frame, (5, 32), (5, 32 + blen), NEON_CYAN, 2)
        cv2.line(frame, (5, 32), (5 + blen, 32), NEON_CYAN, 2)
        # top right
        cv2.line(frame, (w - 5, 32), (w - 5, 32 + blen), NEON_CYAN, 2)
        cv2.line(frame, (w - 5, 32), (w - 5 - blen, 32), NEON_CYAN, 2)
        # bottom left
        cv2.line(frame, (5, h - 32), (5, h - 32 - blen), NEON_CYAN, 2)
        cv2.line(frame, (5, h - 32), (5 + blen, h - 32), NEON_CYAN, 2)
        # bottom right
        cv2.line(frame, (w - 5, h - 32), (w - 5, h - 32 - blen), NEON_CYAN, 2)
        cv2.line(frame, (w - 5, h - 32), (w - 5 - blen, h - 32), NEON_CYAN, 2)
        
        return frame
    
    def havoc_ping(self, alert_type, details, conf=0.0):
        """trigger an alert - logs it, sends to dashboard"""
        # save screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ss_path = os.path.join(ALERTS_DIR, f"{alert_type}_{timestamp}.jpg")
        os.makedirs(ALERTS_DIR, exist_ok=True)
        
        if self.last_frame is not None:
            cv2.imwrite(ss_path, self.last_frame)
        
        # log to database
        self.db.add_alert(alert_type, details, conf, ss_path)
        
        # send to dashboard
        self.syn.publish(TOPICS["alerts"], json.dumps({
            "type": alert_type,
            "details": details,
            "confidence": conf,
            "time": datetime.now().isoformat()
        }))
        
        print(f"[ALERT] {alert_type}: {details} ({conf:.0%})")
    
    def cortex_scan(self, frame):
        """THE MAIN BRAIN - processes one frame through everything
        this is where all the magic happens
        returns the fully processed cyberpunk frame"""
        
        self.last_frame = frame.copy()  # keep original for screenshots
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # step 1: darken everything (cyberpunk base)
        rendered = self.void_filter(frame)
        
        # step 2: face detection + recognition + color coding
        rendered = self.phantom_trace(rendered, rgb)
        
        # step 3: face mesh (468 glowing dots)
        rendered = self.wireframe(rendered, rgb)
        
        # step 4: pose skeleton (neon bones)
        rendered = self.bone_rip(rendered, rgb)
        
        # step 5: object detection (sentinel mode only)
        if self.state == "sentinel":
            rendered = self.detect_objects(rendered)
        
        # step 6: HUD overlay
        rendered = self.burn_hud(rendered, len(self.phantoms))
        
        return rendered
    
    def run(self, mode="buddy"):
        """main loop - grabs frames, processes, displays
        press q to quit"""
        
        self.state = mode
        
        if not self.connect_camera():
            print("[OPTIC] cant start without camera")
            return
        
        print(f"[OPTIC] running in {mode} mode, press q to quit")
        self.db.add_syslog("OPTIC", f"started in {mode} mode")
        
        while True:
            ret, frame = self.feed.read()
            if not ret:
                # camera hiccup, try again
                time.sleep(0.1)
                continue
            
            # the big one
            rendered = self.cortex_scan(frame)
            
            # send processed frame to dashboard via mqtt
            # compress it first otherwise mqtt dies
            _, buf = cv2.imencode('.jpg', rendered,
                                  [cv2.IMWRITE_JPEG_QUALITY, 55])
            self.syn.publish(TOPICS["frame"], buf.tobytes())
            
            # also show on laptop screen (for debugging/demo)
            cv2.imshow("JINX OPTIC", rendered)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.feed.release()
        cv2.destroyAllWindows()
        print("[OPTIC] eye closed")
    
    def flatline(self):
        """cleanup"""
        if self.feed:
            self.feed.release()
        self.db.close()
        cv2.destroyAllWindows()


# run standalone for testing
if __name__ == "__main__":
    eye = OpticNerve()
    
    # use laptop webcam for testing (0)
    # use phone camera for real (CAMERA_URL)
    eye.connect_camera(0)  # change to CAMERA_URL when phone is ready
    eye.run("buddy")