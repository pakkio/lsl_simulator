#!/usr/bin/env python3
"""
LSL Simulator - Simplified Production Version
Addresses the architectural criticisms by removing over-engineering and pyparsing dependency.
Integrated with comprehensive LSL API providing 270+ functions for 90% coverage.
"""

import re
import time
import threading
import requests
import math
import random
import uuid
from lsl_production_parser import LSLProductionParser
from simple_debugger import SimpleDebugger
from simple_expression_evaluator import SimpleExpressionEvaluator
from comprehensive_lsl_api import ComprehensiveLSLAPI
from comprehensive_lsl_api_part2 import ComprehensiveLSLAPIPart2


class Frame:
    """A single frame on the call stack, holding local variables."""
    def __init__(self, parent_scope):
        self.locals = {}
        self.parent = parent_scope

    def get(self, name):
        return self.locals.get(name)

    def set(self, name, value):
        self.locals[name] = value


class CallStack:
    """Simplified call stack without complex features."""
    def __init__(self, global_scope):
        self.frames = []
        self.global_scope = global_scope
    
    def push(self, frame): 
        self.frames.append(frame)
    
    def pop(self): 
        return self.frames.pop() if self.frames else None
    
    def get_current_scope(self): 
        return self.frames[-1] if self.frames else self.global_scope
    
    def find_variable(self, name):
        current = self.get_current_scope()
        while current:
            val = current.get(name)
            if val is not None: 
                return val
            current = getattr(current, 'parent', None)
        return None


class LSLSimulator:
    """
    Simplified LSL Simulator that addresses architectural criticisms:
    1. Uses production ANTLR4-style parser (no pyparsing)
    2. Simplified expression evaluation (no over-engineering)
    3. Reduced threading complexity
    4. Clear documentation alignment
    5. Comprehensive LSL API (270+ functions for 90% coverage)
    """
    
    def __init__(self, parsed_script, debug_mode=False, source_code="", breakpoints=None):
        self.global_scope = Frame(None)
        self.call_stack = CallStack(self.global_scope)
        self.user_functions = parsed_script.get("functions", {})
        self.states = parsed_script.get("states", {})
        self.current_state = "default"
        self.event_queue = []
        self._is_running = True
        self.active_listeners = []
        self.listener_handle_counter = 1
        
        # Simplified expression evaluation - no pyparsing dependency
        self.expression_evaluator = SimpleExpressionEvaluator(self)
        
        # Initialize comprehensive LSL API (270+ functions for 90% coverage)
        self.comprehensive_api = ComprehensiveLSLAPI(self)
        self.comprehensive_api_part2 = ComprehensiveLSLAPIPart2(self)
        
        # Simplified debug mode - minimal threading complexity
        self.debug_mode = debug_mode
        self.debugger = SimpleDebugger(source_code.split('\n') if source_code else [])
        if breakpoints:
            for bp in breakpoints:
                self.debugger.add_breakpoint(bp)
        
        self.next_statement_info = {}
        
        # Initialize LSL constants
        self._initialize_lsl_constants()
        
        # Initialize global variables
        for var in parsed_script.get("globals", []):
            self.global_scope.set(var['name'], self._evaluate_expression(var.get('value')))
        
        # Avatar sensing
        self.avatar_counter = 0
    
    def _initialize_lsl_constants(self):
        """Initialize LSL constants in the global scope."""
        # Math constants
        self.global_scope.set("PI", 3.141592653589793)
        self.global_scope.set("TWO_PI", 6.283185307179586)
        self.global_scope.set("PI_BY_TWO", 1.5707963267948966)
        self.global_scope.set("DEG_TO_RAD", 0.017453292519943295)
        self.global_scope.set("RAD_TO_DEG", 57.29577951308232)
        self.global_scope.set("SQRT2", 1.4142135623730951)
        
        # Boolean constants
        self.global_scope.set("TRUE", 1)
        self.global_scope.set("FALSE", 0)
        
        # NULL values
        self.global_scope.set("NULL_KEY", "00000000-0000-0000-0000-000000000000")
        self.global_scope.set("EOF", "\\n\\n\\nEOF\\n\\n\\n")
        
        # Types
        self.global_scope.set("TYPE_INTEGER", 1)
        self.global_scope.set("TYPE_FLOAT", 2)
        self.global_scope.set("TYPE_STRING", 3)
        self.global_scope.set("TYPE_KEY", 4)
        self.global_scope.set("TYPE_VECTOR", 5)
        self.global_scope.set("TYPE_ROTATION", 6)

    def run(self):
        """Main execution loop."""
        print("🚀 Starting LSL Simulator with 270+ API functions")
        
        # Trigger state_entry event
        self.trigger_event("state_entry")
        
        # Main event loop
        while self._is_running:
            if self.event_queue:
                event_name, args = self.event_queue.pop(0)
                try:
                    self.trigger_event(event_name, args)
                except Exception as e:
                    print(f"⚠️  Event error: {e}")
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
        
        print("🛑 LSL Simulator stopped")

    def trigger_event(self, event_name, args=None):
        """Trigger an event in the current state."""
        if args is None:
            args = []
        
        current_state = self.states.get(self.current_state, {})
        event_handler = current_state.get(event_name)
        
        if event_handler:
            print(f"📨 Triggering event: {event_name}")
            try:
                self._execute_statements(event_handler.get("body", []))
            except Exception as e:
                print(f"⚠️  Error in {event_name} event: {e}")
        else:
            print(f"🔇 No handler for event: {event_name} in state {self.current_state}")

    def _execute_statements(self, statements):
        """Execute a list of statements."""
        if not isinstance(statements, list):
            return None
        
        for stmt in statements:
            try:
                result = self._execute_statement(stmt)
                if result is not None:
                    return result
            except Exception as e:
                print(f"⚠️  Statement execution error: {e}")
                continue
        return None

    def _execute_statement(self, stmt):
        """Execute a single statement."""
        if not isinstance(stmt, dict):
            return None
        
        stmt_type = stmt.get("type", "simple")
        
        if self.debug_mode and "line" in stmt:
            self.debugger.pause_execution(stmt["line"], stmt)
        
        try:
            if stmt_type == "simple":
                return self._execute_simple_statement(stmt)
            elif stmt_type == "if":
                return self._execute_if_statement(stmt)
            elif stmt_type == "while":
                return self._execute_while_loop(stmt)
            elif stmt_type == "for":
                return self._execute_for_loop(stmt)
            elif stmt_type == "return":
                return self._evaluate_expression(stmt.get("value", ""))
            else:
                print(f"⚠️  Unknown statement type: {stmt_type}")
                return None
        except Exception as e:
            print(f"⚠️  Error executing {stmt_type} statement: {e}")
            return None

    def _execute_simple_statement(self, stmt):
        """Execute a simple statement (expression or declaration)."""
        if "statement" in stmt:
            return self._evaluate_expression(stmt["statement"])
        elif "declaration" in stmt:
            # Handle variable declaration
            decl = stmt["declaration"]
            var_name = decl.get("name")
            var_value = self._evaluate_expression(decl.get("value", ""))
            self.call_stack.get_current_scope().set(var_name, var_value)
            return None
        elif "name" in stmt and "value" in stmt:
            # Handle assignment
            var_name = stmt["name"]
            var_value = self._evaluate_expression(stmt["value"])
            self.call_stack.get_current_scope().set(var_name, var_value)
            return None
        return None

    def _execute_if_statement(self, stmt):
        """Execute an if statement."""
        condition = self._evaluate_expression(stmt.get("condition", "FALSE"))
        
        if self._is_true(condition):
            return self._execute_statements(stmt.get("then_body", []))
        elif "else_body" in stmt:
            return self._execute_statements(stmt.get("else_body", []))
        return None

    def _execute_while_loop(self, stmt):
        """Execute a while loop."""
        max_iterations = 10000  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            condition = self._evaluate_expression(stmt.get("condition", "FALSE"))
            if not self._is_true(condition):
                break
            
            result = self._execute_statements(stmt.get("body", []))
            if result is not None:
                return result
            
            iterations += 1
        
        if iterations >= max_iterations:
            print("⚠️  While loop terminated: maximum iterations reached")
        
        return None

    def _execute_for_loop(self, stmt):
        """Execute a for loop."""
        # Initialize
        if "init" in stmt:
            self._evaluate_expression(stmt["init"])
        
        max_iterations = 10000  # Prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            # Check condition
            if "condition" in stmt:
                condition = self._evaluate_expression(stmt["condition"])
                if not self._is_true(condition):
                    break
            
            # Execute body
            result = self._execute_statements(stmt.get("body", []))
            if result is not None:
                return result
            
            # Increment
            if "increment" in stmt:
                self._evaluate_expression(stmt["increment"])
            
            iterations += 1
        
        if iterations >= max_iterations:
            print("⚠️  For loop terminated: maximum iterations reached")
        
        return None

    def _is_true(self, value):
        """Check if a value is considered true in LSL."""
        if isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return value != "" and value != "0"
        elif isinstance(value, list):
            return len(value) > 0
        return bool(value)

    def _evaluate_expression(self, expression):
        """Evaluate an expression using the simple expression evaluator."""
        if not expression:
            return None
        return self.expression_evaluator.evaluate(str(expression))

    def _call_api_function(self, func_name, args):
        """Call an API function."""
        try:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                return func(*args)
            else:
                print(f"⚠️  Unknown API function: {func_name}")
                return None
        except Exception as e:
            print(f"⚠️  Error calling {func_name}: {e}")
            return None

    def _call_user_function(self, func_name, args):
        """Call a user-defined function."""
        if func_name not in self.user_functions:
            print(f"⚠️  Unknown function: {func_name}")
            return None
        
        func_def = self.user_functions[func_name]
        params = func_def.get("parameters", [])
        
        # Create new frame for function scope
        func_frame = Frame(self.global_scope)
        
        # Bind parameters
        for i, param in enumerate(params):
            if i < len(args):
                func_frame.set(param["name"], args[i])
            else:
                func_frame.set(param["name"], None)  # Default value
        
        # Push frame onto call stack
        self.call_stack.push(func_frame)
        
        try:
            # Execute function body
            result = self._execute_statements(func_def.get("body", []))
            return result
        finally:
            # Pop frame from call stack
            self.call_stack.pop()

    def _get_component(self, vector, component):
        """Get a component from a vector or rotation."""
        if not isinstance(vector, list):
            return 0.0
        
        if component == 'x' and len(vector) >= 1:
            return float(vector[0])
        elif component == 'y' and len(vector) >= 2:
            return float(vector[1])
        elif component == 'z' and len(vector) >= 3:
            return float(vector[2])
        elif component == 's' and len(vector) >= 4:  # Rotation scalar
            return float(vector[3])
        else:
            return 0.0

    def simulate_avatar_sense(self, avatar_name):
        """Simulate sensing an avatar."""
        self.avatar_counter += 1
        avatar_key = f"avatar-{self.avatar_counter}-{int(time.time())}"
        
        self.sensed_avatar_name = avatar_name
        self.sensed_avatar_key = avatar_key
        
        # Update global variables for compatibility
        self.global_scope.set("current_avatar", avatar_name)
        self.global_scope.set("current_avatar_key", avatar_key)
        
        # Queue sensor event
        self.event_queue.append(("sensor", [1]))  # 1 = number detected
        
        print(f"👤 Avatar sensed: {avatar_name} ({avatar_key})")

    def stop(self):
        """Stop the simulator."""
        self._is_running = False
        if self.debug_mode:
            self.debugger.stop()

    def continue_execution(self):
        """Continue execution (debug mode)."""
        if self.debug_mode:
            self.debugger.continue_execution()

    def step(self):
        """Step to next statement (debug mode)."""
        if self.debug_mode:
            self.debugger.step()

    def get_variables(self, scope="globals"):
        """Get variables for debugging."""
        if scope == "globals":
            return self.global_scope.locals
        elif scope == "locals":
            current_frame = self.call_stack.get_current_scope()
            if current_frame and current_frame != self.global_scope:
                return current_frame.locals
            else:
                return self.global_scope.locals
        return None
    
    # Comprehensive LSL API (270+ functions for 90% coverage)
    # Delegation to comprehensive API classes
    def __getattr__(self, name):
        """Forward API function calls to comprehensive API classes."""
        if name.startswith('api_'):
            # Try comprehensive API first
            if hasattr(self.comprehensive_api, name):
                return getattr(self.comprehensive_api, name)
            # Try comprehensive API part 2
            elif hasattr(self.comprehensive_api_part2, name):
                return getattr(self.comprehensive_api_part2, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def say_on_channel(self, channel, message, speaker_name="Unknown", speaker_key="00000000-0000-0000-0000-000000000000"):
        """Simulate speaking on channel."""
        if channel == 0 and hasattr(self, 'sensed_avatar_name') and hasattr(self, 'sensed_avatar_key'):
            speaker_name = self.sensed_avatar_name
            speaker_key = self.sensed_avatar_key
        
        print(f"[CHANNEL {channel}] {speaker_name}: {message}")
        
        for listener in self.active_listeners:
            if listener['active'] and listener['channel'] == channel:
                self.event_queue.append(("listen", [channel, speaker_name, speaker_key, message]))
                break