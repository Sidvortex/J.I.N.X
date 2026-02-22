"""
WEB CONTROL / APP.PY — FLASK CONTROL PANEL
Phone/tablet web interface. Navigate to http://LAPTOP_IP:5000
Features: Live camera feed, mode switching, voice commands, face management,
          document upload, code paste + review, network stats.
"""

import os
import sys
import json
import base64
import threading
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from flask import Flask, render_template, request, jsonify, Response
import paho.mqtt.client as mqtt
import dna

app = Flask(__name__)

# Global state shared between MQTT and web
state = {
    "frame":        None,       # Latest base64 JPEG frame
    "mode":         dna.DEFAULT_MODE,
    "battery_pct":  100,
    "doom_level":   0.0,
    "alerts":       [],         # Recent alerts list
    "network":      {},
    "audio":        {},
    "agent_response": "",
    "code_review":  "",
}

# ── MQTT Client ────────────────────────────────────────────────────────────

mqtt_client = mqtt.Client()

def _on_mqtt_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode("utf-8", errors="ignore")

    if topic == dna.TOPIC["frame"]:
        state["frame"] = payload

    elif topic == dna.TOPIC["battery"]:
        try:
            data = json.loads(payload)
            state["battery_pct"] = int(data.get("percent", 100))
        except Exception:
            pass

    elif topic == dna.TOPIC["doom_level"]:
        try:
            state["doom_level"] = float(payload)
        except Exception:
            pass

    elif topic == dna.TOPIC["alerts"]:
        state["alerts"].insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "msg": payload
        })
        state["alerts"] = state["alerts"][:50]  # Keep last 50

    elif topic == dna.TOPIC["network_stats"]:
        try:
            state["network"] = json.loads(payload)
        except Exception:
            pass

    elif topic == dna.TOPIC["audio"]:
        try:
            state["audio"] = json.loads(payload)
        except Exception:
            pass

    elif topic == dna.TOPIC["command"]:
        try:
            cmd = json.loads(payload)
            if cmd.get("type") == "agent_response":
                state["agent_response"] = cmd.get("response", "")
            elif cmd.get("type") == "code_review_result":
                state["code_review"] = cmd.get("review", "")
        except Exception:
            pass

def _start_mqtt():
    mqtt_client.on_message = _on_mqtt_message
    try:
        mqtt_client.connect(dna.MQTT_BROKER, dna.MQTT_PORT, keepalive=60)
        for topic in dna.TOPIC.values():
            mqtt_client.subscribe(topic)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"[WEB] MQTT connection failed: {e}")

threading.Thread(target=_start_mqtt, daemon=True).start()


# ── Helper ─────────────────────────────────────────────────────────────────

def publish(topic: str, payload):
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    try:
        mqtt_client.publish(topic, str(payload))
    except Exception:
        pass


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    """Polling endpoint for React/JS frontend."""
    return jsonify({
        "mode":         state["mode"],
        "battery_pct":  state["battery_pct"],
        "doom_level":   round(state["doom_level"], 3),
        "alerts":       state["alerts"][:10],
        "network":      state.get("network", {}),
        "audio":        state.get("audio", {}),
        "agent_response": state.get("agent_response", ""),
        "code_review":  state.get("code_review", ""),
    })


@app.route("/api/frame")
def api_frame():
    """Latest camera frame as base64 JPEG."""
    frame = state.get("frame")
    if frame:
        return jsonify({"frame": frame})
    return jsonify({"frame": None})


@app.route("/api/command", methods=["POST"])
def api_command():
    """Send any command to JINX."""
    data   = request.get_json()
    action = data.get("action", "")
    payload = data.get("payload", {})

    if action == "set_mode":
        new_mode = payload.get("mode", dna.DEFAULT_MODE)
        publish(dna.TOPIC["mode"], new_mode)
        state["mode"] = new_mode
        return jsonify({"ok": True})

    elif action == "speak":
        text = payload.get("text", "")
        publish(dna.TOPIC["web_command"], {"action": "speak", "text": text})
        return jsonify({"ok": True})

    elif action == "roast":
        name = payload.get("name", "")
        publish(dna.TOPIC["web_command"], {"action": "roast", "name": name})
        return jsonify({"ok": True})

    elif action == "set_led":
        color = payload.get("color", "white")
        publish(dna.TOPIC["led"], f"color:{color}")
        return jsonify({"ok": True})

    elif action == "motor":
        direction = payload.get("direction", "stop")
        publish(dna.TOPIC["motor"], direction)
        return jsonify({"ok": True})

    elif action == "register_face":
        name  = payload.get("name", "")
        label = payload.get("label", "safe")
        publish(dna.TOPIC["web_command"], {"action": "register_face", "name": name, "label": label})
        return jsonify({"ok": True})

    elif action == "ask_agent":
        question = payload.get("question", "")
        state["agent_response"] = "Thinking..."
        publish(dna.TOPIC["web_command"], {"action": "query", "question": question})
        return jsonify({"ok": True})

    elif action == "review_code":
        code     = payload.get("code", "")
        filename = payload.get("filename", "code.py")
        state["code_review"] = "Reviewing..."
        publish(dna.TOPIC["command"], {"type": "code_review", "code": code, "filename": filename})
        return jsonify({"ok": True})

    elif action == "voice_command":
        text = payload.get("text", "")
        publish(dna.TOPIC["web_command"], {"action": "command", "text": text})
        return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "Unknown action"})


@app.route("/api/upload_document", methods=["POST"])
def upload_document():
    """Upload a document to JINX's knowledge base."""
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file"})

    file = request.files["file"]
    doc_dir = Path(dna.DOCUMENTS_DIR)
    doc_dir.mkdir(parents=True, exist_ok=True)

    save_path = doc_dir / file.filename
    file.save(str(save_path))

    publish(dna.TOPIC["web_command"], {"action": "add_document", "path": str(save_path)})
    return jsonify({"ok": True, "filename": file.filename})


@app.route("/api/alerts/clear", methods=["POST"])
def clear_alerts():
    state["alerts"] = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    print(f"[WEB] Control panel starting at http://{dna.LAPTOP_IP}:{dna.WEB_PORT}")
    app.run(host="0.0.0.0", port=dna.WEB_PORT, debug=False, threaded=True)
