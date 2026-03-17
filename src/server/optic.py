"""
OPTIC.PY — VISUAL CORTEX
Handles: Camera feed, face detection/recognition, pose estimation,
         hand gesture recognition, 468-point face mesh, object detection,
         head tracking commands, display frame publishing.
"""

import cv2
import time
import json
import base64
import threading
import numpy as np
from datetime import datetime
from pathlib import Path

import face_recognition
import mediapipe as mp
from ultralytics import YOLO

import dna
from blackbox import Blackbox
from synapse  import Synapse


class Optic:
    def __init__(self, synapse: Synapse, blackbox: Blackbox):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.running   = False
        self.mode      = dna.DEFAULT_MODE

        # Camera
        self.cap       = None
        self.frame     = None
        self.frame_lock = threading.Lock()

        # ML Models
        self.yolo       = None
        self.mp_face    = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.7)
        self.mp_mesh    = mp.solutions.face_mesh.FaceMesh(max_num_faces=5, refine_landmarks=True)
        self.mp_pose    = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self.mp_hands   = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_draw    = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        # Face recognition database
        self.known_encodings = []
        self.known_names     = []
        self.known_labels    = {}   # name -> "safe" | "threat"

        # State tracking
        self.detected_faces      = []
        self.current_target_face = None  # For head tracking (x, y normalized)
        self.gesture_state        = "none"
        self.last_frame_time      = 0
        self.frame_interval       = 1.0 / dna.VISION_FPS

        # Colors (BGR)
        self.COLORS = {
            "safe":    (0, 255, 100),   # Neon green
            "unknown": (255, 200, 0),   # Cyan-ish
            "threat":  (0, 50, 255),    # Red
            "object":  (200, 0, 255),   # Purple
        }

        self._load_face_db()
        self._load_yolo()

        # Subscribe to mode changes
        synapse.subscribe(dna.TOPIC["mode"], self._on_mode_change)
        synapse.subscribe(dna.TOPIC["web_command"], self._on_web_command)

    def _load_yolo(self):
        try:
            self.yolo = YOLO("yolov5n.pt")
            print("  [OPTIC] YOLOv5-nano loaded")
        except Exception as e:
            print(f"  [OPTIC] YOLO load failed: {e}")

    def _load_face_db(self):
        """Load all face images from known_faces/ directory."""
        faces_dir = Path(dna.KNOWN_FACES_DIR)
        if not faces_dir.exists():
            faces_dir.mkdir(parents=True)
            return

        for img_path in faces_dir.glob("*.jpg"):
            name = img_path.stem
            try:
                img      = face_recognition.load_image_file(str(img_path))
                encs     = face_recognition.face_encodings(img)
                if encs:
                    self.known_encodings.append(encs[0])
                    self.known_names.append(name)
                    label = dna.FACE_LABELS.get(name, "unknown")
                    self.known_labels[name] = label
            except Exception as e:
                print(f"  [OPTIC] Failed to load {name}: {e}")

        print(f"  [OPTIC] Loaded {len(self.known_names)} faces: {self.known_names}")

    def register_face(self, name: str, label: str = "safe") -> bool:
        """Register current frame's face into the database."""
        if self.frame is None:
            return False
        rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if not encs:
            return False

        # Save image
        save_path = Path(dna.KNOWN_FACES_DIR) / f"{name}.jpg"
        cv2.imwrite(str(save_path), self.frame)

        # Add to runtime database
        self.known_encodings.append(encs[0])
        self.known_names.append(name)
        self.known_labels[name] = label
        dna.FACE_LABELS[name] = label

        self.blackbox.log_event("FACE_REGISTERED", {"name": name, "label": label})
        return True

    def _on_mode_change(self, payload: str):
        self.mode = payload.strip()

    def _on_web_command(self, payload: str):
        try:
            cmd = json.loads(payload)
            if cmd.get("action") == "register_face":
                self.register_face(cmd["name"], cmd.get("label", "safe"))
        except Exception:
            pass

    def _open_camera(self):
        """Open IP camera stream with retries."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                cap = cv2.VideoCapture(dna.CAMERA_URL)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if cap.isOpened():
                    self.cap = cap
                    print(f"  [OPTIC] Camera connected: {dna.CAMERA_URL}")
                    return True
            except Exception:
                pass
            print(f"  [OPTIC] Camera attempt {attempt+1}/{max_retries} failed, retrying...")
            time.sleep(3)
        print("  [OPTIC] WARNING: Could not connect to camera. Using local webcam.")
        self.cap = cv2.VideoCapture(0)
        return self.cap.isOpened()

    def phantom_trace(self, rgb_frame) -> list:
        """Detect and recognize faces. Returns list of face dicts."""
        results = []
        small   = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
        locs    = face_recognition.face_locations(small)
        encs    = face_recognition.face_encodings(small, locs)

        for enc, loc in zip(encs, locs):
            name, label = "Unknown", "unknown"

            if self.known_encodings:
                dists   = face_recognition.face_distance(self.known_encodings, enc)
                best_idx = int(np.argmin(dists))
                if dists[best_idx] < dna.FACE_TOLERANCE:
                    name  = self.known_names[best_idx]
                    label = self.known_labels.get(name, "safe")

            # Scale back up (we processed at 0.5x)
            top, right, bottom, left = [v * 2 for v in loc]
            results.append({
                "name": name, "label": label,
                "box": (left, top, right, bottom),
                "center": ((left + right) // 2, (top + bottom) // 2),
            })

        return results

    def bone_rip(self, rgb_frame, display_frame) -> np.ndarray:
        """Pose estimation — draws neon skeleton overlay."""
        results = self.mp_pose.process(rgb_frame)
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                display_frame, results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_draw.DrawingSpec(
                    color=(0, 255, 200), thickness=2, circle_radius=3),
                connection_drawing_spec=self.mp_draw.DrawingSpec(
                    color=(0, 200, 255), thickness=2),
            )
        return display_frame

    def wireframe(self, rgb_frame, display_frame) -> np.ndarray:
        """468-point face mesh — cyberpunk scan effect."""
        results = self.mp_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            for lm in results.multi_face_landmarks:
                self.mp_draw.draw_landmarks(
                    display_frame, lm,
                    mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_draw_styles.get_default_face_mesh_tesselation_style(),
                )
        return display_frame

    def read_hands(self, rgb_frame) -> str:
        """Hand gesture recognition — returns gesture string."""
        results = self.mp_hands.process(rgb_frame)
        if not results.multi_hand_landmarks:
            return "none"

        for hand_landmarks in results.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            # Simple gesture detection by finger state
            tips  = [4, 8, 12, 16, 20]  # Thumb, index, middle, ring, pinky tips
            bases = [3, 6, 10, 14, 18]  # Corresponding base joints

            fingers_up = []
            for tip, base in zip(tips, bases):
                fingers_up.append(lm[tip].y < lm[base].y)

            count = sum(fingers_up)
            # Map common gestures
            if count == 0:   return "fist"
            if count == 5:   return "open_hand"
            if fingers_up[1] and not any(fingers_up[2:]):  return "point"
            if fingers_up[1] and fingers_up[2] and not fingers_up[0]: return "peace"
            if fingers_up[0] and fingers_up[4] and count == 2: return "rock"

        return "none"

    def _draw_face_box(self, frame, face: dict) -> np.ndarray:
        """Draw colored bounding box + label for detected face."""
        label = face["label"]
        color = self.COLORS.get(label, self.COLORS["unknown"])
        l, t, r, b = face["box"]
        name_text = face["name"]
        tag = {"safe": "✓ SAFE", "threat": "⚠ THREAT", "unknown": "? UNKNOWN"}[label]

        # Main box
        cv2.rectangle(frame, (l, t), (r, b), color, 2)

        # Corner accents (cyberpunk style)
        clen = 15
        for cx, cy, dx, dy in [(l, t, 1, 1), (r, t, -1, 1), (l, b, 1, -1), (r, b, -1, -1)]:
            cv2.line(frame, (cx, cy), (cx + dx * clen, cy), color, 3)
            cv2.line(frame, (cx, cy), (cx, cy + dy * clen), color, 3)

        # Label background
        label_txt = f"  {name_text} | {tag}  "
        (tw, th), _ = cv2.getTextSize(label_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (l, t - th - 10), (l + tw, t), color, -1)
        cv2.putText(frame, label_txt, (l, t - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        return frame

    def _publish_head_track(self, faces: list, frame_w: int, frame_h: int):
        """Send head servo commands to track nearest face."""
        if not faces or not dna.HEAD_TRACK_ENABLED:
            return
        # Track largest face (closest person)
        largest = max(faces, key=lambda f: (f["box"][2]-f["box"][0]) * (f["box"][3]-f["box"][1]))
        cx, cy  = largest["center"]
        # Normalize to 0-1
        nx, ny  = cx / frame_w, cy / frame_h
        self.synapse.publish(dna.TOPIC["head_track"], json.dumps({"x": nx, "y": ny}))
        self.synapse.publish(dna.TOPIC["eye_track"],  json.dumps({"x": nx, "y": ny}))

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Run all vision models on one frame and return annotated result."""
        display = frame.copy()
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w    = frame.shape[:2]

        # Face detection + recognition
        faces = self.phantom_trace(rgb)
        self.detected_faces = faces

        for face in faces:
            display = self._draw_face_box(display, face)

            # Alert on threats
            if face["label"] == "threat":
                self.synapse.publish(dna.TOPIC["eyes"], "threat")
                self.synapse.publish(dna.TOPIC["led"],  "threat")
                self.synapse.publish(dna.TOPIC["buzzer"], "on")
                alert_msg = f"THREAT DETECTED: {face['name']}"
                self.synapse.publish(dna.TOPIC["alerts"], alert_msg)
                self.blackbox.log_event("THREAT_DETECTED", {"name": face["name"]}, frame=display)

            elif face["label"] == "unknown":
                self.synapse.publish(dna.TOPIC["eyes"], "scanning")
                self.synapse.publish(dna.TOPIC["led"],  "scan")

        # Head tracking
        self._publish_head_track(faces, w, h)

        # Mode-specific overlays
        if self.mode == dna.Mode.SENTINEL:
            display = self.bone_rip(rgb, display)
            # YOLO object detection
            if self.yolo:
                results = self.yolo(frame, verbose=False, conf=dna.YOLO_CONFIDENCE)
                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls_name = r.names[int(box.cls[0])]
                        if cls_name == "person":
                            continue  # Already handled by face recog
                        cv2.rectangle(display, (x1, y1), (x2, y2), self.COLORS["object"], 1)
                        cv2.putText(display, cls_name, (x1, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.COLORS["object"], 1)

        elif self.mode == dna.Mode.BUDDY:
            # Show pose skeleton when someone is dancing / moving
            display = self.bone_rip(rgb, display)

        # Gesture recognition
        gesture = self.read_hands(rgb)
        if gesture != self.gesture_state and gesture != "none":
            self.gesture_state = gesture
            self.synapse.publish(dna.TOPIC["command"],
                                 json.dumps({"type": "gesture", "value": gesture}))

        # HUD overlay
        timestamp = datetime.now().strftime("%H:%M:%S")
        mode_txt  = f"MODE: {self.mode.upper()}"
        fps_txt   = f"FPS: {1.0/max(self.frame_interval, 0.001):.0f}"

        cv2.putText(display, mode_txt,  (10, 25),  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 1)
        cv2.putText(display, timestamp, (10, 50),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        cv2.putText(display, fps_txt,   (10, 75),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 100), 1)
        cv2.putText(display, f"FACES: {len(faces)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)

        return display

    def get_current_frame(self) -> np.ndarray | None:
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    def run(self):
        """Main vision loop."""
        self.running = True
        if not self._open_camera():
            print("  [OPTIC] ERROR: No camera available. Vision disabled.")
            return

        print("  [OPTIC] Vision loop started")

        while self.running:
            loop_start = time.time()

            ret, frame = self.cap.read()
            if not ret:
                print("  [OPTIC] Lost camera feed, reconnecting...")
                time.sleep(2)
                self._open_camera()
                continue

            with self.frame_lock:
                self.frame = frame

            try:
                annotated = self._process_frame(frame)

                # Encode and publish to dashboard/tablet
                _, jpeg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 70])
                b64     = base64.b64encode(jpeg.tobytes()).decode("utf-8")
                self.synapse.publish(dna.TOPIC["frame"], b64)

            except Exception as e:
                print(f"  [OPTIC] Frame processing error: {e}")

            elapsed = time.time() - loop_start
            sleep_t = max(0, self.frame_interval - elapsed)
            time.sleep(sleep_t)

        if self.cap:
            self.cap.release()
        print("  [OPTIC] Vision loop stopped")

    def stop(self):
        self.running = False
