# genesis.py - JINX main startup
# this is the file that starts everything
# run this and jinx comes to life
#
# starts all modules in separate threads:
# optic (vision), vocoder (voice), echo_hunter (audio),
# ice_wall (network), hivemind (sensor fusion)
#
# also starts the dashboard server
#
# usage: python genesis.py

import threading
import time
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(__file__))

from dna import *
from blackbox import JinxDB
from psyche import say


def print_banner():
    banner = """
\033[36m
     ██╗██╗███╗   ██╗██╗  ██╗
     ██║██║████╗  ██║╚██╗██╔╝
     ██║██║██╔██╗ ██║ ╚███╔╝ 
██   ██║██║██║╚██╗██║ ██╔██╗ 
╚█████╔╝██║██║ ╚████║██╔╝ ██╗
 ╚════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
\033[0m
\033[35m  JUDGMENTAL INTELLIGENCE WITH
  NEURAL EXECUTION  v2.0.77\033[0m
"""
    print(banner)


def loading_sequence():
    """fancy boot sequence for terminal"""
    modules = [
        ("SYNAPSE", "MQTT Broker"),
        ("BLACKBOX", "Database"),
        ("PSYCHE", "Personality Matrix"),
        ("OPTIC", "Visual Cortex"),
        ("VOCODER", "Voice System"),
        ("ECHO", "Sound Detection"),
        ("ICE", "Network Defense"),
        ("HIVEMIND", "Sensor Fusion"),
    ]

    for code, name in modules:
        print(f"\033[32m[INIT]\033[0m Loading {code} ({name})...", end="", flush=True)
        time.sleep(0.3)
        print(f" \033[32m✓\033[0m")

    print(f"\n\033[35m⚡ JINX NEURAL CORE ONLINE ⚡\033[0m\n")


def start_optic(mode):
    """start vision system in a thread"""
    try:
        from optic import OpticNerve
        eye = OpticNerve()
        eye.run(mode)
    except Exception as e:
        print(f"\033[31m[ERROR] optic crashed: {e}\033[0m")


def start_vocoder():
    """start voice system in a thread"""
    try:
        from vocoder import Vocoder
        voice = Vocoder()
        voice.eavesdrop()
    except Exception as e:
        print(f"\033[31m[ERROR] vocoder crashed: {e}\033[0m")


def start_echo_hunter():
    """start audio classification in a thread"""
    try:
        from echo_hunter import EchoHunter
        echo = EchoHunter()
        if echo.model is not None:
            echo.patrol()
        else:
            print("[ECHO] no model loaded, skipping audio patrol")
            print("[ECHO] train with: python echo_hunter.py --train")
    except Exception as e:
        print(f"\033[31m[ERROR] echo_hunter crashed: {e}\033[0m")


def start_ice_wall():
    """start network monitoring in a thread"""
    try:
        from ice_wall import IceWall
        ice = IceWall()
        ice.patrol()
    except Exception as e:
        print(f"\033[31m[ERROR] ice_wall crashed: {e}\033[0m")


def start_hivemind():
    """start sensor fusion in a thread"""
    try:
        from hivemind import HiveMind
        hive = HiveMind()
        hive.patrol()
    except Exception as e:
        print(f"\033[31m[ERROR] hivemind crashed: {e}\033[0m")


def start_dashboard():
    """start streamlit dashboard"""
    try:
        import subprocess
        dashboard_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "dashboard", "nexus.py"
        )
        if os.path.exists(dashboard_path):
            subprocess.Popen([
                "streamlit", "run", dashboard_path,
                "--server.port", str(DASHBOARD_PORT),
                "--server.headless", "true"
            ])
            print(f"[NEXUS] dashboard at http://localhost:{DASHBOARD_PORT}")
        else:
            print("[NEXUS] dashboard not found, skipping")
    except Exception as e:
        print(f"[NEXUS] dashboard failed: {e}")


def main():
    print_banner()
    loading_sequence()

    db = JinxDB(DB_PATH)
    db.add_syslog("GENESIS", "JINX is waking up")

    mode = "buddy"  # default mode
    if "--sentinel" in sys.argv:
        mode = "sentinel"
        print("[GENESIS] starting in SENTINEL mode")

    # figure out which modules to start
    skip_vision = "--no-vision" in sys.argv
    skip_voice = "--no-voice" in sys.argv
    skip_audio = "--no-audio" in sys.argv
    skip_network = "--no-network" in sys.argv
    skip_dashboard = "--no-dashboard" in sys.argv

    threads = []

    # start modules as daemon threads
    # daemon = they die when main thread dies

    if not skip_vision:
        t = threading.Thread(target=start_optic, args=(mode,), daemon=True, name="optic")
        threads.append(t)
        print("[GENESIS] optic queued")

    if not skip_voice:
        t = threading.Thread(target=start_vocoder, daemon=True, name="vocoder")
        threads.append(t)
        print("[GENESIS] vocoder queued")

    if not skip_audio:
        t = threading.Thread(target=start_echo_hunter, daemon=True, name="echo")
        threads.append(t)
        print("[GENESIS] echo_hunter queued")

    if not skip_network:
        t = threading.Thread(target=start_ice_wall, daemon=True, name="ice")
        threads.append(t)
        print("[GENESIS] ice_wall queued")

    # always start hivemind (sensor fusion)
    t = threading.Thread(target=start_hivemind, daemon=True, name="hivemind")
    threads.append(t)

    # start dashboard
    if not skip_dashboard:
        start_dashboard()

    # launch all threads
    print(f"\n[GENESIS] starting {len(threads)} modules...")
    for t in threads:
        t.start()
        time.sleep(0.5)  # small delay between starts

    print(f"\n[GENESIS] ⚡ ALL SYSTEMS GO ⚡")
    print(f"[GENESIS] mode: {mode}")
    print(f"[GENESIS] modules: {len(threads)} active")
    print(f"[GENESIS] press Ctrl+C to shutdown\n")

    db.add_syslog("GENESIS", f"all modules started in {mode} mode")

    # keep main thread alive
    try:
        while True:
            # periodic health check
            alive_count = sum(1 for t in threads if t.is_alive())
            if alive_count < len(threads):
                dead = [t.name for t in threads if not t.is_alive()]
                print(f"\033[33m[GENESIS] warning: {dead} modules died\033[0m")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n[GENESIS] shutting down JINX...")
        print("[GENESIS] goodnight 💤")
        db.add_syslog("GENESIS", "JINX shutting down")
        db.close()
        sys.exit(0)


if __name__ == "__main__":
    # usage:
    # python genesis.py                    → normal startup
    # python genesis.py --sentinel         → start in sentinel mode
    # python genesis.py --no-vision        → skip camera
    # python genesis.py --no-voice         → skip voice
    # python genesis.py --no-audio         → skip audio classification
    # python genesis.py --no-network       → skip network monitoring
    # python genesis.py --no-dashboard     → skip dashboard
    # 
    # combine flags:
    # python genesis.py --no-vision --no-audio → voice + network only
    # 
    # for testing specific modules, run them directly:
    # python optic.py
    # python vocoder.py
    # etc

    main()