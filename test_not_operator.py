#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lsl_simulator import LSLSimulator

# Test logical NOT operator
parsed_script = {
    "states": {"default": {"state_entry": {"body": []}}},
    "functions": {},
    "globals": {}
}

simulator = LSLSimulator(parsed_script)

# Set a test variable
simulator.global_scope.set("notecard_read_complete", 1)

# Test logical NOT expressions
test_expressions = [
    '!notecard_read_complete',
    '!(notecard_read_complete)',
    '!1',
    '!0',
    '!TRUE',
    '!FALSE'
]

print("Testing logical NOT operator:")
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