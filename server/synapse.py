# synapse.py - jinx's nervous system
# handles all mqtt communication between laptop, esp32, and dashboard
# basically the middleman that routes messages between everything
#
# this is separate from the mqtt usage in other files because
# sometimes we need a central place to coordinate messages
# and handle cross-module communication

import json
import time
import paho.mqtt.client as mqtt
import threading

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dna import *
from blackbox import JinxDB


class Synapse:
    def __init__(self):
        print("[SYNAPSE] connecting nervous system...")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        self.db = JinxDB(DB_PATH)

        # track system state
        self.state = {
            "mode": "buddy",
            "esp32_online": False,
            "camera_online": False,
            "audio_online": False,
            "battery_percent": -1,
            "battery_voltage": 0.0,
            "faces_detected": 0,
            "last_alert": None,
            "uptime_start": time.time(),
        }

        # callbacks that other modules can register
        # key = topic, value = list of callback functions
        self.callbacks = {}

        self.alive = True

        try:
            self.client.connect(LAPTOP_IP, MQTT_PORT)
            self.client.loop_start()
            print("[SYNAPSE] connected to mqtt broker")
        except Exception as e:
            print(f"[SYNAPSE] connection failed: {e}")
            print("[SYNAPSE] is mosquitto running? sudo systemctl start mosquitto")

        self.db.add_syslog("SYNAPSE", "nervous system online")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """subscribe to ALL jinx topics when connected"""
        print("[SYNAPSE] mqtt connected, subscribing to all topics...")

        # subscribe to everything jinx related
        self.client.subscribe("jinx/#")
        self.state["esp32_online"] = False  # will be set when esp32 checks in

    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        print("[SYNAPSE] mqtt disconnected!")
        self.db.add_syslog("SYNAPSE", "mqtt disconnected", "WARNING")

    def _on_message(self, client, userdata, msg):
        """central message handler - routes messages to registered callbacks"""
        topic = msg.topic
        
        try:
            # try to parse as json
            payload = json.loads(msg.payload.decode())
        except:
            # binary data (like camera frames) or plain text
            payload = msg.payload

        # update internal state based on topic
        self._update_state(topic, payload)

        # call registered callbacks
        if topic in self.callbacks:
            for cb in self.callbacks[topic]:
                try:
                    cb(topic, payload)
                except Exception as e:
                    print(f"[SYNAPSE] callback error on {topic}: {e}")

    def _update_state(self, topic, payload):
        """update internal state tracking"""
        
        if topic == TOPICS["status"]:
            if isinstance(payload, dict):
                if payload.get("state") == "online":
                    self.state["esp32_online"] = True
                    print("[SYNAPSE] esp32 is online!")

        elif topic == TOPICS["battery"]:
            if isinstance(payload, dict):
                self.state["battery_percent"] = payload.get("percent", -1)
                self.state["battery_voltage"] = payload.get("voltage", 0.0)

        elif topic == TOPICS["mode"]:
            if isinstance(payload, dict):
                self.state["mode"] = payload.get("mode", "buddy")

        elif topic == TOPICS["alerts"]:
            if isinstance(payload, dict):
                self.state["last_alert"] = payload

    def register_callback(self, topic, callback):
        """let other modules register for specific topics
        usage: synapse.register_callback("jinx/battery", my_function)"""
        if topic not in self.callbacks:
            self.callbacks[topic] = []
        self.callbacks[topic].append(callback)

    def send(self, topic, data):
        """convenience method to publish"""
        if isinstance(data, dict):
            self.client.publish(topic, json.dumps(data))
        elif isinstance(data, bytes):
            self.client.publish(topic, data)
        else:
            self.client.publish(topic, str(data))

    def send_eyes(self, state):
        self.send(TOPICS["eyes"], {"state": state})

    def send_led(self, mode):
        self.send(TOPICS["led"], {"mode": mode})

    def send_motor(self, action, duration=1000, speed=200):
        self.send(TOPICS["motor"], {
            "action": action, "duration": duration, "speed": speed
        })

    def send_sound(self, sfx_id):
        self.send(TOPICS["sound"], {"sfx": sfx_id})

    def send_buzzer(self, beeps=1):
        self.send(TOPICS["buzzer"], {"beeps": beeps})

    def get_state(self):
        """get current system state"""
        self.state["uptime"] = int(time.time() - self.state["uptime_start"])
        return self.state.copy()

    def flatline(self):
        """shutdown"""
        self.alive = False
        self.client.loop_stop()
        self.client.disconnect()
        self.db.close()
        print("[SYNAPSE] nervous system offline")


if __name__ == "__main__":
    syn = Synapse()

    # test sending some commands
    print("\ntesting synapse...")

    time.sleep(1)

    syn.send_eyes("happy")
    print("sent: eyes happy")

    syn.send_led("purple_breathe")
    print("sent: led purple")

    syn.send_sound(1)
    print("sent: boot sound")

    print("\nstate:", syn.get_state())

    print("\nlistening for messages (ctrl+c to stop)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopped")

    syn.flatline()