#!/bin/bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt
echo ""
echo "Setup complete. Activate the environment with: source venv/bin/activate"
