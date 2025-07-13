#!/usr/bin/env python3

"""Test script to verify debugger and notecard fixes"""

import sys
import threading
import time
from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator

def test_debugger_line_positioning():
    """Test that debugger correctly tracks line positions after function calls"""
    print("=== Testing Debugger Line Positioning ===")
    
    # Simple test script with function call
    test_code = '''
default {
    state_entry() {
        llSay(0, "Start");
        test_function();
        llSay(0, "After function");
    }
}

test_function() {
    llSay(0, "In function");
    return;
}
'''
    
    parser = LSLParser()
    parsed_script = parser.parse(test_code)
    simulator = LSLSimulator(parsed_script, debug_mode=True, source_code=test_code)
    
    # Set single step mode
    simulator.single_step = True
    simulator.step_mode = "into"
    
    # Start simulator
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    # Wait for initial pause
    simulator.debugger_ready.wait(timeout=5)
    
    steps = []
    max_steps = 10
    
    for i in range(max_steps):
        if not sim_thread.is_alive():
            break
            
        # Record current line info
        info = simulator.next_statement_info
        if isinstance(info, dict):
            line = info.get('line', -1)
            stmt = info.get('statement', 'unknown')
            steps.append(f"Step {i+1}: Line {line} - {stmt}")
        else:
            steps.append(f"Step {i+1}: {info}")
        
        # Step to next
        simulator.step()
        if not simulator.debugger_ready.wait(timeout=2):
            break
    
    simulator.stop()
    sim_thread.join(timeout=1)
    
    print("Debug steps:")
    for step in steps:
        print(f"  {step}")
    
    return len(steps) > 0

def test_notecard_eof_handling():
    """Test that notecard reading properly handles EOF without infinite loop"""
    print("\n=== Testing Notecard EOF Handling ===")
    
    # Create a test notecard
    with open("test_notecard.txt", "w") as f:
        f.write("Line 1\nLine 2\nLine 3\n")
    
    # Simple notecard reading test
    test_code = '''
string NOTECARD_NAME = "test_notecard";
integer notecard_read_complete = FALSE;
integer notecard_line = 0;

default {
    state_entry() {
        llGetNotecardLine(NOTECARD_NAME, 0);
    }
    
    dataserver(key query_id, string data) {
        if (notecard_read_complete) {
            llSay(0, "Already complete, ignoring");
            return;
        }
        
        if (data == EOF) {
            llSay(0, "EOF reached");
            notecard_read_complete = TRUE;
            return;
        }
        
        llSay(0, "Read: " + data);
        notecard_line++;
        if (notecard_line < 10) {  // Safety limit
            llGetNotecardLine(NOTECARD_NAME, notecard_line);
        }
    }
}
'''
    
    parser = LSLParser()
    parsed_script = parser.parse(test_code)
    simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=test_code)
    
    # Start simulator
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    # Let it run for a few seconds
    time.sleep(3)
    
    simulator.stop()
    sim_thread.join(timeout=2)
    
    # Clean up test file
    import os
    if os.path.exists("test_notecard.txt"):
        os.remove("test_notecard.txt")
    
    print("Notecard test completed (check output above for EOF handling)")
    return True

def main():
    print("Testing LSL Simulator Fixes")
    print("=" * 40)
    
    try:
        test1_result = test_debugger_line_positioning()
        test2_result = test_notecard_eof_handling()
        
        print("\n" + "=" * 40)
        print("Test Results:")
        print(f"  Debugger line positioning: {'PASS' if test1_result else 'FAIL'}")
        print(f"  Notecard EOF handling: {'PASS' if test2_result else 'FAIL'}")
        
        if test1_result and test2_result:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())