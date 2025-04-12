import os

# src/config.py
BASE_DIR     = os.path.dirname(__file__)  # .../your‑project/src
ENGINE_PATH  = os.path.abspath(
    os.path.join(BASE_DIR, os.pardir, "stockfish.exe")
)
ENGINE_DEPTH = 15
