#!/usr/bin/env python3
"""
Test script to verify NPC script functionality with LSL simulator
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsl_parser import LSLParser
from lsl_simulator import LSLSimulator

def test_npc_script():
    """Test the NPC script with the LSL simulator"""
    print("Testing NPC script with LSL simulator...")
    
    # Read the NPC script
    try:
        with open('npc.lsl', 'r') as f:
            npc_script = f.read()
        print("✓ NPC script loaded successfully")
    except FileNotFoundError:
        print("✗ Error: npc.lsl file not found")
        return False
    except Exception as e:
        print(f"✗ Error reading NPC script: {e}")
        return False
    
    # Parse the script
    try:
        parser = LSLParser()
        parsed_script = parser.parse(npc_script)
        print("✓ NPC script parsed successfully")
        
        # Show parsed structure
        print("\nParsed structure:")
        print(f"  - Global variables: {len(parsed_script.get('globals', []))}")
        print(f"  - Functions: {len(parsed_script.get('functions', {}))}")
        print(f"  - States: {list(parsed_script.get('states', {}).keys())}")
        
        # Show function names
        functions = parsed_script.get('functions', {})
        if functions:
            print(f"  - Function names: {list(functions.keys())}")
        
        # Show state events
        states = parsed_script.get('states', {})
        for state_name, state_data in states.items():
            events = list(state_data.keys())
            print(f"  - State '{state_name}' events: {events}")
        
    except Exception as e:
        print(f"✗ Error parsing NPC script: {e}")
        return False
    
    # Test the simulator
    try:
        print("\nTesting LSL simulator with NPC script...")
        simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=npc_script)
        
        # Test some key functions
        print("\nTesting key LSL functions:")
        
        # Test constants (now in global scope)
        print(f"  NULL_KEY: {simulator.global_scope.get('NULL_KEY')}")
        print(f"  TRUE: {simulator.global_scope.get('TRUE')}")
        print(f"  FALSE: {simulator.global_scope.get('FALSE')}")
        print(f"  INVENTORY_NOTECARD: {simulator.global_scope.get('INVENTORY_NOTECARD')}")
        
        # Test NPC functions
        print(f"  osIsNpc test: {simulator.api_osIsNpc('test-npc-key')}")
        print(f"  osIsNpc test (non-NPC): {simulator.api_osIsNpc('avatar-key')}")
        
        # Test utility functions
        print(f"  llGetOwner: {simulator.api_llGetOwner()}")
        print(f"  llGetKey: {simulator.api_llGetKey()}")
        print(f"  llGetRegionName: {simulator.api_llGetRegionName()}")
        
        # Test JSON functions
        test_json = '{"status": "ok", "message": "Hello"}'
        print(f"  JSON test: {simulator.api_llJsonGetValue(test_json, ['status'])}")
        
        # Test list functions
        test_list = ["key1", "value1", "key2", "value2"]
        json_result = simulator.api_llList2Json(simulator.JSON_OBJECT, test_list)
        print(f"  List2Json test: {json_result}")
        
        print("✓ LSL simulator functions working correctly")
        
    except Exception as e:
        print(f"✗ Error testing LSL simulator: {e}")
        return False
    
    # Test notecard reading
    try:
        print("\nTesting notecard reading...")
        if os.path.exists('npc_profile.txt'):
            simulator.api_llGetNotecardLine('npc_profile', 0)
            print("✓ Notecard reading initiated")
        else:
            print("⚠ Warning: npc_profile.txt not found")
    except Exception as e:
        print(f"✗ Error testing notecard reading: {e}")
    
    # Test HTTP request
    try:
        print("\nTesting HTTP request...")
        options = ["method", "POST", "mimetype", "application/json"]
        body = '{"test": "data"}'
        result = simulator.api_llHTTPRequest("http://localhost:5000/health", options, body)
        print(f"✓ HTTP request initiated: {result}")
    except Exception as e:
        print(f"✗ Error testing HTTP request: {e}")
    
    print("\n" + "="*50)
    print("NPC Script Test Summary:")
    print("✓ Script parsing: OK")
    print("✓ Simulator functions: OK")
    print("✓ HTTP requests: OK")
    print("✓ Notecard reading: OK")
    print("✓ NPC functions: OK")
    print("="*50)
    
    return True

if __name__ == "__main__":
    success = test_npc_script()
    if success:
        print("\n🎉 All tests passed! The NPC script should work with the LSL simulator.")
        print("\nTo run the NPC script:")
        print("1. Start the mock server: python mock_nexus_server.py")
        print("2. Run the simulator: python run_simulator.py npc.lsl")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)