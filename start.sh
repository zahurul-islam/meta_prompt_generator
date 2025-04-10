#!/bin/bash

echo "===================================================="
echo "  Meta Prompt Generator - Quick Start"
echo "===================================================="
echo ""
echo "This script will help you get started with the Meta Prompt Generator."
echo "Choose one of the following options:"
echo ""
echo "1) Run with Docker (recommended)"
echo "2) Run locally (requires Python 3.8+)"
echo "3) Exit"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting with Docker..."
        echo "This will build and start the application using Docker Compose."
        echo ""
        
        # Check if Docker is installed and running
        if ! command -v docker &> /dev/null; then
            echo "Error: Docker is not installed or not in your PATH."
            echo "Please install Docker and try again."
            exit 1
        fi
        
        if ! docker info &> /dev/null; then
            echo "Error: Docker daemon is not running or you don't have permission to access it."
            echo "Try running: sudo systemctl start docker"
            echo "Or add your user to the docker group: sudo usermod -aG docker $USER"
            exit 1
        fi
        
        # Run with Docker Compose
        docker-compose up --build
        ;;
        
    2)
        echo ""
        echo "Running locally..."
        echo "This will set up a Python virtual environment and install dependencies."
        echo ""
        
        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo "Error: Python 3 is not installed or not in your PATH."
            echo "Please install Python 3.8+ and try again."
            exit 1
        fi
        
        # Run the setup script
        chmod +x ./scripts/setup.sh
        ./scripts/setup.sh
        
        # Run the Gradio UI
        chmod +x ./scripts/run_gradio.sh
        ./scripts/run_gradio.sh
        ;;
        
    3)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
