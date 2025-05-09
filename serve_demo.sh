#!/bin/bash
set -e

echo -e "\033[1;34m>>> Starting Yojna Khojna Demo\033[0m"

# Start backend server
echo -e "\033[1;34m>>> Starting backend server...\033[0m"
python -m uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "\033[1;34m>>> Backend server started on port 8000\033[0m"

# Wait for backend to initialize
sleep 2

# Start frontend dev server
cd frontend
echo -e "\033[1;34m>>> Starting frontend dev server...\033[0m"
BROWSER=none npx vite --host --port 3000 &
FRONTEND_PID=$!
echo -e "\033[1;34m>>> Frontend dev server started on port 3000\033[0m"

# Display URLs
echo -e "\033[1;34m>>> Services started successfully!\033[0m"
echo -e "\033[1;34m>>> Backend API: http://localhost:8000\033[0m"
echo -e "\033[1;34m>>> Frontend: http://localhost:3000\033[0m"
echo -e "\033[1;34m>>> To create a public URL, run in another terminal: cloudflared tunnel --url http://localhost:3000\033[0m"
echo -e "\033[1;34m>>> Press Ctrl+C to stop all services\033[0m"

# Cleanup on exit
trap "echo -e '\033[1;34m>>> Shutting down services...\033[0m'; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null" EXIT

# Keep the script running
wait 