#!/usr/bin/env python3

"""
Test script to verify that complex LSL constructs parse correctly after the fix
"""

from lsl_antlr_parser import LSLParser

def test_complex_constructs():
    print("=== Testing Complex LSL Constructs ===")
    
    # Test case with complex control structures
    complex_code = """
    default {
        state_entry() {
            if (condition) {
                llSay(0, "Hello");
                other_function();
            } else if (other_condition) {
                llSay(0, "World");
            } else {
                llSay(0, "Default");
            }
            
            for (integer i = 0; i < 10; i++) {
                llSay(0, "Count: " + (string)i);
            }
            
            while (running) {
                do_something();
            }
        }
        
        timer() {
            llSay(0, "Timer fired");
        }
    }
    
    some_function() {
        return 42;
    }
    """
    
    parser = LSLParser()
    
    print("Testing complex code with if/else, loops, etc.:")
    print()
    
    try:
        result = parser.parse(complex_code)
        print("✓ Complex code parsed successfully")
        print(f"States found: {list(result.get('states', {}).keys())}")
        print(f"Functions found: {list(result.get('functions', {}).keys())}")
        
        # Check the state_entry event
        default_state = result.get('states', {}).get('default', {})
        state_entry = default_state.get('state_entry', {})
        body = state_entry.get('body', [])
        print(f"state_entry body has {len(body)} statements")
        
        # Show statement types
        for i, stmt in enumerate(body):
            if isinstance(stmt, dict):
                print(f"  Statement {i}: {stmt.get('type', 'unknown')}")
            else:
                print(f"  Statement {i}: {stmt}")
        
    except Exception as e:
        print(f"✗ Complex code failed: {e}")
        import traceback
        traceback.print_exc()

def test_npc_sample():
    print("\n=== Testing Sample from npc.lsl ===")
    
    # Test a sample from the actual npc.lsl file
    npc_sample = """
    dataserver(key query_id, string data) {
        llSay(0, "[DEBUG] dataserver: notecard_read_complete=" + (string)notecard_read_complete + ", data='" + data + "'");
        
        if (notecard_read_complete) {
            llSay(0, "[DEBUG] dataserver: skipping - already complete");
            return;
        }
        
        if (data == EOF) {
            llSay(0, "[DEBUG] dataserver: EOF reached, setting notecard_read_complete=TRUE");
            notecard_read_complete = TRUE;
            
            if (!is_registered) {
                llSay(0, "[DEBUG] dataserver: All notecard data read, registering with nexus");
                register_with_nexus();
            }
        } else if (data != EOF) {
            llSay(0, "[DEBUG] dataserver: Read line " + (string)notecard_line + ": " + data);
            npc_profile_data += data + "\\n";
            notecard_line++;
            llGetNotecardLine(NOTECARD_NAME, notecard_line);
        }
    }
    """
    
    parser = LSLParser()
    
    print("Testing real npc.lsl event handler:")
    print()
    
    try:
        # Parse just this event as if it were in a state
        wrapped_code = f"default {{ {npc_sample} }}"
        result = parser.parse(wrapped_code)
        print("✓ NPC sample parsed successfully")
        
        # Check the dataserver event
        default_state = result.get('states', {}).get('default', {})
        dataserver = default_state.get('dataserver', {})
        body = dataserver.get('body', [])
        print(f"dataserver body has {len(body)} statements")
        
        # Show statement types
        for i, stmt in enumerate(body[:5]):  # Show first 5 statements
            if isinstance(stmt, dict):
                print(f"  Statement {i}: {stmt.get('type', 'unknown')}")
            else:
                print(f"  Statement {i}: {stmt}")
        
    except Exception as e:
        print(f"✗ NPC sample failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complex_constructs()
    test_npc_sample()