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
