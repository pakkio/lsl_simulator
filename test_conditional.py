#!/usr/bin/env python3

from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator
import json

def test_conditional_logic():
    """Test if/else if logic specifically"""
    
    test_code = '''
default {
    state_entry() {
        string data = "EOF";
        
        if (data == EOF) {
            llSay(0, "Matched EOF");
        }
        else if (data != EOF) {
            llSay(0, "Not EOF");
        }
        
        llSay(0, "Done");
    }
}
'''
    
    print("=== Testing Conditional Logic ===")
    print("Test code:")
    print(test_code)
    print("\nParsing...")
    
    parser = LSLParser()
    parsed_script = parser.parse(test_code)
    
    print("Parsed structure:")
    print(json.dumps(parsed_script, indent=2, default=str))
    
    print("\nRunning simulator...")
    simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=test_code)
    
    import threading
    import time
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    time.sleep(2)
    simulator.stop()
    sim_thread.join(timeout=1)
    
    print("=== Test completed ===")

if __name__ == "__main__":
    test_conditional_logic()