# 🖥️ RemoteDock

> Turn your mobile device into a real-time, custom PC command center over your local network.

**RemoteDock** is a lightweight, low-latency remote administration system consisting of a **React Native (Expo)** mobile application and a **Python (Flask)** Windows companion server. It allows host control, low-overhead screen mirroring, media management, hotkey injection, and hardware telemetry without reliance on third-party cloud services or subscriptions.

---

## 🛠️ Architecture & Tech Stack

```
   ┌────────────────────────┐              Local Wi-Fi             ┌────────────────────────┐
   │ React Native (Expo)    │ ───────────────────────────────────► │ Python (Flask Server)  │
   │ Mobile Client          │ ◄─────────────────────────────────── │ Windows Host PC        │
   └────────────────────────┘          HTTP / REST & Base64        └────────────────────────┘

```

* **Mobile Client:** React Native, Expo Router, TypeScript, `react-native-reanimated`
* **Backend Server:** Python 3.8+, Flask, Flask-CORS
* **Windows API Integration:** `pyautogui`, `pycaw` (COM interfaces for core volume scalar control), `screen-brightness-control`, `mss`, `Pillow (PIL)`, `psutil`
* **Networking & Protocols:** Local HTTP REST API, base64 JPEG payload streaming, auto IP discovery

---

## ✨ Features

* 🖱️ **Multitouch Trackpad:** Relative mouse movement, tap-to-click, double-click, two-finger scroll emulation, and haptic feedback.
* 🎵 **Audio & Display Control:** Master volume adjustments mapping to native Windows endpoints (`IAudioEndpointVolume`) alongside display brightness regulation.
* ⌨️ **Virtual Keyboard & Hotkey Suite:** System modifier key combinations (Ctrl, Alt, Win, Shift) and 1-tap shortcuts (Task Manager, Lock, Copy/Paste, Screen Grab).
* 🖥️ **Live Display Mirroring:** Live 2–5 FPS desktop screen capture via `mss` & `PIL` compressed to base64 JPEG strings.
* 📊 **Hardware Diagnostics:** Real-time polling for CPU utilization, RAM usage, storage allocations, active network throughput ($KB/s$), battery health, and system uptime.
* 📂 **Custom App Launcher:** Editable application grid to launch native desktop binaries (`.exe`) or web URIs directly on host PC.
* 📐 **Adaptive UI:** Built for dynamic **Portrait and Landscape** screen orientation modes.

---

## 🚀 Setup & Installation

### 1. Host Server Setup (Windows Laptop)

#### Prerequisites

* **Python 3.8 or higher** installed and added to `PATH`.

#### Step 1: Install Dependencies

Open Command Prompt (`cmd`) or PowerShell and run:

```bash
pip install flask flask-cors pyautogui pycaw comtypes screen-brightness-control mss Pillow psutil

```

#### Step 2: Open Firewall Port (Required)

Allow incoming TCP traffic on port `9999` through Windows Firewall. Run Command Prompt as **Administrator**:

```cmd
netsh advfirewall firewall add rule name="RemoteDock" dir=in action=allow protocol=TCP localport=9999

```

#### Step 3: Run the Server

Create a file named `server.py` and paste your backend script. Run it using:

```bash
python server.py

```

*(The terminal will output your laptop’s local IP address, e.g., `192.168.1.5`)*

---

### 2. Mobile Client Setup (App)

#### Option A: Running via Expo (Development)

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/RemoteDock.git
cd RemoteDock
npm install

```


2. Start the Expo development server:
```bash
npx expo start

```


3. Scan the QR code using **Expo Go** (Android) or run on an emulator.

#### Option B: Building standalone APK

To build an installable Android APK:

```bash
npx eas build -p android --profile preview

```

---

## 🔌 API Endpoints Reference

The companion server runs on `http://<LAPTOP_IP>:9999` by default.

### Health & Monitoring

| Endpoint | Method | Response | Description |
| --- | --- | --- | --- |
| `/ping` | `GET` | `"ok"` | Health check to verify host connection. |
| `/status` | `GET` | `JSON` | Fetches CPU, RAM, Disk, Network speeds, Battery state, Temperature, and Uptime telemetry. |
| `/screenshot` | `GET` | `JSON` | Returns a base64-encoded JPEG image string of the primary display. |

### Command Controller Endpoint

`POST /command`

All system input and action triggers are sent via a single JSON payload route:

```json
{
  "type": "<COMMAND_TYPE>",
  "data": { ... }
}

```

#### Supported Payload Formats:

* **Mouse Movement:**
```json
{ "type": "mouse_move", "data": { "dx": 15, "dy": -10 } }

```


* **Mouse Clicks:**
```json
{ "type": "mouse_click", "data": { "button": "left" } } // Options: "left", "right", "double"

```


* **Scrolling:**
```json
{ "type": "scroll", "data": { "dy": -50 } }

```


* **Media Controls:**
```json
{ "type": "media", "data": { "action": "play_pause" } } // Options: "play_pause", "next", "prev", "stop"

```


* **Master Volume Scalar Set:**
```json
{ "type": "volume_set", "data": { "level": 50 } } // 0-100 percentage

```


* **Display Brightness:**
```json
{ "type": "brightness_set", "data": { "level": 70 } } // 0-100 percentage

```


* **Single Key Press / Combinations:**
```json
{ "type": "key", "data": { "modifiers": ["ctrl", "alt"], "key": "del" } }

```


* **Text Input Injection:**
```json
{ "type": "text", "data": { "text": "Hello World!" } }

```


* **Launch Native Application / Executable:**
```json
{ "type": "launch_app", "data": { "path": "calc.exe" } }

```


* **Open URL in Default Browser:**
```json
{ "type": "open_url", "data": { "url": "https://youtube.com" } }

```



---

## 🛠️ Common Troubleshooting

* **App cannot connect to Server:**
* Ensure both laptop and mobile device are connected to the **same Wi-Fi network**.
* Confirm that the firewall port rule was executed in Administrator CMD.
* Verify your host IP using `ipconfig` in CMD.


* **Volume control not responding:**
* Ensure `pycaw` and `comtypes` are properly installed in your active Python environment.


* **Screen Mirroring fails (503 Error):**
* Check that `mss` and `Pillow` packages are installed.



---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to extend features (e.g., WebSockets integration, bi-directional clipboard sync, Wake-on-LAN).

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
