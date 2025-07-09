#!/usr/bin/env python3
"""
Full test of NPC script with mock server
"""

import sys
import os
import time
import threading
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsl_parser import LSLParser
from lsl_simulator import LSLSimulator

def run_mock_server():
    """Run the mock server in background"""
    try:
        print("Starting mock Nexus server...")
        server_process = subprocess.Popen([
            sys.executable, 'mock_nexus_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give server time to start
        time.sleep(2)
        
        # Check if server is still running
        if server_process.poll() is None:
            print("✓ Mock server started successfully")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            print(f"✗ Mock server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Error starting mock server: {e}")
        return None

def test_full_npc():
    """Test the full NPC system"""
    print("="*60)
    print("FULL NPC SYSTEM TEST")
    print("="*60)
    
    # Start mock server
    server_process = run_mock_server()
    if not server_process:
        return False
    
    try:
        # Load and parse NPC script
        with open('npc.lsl', 'r') as f:
            npc_script = f.read()
        
        parser = LSLParser()
        parsed_script = parser.parse(npc_script)
        print("✓ NPC script loaded and parsed")
        
        # Create simulator
        simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=npc_script)
        print("✓ LSL simulator created")
        
        # Test HTTP connectivity
        print("\nTesting HTTP connectivity to mock server...")
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✓ Mock server is responding")
                print(f"  Response: {response.json()}")
            else:
                print(f"⚠ Mock server returned status {response.status_code}")
        except Exception as e:
            print(f"✗ Cannot connect to mock server: {e}")
            return False
        
        # Run simulation for a short time
        print("\nRunning NPC simulation...")
        
        def run_simulation():
            try:
                simulator.run()
            except Exception as e:
                print(f"Simulator error: {e}")
        
        sim_thread = threading.Thread(target=run_simulation)
        sim_thread.daemon = True
        sim_thread.start()
        
        # Let it run for a few seconds
        time.sleep(5)
        
        # Stop simulation
        simulator.stop()
        
        print("✓ NPC simulation completed")
        
        # Test NPC registration manually
        print("\nTesting NPC registration...")
        
        # Read the notecard content
        with open('npc_profile.txt', 'r') as f:
            profile_content = f.read()
        
        registration_data = {
            "profile": profile_content,
            "region": "Test Region",
            "position": [128.0, 128.0, 25.0],
            "owner": "owner-uuid-12345",
            "object_key": "object-uuid-67890"
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/npc/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✓ NPC registration successful")
                print(f"  NPC Name: {result.get('npc_name')}")
                print(f"  NPC Role: {result.get('role')}")
                print(f"  Capabilities: {list(result.get('capabilities', {}).keys())}")
            else:
                print(f"✗ NPC registration failed: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Error testing NPC registration: {e}")
        
        # Test hook interaction
        print("\nTesting hook interaction...")
        
        hook_data = {
            "avatar": "test-avatar-uuid",
            "avatar_name": "Test User",
            "region": "Test Region",
            "npc_profile": profile_content
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/npc/hook",
                json=hook_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Hook interaction successful")
                print(f"  NPC says: {result.get('say')}")
                print(f"  Text display: {result.get('text_display')}")
                print(f"  Animation: {result.get('animation')}")
            else:
                print(f"✗ Hook interaction failed: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Error testing hook interaction: {e}")
        
        # Test talk interaction
        print("\nTesting talk interaction...")
        
        talk_data = {
            "avatar": "test-avatar-uuid",
            "avatar_name": "Test User",
            "message": "Hello, can you help me?",
            "conversation_state": "greeting",
            "npc_profile": profile_content
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/npc/talk",
                json=talk_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Talk interaction successful")
                print(f"  NPC says: {result.get('say')}")
                print(f"  Text display: {result.get('text_display')}")
                print(f"  Conversation state: {result.get('conversation_state')}")
            else:
                print(f"✗ Talk interaction failed: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Error testing talk interaction: {e}")
        
        print("\n" + "="*60)
        print("FULL NPC SYSTEM TEST COMPLETED")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ Error in full test: {e}")
        return False
        
    finally:
        # Clean up server process
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✓ Mock server stopped")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print("✓ Mock server killed")

if __name__ == "__main__":
    success = test_full_npc()
    print(f"\n{'🎉 All tests passed!' if success else '❌ Some tests failed.'}")
    sys.exit(0 if success else 1)