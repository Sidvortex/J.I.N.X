# ice_wall.py - jinx's network security monitor
# scans the local network for devices, detects new connections
# and monitors for suspicious activity
#
# named after the ICE (Intrusion Countermeasures Electronics) 
# from cyberpunk fiction because that sounds way cooler
# than "network_monitor.py"
#
# uses scapy for packet stuff and basic anomaly detection
# the ml model is trained on NSL-KDD dataset

import json
import os
import time
import threading
import subprocess
import paho.mqtt.client as mqtt
from datetime import datetime

try:
    from scapy.all import ARP, Ether, srp, sniff, IP, TCP, UDP
    SCAPY_OK = True
except:
    print("[ICE] scapy not installed, network monitoring limited")
    SCAPY_OK = False

try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    ML_OK = True
except:
    print("[ICE] sklearn not available for anomaly detection")
    ML_OK = False

import sys
sys.path.insert(0, os.path.dirname(__file__))

from dna import *
from blackbox import JinxDB


class IceWall:
    def __init__(self):
        print("[ICE] initializing network defense...")

        # mqtt
        self.syn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.syn.connect(LAPTOP_IP, MQTT_PORT)

        # database
        self.db = JinxDB(DB_PATH)

        # known devices on our network
        # mac -> {ip, name, first_seen, last_seen, trusted}
        self.known_devices = {}
        self.trusted_macs = set()  # devices we know are safe

        # add our own devices as trusted
        self._add_trusted_defaults()

        # anomaly detection model
        self.anomaly_model = None
        if ML_OK:
            model_path = "models/network_anomaly.pkl"
            if os.path.exists(model_path):
                try:
                    self.anomaly_model = joblib.load(model_path)
                    print("[ICE] anomaly detection model loaded")
                except:
                    print("[ICE] couldnt load anomaly model")

        self.alive = True
        self.scan_interval = 30  # seconds between network scans

        self.db.add_syslog("ICE", "network defense ready")
        print("[ICE] ice wall up")

    def _add_trusted_defaults(self):
        """add devices we know are ours"""
        # these get populated as we discover them
        # for now just mark our known IPs
        self.trusted_ips = {
            LAPTOP_IP,    # our laptop
            PHONE_IP,     # redmi phone
            TABLET_IP,    # tablet
            ESP32_IP,     # esp32
            "192.168.1.1" # router usually
        }

    def scan_network(self, ip_range="192.168.1.0/24"):
        """scan the local network for all connected devices
        uses ARP to find everyone on the network
        returns list of {ip, mac} dicts"""

        if not SCAPY_OK:
            # fallback: use arp command
            return self._scan_fallback()

        try:
            # create ARP request
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp

            # send and receive
            result = srp(packet, timeout=3, verbose=0)[0]

            devices = []
            for sent, received in result:
                devices.append({
                    "ip": received.psrc,
                    "mac": received.hwsrc
                })

            return devices

        except Exception as e:
            print(f"[ICE] scan error: {e}")
            return self._scan_fallback()

    def _scan_fallback(self):
        """fallback network scan using system commands
        works without scapy but gives less info"""
        devices = []
        try:
            # use arp table
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True, text=True, timeout=10
            )

            for line in result.stdout.split('\n'):
                # parse arp output
                # format varies by OS but generally: hostname (ip) at mac
                if '(' in line and ')' in line:
                    try:
                        ip = line.split('(')[1].split(')')[0]
                        parts = line.split()
                        for p in parts:
                            if ':' in p and len(p) == 17:  # MAC address
                                devices.append({"ip": ip, "mac": p})
                                break
                    except:
                        continue

        except Exception as e:
            print(f"[ICE] fallback scan error: {e}")

        return devices

    def process_scan(self, devices):
        """process scan results - detect new devices, update known list"""

        current_macs = set()

        for dev in devices:
            mac = dev["mac"]
            ip = dev["ip"]
            current_macs.add(mac)

            if mac not in self.known_devices:
                # NEW DEVICE!
                is_trusted = ip in self.trusted_ips

                self.known_devices[mac] = {
                    "ip": ip,
                    "name": self._resolve_hostname(ip),
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "trusted": is_trusted
                }

                if not is_trusted:
                    print(f"[ICE] ⚠️ NEW DEVICE: {ip} ({mac})")

                    # alert!
                    self.syn.publish(TOPICS["alerts"], json.dumps({
                        "type": "NEW_DEVICE",
                        "details": f"IP: {ip}, MAC: {mac}",
                        "time": datetime.now().isoformat()
                    }))

                    self.syn.publish(TOPICS["led"], json.dumps({"mode": "yellow_pulse"}))
                    self.db.add_alert("NEW_DEVICE", f"{ip} ({mac})", 0.8)
                    self.db.add_network_event(mac, ip, "NEW_DEVICE", "first seen on network")
                else:
                    print(f"[ICE] trusted device: {ip} ({mac})")
                    self.db.add_network_event(mac, ip, "TRUSTED_DEVICE", "known device connected")

            else:
                # update last seen
                self.known_devices[mac]["last_seen"] = datetime.now().isoformat()
                self.known_devices[mac]["ip"] = ip  # ip might change

        # check for disappeared devices
        for mac in list(self.known_devices.keys()):
            if mac not in current_macs:
                dev = self.known_devices[mac]
                # dont alert immediately, devices go offline sometimes
                # could add a counter here if we wanted

        # send full device list to dashboard
        device_list = []
        for mac, info in self.known_devices.items():
            device_list.append({
                "mac": mac,
                "ip": info["ip"],
                "name": info["name"],
                "trusted": info["trusted"],
                "last_seen": info["last_seen"]
            })

        self.syn.publish("jinx/network_devices", json.dumps(device_list))

    def _resolve_hostname(self, ip):
        """try to get hostname for an IP
        doesnt always work but nice when it does"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return "unknown"

    def get_network_stats(self):
        """get current network statistics"""
        stats = {
            "total_devices": len(self.known_devices),
            "trusted": sum(1 for d in self.known_devices.values() if d["trusted"]),
            "unknown": sum(1 for d in self.known_devices.values() if not d["trusted"]),
            "devices": []
        }

        for mac, info in self.known_devices.items():
            stats["devices"].append({
                "mac": mac,
                "ip": info["ip"],
                "name": info["name"],
                "trusted": info["trusted"]
            })

        return stats

    def train_anomaly_model(self, data_path="data/nsl-kdd/"):
        """train anomaly detection on NSL-KDD dataset
        this is optional but adds a nice ML component to the project"""

        if not ML_OK:
            print("[ICE] need sklearn for this")
            return

        print("[ICE] training anomaly detection model...")

        train_file = os.path.join(data_path, "KDDTrain+.txt")
        if not os.path.exists(train_file):
            print(f"[ICE] dataset not found: {train_file}")
            print("[ICE] download NSL-KDD from:")
            print("       https://www.unb.ca/cic/datasets/nsl.html")
            return

        # NSL-KDD column names
        columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
            'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
            'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
            'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
            'dst_host_srv_rerror_rate', 'attack_type', 'difficulty_level'
        ]

        df = pd.read_csv(train_file, names=columns)
        print(f"[ICE] loaded {len(df)} training samples")

        # binary classification: normal vs attack
        df['label'] = (df['attack_type'] != 'normal').astype(int)

        # select numeric features only (keep it simple)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols.remove('label')
        if 'difficulty_level' in numeric_cols:
            numeric_cols.remove('difficulty_level')

        X = df[numeric_cols].values
        y = df['label'].values

        # train random forest
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, roc_auc_score

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        print("\n[ICE] Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
        print(f"[ICE] ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")

        # save model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/network_anomaly.pkl")
        print("[ICE] model saved to models/network_anomaly.pkl")

        self.anomaly_model = model

    def patrol(self):
        """main loop - periodically scans network"""

        print(f"[ICE] network patrol active (scanning every {self.scan_interval}s)")

        while self.alive:
            try:
                print("[ICE] scanning network...")
                devices = self.scan_network()
                print(f"[ICE] found {len(devices)} devices")

                self.process_scan(devices)

                stats = self.get_network_stats()
                self.syn.publish("jinx/network_stats", json.dumps(stats))

                print(f"[ICE] trusted: {stats['trusted']}, unknown: {stats['unknown']}")

            except Exception as e:
                print(f"[ICE] patrol error: {e}")

            time.sleep(self.scan_interval)

    def flatline(self):
        """shutdown"""
        self.alive = False
        self.syn.disconnect()
        self.db.close()
        print("[ICE] ice wall down")


if __name__ == "__main__":
    import sys as _sys
    import numpy as np

    ice = IceWall()

    if "--train" in _sys.argv:
        ice.train_anomaly_model()
    elif "--scan" in _sys.argv:
        devices = ice.scan_network()
        print(f"\nfound {len(devices)} devices:")
        for d in devices:
            print(f"  {d['ip']} - {d['mac']}")
    else:
        try:
            ice.patrol()
        except KeyboardInterrupt:
            print("\nstopped")

    ice.flatline()