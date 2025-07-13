#!/usr/bin/env python3
"""Simple test to verify basic functionality"""

import sys
sys.path.append('.')
from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator
import threading
import time

# Very simple test
test_script = '''
default {
    state_entry() {
        llSay(0, "Hello world!");
    }
}
'''

print("=== Simple test ===")
parser = LSLParser()
parsed = parser.parse(test_script)
sim = LSLSimulator(parsed)

# Run simulator in thread
sim_thread = threading.Thread(target=sim.run)
sim_thread.daemon = True
sim_thread.start()

time.sleep(2)
print("=== Test complete ===")