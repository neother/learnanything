#!/bin/bash

echo ""
echo "========================================"
echo "  Starting Learn Anything Development"
echo "========================================"
echo ""

# Stop processes running on ports 3000 and 8000
echo "Checking for existing processes on ports 3000 and 8000..."
pkill -f "uvicorn\|npm start" || true
for PORT in 3000 8000; do
  if command -v lsof > /dev/null; then
    PID=$(lsof -ti tcp:$PORT)
  else
    # Fallback for systems without lsof
    PID=$(netstat -tulpn 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
  fi

  if [ -n "$PID" ]; then
    echo "Stopping process on port $PORT (PID: $PID)..."
    kill -9 $PID 2>/dev/null
  fi
done

echo ""
echo "Starting backend (FastAPI with uvicorn)..."
cd backend/backend

# Check if we're in a virtual environment, if not try to activate one
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    elif [ -f "../venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source ../venv/bin/activate
    fi
fi

# Check if uvicorn is installed and install if needed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Installing uvicorn..."
    python3 -m pip install uvicorn
fi

# Start the backend with more detailed logging
echo "Starting backend server..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug > ../../backend.log 2>&1 &
BACKEND_PID=$!

cd ../..
echo "Waiting for backend to start..."

# Wait for up to 15 seconds for the backend to start
for i in {1..15}; do
    if command -v lsof > /dev/null; then
        if lsof -ti tcp:8000 > /dev/null 2>&1; then
            echo "✓ Backend started successfully!"
            break
        fi
    else
        # Fallback check using netstat or ss
        if netstat -tuln 2>/dev/null | grep ":8000 " > /dev/null || ss -tuln 2>/dev/null | grep ":8000 " > /dev/null; then
            echo "✓ Backend started successfully!"
            break
        fi
    fi

    if [ $i -eq 15 ]; then
        echo "❌ Backend failed to start within 15 seconds"
        echo "Check backend.log for errors:"
        echo ""
        echo "--- Last 10 lines of backend.log ---"
        tail -n 10 backend.log 2>/dev/null || echo "Could not read backend.log"
        exit 1
    fi

    sleep 1
    echo "  Waiting for backend... ($i/15)"
done

echo ""
echo "Starting frontend (npm start)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start frontend in background without opening browser
BROWSER=none npm start > /dev/null 2>&1 &
FRONTEND_PID=$!

cd ..

echo "Waiting for servers to initialize..."
sleep 5

# Final check if backend is running
backend_running=false
if command -v lsof > /dev/null; then
    if lsof -ti tcp:8000 > /dev/null 2>&1; then
        backend_running=true
    fi
else
    if netstat -tuln 2>/dev/null | grep ":8000 " > /dev/null || ss -tuln 2>/dev/null | grep ":8000 " > /dev/null; then
        backend_running=true
    fi
fi

if [ "$backend_running" = false ]; then
    echo "❌ Error: Backend failed to start on port 8000"
    echo "Check backend.log for errors:"
    echo ""
    tail -n 20 backend.log 2>/dev/null || echo "Could not read backend.log"
    exit 1
fi

# Check if frontend is running (give it more time)
sleep 3
frontend_running=false
if command -v lsof > /dev/null; then
    if lsof -ti tcp:3000 > /dev/null 2>&1; then
        frontend_running=true
    fi
else
    if netstat -tuln 2>/dev/null | grep ":3000 " > /dev/null || ss -tuln 2>/dev/null | grep ":3000 " > /dev/null; then
        frontend_running=true
    fi
fi

if [ "$frontend_running" = false ]; then
    echo "❌ Warning: Frontend may still be starting on port 3000"
    echo "Give it a few more seconds and check http://localhost:3000"
fi

echo ""
echo "========================================"
echo "✓ Development servers started!"
echo "========================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📝 Backend log: backend.log"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."

    # Kill backend
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi

    # Kill frontend
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi

    # Cleanup any remaining processes on our ports
    for PORT in 3000 8000; do
        if command -v lsof > /dev/null; then
            PID=$(lsof -ti tcp:$PORT 2>/dev/null)
        else
            PID=$(netstat -tulpn 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
        fi

        if [ -n "$PID" ] && [ "$PID" != "0" ]; then
            echo "Cleaning up remaining process on port $PORT (PID: $PID)..."
            kill -9 $PID 2>/dev/null
        fi
    done

    echo "✓ All servers stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Keep script running and wait for user to press Ctrl+C
while true; do
    sleep 1
done