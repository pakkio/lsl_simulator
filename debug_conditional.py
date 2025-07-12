#!/usr/bin/env python3

from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator
import json

def debug_conditional_parsing():
    """Debug exactly how conditionals are parsed and executed"""
    
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
    
    print("=== Debugging Conditional Parsing ===")
    
    parser = LSLParser()
    parsed_script = parser.parse(test_code)
    
    # Get the state_entry body
    state_entry_body = parsed_script["states"]["default"]["state_entry"]["body"]
    
    print("Parsed statements:")
    for i, stmt in enumerate(state_entry_body):
        print(f"  {i}: {repr(stmt)}")
    
    print("\nRunning with debug mode...")
    simulator = LSLSimulator(parsed_script, debug_mode=True, source_code=test_code)
    
    # Override _execute_statements to add debug info
    original_execute = simulator._execute_statements
    def debug_execute_statements(statements):
        print(f"\n--- Executing {len(statements)} statements ---")
        for i, stmt in enumerate(statements):
            print(f"Statement {i}: {repr(stmt)}")
        result = original_execute(statements)
        print(f"--- Execution completed ---\n")
        return result
    
    simulator._execute_statements = debug_execute_statements
    
    import threading
    import time
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    time.sleep(3)
    simulator.stop()
    sim_thread.join(timeout=1)

if __name__ == "__main__":
    debug_conditional_parsing()