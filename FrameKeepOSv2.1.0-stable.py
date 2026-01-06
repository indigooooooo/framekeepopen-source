# FrameKeep - (C) 2025 Tanner Lucier
# Licensed under GPLv3

import os, sys, json, time, datetime, threading, subprocess, ctypes
import tkinter as tk
from tkinter import filedialog
import cv2, numpy as np, mss
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
try:
    import msvcrt
except ImportError:
    msvcrt = None

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
OPENH264_DIR = os.path.join(BASE_DIR, "openh264")
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe")
if os.path.isdir(OPENH264_DIR):
    os.environ["PATH"] = OPENH264_DIR + os.pathsep + os.environ.get("PATH", "")

APP_NAME = "FrameKeepOS"
ctypes.windll.kernel32.SetConsoleTitleW(APP_NAME)
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
os.makedirs(APPDATA_DIR, exist_ok=True)

DEFAULT_CONFIG = {"fps": 5, "downscale_factor": 0.5, "codec": "H264", "chunk_minutes": 60, "convert_to_mp4": True, "use_crf": True, "crf_value": 23}
COLORS = {"RED": "\x1b[31m", "GREEN": "\x1b[32m", "CYAN": "\x1b[36m", "YELLOW": "\x1b[33m", "MAGENTA": "\x1b[35m", "RESET": "\x1b[0m"}
FOURCC_AVC1 = cv2.VideoWriter_fourcc(*"avc1")
FOURCC_MJPG = cv2.VideoWriter_fourcc(*"MJPG")
state = dict(running=True, recording=False, paused=False, force_new_file=False)
config_lock = threading.Lock()
shared_config = dict()

def ts():
    return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")

def log(tag, msg, color="RESET"):
    print(f"{ts()} {COLORS[color]}[{tag}]{COLORS['RESET']} {msg}", flush=True)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    return None

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

def pick_log_directory():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(title="Select FrameKeepOS Folder")
    root.destroy()
    return path

def today_folder(root):
    path = os.path.join(root, datetime.date.today().strftime("%Y-%m-%d"))
    os.makedirs(path, exist_ok=True)
    return path

def chunk_name(folder):
    return os.path.join(folder, datetime.datetime.now().strftime("%H-%M-%S.mkv"))

def probe_h264(w, h):
    test = os.path.join(APPDATA_DIR, "_probe.mp4")
    vw = cv2.VideoWriter(test, FOURCC_AVC1, 1, (w, h))
    ok = vw.isOpened()
    vw.release()
    os.path.exists(test) and os.remove(test)
    return ok

def print_config(cfg, old_cfg=None):
    log("CONFIG", "Active options:", "CYAN")
    def fmt(key, value, display_value=None):
        display = display_value if display_value is not None else value
        if old_cfg and old_cfg.get(key) != value:
            return f"{COLORS['CYAN']}{display}{COLORS['RESET']}"
        return str(display)
    crf_line = f"\n                           CRF value: {fmt('crf_value', cfg['crf_value'])}" if cfg["use_crf"] else ""
    print(f"                           Codec: {fmt('codec', cfg['codec'])}\n                           Convert to MP4: {fmt('convert_to_mp4', cfg['convert_to_mp4'], 'ON' if cfg['convert_to_mp4'] else 'OFF')}\n                           Use CRF: {fmt('use_crf', cfg['use_crf'], 'ON' if cfg['use_crf'] else 'OFF')}{crf_line}\n                           FPS: {fmt('fps', cfg['fps'])}\n                           Downscale factor: {fmt('downscale_factor', cfg['downscale_factor'])}\n                           Chunk duration: {fmt('chunk_minutes', cfg['chunk_minutes'])} minutes", flush=True)

def refresh_config():
    if state["recording"] or state["paused"]:
        log("ERROR", "You must stop your current recording to refresh your configuration", "RED")
        return False
    log("CONFIG", "Fetching new configuration settings..", "CYAN")
    try:
        if not (new_cfg := load_config()):
            log("ERROR", "Configuration file not found", "RED")
            return False
        with config_lock:
            old_cfg = shared_config.copy() if shared_config else {}
            if new_cfg == old_cfg:
                log("CONFIG", "No new configuration changes found", "YELLOW")
                return True
            shared_config.clear()
            shared_config.update(new_cfg)
        log("CONFIG", "New settings found and applied", "GREEN")
        print_config(new_cfg, old_cfg)
        return True
    except Exception as e:
        log("ERROR", f"Failed to refresh configuration: {str(e)}", "RED")
        return False

def spawn_conversion(path, cfg):
    if cfg["convert_to_mp4"] and path:
        threading.Thread(target=convert_mkv_to_mp4, args=(path, cfg), daemon=True).start()

def convert_mkv_to_mp4(mkv, cfg):
    if not (os.path.exists(FFMPEG_PATH) and os.path.exists(mkv)):
        log("WARN", f"Skipping conversion: {mkv}", "YELLOW")
        return
    mp4 = mkv.replace(".mkv", ".mp4")
    log("CONVERTING", f"{os.path.basename(mkv)} → MP4", "MAGENTA")
    cmd = [FFMPEG_PATH, "-y", "-i", mkv, "-c:v", "libx264", "-preset", "fast", *(["-crf", str(cfg["crf_value"])] if cfg["use_crf"] else []), mp4]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        os.remove(mkv)
        log("CONVERTED", mp4, "GREEN")
    except Exception as e:
        log("FAILED", str(e), "RED")

def recorder_loop():
    recorder_loop.last_file = None
    log("INIT", "Initializing FrameKeepOS", "CYAN")
    ffmpeg_exists = os.path.exists(FFMPEG_PATH)
    log("INIT", "ffmpeg.exe detected" if ffmpeg_exists else "ffmpeg.exe not found", "GREEN" if ffmpeg_exists else "YELLOW")
    if not (cfg := load_config()):
        cfg = DEFAULT_CONFIG | {"log_root": pick_log_directory()}
        save_config(cfg)
    with config_lock:
        shared_config.clear()
        shared_config.update(cfg)
    chunk_seconds = cfg["chunk_minutes"] * 60
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sw, sh = monitor["width"], monitor["height"]
        tw, th = int(sw * cfg["downscale_factor"]), int(sh * cfg["downscale_factor"])
        log("INIT", f"Capturing Monitor 1 ({sw}x{sh}) → {tw}x{th}", "GREEN")
        print_config(cfg)
        fourcc = FOURCC_AVC1 if cfg["codec"].upper() == "H264" and probe_h264(tw, th) else FOURCC_MJPG
        h264_available = fourcc == FOURCC_AVC1
        log("INIT", "H.264 encoder available" if h264_available else "Falling back to MJPG", "GREEN" if h264_available else "YELLOW")
        log("INIT", "Initialization complete. Ready to record", "CYAN")
        out, start = None, None
        while state["running"]:
            with config_lock:
                if shared_config and shared_config != cfg:
                    cfg = shared_config.copy()
                    chunk_seconds = cfg["chunk_minutes"] * 60
                    tw, th = int(sw * cfg["downscale_factor"]), int(sh * cfg["downscale_factor"])
                    fourcc = FOURCC_AVC1 if cfg["codec"].upper() == "H264" and probe_h264(tw, th) else FOURCC_MJPG
                    if out:
                        out.release()
                        out = None
            if state["force_new_file"]:
                if out:
                    out.release()
                    log("STOPPED", "Recording stopped", "YELLOW")
                    spawn_conversion(recorder_loop.last_file, cfg)
                out = start = None
                state["force_new_file"] = False
            if not state["recording"] or state["paused"]:
                time.sleep(0.2)
                continue
            if not out:
                recorder_loop.last_file = chunk_name(today_folder(cfg["log_root"]))
                out = cv2.VideoWriter(recorder_loop.last_file, fourcc, cfg["fps"], (tw, th))
                start = time.time()
                log("RECORDING", recorder_loop.last_file, "CYAN")
            if time.time() - start >= chunk_seconds:
                out.release()
                log("STOPPED", "Recording finished", "YELLOW")
                spawn_conversion(recorder_loop.last_file, cfg)
                out = None
                continue
            frame = cv2.resize(np.array(sct.grab(monitor))[:, :, :3], (tw, th), interpolation=cv2.INTER_AREA)
            out.write(frame)
            time.sleep(1 / cfg["fps"])

def current_icon():
    color = "red" if state["recording"] and not state["paused"] else "yellow" if state["paused"] else "gray"
    img = Image.new("RGB", (64, 64), "black")
    ImageDraw.Draw(img).ellipse((16, 16, 48, 48), fill=color)
    return img

def start_recording(icon, _):
    state.update(recording=True, paused=False)
    log("INIT", "Recording started", "CYAN")
    icon.icon = current_icon()

def pause_recording(icon, _):
    if state["recording"]:
        state["paused"] = True
        log("PAUSED", "Recording paused", "YELLOW")
        icon.icon = current_icon()

def stop_recording(icon, _):
    state.update(recording=False, paused=False, force_new_file=True)
    icon.icon = current_icon()

def quit_app(icon, _):
    log("STOPPED", "FrameKeepOS shutting down", "YELLOW")
    state["running"] = False
    icon.stop()

def keyboard_monitor_win32():
    """Windows-specific keyboard monitoring for Ctrl+R"""
    if sys.platform != "win32" or not msvcrt:
        return
    VK_CONTROL, VK_R = 0x11, 0x52
    user32 = ctypes.windll.user32
    last_ctrl_state = last_r_state = False
    while state["running"]:
        try:
            ctrl_pressed = user32.GetAsyncKeyState(VK_CONTROL) & 0x8000 != 0
            r_pressed = user32.GetAsyncKeyState(VK_R) & 0x8000 != 0
            if ctrl_pressed and r_pressed and not last_r_state and last_ctrl_state:
                refresh_config()
            last_ctrl_state, last_r_state = ctrl_pressed, r_pressed
        except Exception:
            pass
        time.sleep(0.05)

def tray_loop():
    pystray.Icon(APP_NAME, current_icon(), APP_NAME, pystray.Menu(item("Start Recording", start_recording), item("Pause Recording", pause_recording), item("Stop Recording", stop_recording), pystray.Menu.SEPARATOR, item("Quit", quit_app))).run()

if __name__ == "__main__":
    threading.Thread(target=recorder_loop, daemon=True).start()
    if sys.platform == "win32" and msvcrt:
        threading.Thread(target=keyboard_monitor_win32, daemon=True).start()
    tray_loop()