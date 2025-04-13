pip install -r requirements.txt
apt-get install build-essential
apt-get update && apt-get install -y libstdc++6
# Ensure the Stockfish binary is executable
chmod +x stockfish
chmod +x stockfish/stockfish-ubuntu-x86-64-avx512