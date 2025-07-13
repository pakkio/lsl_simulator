#!/usr/bin/env python3

from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator
import threading
import time

def test_npc_dataserver_logic():
    """Test the exact NPC dataserver logic with else if"""
    
    test_code = '''
integer notecard_read_complete = FALSE;

default {
    state_entry() {
        string data = "EOF";
        
        // Skip processing if already complete
        if (notecard_read_complete) {
            llSay(0, "Already complete");
            return;
        }
        
        // Handle EOF - notecard reading is complete
        if (data == EOF) {
            llSay(0, "EOF reached");
            notecard_read_complete = TRUE;
        }
        else if (data != EOF) {
            llSay(0, "Not EOF");
        }
        
        llSay(0, "Done");
    }
}
'''
    
    print("=== Testing NPC Dataserver Logic ===")
    print("Expected: 'EOF reached' then 'Done' (NOT 'Not EOF')")
    
    parser = LSLParser()
    parsed_script = parser.parse(test_code)
    simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=test_code)
    
    # Start simulator
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    # Let it run
    time.sleep(2)
    
    simulator.stop()
    sim_thread.join(timeout=1)
    
    print("=== Test completed ===")

if __name__ == "__main__":
    test_npc_dataserver_logic()