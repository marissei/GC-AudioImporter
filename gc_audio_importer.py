import json
import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "GC-AudioImpoter"

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".gc_audio_importer.json")

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def find_ffmpeg():
    folders = [os.path.dirname(os.path.abspath(sys.argv[0])),
               os.path.dirname(os.path.abspath(sys.executable)),
               getattr(sys, "_MEIPASS", "")]
    for folder in folders:
        if not folder:
            continue
        for name in ("ffmpeg.exe", "ffmpeg"):
            candidate = os.path.join(folder, name)
            if os.path.isfile(candidate):
                return candidate
    return shutil.which("ffmpeg")


def _syncsafe(b):
    return (b[0] << 21) | (b[1] << 14) | (b[2] << 7) | b[3]


def inspect_mp3(path):
    found = {"id3v2": False, "cover_art": False, "vbr_header": False,
             "id3v1": False, "tag_bytes": 0}

    with open(path, "rb") as f:
        head = f.read(10)
        audio_start = 0

        if head[:3] == b"ID3":
            size = _syncsafe(head[6:10])
            found["id3v2"] = True
            found["tag_bytes"] = size + 10
            audio_start = size + 10
            f.seek(10)
            tag = f.read(size)

            if b"APIC" in tag or b"PIC" in tag[:2000]:
                found["cover_art"] = True

        f.seek(audio_start)
        first_frame = f.read(2048)
        if any(tag in first_frame for tag in (b"Xing", b"Info", b"VBRI")):
            found["vbr_header"] = True

        f.seek(-128, os.SEEK_END)
        if f.read(3) == b"TAG":
            found["id3v1"] = True

    notes = []
    if found["id3v2"]:
        kb = found["tag_bytes"] / 1024
        notes.append(f"ID3v2 tag at the start ({kb:.0f} KB)")
    if found["cover_art"]:
        notes.append("embedded cover art")
    if found["vbr_header"]:
        notes.append("Xing/VBR header")
    if found["id3v1"]:
        notes.append("ID3v1 tag at the end")
    return found, notes


def convert(ffmpeg, src, out_dir, fmt="ogg", quality=5):
    base = os.path.splitext(os.path.basename(src))[0]
    out_path = os.path.join(out_dir, f"{base}.{fmt}")

    cmd = [
        ffmpeg, "-y", "-v", "error",
        "-i", src,
        "-map", "0:a:0",
        "-vn",
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
    ]

    if fmt == "wav":
        cmd += ["-c:a", "pcm_s16le", "-ar", "44100"]
    else:
        cmd += ["-c:a", "libvorbis", "-q:a", str(quality), "-ar", "44100"]

    cmd.append(out_path)

    result = subprocess.run(cmd, capture_output=True, text=True,
                            creationflags=NO_WINDOW)
    if result.returncode != 0:
        lines = (result.stderr or "").strip().splitlines()
        raise RuntimeError(lines[-1] if lines else "ffmpeg failed")
    return out_path


def process_files(files, out_dir, fmt, quality, log):
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        log("Couldn't find ffmpeg. Put ffmpeg.exe next to this program.")
        return 0

    os.makedirs(out_dir, exist_ok=True)
    done = 0
    for src in files:
        name = os.path.basename(src)
        try:
            _, notes = inspect_mp3(src)
            log(f"{name}: " + (", ".join(notes) if notes else "looks clean already"))
            out = convert(ffmpeg, src, out_dir, fmt, quality)
            log(f"   -> {os.path.basename(out)}  done")
            done += 1
        except Exception as e:
            log(f"   !! failed: {e}")
    log(f"Finished, {done}/{len(files)} converted.")
    return done


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except OSError:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("620x480")
        self.minsize(520, 420)

        cfg = load_config()
        self.files = []
        self.out_dir = tk.StringVar(value=cfg.get("out_dir", ""))
        self.fmt = tk.StringVar(value=cfg.get("fmt", "ogg"))

        pad = {"padx": 10, "pady": 4}

        top = ttk.Frame(self)
        top.pack(fill="both", expand=True, **pad)
        self.listbox = tk.Listbox(top, height=6, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(top, command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        
