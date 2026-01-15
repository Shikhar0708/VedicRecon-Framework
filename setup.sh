#!/bin/bash

# VedicRecon Framework - Linux Setup Utility
# Version: 1.0.0-alpha

echo "--- [ VedicRecon Setup: Linux ] ---"

# 1. Check for Root/Sudo
if [ "$EUID" -ne 0 ]; then 
  echo "[!] Please run as root or with sudo"
  exit
fi
#need to create these directories
echo "[*] Creating ouput/reports directory"
mkdir -p output reports
# 2. Update and Install System Dependencies
echo "[*] Installing system dependencies (nmap, ffuf, golang)..."
apt-get update -y && apt-get install -y \
    nmap \
    ffuf \
    golang-go \
    python3-pip \
    python3-venv \

# 3. Setup Python Virtual Environment
echo "[*] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install pandas requests google-generativeai python-dotenv
fi

# 4. Compile Go Muscle
echo "[*] Compiling Go core binaries..."
mkdir -p bin
cd core
go build -o ../bin/vr_core_linux .
cd ..

# 5. Initialize Directory Structure
echo "[*] Creating workspace folders..."
mkdir -p output reports .runtime_integrity

# 6. Set Permissions
chmod +x bin/vr_core_linux
chmod +x main.py

echo "[+] Setup Complete. Run the tool with: sudo ./venv/bin/python3 main.py"