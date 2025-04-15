import os
import platform

# src/config.py
BASE_DIR     = os.path.dirname(__file__)  # .../your‑project/src

# Dynamically select the Stockfish binary based on the operating system
if platform.system() == "Windows":
    ENGINE_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../stockfish.exe")
    )
else:
    ENGINE_PATH = os.path.abspath(
        os.path.join(BASE_DIR, "../stockfish/stockfish-ubuntu-x86-64-avx512")
    )

ENGINE_DEPTH = 15
ENGINE_TIME_MS = 1000  # Default time in milliseconds for engine calculations
