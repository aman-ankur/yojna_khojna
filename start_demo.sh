#!/bin/bash
set -e

# Print colored status messages
function echo_status() {
  echo -e "\033[1;34m>>> $1\033[0m"
}

echo_status "Starting Yojna Khojna Demo"
echo_status "Step 1: Building frontend..."

# Navigate to frontend directory and build
cd frontend
npm run build

echo_status "Frontend built successfully!"
echo_status "Step 2: Starting backend server..."

# Navigate back to project root
cd ..

# Start the backend server
echo_status "Starting FastAPI server (press Ctrl+C to stop)..."
python -m uvicorn backend.src.main:app --host 0.0.0.0 --port 8000

# Note: To expose this server via ngrok, run in another terminal:
# ngrok http 8000 