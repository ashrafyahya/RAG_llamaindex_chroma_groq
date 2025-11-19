#!/bin/bash

# Startup script for RAG System (Backend + Frontend)
# This script starts both the FastAPI backend and React frontend

echo "🚀 Starting RAG System..."
echo ""

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
cd backend
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start backend in background
echo "🔧 Starting FastAPI backend on port 8000..."
python main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if frontend dependencies are installed
echo ""
echo "📦 Checking frontend dependencies..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "🎨 Starting React frontend on port 3000..."
npm start

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

# Register cleanup function
trap cleanup INT TERM

# Keep script running
wait
