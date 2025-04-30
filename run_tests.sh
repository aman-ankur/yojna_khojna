#!/bin/bash

# This script runs all tests with the correct Python path settings
# For selective test runs, use backend/run_tests.sh instead

# Change to the project root directory (where this script is located)
cd "$(dirname "$0")"

# Set PYTHONPATH to include the current directory (project root) 
# This ensures imports like "from backend.src..." work properly
export PYTHONPATH=.:$PYTHONPATH

# Run pytest with verbose output
python -m pytest backend/tests -v 