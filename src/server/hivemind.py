"""
HIVEMIND.PY — SENSOR FUSION
Combines visual, audio, network, and proximity scores into a unified
"doom_level" threat assessment. Also tracks battery state from ESP32.
"""

import json
import time
import threading
import dna
from blackbox import Blackbox
from synapse  import Synapse


class Hivemind:
    def __init__(self, synapse: Synapse, blackbox: Blackbox):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.running   = False

        # Component scores (0.0 - 1.0)
        self.scores = {
            "visual":    0.0,
            "audio":     0.0,
            "network":   0.0,
            "proximity": 0.0,
        }
        self.doom_level     = 0.0
        self.battery_pct    = 100
        self.battery_voltage = 8.4
        self.low_battery_alerted = False

        # Decay: scores fade over time if not refreshed
        self.score_times = {k: 0 for k in self.scores}
        self.decay_time  = 10.0  # seconds before score decays

        # Subscribe to score updates from other modules
        synapse.subscribe(dna.TOPIC["battery"], self._on_battery)
        synapse.subscribe(dna.TOPIC["sensors"], self._on_sensors)
        synapse.subscribe(dna.TOPIC["audio"],   self._on_audio_score)
        synapse.subscribe(dna.TOPIC["alerts"],  self._on_alert)

    def update_score(self, source: str, score: float):
        """Update a component score."""
        self.scores[source]     = max(0.0, min(1.0, score))
        self.score_times[source] = time.time()
        self._recalculate()

    def _recalculate(self):
        """Weighted average of all component scores with time decay."""
        now      = time.time()
        weights  = dna.FUSION_WEIGHTS
        total_w  = 0.0
        total_s  = 0.0

        for source, score in self.scores.items():
            age = now - self.score_times.get(source, 0)
            if age > self.decay_time:
                decay_factor = max(0.0, 1.0 - (age - self.decay_time) / 30.0)
                effective_score = score * decay_factor
            else:
                effective_score = score

            w = weights.get(source, 0.1)
            total_s += effective_score * w
            total_w += w

        self.doom_level = total_s / total_w if total_w > 0 else 0.0
        self.synapse.publish(dna.TOPIC["doom_level"], f"{self.doom_level:.3f}")

        if self.doom_level > dna.DOOM_ALERT_THRESHOLD:
            self.synapse.publish(dna.TOPIC["led"],   "alert")
            self.synapse.publish(dna.TOPIC["eyes"],  "threat")
            self.blackbox.log_event("HIGH_DOOM", {"doom_level": self.doom_level, "scores": self.scores})

    def _on_battery(self, payload: str):
        try:
            data = json.loads(payload)
            self.battery_pct      = int(data.get("percent", 100))
            self.battery_voltage  = float(data.get("voltage", 8.4))

            # Low battery alert
            if self.battery_pct < dna.BATTERY_LOW_PERCENT and not self.low_battery_alerted:
                self.low_battery_alerted = True
                self.synapse.publish(dna.TOPIC["eyes"],  "sleepy")
                self.synapse.publish(dna.TOPIC["led"],   "battery_low")
                self.synapse.publish(dna.TOPIC["sound"], "battery_low")
                self.synapse.publish(dna.TOPIC["alerts"], f"BATTERY LOW: {self.battery_pct}%")
                self.blackbox.log_event("BATTERY_LOW", {"percent": self.battery_pct})

            elif self.battery_pct >= dna.BATTERY_LOW_PERCENT + 5:
                self.low_battery_alerted = False

        except Exception:
            pass

    def _on_sensors(self, payload: str):
        """Process proximity/depth sensor data from ESP32."""
        try:
            data = json.loads(payload)
            us1_cm   = data.get("us1_cm", 999)
            us2_cm   = data.get("us2_cm", 999)
            ir_left  = data.get("ir_left", 0)
            ir_right = data.get("ir_right", 0)
            tof_down = data.get("tof_down_mm", 999)  # VL53L0X facing down
            tof_fwd  = data.get("tof_fwd_mm", 999)   # VL53L0X facing forward

            # Table edge detection (VL53L0X facing down goes to large value = edge)
            if tof_down > dna.DEPTH_DANGER_MM:
                self.synapse.publish(dna.TOPIC["motor"], "stop")
                self.synapse.publish(dna.TOPIC["alerts"], "TABLE EDGE DETECTED — STOPPING")
                self.synapse.publish(dna.TOPIC["buzzer"], "on")

            # Forward obstacle
            min_dist = min(us1_cm, us2_cm, tof_fwd / 10)
            if min_dist < dna.OBSTACLE_DANGER_CM:
                proximity_score = 1.0 - (min_dist / dna.OBSTACLE_DANGER_CM)
                self.update_score("proximity", proximity_score)
                self.synapse.publish(dna.TOPIC["motor"], "stop")
            else:
                self.update_score("proximity", 0.0)

        except Exception:
            pass

    def _on_audio_score(self, payload: str):
        try:
            data  = json.loads(payload)
            label = data.get("label", "")
            conf  = float(data.get("confidence", 0))
            score = conf if label in dna.AUDIO_THREAT_CLASSES else 0.0
            self.update_score("audio", score)
        except Exception:
            pass

    def _on_alert(self, payload: str):
        """Visual threat alerts increase visual score."""
        if "THREAT" in payload.upper():
            self.update_score("visual", 0.9)

    def run(self):
        """Periodic decay recalculation."""
        self.running = True
        while self.running:
            self._recalculate()
            time.sleep(2)

    def stop(self):
        self.running = False
