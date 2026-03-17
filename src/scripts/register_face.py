"""
REGISTER_FACE.PY — Add faces to JINX's recognition database
Usage:
    python scripts/register_face.py --name "YourName" --label safe
    python scripts/register_face.py --name "BadPerson" --label threat
    python scripts/register_face.py --file path/to/photo.jpg --name "Someone"
    python scripts/register_face.py --live --name "YourName"  (capture from camera)
"""

import sys
import os
import argparse
import shutil
import cv2
import face_recognition
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
import dna


def register_from_file(image_path: str, name: str, label: str):
    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found: {image_path}")
        return False

    img = face_recognition.load_image_file(str(path))
    encs = face_recognition.face_encodings(img)
    if not encs:
        print("[ERROR] No face detected in image. Use a clear, front-facing photo.")
        return False

    dest = Path(dna.KNOWN_FACES_DIR) / f"{name}.jpg"
    shutil.copy2(str(path), str(dest))
    print(f"[OK] Registered {name} ({label}) → {dest}")
    return True


def register_from_camera(name: str, label: str):
    print(f"[INFO] Opening camera for live capture...")
    print("[INFO] Press SPACE to capture, Q to quit")

    cap = cv2.VideoCapture(dna.CAMERA_URL)
    if not cap.isOpened():
        print("[WARN] Could not open IP camera, trying local webcam...")
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] No camera available")
        return False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show face detection preview
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        for (top, right, bottom, left) in locs:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 100), 2)

        cv2.putText(frame, f"Registering: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 200), 2)
        cv2.putText(frame, "SPACE=capture  Q=quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.imshow("Register Face", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if not locs:
                print("[WARN] No face detected, try again")
                continue
            dest = Path(dna.KNOWN_FACES_DIR) / f"{name}.jpg"
            cv2.imwrite(str(dest), frame)
            print(f"[OK] Captured and registered {name} ({label}) → {dest}")
            cap.release()
            cv2.destroyAllWindows()
            return True
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False


def main():
    parser = argparse.ArgumentParser(description="Register a face in JINX's database")
    parser.add_argument("--name",  required=True, help="Person's name (no spaces)")
    parser.add_argument("--label", default="safe", choices=["safe", "threat"], help="Label for this person")
    parser.add_argument("--file",  help="Path to photo file")
    parser.add_argument("--live",  action="store_true", help="Capture from camera")
    args = parser.parse_args()

    # Sanitize name
    name = args.name.strip().replace(" ", "_").lower()

    # Ensure directory exists
    Path(dna.KNOWN_FACES_DIR).mkdir(parents=True, exist_ok=True)

    if args.file:
        success = register_from_file(args.file, name, args.label)
    elif args.live:
        success = register_from_camera(name, args.label)
    else:
        print("[ERROR] Specify --file <path> or --live")
        sys.exit(1)

    if success:
        print(f"\n[DONE] Add this to server/dna.py FACE_LABELS:")
        print(f'  "{name}": "{args.label}",')
        print("\n[NOTE] Restart JINX or run genesis.py for changes to take effect.")
    else:
        print("[FAILED] Registration unsuccessful.")
        sys.exit(1)


if __name__ == "__main__":
    main()
