import os
import sys
import json
import time
import datetime
import threading
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

if getattr(sys, 'frozen', False):
    os.add_dll_directory(sys._MEIPASS)

FPS = 5
DOWNSCALE_FACTOR = 0.5
CHUNK_DURATION = 3600  # 1 hour

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
            cfg = json.load(f)
    else:
        cfg = None

    return cfg

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

# ---------- RECORDER THREAD ----------
def recorder_loop():
    cfg = load_config()

    if cfg is None:
        folder = pick_log_directory()
        cfg = {
            "log_root": folder,
            "fps": FPS,
            "downscale_factor": DOWNSCALE_FACTOR,
            "codec": "H264"  # DEFAULT
        }
        save_config(cfg)
    else:
        folder = cfg["log_root"]
        cfg.setdefault("codec", "H264")
        save_config(cfg)

    codec_choice = cfg["codec"].upper()

    with mss.mss() as sct:
        monitor = sct.monitors[1]

        sw, sh = monitor["width"], monitor["height"]
        tw, th = int(sw * DOWNSCALE_FACTOR), int(sh * DOWNSCALE_FACTOR)

        # ---------- CODEC SELECTION ----------
        if codec_choice == "H264":
            fourcc = cv2.VideoWriter_fourcc(*"H264")
            test_path = os.path.join(folder, "codec_test.mkv")
            test_writer = cv2.VideoWriter(test_path, fourcc, FPS, (tw, th))

            if not test_writer.isOpened():
                print("[WARN] H.264 unavailable, falling back to MJPG.")
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")

            test_writer.release()
            if os.path.exists(test_path):
                os.remove(test_path)

        else:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        out = None
        chunk_start = None

        while state["running"]:

            if state["force_new_file"]:
                if out:
                    out.release()
                    out = None
                chunk_start = None
                state["force_new_file"] = False

            if not state["recording"] or state["paused"]:
                time.sleep(0.2)
                continue

            if out is None:
                day_folder = get_today_folder(folder)
                file_path = get_chunk_filename(day_folder)
                out = cv2.VideoWriter(file_path, fourcc, FPS, (tw, th))
                chunk_start = time.time()
                print(f"[RECORDING] {file_path}")

            if time.time() - chunk_start >= CHUNK_DURATION:
                out.release()
                out = None
                continue

            frame = np.array(sct.grab(monitor))[:, :, :3]
            frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)
            out.write(frame)

            time.sleep(1 / FPS)

        if out:
            out.release()

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
    state["recording"] = True
    state["paused"] = False
    icon.icon = get_icon()

def pause_recording(icon, _):
    if state["recording"]:
        state["paused"] = True
        icon.icon = get_icon()

def stop_recording(icon, _):
    state["recording"] = False
    state["paused"] = False
    state["force_new_file"] = True
    icon.icon = get_icon()

def quit_app(icon, _):
    state["running"] = False
    icon.stop()

# ---------- MENU ----------
def build_menu():
    return pystray.Menu(
        item("Start Recording", start_recording,
             checked=lambda _: state["recording"] and not state["paused"]),
        item("Pause Recording", pause_recording,
             checked=lambda _: state["paused"]),
        item("Stop Recording", stop_recording,
             checked=lambda _: not state["recording"]),
        pystray.Menu.SEPARATOR,
        item("Quit", quit_app)
    )

def tray_loop():
    icon = pystray.Icon("FrameKeepOS", get_icon(), "FrameKeepOS", build_menu())
    icon.run()

# ---------- MAIN ----------
if __name__ == "__main__":
    threading.Thread(target=recorder_loop, daemon=True).start()
    tray_loop()
