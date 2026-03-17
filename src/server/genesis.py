#!/usr/bin/env python3
"""
GENESIS.PY — DESKBOT MAIN STARTUP
Launches all modules, handles startup sequence and graceful shutdown.

Usage:
    python server/genesis.py
    python server/genesis.py --sentinel
    python server/genesis.py --no-vision --no-audio
    python server/genesis.py --agent-mode  (code review / doc Q&A focus)
"""

import sys
import os
import time
import signal
import argparse
import threading
import subprocess
from datetime import datetime

# Add server directory to path
sys.path.insert(0, os.path.dirname(__file__))

import dna
from synapse    import Synapse
from blackbox   import Blackbox
from psyche     import Psyche
from optic      import Optic
from vocoder    import Vocoder
from echo_hunter import EchoHunter
from ice_wall   import IceWall
from hivemind   import Hivemind
from agent      import Agent


BANNER = r"""
     ██████╗ ███████╗███████╗██╗  ██╗██████╗  ██████╗ ████████╗
     ██╔══██╗██╔════╝██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
     ██║  ██║█████╗  ███████╗█████╔╝ ██████╔╝██║   ██║   ██║   
     ██║  ██║██╔══╝  ╚════██║██╔═██╗ ██╔══██╗██║   ██║   ██║   
     ██████╔╝███████╗███████║██║  ██╗██████╔╝╚██████╔╝   ██║   
     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   

           JUDGMENTAL AI DESK COMPANION  v2.1.0
           Built from a dead ThinkPad and a dream.
"""


def parse_args():
    parser = argparse.ArgumentParser(description="DESKBOT — Judgmental AI Companion")
    parser.add_argument("--sentinel",    action="store_true", help="Start in sentinel mode")
    parser.add_argument("--agent-mode",  action="store_true", help="Start in agent mode (code/doc focus)")
    parser.add_argument("--no-vision",   action="store_true", help="Skip camera/vision module")
    parser.add_argument("--no-voice",    action="store_true", help="Skip voice module")
    parser.add_argument("--no-audio",    action="store_true", help="Skip audio classification")
    parser.add_argument("--no-network",  action="store_true", help="Skip network monitoring")
    parser.add_argument("--no-dashboard",action="store_true", help="Skip Streamlit dashboard")
    parser.add_argument("--no-web",      action="store_true", help="Skip web control server")
    return parser.parse_args()


class Deskbot:
    def __init__(self, args):
        self.args     = args
        self.modules  = {}
        self.running  = False
        self.start_time = datetime.now()

        # Determine startup mode
        if args.sentinel:
            self.mode = dna.Mode.SENTINEL
        elif args.agent_mode:
            self.mode = dna.Mode.AGENT
        else:
            self.mode = dna.DEFAULT_MODE

    def _init_print(self, label: str, status: str = "✓"):
        icons = {"✓": "\033[92m✓\033[0m", "✗": "\033[91m✗\033[0m", "~": "\033[93m~\033[0m"}
        icon = icons.get(status, status)
        print(f"  [INIT] Loading {label:<35} {icon}")
        time.sleep(0.1)

    def startup(self):
        print(BANNER)
        print(f"  Starting in \033[96m{self.mode.upper()}\033[0m mode")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # 1. SYNAPSE — MQTT must come first (everything uses it)
            synapse = Synapse()
            synapse.connect()
            self.modules["synapse"] = synapse
            self._init_print("SYNAPSE (MQTT Bridge)")

            # 2. BLACKBOX — Logging
            blackbox = Blackbox()
            self.modules["blackbox"] = blackbox
            self._init_print("BLACKBOX (Database)")

            # 3. PSYCHE — Personality
            psyche = Psyche()
            self.modules["psyche"] = psyche
            self._init_print("PSYCHE (Personality Matrix)")

            # 4. OPTIC — Vision
            if not self.args.no_vision:
                optic = Optic(synapse, blackbox)
                self.modules["optic"] = optic
                self._init_print("OPTIC (Visual Cortex)")
            else:
                self._init_print("OPTIC (Visual Cortex) — SKIPPED", "~")

            # 5. VOCODER — Voice
            if not self.args.no_voice:
                vocoder = Vocoder(synapse, blackbox, psyche, self.modules.get("optic"))
                self.modules["vocoder"] = vocoder
                self._init_print("VOCODER (Voice System)")
            else:
                self._init_print("VOCODER (Voice System) — SKIPPED", "~")

            # 6. ECHO HUNTER — Audio Classification
            if not self.args.no_audio:
                echo = EchoHunter(synapse, blackbox)
                self.modules["echo"] = echo
                self._init_print("ECHO HUNTER (Sound Detection)")
            else:
                self._init_print("ECHO HUNTER (Sound Detection) — SKIPPED", "~")

            # 7. ICE WALL — Network
            if not self.args.no_network:
                ice = IceWall(synapse, blackbox)
                self.modules["ice"] = ice
                self._init_print("ICE WALL (Network Defense)")
            else:
                self._init_print("ICE WALL (Network Defense) — SKIPPED", "~")

            # 8. HIVEMIND — Sensor Fusion
            hivemind = Hivemind(synapse, blackbox)
            self.modules["hivemind"] = hivemind
            self._init_print("HIVEMIND (Sensor Fusion)")

            # 9. AGENT — AI Agent (code review, doc Q&A)
            agent = Agent(synapse, blackbox, psyche)
            self.modules["agent"] = agent
            self._init_print("AGENT (AI Code/Doc Agent)")

        except Exception as e:
            print(f"\n  \033[91m[FATAL] Module init failed: {e}\033[0m")
            self.shutdown()
            sys.exit(1)

        print()
        print("  \033[96m⚡ DESKBOT NEURAL CORE ONLINE ⚡\033[0m")
        print()

        # Launch dashboard in background
        if not self.args.no_dashboard:
            self._launch_dashboard()

        # Launch web control server
        if not self.args.no_web:
            self._launch_web_control()

        return True

    def _launch_dashboard(self):
        def _run():
            dash_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'nexus.py')
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", dash_path,
                 "--server.port", str(dna.DASHBOARD_PORT),
                 "--server.headless", "true"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        threading.Thread(target=_run, daemon=True).start()
        print(f"  [WEB] Dashboard: http://{dna.LAPTOP_IP}:{dna.DASHBOARD_PORT}")

    def _launch_web_control(self):
        def _run():
            web_path = os.path.join(os.path.dirname(__file__), '..', 'web_control', 'app.py')
            subprocess.Popen(
                [sys.executable, web_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        threading.Thread(target=_run, daemon=True).start()
        print(f"  [WEB] Control Panel: http://{dna.LAPTOP_IP}:{dna.WEB_PORT}")

    def run(self):
        self.running = True
        threads = []

        # Start each module in its own thread
        module_runners = {
            "optic":    lambda: self.modules["optic"].run(),
            "vocoder":  lambda: self.modules["vocoder"].run(),
            "echo":     lambda: self.modules["echo"].run(),
            "ice":      lambda: self.modules["ice"].run(),
            "hivemind": lambda: self.modules["hivemind"].run(),
            "agent":    lambda: self.modules["agent"].run(),
        }

        for name, runner in module_runners.items():
            if name in self.modules:
                t = threading.Thread(target=runner, name=name, daemon=True)
                t.start()
                threads.append(t)

        # Set initial mode
        synapse = self.modules["synapse"]
        synapse.publish(dna.TOPIC["mode"], self.mode)
        synapse.publish(dna.TOPIC["eyes"], "boot")
        synapse.publish(dna.TOPIC["led"], "boot")

        # Announce startup
        vocoder = self.modules.get("vocoder")
        if vocoder:
            time.sleep(2)  # Let boot animation play
            vocoder.speak(f"Systems online. I am {dna.BOT_NAME}. Try not to bore me.")

        print("\n  Press Ctrl+C to shutdown\n")

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        print("\n  [SHUTDOWN] Initiating graceful shutdown...")
        self.running = False

        vocoder = self.modules.get("vocoder")
        if vocoder:
            vocoder.speak("Going offline. Try not to miss me.")
            time.sleep(2)

        synapse = self.modules.get("synapse")
        if synapse:
            synapse.publish(dna.TOPIC["eyes"], "sleep")
            synapse.publish(dna.TOPIC["led"], "off")
            synapse.disconnect()

        print("  [SHUTDOWN] Complete. Goodbye.")


def main():
    args   = parse_args()
    bot    = Deskbot(args)
    signal.signal(signal.SIGTERM, lambda s, f: bot.shutdown())

    if bot.startup():
        bot.run()


if __name__ == "__main__":
    main()
