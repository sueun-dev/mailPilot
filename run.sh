#!/bin/bash

# Set UTF-8 encoding for proper Korean support
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Run the application with uv
uv run python src/main.py