#!/bin/bash
# Helper script to run the discussion system specifically handling local site-packages

# Get user site packages directory
SITE_PACKAGES=$(python3 -m site --user-site)

# Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$SITE_PACKAGES

echo "Starting Triadic Discussion System..."
echo "Using PYTHONPATH: $PYTHONPATH"

python3 main.py
