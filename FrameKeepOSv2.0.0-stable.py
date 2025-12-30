# FrameKeep - (C) 2025 Tanner Lucier
# Licensed under GPLv3 - see LICENSE file for details

# ============ DLL / PATH SETUP (this throws errors if it goes anywhere else) ============
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OPENH264_DIR = os.path.join(BASE_DIR, "openh264")
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe")

# PREPEND OpenH264 directory to PATH (FFmpeg REQUIRES THIS)
if os.path.isdir(OPENH264_DIR):
    os.environ["PATH"] = OPENH264_DIR + os.pathsep + os.environ.get("PATH", "")

# ================= NORMAL IMPORTS =================
import json
import time
import datetime
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np
import mss

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

# ================= APP / CONFIG =================
APP_NAME = "FrameKeepOS"

APPDATA_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

def ts():
    return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")

FPS = 5
DOWNSCALE_FACTOR = 0.5

RED = "\x1b[31m"
GREEN = "\x1b[32m"
CYAN = "\x1b[36m"
YELLOW = "\x1b[33m"
MAGENTA = "\x1b[35m"
RESET = "\x1b[0m"

# ---------- GLOBAL STATE ----------
state = {
    "running": True,
    "recording": False,
    "paused": False,
    "force_new_file": False
}

# ---------- CONFIG ----------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

def pick_log_directory():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select FrameKeepOS Folder")
    root.destroy()
    return folder

# ---------- DIRECTORIES ----------
def get_today_folder(root):
    today = datetime.date.today().strftime("%Y-%m-%d")
    path = os.path.join(root, today)
    os.makedirs(path, exist_ok=True)
    return path

def get_chunk_filename(folder):
    now = datetime.datetime.now()
    return os.path.join(folder, now.strftime("%H-%M-%S.mkv"))

# ---------- MKV → MP4 CONVERSION ----------
def convert_mkv_to_mp4(mkv_path, cfg):
    if not os.path.exists(FFMPEG_PATH) or not os.path.exists(mkv_path):
        print(f"{ts()} {YELLOW}[WARN]{RESET} ffmpeg not found, skipping conversion: {mkv_path}")
        sys.stdout.flush()
        return

    mp4_path = mkv_path.replace(".mkv", ".mp4")

    print(f"{ts()} {MAGENTA}[CONVERTING]{RESET} {os.path.basename(mkv_path)} → MP4")
    sys.stdout.flush()

    try:
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", mkv_path,
            "-c:v", "libx264",
            "-preset", "fast"
        ]

        if cfg.get("convert_to_mp4", False) and cfg.get("use_crf", False):
            cmd.extend(["-crf", str(cfg.get("crf_value", 23))])

        cmd.append(mp4_path)

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        os.remove(mkv_path)
        print(f"{ts()} {GREEN}[CONVERTED]{RESET} {mp4_path}")
        sys.stdout.flush()

    except Exception as e:
        print(f"{ts()} {RED}[CONVERT FAILED]{RESET} {mkv_path}: {e}")
        sys.stdout.flush()

# ---------- H.264 PROBE ----------
def probe_h264(width, height):
    test_path = os.path.join(APPDATA_DIR, "_h264_probe.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"avc1")

    writer = cv2.VideoWriter(test_path, fourcc, 1, (width, height))
    ok = writer.isOpened()
    writer.release()

    if os.path.exists(test_path):
        os.remove(test_path)

    return ok

# ---------- RECORDER THREAD ----------
def recorder_loop():
    recorder_loop.last_file = None

    print(f"{ts()} {CYAN}[INIT]{RESET} Initializing FrameKeepOS")
    sys.stdout.flush()

    if not os.path.exists(FFMPEG_PATH):
        print(f"{ts()} {YELLOW}[WARN]{RESET} ffmpeg.exe not found")
    else:
        print(f"{ts()} {GREEN}[INIT]{RESET} ffmpeg.exe detected")
    sys.stdout.flush()

    cfg = load_config()
    if cfg is None:
        folder = pick_log_directory()
        cfg = {
            "log_root": folder,
            "fps": FPS,
            "downscale_factor": DOWNSCALE_FACTOR,
            "codec": "H264",
            "chunk_minutes": 60,
            "convert_to_mp4": True,
            "use_crf": True,
            "crf_value": 23
        }
        save_config(cfg)
    else:
        folder = cfg["log_root"]
        cfg.setdefault("codec", "H264")
        cfg.setdefault("convert_to_mp4", True)
        cfg.setdefault("chunk_minutes", 60)
        cfg.setdefault("use_crf", True)
        cfg.setdefault("crf_value", 23)
        save_config(cfg)

    chunk_duration = int(cfg["chunk_minutes"]) * 60

    with mss.mss() as sct:
        monitor_index = 1
        monitor = sct.monitors[monitor_index]

        sw, sh = monitor["width"], monitor["height"]
        tw, th = int(sw * DOWNSCALE_FACTOR), int(sh * DOWNSCALE_FACTOR)

        print(f"{ts()} {GREEN}[INIT]{RESET} Capturing monitor {monitor_index} ({sw}x{sh}) → {tw}x{th}")
        sys.stdout.flush()

        print(f"{ts()} {CYAN}[CONFIG]{RESET} Active options:")
        print(f"                           Codec: {cfg['codec']}")
        print(f"                           Convert to MP4: {'ON' if cfg.get('convert_to_mp4', False) else 'OFF'}")
        print(f"                           Use CRF: {'ON' if cfg.get('use_crf', False) else 'OFF'}")
        if cfg.get("use_crf", False):
            print(f"                           CRF value: {cfg.get('crf_value', 23)}")
        print(f"                           FPS: {cfg.get('fps', FPS)}")
        print(f"                           Downscale factor: {cfg.get('downscale_factor', DOWNSCALE_FACTOR)}")
        print(f"                           Chunk duration: {cfg.get('chunk_minutes', 60)} minutes")
        sys.stdout.flush()

        if cfg["codec"].upper() == "H264" and probe_h264(tw, th):
            print(f"{ts()} {GREEN}[INIT]{RESET} H.264 encoder available")
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
        else:
            print(f"{ts()} {YELLOW}[WARN]{RESET} Falling back to MJPG")
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        print(f"{ts()} {GREEN}[INIT]{RESET} Initialization complete. Ready to record")
        sys.stdout.flush()

        out = None
        chunk_start = None

        while state["running"]:
            if state["force_new_file"]:
                if out:
                    out.release()
                    print(f"{ts()} {YELLOW}[STOPPED]{RESET} Recording stopped")
                    sys.stdout.flush()

                    if cfg["convert_to_mp4"] and recorder_loop.last_file:
                        threading.Thread(
                            target=convert_mkv_to_mp4,
                            args=(recorder_loop.last_file, cfg),
                            daemon=True
                        ).start()
                    out = None
                chunk_start = None
                state["force_new_file"] = False

            if not state["recording"] or state["paused"]:
                time.sleep(0.2)
                continue

            if out is None:
                day_folder = get_today_folder(folder)
                recorder_loop.last_file = get_chunk_filename(day_folder)
                out = cv2.VideoWriter(recorder_loop.last_file, fourcc, FPS, (tw, th))
                chunk_start = time.time()
                print(f"{ts()} {CYAN}[RECORDING]{RESET} {recorder_loop.last_file}")
                sys.stdout.flush()

            if time.time() - chunk_start >= chunk_duration:
                out.release()
                if cfg["convert_to_mp4"] and recorder_loop.last_file:
                    threading.Thread(
                        target=convert_mkv_to_mp4,
                        args=(recorder_loop.last_file, cfg),
                        daemon=True
                    ).start()
                out = None
                continue

            frame = np.array(sct.grab(monitor))[:, :, :3]
            frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)
            out.write(frame)
            time.sleep(1 / FPS)

# ---------- TRAY ICON ----------
def create_icon_image(color):
    img = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill=color)
    return img

def get_icon():
    if state["recording"] and not state["paused"]:
        return create_icon_image("red")
    if state["paused"]:
        return create_icon_image("yellow")
    return create_icon_image("gray")

def start_recording(icon, _):
    print(f"{ts()} {CYAN}[INIT]{RESET} Recording started")
    state["recording"] = True
    state["paused"] = False
    icon.icon = get_icon()

def pause_recording(icon, _):
    if state["recording"]:
        state["paused"] = True
        print(f"{ts()} {YELLOW}[PAUSED]{RESET} Recording paused")
        icon.icon = get_icon()

def stop_recording(icon, _):
    state["recording"] = False
    state["paused"] = False
    state["force_new_file"] = True
    icon.icon = get_icon()

def quit_app(icon, _):
    print(f"{ts()} {YELLOW}[STOPPED]{RESET} FrameKeepOS shutting down")
    state["running"] = False
    icon.stop()

def build_menu():
    return pystray.Menu(
        item("Start Recording", start_recording),
        item("Pause Recording", pause_recording),
        item("Stop Recording", stop_recording),
        pystray.Menu.SEPARATOR,
        item("Quit", quit_app)
    )

def tray_loop():
    icon = pystray.Icon("FrameKeepOS", get_icon(), "FrameKeepOS", build_menu())
    icon.run()

if __name__ == "__main__":
    threading.Thread(target=recorder_loop, daemon=True).start()
    tray_loop()
