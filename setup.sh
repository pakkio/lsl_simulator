#!/bin/bash
echo "=== LSL Simulator Auto-Test Setup ==="

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
echo "=== Starting NPC Simulator ==="

# Create an expect script to automate the LSL simulator
cat > auto_test.exp << 'EOF'
#!/usr/bin/expect -f

set timeout 60
spawn poetry run python lsl.py npc.lsl

# Wait for notecard reading to complete
expect {
    "notecard_read_complete=1" {
        puts "\nAUTO: Notecard reading completed"
    }
    timeout {
        puts "\nAUTO: Timeout waiting for notecard reading"
        exit 1
    }
}

# Wait for registration to complete
expect {
    "Registration successful!" {
        puts "\nAUTO: Registration completed"
    }
    timeout {
        puts "\nAUTO: Timeout waiting for registration"
        exit 1
    }
}

# Wait for interactive session to start
expect {
    "Type 'help' or 'h' for available commands." {
        puts "\nAUTO: Interactive session started"
        sleep 2
    }
    timeout {
        puts "\nAUTO: Timeout waiting for interactive session"
        exit 1
    }
}

# Simulate avatar approach
puts "\nAUTO: Simulating john approaching..."
send "sense john\r"

# Wait for sensor processing
expect {
    "current_avatar set to:" {
        puts "\nAUTO: Avatar sensing completed"
        sleep 1
    }
    timeout {
        puts "\nAUTO: Timeout waiting for avatar sensing"
    }
}

# Simulate avatar saying hi
puts "\nAUTO: Simulating john saying 'hi'..."
send "s 1 hi\r"

# Wait for HTTP request
expect {
    "MATCHED CURRENT AVATAR - Sending talk request" {
        puts "\nAUTO: HTTP talk request triggered!"
        sleep 2
    }
    "ID mismatch - ignoring message" {
        puts "\nAUTO: Avatar ID mismatch - test failed"
    }
    timeout {
        puts "\nAUTO: Timeout waiting for talk request"
    }
}

puts "\nAUTO: Test sequence completed!"
puts "AUTO: You can continue interacting manually or press Ctrl+C to exit"

# Keep session alive for manual interaction
interact
EOF

chmod +x auto_test.exp

# Check if expect is installed
if ! command -v expect &> /dev/null; then
    echo "ERROR: 'expect' is not installed. Installing it..."
    sudo apt-get update && sudo apt-get install -y expect
fi

# Run the automated test
echo "Running automated NPC test..."
if ./auto_test.exp; then
    echo "Automation completed successfully!"
else
    echo "Automation failed, but you can test manually:"
    echo "1. Run: poetry run python lsl.py npc.lsl"  
    echo "2. Wait for 'Type help or h for available commands'"
    echo "3. Type: sense john"
    echo "4. Type: s 1 hi"
    echo "5. Look for 'HTTP talk request triggered'"
fi

# Cleanup
rm -f auto_test.exp