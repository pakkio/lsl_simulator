#!/usr/bin/env python3
"""
Simple runner for the NPC script
"""

import sys
import os
import time
import threading

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator

def run_npc_script():
    """Run the NPC script"""
    print("Starting NPC script simulation...")
    
    # Read the NPC script
    try:
        with open('npc.lsl', 'r') as f:
            npc_script = f.read()
        print("✓ NPC script loaded")
    except Exception as e:
        print(f"✗ Error loading NPC script: {e}")
        return False
    
    # Parse the script
    try:
        parser = LSLParser()
        parsed_script = parser.parse(npc_script)
        print("✓ NPC script parsed")
    except Exception as e:
        print(f"✗ Error parsing NPC script: {e}")
        return False
    
    # Create and run simulator
    try:
        print("✓ Starting LSL simulator...")
        simulator = LSLSimulator(parsed_script, debug_mode=False, source_code=npc_script)
        
        # Run the simulation in a separate thread
        def run_simulation():
            try:
                simulator.run()
            except Exception as e:
                print(f"Simulator error: {e}")
        
        sim_thread = threading.Thread(target=run_simulation)
        sim_thread.daemon = True
        sim_thread.start()
        
        print("✓ NPC simulation started")
        print("✓ Mock NPC will run state_entry event")
        print("\nPress Ctrl+C to stop the simulation")
        
        # Keep the main thread alive
        try:
            while sim_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✓ Simulation stopped by user")
            simulator.stop()
        
        return True
        
    except Exception as e:
        print(f"✗ Error running simulator: {e}")
        return False

if __name__ == "__main__":
    success = run_npc_script()
    if not success:
        sys.exit(1)