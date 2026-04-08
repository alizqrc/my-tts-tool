#!/bin/bash
# Go to project folder
cd ~/my-tts-clean

# Activate virtual environment
source venv/bin/activate

# Run Flask app in background and open browser automatically
python -m webbrowser -t "http://127.0.0.1:8000" &
python app.py
