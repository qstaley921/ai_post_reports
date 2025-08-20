#!/usr/bin/env bash
# Full-stack development start script

echo "🚀 Starting AI Post Report Full-Stack Development Environment..."
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: Not in the AI Post Report directory"
    exit 1
fi

# Start backend in background
echo "🔧 Starting Backend (FastAPI)..."
(
    cd "$(dirname "$0")/.."
    source venv/bin/activate 2>/dev/null || { echo "No venv found, creating..."; python3 -m venv venv; source venv/bin/activate; }
    pip install -q -r docs/requirements-backend.txt
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
) &

# Give backend time to start
sleep 3

# Start frontend in background  
echo "🌐 Starting Frontend (Static Server)..."
python3 -m http.server 8080 &

echo ""
echo "✅ Services started:"
echo "   🔧 Backend API: http://localhost:8000"
echo "   🌐 Frontend App: http://localhost:8080"
echo "   📖 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo ""

# Wait for background processes
wait
