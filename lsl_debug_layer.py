#!/usr/bin/env python3
"""
LSL Debug Layer
Provides debugging capabilities on top of the core engine
"""

import threading
import time
from typing import Any, Dict, List, Optional, Set
from experimental.lsl_core_engine import LSLCoreEngine

class LSLDebugLayer:
    """Debug wrapper around LSL core engine"""
    
    def __init__(self, script_source: str, debug_mode: bool = False, breakpoints: Optional[Set[int]] = None):
        self.core = LSLCoreEngine(script_source)
        self.debug_mode = debug_mode
        self.source_lines = script_source.split('\n')
        self.breakpoints = breakpoints or set()
        
        # Debug state
        self.execution_paused = threading.Event()
        self.debugger_ready = threading.Event()
        self.single_step = False
        self.current_line = 0
        self.next_statement_info = {}
        
        # Set initial state
        if not debug_mode:
            self.execution_paused.set()  # Always running if not in debug mode
    
    def set_breakpoint(self, line_number: int):
        """Set a breakpoint at the specified line"""
        self.breakpoints.add(line_number)
    
    def remove_breakpoint(self, line_number: int):
        """Remove a breakpoint from the specified line"""
        self.breakpoints.discard(line_number)
    
    def step_into(self):
        """Step into the next statement"""
        self.single_step = True
        self.execution_paused.set()
    
    def step_over(self):
        """Step over the next statement"""
        self.single_step = True
        self.execution_paused.set()
    
    def continue_execution(self):
        """Continue execution until next breakpoint"""
        self.single_step = False
        self.execution_paused.set()
    
    def pause_execution(self):
        """Pause execution"""
        self.execution_paused.clear()
    
    def get_call_stack(self) -> List[Dict[str, Any]]:
        """Get the current call stack"""
        stack_info = []
        for i, frame in enumerate(self.core.call_stack.frames):
            stack_info.append({
                'frame_id': i,
                'function': 'user_function',  # Would need to track function names
                'line': self.current_line,
                'locals': dict(frame.locals)
            })
        return stack_info
    
    def get_variables(self) -> Dict[str, Any]:
        """Get current variables (global and local)"""
        variables = {}
        
        # Global variables
        variables.update(self.core.global_scope.locals)
        
        # Local variables from current frame
        current_frame = self.core.call_stack.get_current_scope()
        if current_frame != self.core.global_scope:
            local_vars = {f"local_{k}": v for k, v in current_frame.locals.items()}
            variables.update(local_vars)
        
        return variables
    
    def evaluate_expression(self, expression: str) -> Any:
        """Evaluate an expression in the current context"""
        try:
            # Parse and evaluate the expression
            ast_expr = self.core.parser._parse_expression(expression)
            return self.core.evaluator.evaluate(ast_expr)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_source_line(self, line_number: int) -> str:
        """Get source code line"""
        if 0 <= line_number < len(self.source_lines):
            return self.source_lines[line_number]
        return ""
    
    def get_execution_info(self) -> Dict[str, Any]:
        """Get current execution information"""
        return {
            'current_line': self.current_line,
            'is_paused': not self.execution_paused.is_set(),
            'breakpoints': list(self.breakpoints),
            'single_step': self.single_step,
            'call_stack_depth': len(self.core.call_stack.frames),
            'current_state': self.core.current_state
        }
    
    def _check_breakpoint(self, line_number: int):
        """Check if we should break at this line"""
        if not self.debug_mode:
            return
        
        self.current_line = line_number
        
        # Check for breakpoint or single step
        if line_number in self.breakpoints or self.single_step:
            self.single_step = False
            self.execution_paused.clear()
            self.debugger_ready.set()
            
            # Wait for debugger to continue
            self.execution_paused.wait()
    
    def _execute_with_debug(self, func, *args, **kwargs):
        """Execute a function with debug checks"""
        if self.debug_mode:
            # Check for breakpoints before execution
            self._check_breakpoint(self.current_line)
        
        return func(*args, **kwargs)
    
    # Proxy methods to core engine
    
    def trigger_event(self, event_name: str, *args):
        """Trigger an event with debug support"""
        return self._execute_with_debug(self.core.trigger_event, event_name, *args)
    
    def call_function(self, name: str, args: List[Any]) -> Any:
        """Call function with debug support"""
        return self._execute_with_debug(self.core.call_function, name, args)
    
    def is_running(self) -> bool:
        """Check if engine is running"""
        return self.core.is_running()
    
    def stop(self):
        """Stop the engine"""
        self.core.stop()
        self.execution_paused.set()  # Release any waiting debugger
    
    def get_global_scope(self):
        """Get global scope"""
        return self.core.global_scope
    
    def get_call_stack_obj(self):
        """Get call stack object"""
        return self.core.call_stack
    
    def get_current_state(self) -> str:
        """Get current state"""
        return self.core.current_state
    
    def set_current_state(self, state: str):
        """Set current state"""
        self.core.current_state = state
    
    def get_ast(self):
        """Get the AST"""
        return self.core.ast