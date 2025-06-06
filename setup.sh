#!/bin/bash

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python 3.9 if not already installed
if ! command -v python3.9 &> /dev/null; then
    echo "Installing Python 3.9..."
    brew install python@3.9
fi

# Install system dependencies
echo "Installing system dependencies..."
brew install tesseract
brew install poppler

# Create and activate virtual environment with Python 3.9
echo "Setting up Python virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate"
echo "streamlit run frontend/app.py" 