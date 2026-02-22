"""
SYNAPSE.PY — MQTT CENTRAL HUB
All inter-module communication goes through here.
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
import dna


class Synapse:
    def __init__(self):
        self.client      = mqtt.Client()
        self.subscribers = {}  # topic -> [callback]
        self._connected  = False

        self.client.on_connect    = self._on_connect
        self.client.on_message    = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def connect(self):
        retries = 0
        while retries < 10:
            try:
                self.client.connect(dna.MQTT_BROKER, dna.MQTT_PORT, keepalive=60)
                self.client.loop_start()
                time.sleep(0.5)
                if self._connected:
                    return
            except Exception as e:
                print(f"  [SYNAPSE] MQTT connect failed (attempt {retries+1}): {e}")
                time.sleep(2)
            retries += 1
        raise ConnectionError("Could not connect to MQTT broker. Is Mosquitto running?")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            print(f"  [SYNAPSE] MQTT connected to {dna.MQTT_BROKER}:{dna.MQTT_PORT}")
            for topic in self.subscribers:
                client.subscribe(topic)
        else:
            print(f"  [SYNAPSE] MQTT connection failed: rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            print("  [SYNAPSE] MQTT disconnected unexpectedly, reconnecting...")
            time.sleep(2)
            self.connect()

    def _on_message(self, client, userdata, msg):
        topic   = msg.topic
        payload = msg.payload.decode("utf-8", errors="ignore")
        callbacks = self.subscribers.get(topic, [])
        for cb in callbacks:
            try:
                threading.Thread(target=cb, args=(payload,), daemon=True).start()
            except Exception as e:
                print(f"  [SYNAPSE] Callback error on {topic}: {e}")

    def subscribe(self, topic: str, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
            if self._connected:
                self.client.subscribe(topic)
        self.subscribers[topic].append(callback)

    def publish(self, topic: str, payload, retain: bool = False):
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        try:
            self.client.publish(topic, str(payload), retain=retain)
        except Exception as e:
            print(f"  [SYNAPSE] Publish error on {topic}: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
