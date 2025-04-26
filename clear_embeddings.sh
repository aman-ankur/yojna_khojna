#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the virtual environment path relative to the script directory
VENV_PATH="$SCRIPT_DIR/backend/yojna/bin/activate"

# Define the Python script path relative to the script directory
PYTHON_SCRIPT="$SCRIPT_DIR/backend/src/delete_embeddings.py"

# Check if virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH" >&2
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH"

# Check if activation was successful (optional, based on how venv behaves)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment." >&2
    exit 1
fi

echo "Virtual environment activated."

# Run the Python script
echo "Running the embedding deletion script..."
python "$PYTHON_SCRIPT"

# Deactivate virtual environment (optional, happens automatically when script exits)
# deactivate

echo "Script finished." 