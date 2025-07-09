#!/bin/bash
echo "=== LSL Simulator Setup ==="

# Kill any existing processes on port 5000
echo "Stopping existing server..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start the mock nexus server 
echo "Starting mock nexus server..."
poetry run python mock_nexus_server.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 4

# Check if server is running
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Server is running on http://localhost:5000 (PID: $SERVER_PID)"
else
    echo "❌ Server failed to start"
    exit 1
fi

echo ""
echo "=== Ready to use ==="
echo "• Server: http://localhost:5000"
echo "• Run NPC: ./run_npc.sh" 
echo "• Stop server: lsof -ti:5000 | xargs kill -9"
echo "• Server logs: tail -f server.log"
echo ""