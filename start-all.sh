#!/bin/bash

# Wolmer's Boys' School - WBS Transcript Tracker - Full Stack Startup Script
# This script starts both backend and frontend servers in the background

set -e

echo "=========================================="
echo "WBS Transcript Tracker - Full Stack"
echo "=========================================="

# Check if running from correct directory
if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "Error: Required files not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Clean up on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "Servers stopped."
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo ""
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend

if [ ! -f ".env" ]; then
    echo "Error: backend/.env not found. Please create it first."
    echo "Run: bash start-backend.sh (it will guide you)"
    exit 1
fi

if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd frontend

if [ ! -f ".env.local" ]; then
    echo "Creating frontend/.env.local..."
    cat > .env.local << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8000
EOF
fi

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    yarn install
fi

yarn start &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

cd ..

echo ""
echo "=========================================="
echo -e "${GREEN}Both servers are running!${NC}"
echo "=========================================="
echo ""
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
