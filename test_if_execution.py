#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lsl_simulator import LSLSimulator
from lsl_parser import LSLParser

# Test conditional execution
lsl_code = """
default {
    state_entry() {
        integer test_flag = 0;
        
        if (test_flag) {
            llSay(0, "SHOULD NOT APPEAR - test_flag is 0");
        }
        
        if (!test_flag) {
            llSay(0, "SHOULD APPEAR - test_flag is 0");
        }
        
        if (test_flag == 0) {
            llSay(0, "SHOULD APPEAR - test_flag equals 0");
        } else {
            llSay(0, "SHOULD NOT APPEAR - else branch");
        }
    }
}
"""

print("Testing conditional execution...")

# Parse the script
parser = LSLParser()
parsed = parser.parse(lsl_code)

# Run the simulator
simulator = LSLSimulator(parsed)
simulator.run()

print("Test completed.")