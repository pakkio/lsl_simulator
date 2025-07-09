#!/bin/bash
nohup python mock_nexus_server.py > server.log 2>&1 &
echo "Server started in background, PID: $!"
echo "Log output: tail -f server.log"