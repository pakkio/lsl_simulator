#!/usr/bin/env python3
"""Test complex expressions with function calls"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsl_parser import LSLParser
from lsl_simulator import LSLSimulator

def test_complex_expressions():
    """Test complex expressions with nested function calls"""
    
    test_script = '''
default {
    state_entry() {
        // Test nested function calls
        llSay(0, "Length: " + (string)llStringLength("Hello World"));
        
        // Test function call in list
        list my_list = [llStringLength("test"), "value"];
        llSay(0, "List: " + llDumpList2String(my_list, ","));
        
        // Test function call as parameter to another function call
        llSay(llStringLength("test"), "This channel number is the length of 'test'");
        
        // Test complex expression
        integer total = llStringLength("Hello") + llStringLength("World");
        llSay(0, "Total length: " + (string)total);
    }
}
'''
    
    parser = LSLParser()
    parsed = parser.parse(test_script)
    simulator = LSLSimulator(parsed, debug_mode=False, source_code=test_script)
    
    print("=== Testing Complex Expressions ===")
    simulator.trigger_event('state_entry')

if __name__ == "__main__":
    test_complex_expressions()