import os
from datetime import datetime

def ensure_dir(path_or_dir: str):
    
    directory = path_or_dir if os.path.isdir(path_or_dir) else os.path.dirname(path_or_dir)
    if directory:
        os.makedirs(directory, exist_ok=True)

def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg: str):
    print(f"[{ts()}] {msg}")