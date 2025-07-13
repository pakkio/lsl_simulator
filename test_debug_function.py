#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lsl_simulator import LSLSimulator
from lsl_antlr_parser import LSLParser

# Parse and create simulator
with open("npc.lsl", "r") as f:
    source_code = f.read()

parser = LSLParser()
parsed_script = parser.parse_script(source_code)
simulator = LSLSimulator(parsed_script, debug_mode=True, source_code=source_code)

# Check what functions are parsed
print("User functions:", list(simulator.user_functions.keys()))
if 'setup_corona_visual' in simulator.user_functions:
    func_def = simulator.user_functions['setup_corona_visual']
    print(f"setup_corona_visual function definition: {func_def}")
    print(f"Body: {func_def['body']}")
    print(f"Body length: {len(func_def['body'])}")
    for i, stmt in enumerate(func_def['body']):
        print(f"  Statement {i}: {stmt}")