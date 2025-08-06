#!/bin/bash

# Check if python3-venv is available
if ! python3 -m venv --help &> /dev/null; then
    echo "ERROR: python3-venv is not installed."
    echo "Please run: sudo apt install python3-venv python3-full"
    echo "Then run this script again."
    exit 1
fi

# Remove existing venv if it exists but is broken
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo "Removing broken virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Check if venv was created successfully
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment creation failed."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "Creating .env file..."
cp .env.example .env

echo "Setup complete!"
echo ""
echo "To use the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run commands like: python -m src.main status"