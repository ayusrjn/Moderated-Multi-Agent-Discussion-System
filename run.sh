#!/bin/bash
# Run script for Triadic Discussion System
# Uses the local virtual environment 'env' exclusively

# Ensure we are using the virtual environment python
VENV_PYTHON="./env/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at ./env"
    echo "Please ensure the 'env' directory exists."
    exit 1
fi

# Prevent Python from looking at user site packages (avoids 3.10 vs 3.12 conflicts)
export PYTHONNOUSERSITE=1

# Clear PYTHONPATH to prevent leakage from other setups
unset PYTHONPATH

echo "Starting System using Isolated Environment..."
"$VENV_PYTHON" main.py
