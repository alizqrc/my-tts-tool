#!/bin/bash
# Go to project folder
cd ~/my-tts-clean || exit

# Activate virtual environment
source venv/bin/activate

# Start Flask app
python app.py
