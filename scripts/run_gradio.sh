#!/bin/bash

# Run the Gradio UI
cd "$(dirname "$0")/.."
echo "Starting Meta Prompt Generator Gradio UI..."
python -m src.gradio_ui
