#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lsl_simulator import LSLSimulator

# Test string concatenation with minimal parsed script
parsed_script = {
    "states": {"default": {"state_entry": {"body": []}}},
    "functions": {},
    "globals": {}
}

simulator = LSLSimulator(parsed_script)

# Test simple concatenation
test_expressions = [
    '"hello" + "world"',
    '"DEBUG: " + "test"',
    '"value=" + (string)123',
    '"[DEBUG] dataserver: notecard_read_complete=" + (string)0 + ", data=test"'
]

print("Testing string concatenation:")
for expr in test_expressions:
    try:
        result = simulator._evaluate_expression(expr)
        print(f"Expression: {expr}")
        print(f"Result: {result}")
        print(f"Type: {type(result)}")
        print("---")
    except Exception as e:
        print(f"Expression: {expr}")
        print(f"Error: {e}")
        print("---")