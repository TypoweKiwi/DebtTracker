#!/bin/bash

# Run DebtTracker in development mode on localhost.
# Launches both API (Flask) and Web (React) servers side-by-side.
#
# Usage: ./scripts/run-dev.sh [--no-frontend] [--no-backend]

set -e

# Get repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starting DebtTracker development environment..."
echo "Repo root: $REPO_ROOT"
echo ""

# Parse arguments
NO_FRONTEND=false
NO_BACKEND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-frontend) NO_FRONTEND=true; shift ;;
        --no-backend) NO_BACKEND=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate prerequisites
echo "📋 Checking prerequisites..."

PYTHON_CMD=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON_CMD" ] && [ "$NO_BACKEND" != "true" ]; then
    echo "✗ Python not found. Install from https://python.org"
    exit 1
elif [ -n "$PYTHON_CMD" ]; then
    PYTHON_VER=$($PYTHON_CMD --version 2>&1)
    echo "✓ $PYTHON_VER"
fi

NODE_CMD=$(command -v node || true)
if [ -z "$NODE_CMD" ] && [ "$NO_FRONTEND" != "true" ]; then
    echo "✗ Node.js not found. Install from https://nodejs.org"
    exit 1
elif [ -n "$NODE_CMD" ]; then
    NODE_VER=$($NODE_CMD --version)
    NPM_VER=$(npm --version)
    echo "✓ Node.js: $NODE_VER, npm: $NPM_VER"
fi

# Backend setup
if [ "$NO_BACKEND" != "true" ]; then
    echo ""
    echo "📦 Setting up backend..."
    
    API_DIR="$REPO_ROOT/api"
    VENV_DIR="$API_DIR/.venv"
    
    # Create venv if missing
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating Python virtual environment..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
    
    # Activate venv and install dependencies
    echo "Activating venv and installing dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install -q -r "$API_DIR/requirements.txt"
    echo "✓ Backend ready"
fi

# Frontend setup
if [ "$NO_FRONTEND" != "true" ]; then
    echo ""
    echo "📦 Setting up frontend..."
    
    WEB_DIR="$REPO_ROOT/web"
    
    echo "Installing npm dependencies..."
    cd "$WEB_DIR"
    npm install -q
    cd "$REPO_ROOT"
    echo "✓ Frontend ready"
fi

echo ""
echo "============================================================"
echo "Starting development servers..."
echo "============================================================"

# Start backend
if [ "$NO_BACKEND" != "true" ]; then
    echo ""
    echo "🔵 Backend: http://localhost:5000"
    API_DIR="$REPO_ROOT/api"
    VENV_DIR="$API_DIR/.venv"
    (
        source "$VENV_DIR/bin/activate"
        cd "$API_DIR"
        python app.py
    ) &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    sleep 2
fi

# Start frontend
if [ "$NO_FRONTEND" != "true" ]; then
    echo "🟢 Frontend: http://localhost:3000"
    WEB_DIR="$REPO_ROOT/web"
    (
        cd "$WEB_DIR"
        npm start
    ) &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    sleep 2
fi

echo ""
echo "Both servers should be running. Check logs above for any errors."
echo "Press Ctrl+C to stop all servers."

# Cleanup on interrupt
trap 'cleanup' INT TERM

cleanup() {
    echo ""
    echo ""
    echo "Cleaning up..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "✓ Backend stopped"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✓ Frontend stopped"
    fi
    exit 0
}

# Keep script running
wait
