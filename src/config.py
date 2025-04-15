import os
import platform

BASE_DIR = os.path.dirname(__file__)

# Pick the right Stockfish binary
if platform.system() == "Windows":
    ENGINE_PATH = os.path.abspath(os.path.join(BASE_DIR, "../stockfish.exe"))
else:
    ENGINE_PATH = os.path.abspath(os.path.join(BASE_DIR, "../stockfish"))

ENGINE_DEPTH   = 17
ENGINE_TIME_MS = 1000  # milliseconds per position
