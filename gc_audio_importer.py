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
