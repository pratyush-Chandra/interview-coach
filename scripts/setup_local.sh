#!/bin/bash

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing dependencies for macOS..."
    brew install python@3.11
    brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing dependencies for Linux..."
    sudo apt-get update && sudo apt-get install -y \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgstreamer1.0-0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-libav \
        gstreamer1.0-tools \
        gstreamer1.0-x \
        gstreamer1.0-alsa \
        gstreamer1.0-gl \
        gstreamer1.0-gtk3 \
        gstreamer1.0-qt5 \
        gstreamer1.0-pulseaudio
else
    echo "Unsupported operating system"
    exit 1
fi

# Create and activate virtual environment with Python 3.11
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate"
echo "streamlit run app.py" 