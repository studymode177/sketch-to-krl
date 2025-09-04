#!/bin/bash
# Script to start the Sketch-to-KRL Code Generator application

echo "Starting Sketch-to-KRL Code Generator application..."

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating existing virtual environment..."
    source venv/bin/activate
fi

echo "Running the Flask application..."
python app.py

echo "Application started on http://localhost:5000"