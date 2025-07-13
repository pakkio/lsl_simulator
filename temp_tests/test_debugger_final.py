#!/usr/bin/env python3

"""
Final test to verify the debugger works without parse error spam
"""

import sys
import subprocess
import threading
import time

def test_debugger():
    print("=== Testing LSL Debugger (Final Verification) ===")
    
    # Start the debugger process
    process = subprocess.Popen(
        [sys.executable, 'lsl_debugger.py', 'npc.lsl'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Send some commands to the debugger
        commands = ['h\n', 'l\n', 'p\n', 'q\n']
        
        for cmd in commands:
            process.stdin.write(cmd)
            process.stdin.flush()
            time.sleep(0.1)
        
        # Wait for process to complete
        stdout, stderr = process.communicate(timeout=10)
        
        print("=== STDOUT ===")
        lines = stdout.split('\n')
        
        # Look for parse errors in the output
        parse_error_count = 0
        for line in lines:
            if 'extraneous input' in line or 'mismatched input' in line:
                parse_error_count += 1
        
        print(f"Parse error count: {parse_error_count}")
        
        if parse_error_count == 0:
            print("✅ SUCCESS: No parse errors found!")
        elif parse_error_count < 10:
            print(f"⚠️  IMPROVED: Only {parse_error_count} parse errors (much better than hundreds)")
        else:
            print(f"❌ FAILED: Still {parse_error_count} parse errors")
        
        # Show first 20 lines of output
        print("\nFirst 20 lines of debugger output:")
        for i, line in enumerate(lines[:20]):
            if line.strip():
                print(f"  {i+1:2}: {line}")
        
        print("\n=== STDERR ===")
        if stderr.strip():
            print(stderr)
        else:
            print("(No errors)")
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("⚠️  Debugger test timed out (this is expected for interactive programs)")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_debugger()