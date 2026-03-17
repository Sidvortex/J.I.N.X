"""
ICE WALL.PY — NETWORK DEFENSE
Real-time network device detection, traffic monitoring, and anomaly detection.
Shows on tablet: all devices on network, unknown devices flagged.
"""

import json
import time
import socket
import threading
import dna
from blackbox import Blackbox
from synapse  import Synapse
from datetime import datetime

try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("  [ICE] scapy not available. Install with: pip install scapy")

try:
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    import numpy as np
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False


class IceWall:
    def __init__(self, synapse: Synapse, blackbox: Blackbox):
        self.synapse   = synapse
        self.blackbox  = blackbox
        self.running   = False

        # Known devices {MAC: info}
        self.known_devices  = {}
        self.current_devices = {}
        self.anomaly_model  = None

        self._load_anomaly_model()

    def _load_anomaly_model(self):
        import os
        if not SK_AVAILABLE:
            return
        model_path = "models/network_anomaly.pkl"
        if os.path.exists(model_path):
            self.anomaly_model = joblib.load(model_path)
            print("  [ICE] Network anomaly model loaded")

    def scan_network(self) -> dict:
        """ARP scan to find all devices on LAN."""
        if not SCAPY_AVAILABLE:
            return {}

        devices = {}
        try:
            # Get local network range
            local_ip  = socket.gethostbyname(socket.gethostname())
            network   = ".".join(local_ip.split(".")[:3]) + ".0/24"

            arp_req   = scapy.ARP(pdst=network)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            packet    = broadcast / arp_req
            answered  = scapy.srp(packet, timeout=2, verbose=False)[0]

            for sent, received in answered:
                ip  = received.psrc
                mac = received.hwsrc.upper()
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = "Unknown"

                trusted = mac in [m.upper() for m in dna.TRUSTED_MACS]
                devices[mac] = {
                    "ip": ip, "mac": mac,
                    "hostname": hostname,
                    "trusted": trusted,
                    "first_seen": self.known_devices.get(mac, {}).get("first_seen", datetime.now().isoformat()),
                    "last_seen": datetime.now().isoformat(),
                }
        except Exception as e:
            print(f"  [ICE] Scan error: {e}")

        return devices

    def _check_new_devices(self, current: dict):
        """Flag devices that weren't seen before."""
        for mac, info in current.items():
            if mac not in self.known_devices and not info["trusted"]:
                alert = f"NEW DEVICE: {info['hostname']} ({info['ip']}) MAC:{mac}"
                self.synapse.publish(dna.TOPIC["alerts"], alert)
                self.blackbox.log_event("NEW_DEVICE", info)
                print(f"  [ICE] {alert}")
        self.known_devices = {**self.known_devices, **current}

    def run(self):
        self.running = True
        print("  [ICE] Network monitoring started")

        while self.running:
            devices = self.scan_network()
            if devices:
                self._check_new_devices(devices)
                self.current_devices = devices
                self.synapse.publish(dna.TOPIC["network_stats"], json.dumps({
                    "count": len(devices),
                    "devices": list(devices.values()),
                    "timestamp": datetime.now().isoformat(),
                }))
            time.sleep(dna.NETWORK_SCAN_INTERVAL)

    def stop(self):
        self.running = False
