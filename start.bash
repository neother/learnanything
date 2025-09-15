#!/bin/bash

# Stop processes running on ports 3000 and 8000
for PORT in 3000 8000; do
  PID=$(lsof -ti tcp:$PORT)
  if [ -n "$PID" ]; then
    echo "Stopping process on port $PORT (PID: $PID)..."
    kill -9 $PID
  else
    echo "No process running on port $PORT."
  fi
done

# Start backend first
echo "Starting backend (FastAPI with uvicorn)..."
cd backend/backend

# Check if uvicorn is installed and install if needed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Installing uvicorn..."
    python3 -m pip install uvicorn
fi

# Start the backend with more detailed logging
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug | tee ../../backend.log &
BACKEND_PID=$!
cd ../..
echo "Waiting for backend to start..."
# Wait for up to 10 seconds for the backend to start
for i in {1..10}; do
    if lsof -ti tcp:8000 > /dev/null; then
        echo "Backend started successfully!"
        break
    fi
    sleep 1
    echo "Waiting for backend... ($i/10)"
done

echo "Starting frontend (npm start)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Waiting for servers to initialize..."
sleep 3

# Final check if backend is running
if ! lsof -ti tcp:8000 > /dev/null; then
    echo "Error: Backend failed to start on port 8000"
    echo "Check backend.log for errors:"
    tail -n 20 backend.log
    exit 1
fi

# Check if frontend is running
if ! lsof -ti tcp:3000 > /dev/null; then
    echo "Error: Frontend failed to start on port 3000"
    exit 1
fi

echo "Backend running with PID $BACKEND_PID. Log: backend.log"
echo "Frontend running with PID $FRONTEND_PID."