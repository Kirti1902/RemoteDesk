# server.py — run on your Windows laptop
# pip install flask flask-cors pyautogui pycaw comtypes screen-brightness-control mss Pillow
from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui, subprocess, base64, io, sys
import ctypes
import psutil
import time

app = Flask(__name__)
CORS(app)
pyautogui.FAILSAFE = False

# Volume control (Windows)
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_ctrl = interface.QueryInterface(IAudioEndpointVolume)
except: volume_ctrl = None

# Brightness control
try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except: HAS_SBC = False

# Screenshot
try:
    import mss, mss.tools
    from PIL import Image
    HAS_MSS = True
except: HAS_MSS = False

# Key name fixes
KEY_MAP = {"win":"winleft","winleft":"winleft","winright":"winright"}
def fix_key(k): return KEY_MAP.get(k.lower(), k.lower())

@app.route("/ping")
def ping(): return "ok"

@app.route("/screenshot")
def screenshot():
    if not HAS_MSS: return jsonify(error="mss not installed"), 503
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        pil = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        pil.thumbnail((960, 540), Image.LANCZOS)
        buf = io.BytesIO()
        pil.save(buf, format="JPEG", quality=55)
        b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify(image=b64)

@app.route("/command", methods=["POST"])
def command():
    d = request.json
    print("\n========================")
    print(d)
    print("========================")
    t = d.get("type")
    data = d.get("data", {})
    if t == "mouse_move":
        pyautogui.moveRel(data["dx"], data["dy"], _pause=False)
    elif t == "mouse_click":
        b = data.get("button","left")
        if b == "double": pyautogui.doubleClick()
        elif b == "right": pyautogui.rightClick()
        else: pyautogui.click()
    elif t == "scroll":
        pyautogui.scroll(int(-data["dy"]/10))
    elif t == "media":
        keys={"play_pause":"playpause","next":"nexttrack","prev":"prevtrack","stop":"stop"}
        pyautogui.press(keys.get(data["action"],"playpause"))
    elif t == "volume":
        steps = max(1, abs(int(data["delta"])))
        key = "volumeup" if data["delta"] > 0 else "volumedown"
        for _ in range(steps): pyautogui.press(key)
    elif t == "volume_set":
        if volume_ctrl:
            level = max(0.0, min(1.0, data["level"] / 100.0))
            volume_ctrl.SetMasterVolumeLevelScalar(level, None)
        else:
            pyautogui.press("volumedown", presses=50)
            pyautogui.press("volumeup", presses=int(data["level"] / 2))
    elif t == "brightness_set":
        if HAS_SBC: sbc.set_brightness(int(data["level"]))
    elif t == "mute":
        pyautogui.press("volumemute")
    #elif t == "key":
     #   mods = [fix_key(m) for m in data.get("modifiers", [])]
      #  k = fix_key(data["key"])
       # if mods: pyautogui.hotkey(*mods, k)
        #else: pyautogui.press(k)
    elif t == "text":
        pyautogui.write(data["text"], interval=0.02)
    #elif t == "launch_app":
     #   subprocess.Popen(data["path"], shell=True)
    elif t == "key":
        mods = [fix_key(m) for m in data.get("modifiers", [])]
        k = fix_key(data["key"])
        print("Mods:", mods, "Key:", k)
        # Win + L -> Lock using Windows API
        if ("winleft" in mods or "winright" in mods or "win" in mods) and k == "l":
            print("Locking Windows...")
            ctypes.windll.user32.LockWorkStation()
        elif mods:
            pyautogui.hotkey(*mods, k)
        else:
            pyautogui.press(k)
    elif t == "launch_app":
        path = data["path"]
        print("Launch request:", path)
        if path.lower() == "battery":
            print("Battery button pressed!")
            batt = psutil.sensors_battery()
            print("Battery:", batt)
            if batt is None:
                ctypes.windll.user32.MessageBoxW(
                0,
                "Battery information is not available.",
                "RemoteDock",
                0x40
                )
                return jsonify({"available": False})

            result = {
            "available": True,
            "percent": batt.percent,
            "charging": batt.power_plugged,
            "seconds_left": batt.secsleft
            }

            # Show Windows popup
            message = (
            f"Battery: {batt.percent}%\n\n"
            f"Charging: {'Yes' if batt.power_plugged else 'No'}\n\n"
            )

            if batt.secsleft >= 0:
                hours = batt.secsleft // 3600
                minutes = (batt.secsleft % 3600) // 60
                message += f"Time Left: {hours}h {minutes}m"

            ctypes.windll.user32.MessageBoxW(
            0,
            message,
            "Laptop Battery",
            0x40  # Information icon
            )

        return jsonify(result)

        subprocess.Popen(path, shell=True)
    elif t == "open_url":
        import webbrowser
        webbrowser.open(data["url"])
    return jsonify(ok=True)

_net_last = {"t": time.time(), "s": psutil.net_io_counters().bytes_sent, "r": psutil.net_io_counters().bytes_recv}

@app.route("/status")
def get_status():
    global _net_last
    now = time.time(); nc = psutil.net_io_counters()
    dt = max(0.1, now - _net_last["t"])
    sent_spd = (nc.bytes_sent - _net_last["s"]) / dt / 1024
    recv_spd = (nc.bytes_recv - _net_last["r"]) / dt / 1024
    _net_last = {"t": now, "s": nc.bytes_sent, "r": nc.bytes_recv}
    bat = psutil.sensors_battery()
    temp = None
    try:
        temps = psutil.sensors_temperatures()
        for k in ["coretemp","cpu_thermal","k10temp","acpitz"]:
            if k in temps and temps[k]: temp = round(temps[k][0].current,1); break
    except: pass
    vm = psutil.virtual_memory()
    try: disk = psutil.disk_usage("C:\\")
    except: disk = psutil.disk_usage("/")
    return jsonify(
        cpu_percent=psutil.cpu_percent(interval=0.1), cpu_count=psutil.cpu_count(),
        ram_used=round(vm.used/1048576,1), ram_total=round(vm.total/1048576,1), ram_percent=vm.percent,
        disk_used=round(disk.used/1073741824,2), disk_total=round(disk.total/1073741824,2), disk_percent=disk.percent,
        battery_percent=round(bat.percent) if bat else None,
        battery_charging=bool(bat.power_plugged) if bat else False,
        battery_plugged=bool(bat.power_plugged) if bat else False,
        net_sent_speed=round(sent_spd,1), net_recv_speed=round(recv_spd,1),
        net_sent_total=round(nc.bytes_sent/1048576,1), net_recv_total=round(nc.bytes_recv/1048576,1),
        uptime_seconds=int(time.time()-psutil.boot_time()), temperature=temp)


if __name__ == "__main__":
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    print("\n=== RemoteDock Server ===")
    print(f"Your laptop IP: {ip}")
    print("Port: 9999")
    print("Enter this IP in the app!")
    app.run(host="0.0.0.0", port=9999)
