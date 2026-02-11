#!/bin/bash

# Wolmer's Boys' School - WBS Transcript Tracker Backend Startup Script
# This script starts the FastAPI backend server

set -e

echo "=========================================="
echo "WBS Transcript Tracker - Backend Startup"
echo "=========================================="

# Check if running from correct directory
if [ ! -f "backend/server.py" ]; then
    echo "Error: backend/server.py not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "Error: backend/.env file not found."
    echo "Please create backend/.env with required environment variables."
    echo ""
    echo "Required variables:"
    echo "  MONGO_URL=mongodb://localhost:27017"
    echo "  DB_NAME=wbs_tracker"
    echo "  JWT_SECRET=your-secret-key"
    echo "  CORS_ORIGINS=http://localhost:3000"
    exit 1
fi

# Check if MongoDB is accessible
echo ""
echo "Checking MongoDB connection..."
cd backend

# Check if Python dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "Python dependencies not found. Installing..."
    python -m pip install -r requirements.txt
fi

# Start the backend server
echo ""
echo "Starting FastAPI server on port 8000..."
echo "Backend will be available at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
