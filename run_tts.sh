#!/bin/bash

# Go to project folder
cd ~/my-tts-clean || exit

# Activate virtual environment
source venv/bin/activate

# Run Flask app in the background
python app.py &

# Wait a few seconds for the server to start
sleep 3

# Open the browser automatically
python -m webbrowser -t "http://127.0.0.1:5000"
