# nexus.py - jinx's cyberpunk command center dashboard
# built with streamlit because it was the fastest way to get
# something that looks cool without writing actual frontend code
#
# run with: streamlit run dashboard/nexus.py --server.port 8501
# then open on tablet browser: http://LAPTOP_IP:8501
#
# the CSS took longer than the actual python code ngl
# but it makes everything look like we're in blade runner so worth it

import streamlit as st
import json
import time
import threading
import os
import sys
import numpy as np
from datetime import datetime
from collections import deque

import paho.mqtt.client as mqtt

# path hack so we can import from server folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from dna import *
from blackbox import JinxDB

# ============================================
# PAGE CONFIG - has to be first streamlit call
# ============================================

st.set_page_config(
    page_title="J.I.N.X. // NEXUS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS - the cyberpunk sauce
# ============================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Share+Tech+Mono&display=swap');

/* main background */
.stApp {
    background-color: #050510;
    color: #00ffff;
}

/* hide streamlit default stuff */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* all text */
html, body, [class*="css"] {
    font-family: 'Share Tech Mono', monospace;
    color: #00ffff;
}

/* headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ff00ff !important;
    text-shadow: 0 0 10px #ff00ff44, 0 0 20px #ff00ff22;
    letter-spacing: 2px;
}

h1 {
    text-align: center !important;
    font-size: 2.2em !important;
    text-shadow: 0 0 15px #ff00ff66, 0 0 30px #ff00ff33;
}

/* metric cards */
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    color: #00ffff !important;
    font-size: 1.8em !important;
    text-shadow: 0 0 8px #00ffff44;
}

[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: #888 !important;
    font-size: 0.85em !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

[data-testid="stMetricDelta"] {
    font-family: 'Share Tech Mono', monospace !important;
}

/* metric containers */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0a0a2e, #12122e);
    border: 1px solid #00ffff22;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 0 15px #00ffff11;
}

/* dataframes / tables */
.stDataFrame {
    border: 1px solid #00ffff22;
}

[data-testid="stDataFrame"] {
    background-color: #0a0a1a;
}

/* buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a0030, #300050);
    color: #ff00ff;
    border: 1px solid #ff00ff44;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1px;
    transition: all 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #300050, #500080);
    border-color: #ff00ff;
    box-shadow: 0 0 15px #ff00ff44;
}

/* dividers */
hr {
    border-color: #00ffff22 !important;
}

/* sidebar */
[data-testid="stSidebar"] {
    background-color: #050515;
    border-right: 1px solid #00ffff22;
}

/* selectbox / inputs */
.stSelectbox, .stTextInput {
    font-family: 'Share Tech Mono', monospace;
}

/* custom classes */
.title-glow {
    font-family: 'Orbitron', sans-serif;
    color: #ff00ff;
    text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff66, 0 0 40px #ff00ff33;
    text-align: center;
    font-size: 2.5em;
    letter-spacing: 4px;
    margin-bottom: 0;
}

.subtitle {
    font-family: 'Orbitron', sans-serif;
    color: #00ffff;
    text-align: center;
    font-size: 0.9em;
    letter-spacing: 3px;
    margin-top: 0;
    opacity: 0.7;
}

.alert-critical {
    background: linear-gradient(135deg, #2a0000, #1a0000);
    border-left: 3px solid #ff0040;
    padding: 8px 14px;
    margin: 4px 0;
    border-radius: 0 4px 4px 0;
    color: #ff4060;
    font-size: 0.85em;
    animation: pulse-red 2s infinite;
}

.alert-warning {
    background: linear-gradient(135deg, #2a2a00, #1a1a00);
    border-left: 3px solid #ffaa00;
    padding: 8px 14px;
    margin: 4px 0;
    border-radius: 0 4px 4px 0;
    color: #ffcc44;
    font-size: 0.85em;
}

.alert-info {
    background: linear-gradient(135deg, #000a2a, #000a1a);
    border-left: 3px solid #00aaff;
    padding: 8px 14px;
    margin: 4px 0;
    border-radius: 0 4px 4px 0;
    color: #44ccff;
    font-size: 0.85em;
}

.status-online {
    color: #00ff88;
    text-shadow: 0 0 5px #00ff88;
}

.status-offline {
    color: #ff0040;
    text-shadow: 0 0 5px #ff0040;
}

.device-trusted {
    color: #00ff88;
}

.device-unknown {
    color: #ff4444;
}

.doom-bar {
    height: 20px;
    border-radius: 4px;
    border: 1px solid #00ffff33;
    overflow: hidden;
    background: #0a0a1a;
}

.doom-fill {
    height: 100%;
    transition: width 0.5s;
    border-radius: 3px;
}

.scanline {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        #00ffff05 2px,
        #00ffff05 4px
    );
    z-index: 9999;
}

@keyframes pulse-red {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
</style>

<!-- scanline overlay for that CRT monitor feel -->
<div class="scanline"></div>
""", unsafe_allow_html=True)


# ============================================
# STATE - shared between mqtt thread and streamlit
# ============================================

# using session state to persist data between reruns
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "faces" not in st.session_state:
    st.session_state.faces = []
if "doom_level" not in st.session_state:
    st.session_state.doom_level = 0.0
if "doom_status" not in st.session_state:
    st.session_state.doom_status = "NOMINAL"
if "battery" not in st.session_state:
    st.session_state.battery = -1
if "battery_voltage" not in st.session_state:
    st.session_state.battery_voltage = 0.0
if "mode" not in st.session_state:
    st.session_state.mode = "BUDDY"
if "audio_class" not in st.session_state:
    st.session_state.audio_class = "NORMAL"
if "audio_conf" not in st.session_state:
    st.session_state.audio_conf = 0.0
if "network_devices" not in st.session_state:
    st.session_state.network_devices = []
if "faces_detected" not in st.session_state:
    st.session_state.faces_detected = 0
if "esp32_online" not in st.session_state:
    st.session_state.esp32_online = False
if "last_frame" not in st.session_state:
    st.session_state.last_frame = None


# ============================================
# DATABASE CONNECTION
# ============================================

@st.cache_resource
def get_db():
    """cache database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jinx_database.db')
    return JinxDB(db_path)


# ============================================
# HEADER
# ============================================

st.markdown('<p class="title-glow">⚡ J.I.N.X. ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">JUDGMENTAL INTELLIGENCE WITH NEURAL EXECUTION // NEXUS COMMAND CENTER v2.0.77</p>', unsafe_allow_html=True)

st.markdown("---")


# ============================================
# TOP STATUS BAR
# ============================================

status_cols = st.columns(6)

with status_cols[0]:
    mode = st.session_state.mode
    st.metric("⚡ MODE", mode)

with status_cols[1]:
    faces = st.session_state.faces_detected
    st.metric("👁️ FACES", str(faces))

with status_cols[2]:
    audio = st.session_state.audio_class
    st.metric("🔊 AUDIO", audio.upper()[:12])

with status_cols[3]:
    doom = st.session_state.doom_level
    st.metric("☠️ THREAT", f"{doom:.0%}")

with status_cols[4]:
    batt = st.session_state.battery
    batt_str = f"{batt}%" if batt >= 0 else "N/A"
    st.metric("🔋 POWER", batt_str)

with status_cols[5]:
    net_count = len(st.session_state.network_devices)
    st.metric("🌐 DEVICES", str(net_count))

st.markdown("---")


# ============================================
# MAIN LAYOUT - two columns
# ============================================

left_col, right_col = st.columns([2, 1])


# ---- LEFT COLUMN: camera feed + audio ----

with left_col:
    # camera feed
    st.markdown("### 📹 OPTIC NODE — LIVE FEED")

    camera_placeholder = st.empty()

    # try to show the latest frame if we have one
    if st.session_state.last_frame is not None:
        camera_placeholder.image(
            st.session_state.last_frame,
            channels="BGR",
            use_container_width=True
        )
    else:
        camera_placeholder.markdown("""
        <div style="
            background: #0a0a1a;
            border: 1px solid #00ffff22;
            border-radius: 8px;
            padding: 60px;
            text-align: center;
            color: #00ffff44;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.2em;
        ">
            📹 WAITING FOR CAMERA FEED<br>
            <span style="font-size: 0.7em; color: #ffffff22;">
                start optic.py to see live feed
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # doom level bar
    st.markdown("### ☠️ DOOM LEVEL — THREAT ASSESSMENT")

    doom = st.session_state.doom_level
    doom_status = st.session_state.doom_status

    # color based on level
    if doom > 0.7:
        doom_color = "#ff0040"
    elif doom > 0.4:
        doom_color = "#ffaa00"
    elif doom > 0.2:
        doom_color = "#00aaff"
    else:
        doom_color = "#00ff88"

    st.markdown(f"""
    <div style="margin-bottom: 5px; display: flex; justify-content: space-between;">
        <span style="color: {doom_color}; font-family: 'Orbitron';">{doom_status}</span>
        <span style="color: {doom_color}; font-family: 'Orbitron';">{doom:.0%}</span>
    </div>
    <div class="doom-bar">
        <div class="doom-fill" style="width: {doom*100}%; background: {doom_color};"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # audio section
    st.markdown("### 🔊 ECHO SCANNER — AUDIO MONITOR")

    audio_class = st.session_state.audio_class
    audio_conf = st.session_state.audio_conf

    if audio_class in THREAT_SOUNDS:
        alert_class = "alert-critical"
        audio_icon = "🔴"
    elif audio_class != "NORMAL":
        alert_class = "alert-warning"
        audio_icon = "🟡"
    else:
        alert_class = "alert-info"
        audio_icon = "🟢"

    st.markdown(f"""
    <div class="{alert_class}">
        {audio_icon} <strong>{audio_class.upper()}</strong> — Confidence: {audio_conf:.0%}
    </div>
    """, unsafe_allow_html=True)


# ---- RIGHT COLUMN: alerts + network + battery ----

with right_col:
    # alerts log
    st.markdown("### 🚨 INCIDENT LOG")

    db = get_db()
    recent_alerts = db.get_alerts(10)

    if recent_alerts:
        for alert in recent_alerts:
            ts, atype, details, conf = alert

            # format timestamp
            try:
                t = datetime.fromisoformat(ts)
                time_str = t.strftime("%H:%M:%S")
            except:
                time_str = ts[:8]

            # choose alert style
            if atype in ["THREAT", "AUDIO_THREAT", "HIGH_THREAT"]:
                css = "alert-critical"
                icon = "🔴"
            elif atype in ["UNKNOWN_FACE", "NEW_DEVICE"]:
                css = "alert-warning"
                icon = "🟡"
            else:
                css = "alert-info"
                icon = "🔵"

            st.markdown(f"""
            <div class="{css}">
                <strong>{time_str}</strong> {icon} {atype}<br>
                <span style="opacity: 0.7; font-size: 0.85em;">{details}</span>
                {f' — {conf:.0%}' if conf else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            No incidents recorded. All clear... for now.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # network status
    st.markdown("### 🌐 ICE WALL — NETWORK")

    devices = st.session_state.network_devices

    if devices:
        for dev in devices:
            trusted = dev.get("trusted", False)
            ip = dev.get("ip", "?")
            mac = dev.get("mac", "?")
            name = dev.get("name", "unknown")

            if trusted:
                icon = "🟢"
                css_class = "device-trusted"
                label = "TRUSTED"
            else:
                icon = "🔴"
                css_class = "device-unknown"
                label = "UNKNOWN"

            st.markdown(f"""
            <div style="
                background: #0a0a1a;
                border: 1px solid #00ffff15;
                border-radius: 4px;
                padding: 6px 10px;
                margin: 3px 0;
                font-size: 0.8em;
            ">
                {icon} <span class="{css_class}">{label}</span>
                <strong>{ip}</strong><br>
                <span style="color: #666; font-size: 0.85em;">{mac} | {name}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            No network scan data yet. Start ice_wall.py to monitor.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # battery status
    st.markdown("### 🔋 POWER CORE")

    batt = st.session_state.battery
    voltage = st.session_state.battery_voltage

    if batt >= 0:
        if batt > 60:
            batt_color = "#00ff88"
            batt_status = "NOMINAL"
        elif batt > 30:
            batt_color = "#ffaa00"
            batt_status = "LOW"
        elif batt > 10:
            batt_color = "#ff6600"
            batt_status = "CRITICAL"
        else:
            batt_color = "#ff0040"
            batt_status = "DYING"

        st.markdown(f"""
        <div style="
            background: #0a0a1a;
            border: 1px solid {batt_color}33;
            border-radius: 8px;
            padding: 15px;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: {batt_color}; font-family: 'Orbitron'; font-size: 1.5em;">{batt}%</span>
                <span style="color: {batt_color}; font-family: 'Orbitron';">{batt_status}</span>
            </div>
            <div class="doom-bar">
                <div class="doom-fill" style="width: {batt}%; background: {batt_color};"></div>
            </div>
            <div style="margin-top: 8px; font-size: 0.8em; color: #666;">
                Voltage: {voltage:.2f}V
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            Battery data not available. ESP32 offline?
        </div>
        """, unsafe_allow_html=True)


# ============================================
# BOTTOM SECTION - stats + face log
# ============================================

st.markdown("---")

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.markdown("### 👤 FACE LOG — RECENT DETECTIONS")

    recent_faces = db.get_faces(10)

    if recent_faces:
        for face in recent_faces:
            ts, name, label, conf = face

            try:
                t = datetime.fromisoformat(ts)
                time_str = t.strftime("%H:%M:%S")
            except:
                time_str = ts[:8]

            if label == "safe":
                icon = "🟢"
                color = "#00ff88"
            elif label == "threat":
                icon = "🔴"
                color = "#ff0040"
            else:
                icon = "🔵"
                color = "#00aaff"

            st.markdown(f"""
            <div style="
                padding: 4px 10px;
                margin: 2px 0;
                border-left: 2px solid {color};
                font-size: 0.85em;
            ">
                <strong>{time_str}</strong> {icon}
                <span style="color: {color};">{name}</span>
                — {conf:.0%}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            No faces detected yet. Start optic.py to see detections.
        </div>
        """, unsafe_allow_html=True)

with bottom_right:
    st.markdown("### 📊 SYSTEM STATS")

    stats = db.get_stats()

    stat_cols = st.columns(2)

    with stat_cols[0]:
        st.metric("Total Alerts", stats.get("alerts", 0))
        st.metric("Threats", stats.get("threats", 0))

    with stat_cols[1]:
        st.metric("Faces Seen", stats.get("faces_seen", 0))
        st.metric("Unique People", stats.get("unique_people", 0))


# ============================================
# CONTROL PANEL (sidebar)
# ============================================

with st.sidebar:
    st.markdown("### ⚙️ CONTROL PANEL")

    st.markdown("---")

    # mode selector
    mode_choice = st.selectbox("MODE", ["BUDDY", "SENTINEL"], index=0)

    if st.button("APPLY MODE", use_container_width=True):
        # would send mqtt command here
        st.session_state.mode = mode_choice
        st.success(f"Mode → {mode_choice}")

    st.markdown("---")

    # LED control
    st.markdown("### 💡 LED CONTROL")

    led_choice = st.selectbox("COLOR", [
        "purple_breathe", "solid_cyan", "solid_red", "solid_blue",
        "solid_green", "rainbow", "party", "off"
    ])

    if st.button("SET LED", use_container_width=True):
        st.success(f"LED → {led_choice}")

    st.markdown("---")

    # manual commands
    st.markdown("### 🎮 MANUAL CONTROL")

    mcols = st.columns(3)
    with mcols[0]:
        st.button("⬅️", use_container_width=True)
    with mcols[1]:
        st.button("⬆️", use_container_width=True)
    with mcols[2]:
        st.button("➡️", use_container_width=True)

    mcols2 = st.columns(3)
    with mcols2[0]:
        pass
    with mcols2[1]:
        st.button("⬇️", use_container_width=True)
    with mcols2[2]:
        st.button("⏹️", use_container_width=True)

    st.markdown("---")

    # system info
    st.markdown("### ℹ️ SYSTEM INFO")
    st.markdown(f"""
    ```
    JINX v2.0.77
    Server: {LAPTOP_IP}
    Phone:  {PHONE_IP}
    ESP32:  {ESP32_IP}
    Tablet: {TABLET_IP}
    MQTT:   :{MQTT_PORT}
    ```
    """)


# ============================================
# FOOTER
# ============================================

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #ffffff15; font-size: 0.75em; padding: 10px;">
    J.I.N.X. // JUDGMENTAL INTELLIGENCE WITH NEURAL EXECUTION<br>
    NEXUS COMMAND CENTER v2.0.77<br>
    Built with ♥, sarcasm, and ₹3,750 worth of components
</div>
""", unsafe_allow_html=True)


# ============================================
# AUTO REFRESH
# ============================================

# refresh every 3 seconds to update data
# not ideal but streamlit doesnt have great real-time support
# good enough for demo tho
time.sleep(3)
st.rerun()