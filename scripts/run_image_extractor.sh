#!/bin/bash

# Run the Image Extractor
cd "$(dirname "$0")/.."
echo "Starting Image Data Extractor..."
python -m src.image_extractor
