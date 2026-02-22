# hivemind.py - jinx's sensor fusion engine
# combines signals from vision, audio, and network
# into a single threat score
#
# the idea is: if the camera sees something weird AND
# the mic hears something weird AND there's a new device
# on the network, then its DEFINITELY suspicious
#
# each module gives a score from 0-1 and we combine them
# with weights to get an overall doom_level

import json
import time
import paho.mqtt.client as mqtt
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dna import *
from blackbox import JinxDB


class HiveMind:
    def __init__(self):
        print("[HIVEMIND] initializing sensor fusion...")

        # mqtt
        self.syn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.syn.on_message = self._on_message
        self.syn.connect(LAPTOP_IP, MQTT_PORT)

        # subscribe to signals from all modules
        self.syn.subscribe(TOPICS["alerts"])
        self.syn.subscribe(TOPICS["audio"])
        self.syn.subscribe(TOPICS["battery"])
        self.syn.subscribe("jinx/network_stats")
        self.syn.subscribe("jinx/detected_person")
        self.syn.loop_start()

        # database
        self.db = JinxDB(DB_PATH)

        # individual threat scores (0.0 to 1.0)
        self.visual_score = 0.0   # from optic.py
        self.audio_score = 0.0    # from echo_hunter.py
        self.network_score = 0.0  # from ice_wall.py
        self.proximity_score = 0.0  # from ultrasonic sensors

        # weights - how much each signal matters
        # tweaked these through testing
        self.weights = {
            "visual": 0.35,
            "audio": 0.30,
            "network": 0.20,
            "proximity": 0.15
        }

        # decay rate - scores fade over time if no new alerts
        # so jinx doesnt stay paranoid forever
        self.decay_rate = 0.05  # per second
        self.last_update = time.time()

        # overall threat
        self.doom_level = 0.0

        self.alive = True

        self.db.add_syslog("HIVEMIND", "sensor fusion online")
        print("[HIVEMIND] fusion engine ready")

    def _on_message(self, client, userdata, msg):
        """receive signals from all modules and update scores"""
        try:
            data = json.loads(msg.payload.decode())
        except:
            return

        topic = msg.topic

        if topic == TOPICS["alerts"]:
            alert_type = data.get("type", "")
            conf = data.get("confidence", 0.5)

            if alert_type in ["THREAT", "UNKNOWN_FACE"]:
                self.visual_score = max(self.visual_score, conf)
            elif alert_type == "AUDIO_THREAT":
                self.audio_score = max(self.audio_score, conf)
            elif alert_type == "NEW_DEVICE":
                self.network_score = max(self.network_score, conf)

        elif topic == TOPICS["audio"]:
            if data.get("is_threat", False):
                self.audio_score = max(self.audio_score, data.get("confidence", 0.5))

        elif topic == "jinx/network_stats":
            unknown = data.get("unknown", 0)
            if unknown > 0:
                # more unknown devices = higher score
                self.network_score = min(unknown * 0.3, 1.0)

        # recalculate doom level
        self._recalculate()

    def _recalculate(self):
        """combine all scores into final doom_level"""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # decay old scores (things calm down over time)
        decay = self.decay_rate * elapsed
        self.visual_score = max(0.0, self.visual_score - decay)
        self.audio_score = max(0.0, self.audio_score - decay)
        self.network_score = max(0.0, self.network_score - decay)
        self.proximity_score = max(0.0, self.proximity_score - decay)

        # weighted average
        self.doom_level = (
            self.visual_score * self.weights["visual"] +
            self.audio_score * self.weights["audio"] +
            self.network_score * self.weights["network"] +
            self.proximity_score * self.weights["proximity"]
        )

        # clamp between 0 and 1
        self.doom_level = max(0.0, min(1.0, self.doom_level))

        # publish to dashboard
        self.syn.publish("jinx/doom_level", json.dumps({
            "doom_level": round(self.doom_level, 3),
            "visual": round(self.visual_score, 3),
            "audio": round(self.audio_score, 3),
            "network": round(self.network_score, 3),
            "proximity": round(self.proximity_score, 3),
            "status": self._get_status_label()
        }))

        # trigger actions based on doom level
        if self.doom_level > THREAT_SCORE_THRESHOLD:
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "threat"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "red_strobe"}))
            self.db.add_alert("HIGH_THREAT", f"doom_level: {self.doom_level:.2f}", self.doom_level)
        elif self.doom_level > 0.4:
            self.syn.publish(TOPICS["eyes"], json.dumps({"state": "scanning"}))
            self.syn.publish(TOPICS["led"], json.dumps({"mode": "yellow_pulse"}))
        # if low, dont override current eye/led state
        # other modules handle the default state

    def _get_status_label(self):
        """human readable threat status"""
        if self.doom_level > 0.8:
            return "CRITICAL"
        elif self.doom_level > 0.6:
            return "HIGH"
        elif self.doom_level > 0.4:
            return "ELEVATED"
        elif self.doom_level > 0.2:
            return "GUARDED"
        else:
            return "NOMINAL"

    def get_report(self):
        """get current fusion report"""
        return {
            "doom_level": self.doom_level,
            "status": self._get_status_label(),
            "visual_score": self.visual_score,
            "audio_score": self.audio_score,
            "network_score": self.network_score,
            "proximity_score": self.proximity_score,
            "weights": self.weights
        }

    def patrol(self):
        """main loop - just keeps recalculating as signals come in"""
        print("[HIVEMIND] monitoring all signals...")

        while self.alive:
            self._recalculate()
            time.sleep(1)  # recalc every second

    def flatline(self):
        """shutdown"""
        self.alive = False
        self.syn.loop_stop()
        self.syn.disconnect()
        self.db.close()
        print("[HIVEMIND] sensor fusion offline")


if __name__ == "__main__":
    hm = HiveMind()

    print("\nlistening for signals from all modules...")
    print("doom level will update as events come in")
    print("ctrl+c to stop\n")

    try:
        hm.patrol()
    except KeyboardInterrupt:
        print(f"\nfinal report: {hm.get_report()}")

    hm.flatline()