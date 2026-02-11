#!/bin/bash

# Wolmer's Boys' School - WBS Transcript Tracker Frontend Startup Script
# This script starts the React frontend dev server

set -e

echo "=========================================="
echo "WBS Transcript Tracker - Frontend Startup"
echo "=========================================="

# Check if running from correct directory
if [ ! -f "frontend/package.json" ]; then
    echo "Error: frontend/package.json not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if .env.local file exists
if [ ! -f "frontend/.env.local" ]; then
    echo "Warning: frontend/.env.local not found."
    echo "Creating it with default backend URL..."
    mkdir -p frontend
    cat > frontend/.env.local << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8000
EOF
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "Dependencies not installed. Installing with yarn..."
    yarn install
fi

# Start the frontend dev server
echo ""
echo "Starting React development server on port 3000..."
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

yarn start
