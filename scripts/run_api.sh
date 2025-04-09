#!/bin/bash

# Run the FastAPI server
cd "$(dirname "$0")/.."
echo "Starting Meta Prompt Generator API..."
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
