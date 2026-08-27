#!/usr/bin/env bash
# BATMAN — Ubuntu/Linux Dependency Installer
# Run once:  bash scripts/install_deps.sh

set -euo pipefail

echo "=== BATMAN — Installing system dependencies ==="

sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev

echo ""
echo "=== Creating virtual environment ==="
python3 -m venv .venv
source .venv/bin/activate

echo ""
echo "=== Installing Python packages ==="
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Done ==="
echo "To run BATMAN:"
echo "  source .venv/bin/activate"
echo "  python main.py"
