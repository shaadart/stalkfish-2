# Use a lightweight Linux base image
FROM ubuntu:20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libstdc++6

# Copy the Stockfish binary into the container
COPY stockfish/stockfish-ubuntu-x86-64-avx512 /usr/local/bin/stockfish

# Ensure the binary is executable
RUN chmod +x /usr/local/bin/stockfish

# Expose a port for communication (e.g., 5000)
EXPOSE 5000

# Run Stockfish as a service
CMD ["stockfish"]