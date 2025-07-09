#!/usr/bin/env python3
"""
Simple LSL Debugger - Minimal Threading
Addresses criticism: Complex threading for simple debugging needs.
"""

import time
from typing import Set, Dict, Any, Optional


class SimpleDebugger:
    """
    Simple debugger that avoids complex threading synchronization.
    Uses polling-based approach instead of threading.Event() complexity.
    """
    
    def __init__(self, source_lines: list = None):
        self.source_lines = source_lines or []
        self.breakpoints: Set[int] = set()
        self.paused = False
        self.single_step = False
        self.current_line = -1
        self.debug_commands = []  # Simple command queue
    
    def add_breakpoint(self, line: int):
        """Add a breakpoint at the specified line."""
        self.breakpoints.add(line)
    
    def remove_breakpoint(self, line: int):
        """Remove a breakpoint."""
        self.breakpoints.discard(line)
    
    def should_pause(self, line: int) -> bool:
        """Check if execution should pause at this line."""
        self.current_line = line
        
        # Check for breakpoints
        if line in self.breakpoints:
            self.breakpoints.discard(line)  # Remove breakpoint after hitting
            return True
        
        # Check for single step
        if self.single_step:
            self.single_step = False
            return True
        
        return False
    
    def pause_execution(self, line: int, statement: Dict[str, Any]):
        """Pause execution - simple polling approach."""
        self.paused = True
        print(f"[DEBUG] Paused at line {line}")
        
        if line < len(self.source_lines):
            print(f"[DEBUG] Code: {self.source_lines[line].strip()}")
        
        # Simple polling loop - no complex threading
        while self.paused:
            # Check for debug commands
            if self.debug_commands:
                command = self.debug_commands.pop(0)
                self._process_debug_command(command)
            
            time.sleep(0.1)  # Simple polling
    
    def _process_debug_command(self, command: str):
        """Process debug commands."""
        if command == "continue":
            self.paused = False
        elif command == "step":
            self.single_step = True
            self.paused = False
        elif command == "stop":
            self.paused = False
            # Signal to stop execution (handled by simulator)
    
    def continue_execution(self):
        """Continue execution."""
        self.debug_commands.append("continue")
    
    def step_execution(self):
        """Step to next statement."""
        self.debug_commands.append("step")
    
    def step(self):
        """Step to next statement (alias for step_execution)."""
        self.step_execution()
    
    def stop_execution(self):
        """Stop execution."""
        self.debug_commands.append("stop")
    
    def stop(self):
        """Stop execution (alias for stop_execution)."""
        self.stop_execution()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current debug status."""
        return {
            "paused": self.paused,
            "current_line": self.current_line,
            "breakpoints": list(self.breakpoints),
            "single_step": self.single_step
        }