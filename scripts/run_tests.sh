#!/bin/bash

# Run Python tests
cd "$(dirname "$0")/.."
echo "Running Python tests..."
python -m pytest tests/ -v

# Check the exit code
if [ $? -ne 0 ]; then
    echo "Python tests failed!"
    exit 1
fi

echo "All tests passed!"
exit 0
