#!/usr/bin/env bash
# Run both the FastAPI server and Streamlit app simultaneously.
# Usage: bash scripts/run_all.sh
# Stop:  Ctrl+C (kills both processes)

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "🖥️  Starting Streamlit app  on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both."
echo ""

# Start FastAPI in background
uvicorn app.api.app:app --reload --port 8000 &
PID_API=$!

# Start Streamlit in background
streamlit run app/ui/streamlit_app.py --server.port 8501 --server.headless true &
PID_UI=$!

# Trap Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $PID_API $PID_UI 2>/dev/null
    wait $PID_API $PID_UI 2>/dev/null
    echo "Done."
}
trap cleanup SIGINT SIGTERM

# Wait for either to exit
wait $PID_API $PID_UI
