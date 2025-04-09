#!/bin/bash

# Setup script for Meta Prompt Generator

# Go to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "Setting up Meta Prompt Generator..."
echo "Project root: $PROJECT_ROOT"

# Create a virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required Python packages..."
pip install -r requirements.txt

# Create templates directory if it doesn't exist
if [ ! -d "$PROJECT_ROOT/templates" ]; then
    echo "Creating templates directory..."
    mkdir -p "$PROJECT_ROOT/templates"
fi

echo "Setup complete! You can now run the Gradio UI with: ./scripts/run_gradio.sh"
echo "Or start with Docker using: docker-compose up"
echo "To run the tests: ./scripts/run_tests.sh"
