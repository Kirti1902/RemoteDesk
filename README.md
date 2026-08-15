# 🖥️ RemoteDock

> Turn your mobile device into a real-time, low-latency PC command center over your local network.

**RemoteDock** is a lightweight, full-stack remote system administration tool composed of a **React Native (Expo)** mobile application and a **Python (Flask)** Windows companion server. It provides low-overhead screen mirroring, gesture trackpad control, system volume/brightness regulation, hotkey injection, quick application launching, and live hardware diagnostics—all without third-party cloud dependencies or subscription services.

---

## 🛠️ Architecture & Tech Stack


```

┌────────────────────────┐              Local Wi-Fi             ┌────────────────────────┐
│ React Native (Expo)    │ ───────────────────────────────────► │ Python (Flask Server)  │
│ Mobile Client          │ ◄─────────────────────────────────── │ Windows Host PC        │
└────────────────────────┘          HTTP / REST & Base64        └────────────────────────┘

```

* **Mobile Client:** React Native, Expo Router, TypeScript, `react-native-reanimated`
* **Backend Companion Server:** Python 3.8+, Flask, Flask-CORS
* **Windows API Integration:** `pyautogui`, `pycaw` (Native COM interfaces for `IAudioEndpointVolume`), `screen-brightness-control`, `mss`, `Pillow (PIL)`, `psutil`
* **Networking & Protocols:** Local HTTP REST API, base64 JPEG payload streaming, low-latency ping telemetry

---

## ✨ Features

* 🖱️ **Multitouch Trackpad:** Relative cursor positioning, tap-to-click, double-click, right-click, two-finger scrolling, and dynamic haptic feedback.
* 🎵 **Media & Display Hardware Sliders:** Granular master volume control interfacing directly with Windows audio endpoints (`pycaw`) and display brightness adjustment (`screen-brightness-control`).
* ⌨️ **Virtual Keyboard & Hotkey Suite:** System modifier keys (Ctrl, Alt, Win, Shift) and 1-tap macro shortcuts (Task Manager, Desktop Lock, Copy/Paste, Screen Grab, Select All).
* 🖥️ **Live Display Mirroring:** Low-overhead 2–5 FPS desktop screen stream rendered via high-speed frame capture (`mss`) and PIL compression sent via base64 JPEG strings.
* 📊 **Real-Time System Diagnostics:** Comprehensive system health dashboard displaying:
  * Dynamic Battery charge status percentage & charging plug state.
  * Multi-core CPU utilization percentage.
  * Detailed RAM allocation breakdown (e.g., `12.2 GB / 15.8 GB`).
  * Disk partition usage (e.g., `C: drive capacity`).
  * CPU temperature telemetry (with dynamic fallback).
  * Real-time network throughput (Upload / Download in `KB/s`) and system uptime counter.
* 🚀 **Custom Quick Launch Hub:** Editable application launcher grid supporting two modes:
  * **APP Mode:** Directly launches native Windows binaries (`.exe`) or built-in system tools (Task Manager, Explorer, Calculator, Notepad).
  * **WEB Mode:** Launches pre-configured URL targets directly inside the default web browser (YouTube, Gmail, custom sites).
  * **Interactive Edit Mode:** Long-press tile interaction to customize, add, or manage quick shortcuts.
* 📐 **Adaptive UI Layout:** Complete responsive support for both **Portrait and Landscape** screen orientation modes.

---

## 🚀 Setup & Installation

### 1. Host Companion Server Setup (Windows Host)

#### Prerequisites
* **Python 3.8 or higher** installed and added to environment `PATH`.

#### Step 1: Install Dependencies
Open Command Prompt (`cmd`) or PowerShell and run:

```bash
pip install flask flask-cors pyautogui pycaw comtypes screen-brightness-control mss Pillow psutil

```

#### Step 2: Configure Windows Firewall (Required)

Allow incoming TCP traffic on port `9999`. Run Command Prompt as **Administrator**:

```cmd
netsh advfirewall firewall add rule name="RemoteDock" dir=in action=allow protocol=TCP localport=9999

```

#### Step 3: Launch Companion Server

Create a file named `server.py` and run the script:

```bash
python server.py

```

*(The terminal output will display your host machine's local IP address, e.g., `192.168.1.5:9999`)*

---

### 2. Mobile Client Setup

#### Option A: Run via Expo (Development)

1. Clone the repository and install dependencies:
```bash
git clone [https://github.com/your-username/RemoteDock.git](https://github.com/your-username/RemoteDock.git)
cd RemoteDock
npm install

```


2. Launch the Expo development server:
```bash
npx expo start

```


3. Scan the generated QR code using **Expo Go** (Android/iOS) or run via an emulator.

#### Option B: Build Standalone APK (Android)

Generate an installable standalone Android binary using Expo Application Services (EAS):

```bash
npx eas build -p android --profile preview

```

---

## 🔌 API Endpoints Reference

The companion server listens on `http://<HOST_IP>:9999` by default.

### Telemetry & Diagnostics

| Endpoint | Method | Response Payload Format | Description |
| --- | --- | --- | --- |
| `/ping` | `GET` | `"ok"` | Connection heartbeat check. |
| `/status` | `GET` | `JSON Object` | Returns CPU load, CPU count, RAM used/total/%, Disk used/total/%, Battery %, charging state, network upload/download speeds (`KB/s`), temperature, and total system uptime. |
| `/screenshot` | `GET` | `JSON Object` | Captures primary display frame and returns a base64-encoded JPEG image string. |

### System Action Controller

`POST /command`

All input events and execution requests pass through a unified command router using structured JSON payloads:

```json
{
  "type": "<COMMAND_TYPE>",
  "data": { ... }
}

```

#### Supported Payload Models:

* **Mouse Movement:**
```json
{ "type": "mouse_move", "data": { "dx": 15, "dy": -10 } }

```


* **Mouse Button Clicks:**
```json
{ "type": "mouse_click", "data": { "button": "left" } } // Options: "left", "right", "double"

```


* **Relative Scrolling:**
```json
{ "type": "scroll", "data": { "dy": -50 } }

```


* **Media Playback Controls:**
```json
{ "type": "media", "data": { "action": "play_pause" } } // Options: "play_pause", "next", "prev", "stop"

```


* **Master Volume Set:**
```json
{ "type": "volume_set", "data": { "level": 50 } } // Integer percentage 0-100

```


* **Display Brightness Set:**
```json
{ "type": "brightness_set", "data": { "level": 70 } } // Integer percentage 0-100

```


* **Keystroke / Hotkey Combo:**
```json
{ "type": "key", "data": { "modifiers": ["ctrl", "alt"], "key": "del" } }

```


* **Text String Injection:**
```json
{ "type": "text", "data": { "text": "Hello RemoteDock!" } }

```


* **Launch Native Binary (.EXE / System Command):**
```json
{ "type": "launch_app", "data": { "path": "calc.exe" } }

```


* **Launch Web URL Target:**
```json
{ "type": "open_url", "data": { "url": "[https://youtube.com](https://youtube.com)" } }

```



---

## 🛠️ Troubleshooting

* **App failing to connect to server:**
* Confirm both mobile device and PC are on the **same local Wi-Fi network**.
* Ensure the firewall rule for port `9999` was added successfully via Administrator CMD.
* Check your laptop's current IPv4 address using `ipconfig` in CMD.


* **Volume control unresponsive:**
* Verify `pycaw` and `comtypes` packages are installed in the host Python runtime environment.


* **Screen View HTTP 503 Service Unavailable:**
* Ensure `mss` and `Pillow` are correctly installed on the host server.



---

## 🤝 Contributing

Contributions are welcome! Pull requests for feature enhancements (such as binary WebSocket streaming, bi-directional clipboard sync, and Wake-on-LAN) are actively encouraged.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

```

```
