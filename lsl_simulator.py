import re
import time as time_module
import threading
import requests
import math
import random
import uuid
from queue import Queue
from simple_expression_evaluator import SimpleExpressionEvaluator
from lsl_statement_executor import StatementExecutor
from lsl_api_expanded import LSLAPIExpanded

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
    def __init__(self, global_scope):
        self.frames = []
        self.global_scope = global_scope
    def push(self, frame): self.frames.append(frame)
    def pop(self): return self.frames.pop() if self.frames else None
    def get_current_scope(self): return self.frames[-1] if self.frames else self.global_scope
    def find_variable(self, name):
        current = self.get_current_scope()
        while current:
            val = current.get(name)
            if val is not None: return val
            current = getattr(current, 'parent', None)
        return None

class LSLSimulator:
    def __init__(self, parsed_script, debug_mode=False, source_code="", breakpoints=None):
        self.global_scope = Frame(None)
        self.call_stack = CallStack(self.global_scope)
        self.user_functions = parsed_script.get("functions", {})
        self.states = parsed_script.get("states", {})
        self.current_state = "default"
        # Thread-safe event queue and synchronization
        self.event_queue = Queue()
        self.event_queue_lock = threading.Lock()
        self._is_running = True
        
        # Thread-safe shared state
        self.active_listeners = []  # List of listener dictionaries
        self.listeners_lock = threading.Lock()
        self.listener_handle_counter = 1  # Counter for generating unique handles
        self.counter_lock = threading.Lock()
        # Initialize simple expression evaluator (replaces pyparsing)
        self.expression_evaluator = SimpleExpressionEvaluator(self)
        self.debug_mode = debug_mode
        self.source_lines = source_code.split('\n')
        self.breakpoints = breakpoints if breakpoints is not None else set()
        self.execution_paused = threading.Event()
        self.debugger_ready = threading.Event()
        self.next_statement_info = {}
        self.single_step = False
        self.step_mode = "over"  # "over" or "into"
        self.call_depth = 0  # Track function call depth for step over
        self.avatar_counter = 0  # Counter for sequential avatar keys (protected by counter_lock)
        
        # Sensor detection data for llDetectedKey/llDetectedDist functions
        self.detected_avatars = []  # List of detected avatar data: [{"key": "...", "name": "...", "distance": 2.5}, ...]
        
        # Initialize statement executor
        self.statement_executor = StatementExecutor()
        
        # Initialize comprehensive LSL API (single source of truth)
        self.lsl_api = LSLAPIExpanded()
        
        # Initialize LSL constants in global scope
        self._initialize_lsl_constants()
        
        for var in parsed_script.get("globals", []):
            self.global_scope.set(var['name'], self._evaluate_expression(var.get('value')))

    def _initialize_lsl_constants(self):
        """Initialize LSL constants in the global scope"""
        # Basic constants
        self.global_scope.set("PI", 3.141592653589793)
        self.global_scope.set("PI_BY_TWO", 3.141592653589793 / 2)
        self.global_scope.set("TRUE", 1)
        self.global_scope.set("FALSE", 0)
        self.global_scope.set("NULL_KEY", "00000000-0000-0000-0000-000000000000")
        self.global_scope.set("ZERO_VECTOR", [0.0, 0.0, 0.0])
        
        # Object constants
        self.global_scope.set("AGENT", 1)
        self.global_scope.set("ALL_SIDES", -1)
        self.global_scope.set("OBJECT_POS", 1)
        
        # Inventory constants
        self.global_scope.set("INVENTORY_NOTECARD", 7)
        
        # HTTP constants
        self.global_scope.set("HTTP_METHOD", "method")
        self.global_scope.set("HTTP_MIMETYPE", "mimetype")
        self.global_scope.set("HTTP_CUSTOM_HEADER", "header")
        
        # JSON constants
        self.global_scope.set("JSON_OBJECT", "object")
        self.global_scope.set("JSON_ARRAY", "array")
        self.global_scope.set("JSON_INVALID", "invalid")
        
        # Changed constants
        self.global_scope.set("CHANGED_REGION_RESTART", 1024)
        self.global_scope.set("CHANGED_OWNER", 128)
        
        # String constants
        self.global_scope.set("STRING_TRIM", 0)
        self.global_scope.set("EOF", "EOF")


    def _evaluate_expression(self, expr_str):
        """
        Evaluate an expression using the simple ANTLR4-based evaluator.
        """
        if not expr_str:
            return None
        
        return self.expression_evaluator.evaluate(expr_str)

    def _execute_statements(self, statements):
        i = 0
        while i < len(statements):
            if not self._is_running:
                break

            stmt = statements[i]
            
            # Skip empty statements or comments for debugging purposes
            should_debug = True
            if self.debug_mode:
                stmt_type = stmt.get("type") if isinstance(stmt, dict) else None
                if stmt_type == "simple":
                    statement_text = stmt.get("statement", "")
                    # Skip empty statements or comments
                    if not statement_text or statement_text.strip().startswith("//"):
                        should_debug = False

            # Always ensure next_statement_info is a dictionary with line information
            if isinstance(stmt, dict):
                self.next_statement_info = stmt
                line_num = stmt.get("line", -1)
            else:
                # For string statements, try to find the line number
                stmt_line = self._find_statement_line(stmt) if isinstance(stmt, str) else -1
                self.next_statement_info = {
                    "type": "simple",
                    "statement": str(stmt),
                    "line": stmt_line
                }
                line_num = stmt_line

            if not self._is_running:
                break

            # Execute the statement first
            return_value = None
            if isinstance(stmt, dict):
                stmt_type = stmt.get("type")
                if stmt_type == "simple" or stmt_type == "declaration":
                    return_value = self._execute_simple_statement(stmt)
                elif stmt_type == "expression_statement":
                    # Handle expression statements by executing the expression
                    expression = stmt.get("expression", "")
                    if expression:
                        return_value = self._execute_simple_statement({"type": "simple", "statement": expression})
                elif stmt_type == "assignment":
                    return_value = self._execute_assignment_statement(stmt)
                elif stmt_type == "if":
                    return_value = self._execute_if_statement(stmt)
                elif stmt_type == "while":
                    return_value = self._execute_while_loop(stmt)
                elif stmt_type == "for":
                    return_value = self._execute_for_loop(stmt)
                elif stmt_type == "return":
                    return self._evaluate_expression(stmt.get("value"))
            elif isinstance(stmt, str):
                # Handle raw string statements with proper if/else logic
                stmt_str = stmt.strip()
                if stmt_str and not stmt_str.startswith("//"):
                    # Handle return statements
                    if stmt_str == "return" or stmt_str == "return;":
                        return None  # Early return from function
                    
                    # Handle structured if statements (parsed by ANTLR)
                    if isinstance(stmt, dict) and stmt.get('type') == 'if_statement':
                        return_value = self._execute_if_statement(stmt)
                        if return_value is not None:
                            return return_value
                        i += 1
                        continue
                    
                    # Handle structured statements
                    return_value = self._execute_simple_statement({"type": "simple", "statement": stmt_str})
            
            # Then check for debug pause AFTER execution
            if self.debug_mode and should_debug and (line_num in self.breakpoints or self.single_step):
                # Don't remove breakpoints when hit - keep them active
                
                # Check if we should pause based on step mode and call depth
                should_pause = True
                if self.single_step and self.step_mode == "over":
                    # For step over, only pause if we're at the same or higher call depth
                    current_depth = len(self.call_stack.frames)
                    if current_depth > self.call_depth:
                        should_pause = False
                
                if should_pause:
                    self.single_step = False
                    # Signal that we're paused and wait for debugger to tell us to continue
                    self.debugger_ready.set()
                    self.execution_paused.wait()
                    self.execution_paused.clear()
            
            # Check for early return
            if return_value is not None:
                return return_value
                
            i += 1
        return None

    def _find_statement_line(self, stmt_str):
        """Find the line number for a string statement by searching source code"""
        if not stmt_str or not self.source_lines:
            return -1
        
        # Clean the statement for searching
        search_str = stmt_str.strip()
        if search_str.endswith(';'):
            search_str = search_str[:-1]
        
        # Search for the statement in source lines
        for i, line in enumerate(self.source_lines):
            line_clean = line.strip()
            if line_clean and not line_clean.startswith('//'):
                # Remove semicolon for comparison
                if line_clean.endswith(';'):
                    line_clean = line_clean[:-1]
                
                # Check for exact match or if statement is contained in line
                if search_str in line_clean or line_clean in search_str:
                    # For function calls, be more specific
                    if '(' in search_str and '(' in line_clean:
                        func_name = search_str.split('(')[0].strip()
                        if func_name in line_clean:
                            return i + 1
                    elif search_str == line_clean:
                        return i + 1
        
        return -1

    def _execute_simple_statement(self, stmt):
        """
        Execute a simple statement using the new modular command system.
        This replaces the monolithic 141-line implementation with a clean, extensible architecture.
        """
        return self.statement_executor.execute(stmt, self)

    def _get_component(self, value, component):
        if not isinstance(value, list):
            return 0.0
        if component == 'x':
            return value[0]
        if component == 'y':
            return value[1]
        if component == 'z':
            return value[2]
        if component == 's' and len(value) == 4:
            return value[3]
        return 0.0


    def _find_variable_scope(self, var_name):
        """Find which scope contains a variable, returning the scope or None"""
        current = self.call_stack.get_current_scope()
        while current:
            if hasattr(current, 'locals') and var_name in current.locals:
                return current
            current = getattr(current, 'parent', None)
        return None

    def _execute_assignment_statement(self, stmt):
        """Execute assignment statement with operators like =, +=, -=, etc."""
        lvalue = stmt["lvalue"]
        operator = stmt["operator"]
        expression_text = stmt["expression"]
        
        # Evaluate the right-hand side expression
        new_value = self._evaluate_expression(expression_text)
        
        # Find the correct scope for assignment - prefer existing variable locations
        target_scope = self._find_variable_scope(lvalue)
        if target_scope is None:
            # Variable doesn't exist, create it in current scope
            target_scope = self.call_stack.get_current_scope()
        
        if operator == "=":
            # Simple assignment
            target_scope.set(lvalue, new_value)
        elif operator == "+=":
            # Addition assignment
            if lvalue in target_scope.locals:
                current_value = target_scope.get(lvalue)
            else:
                current_value = ""
            
            if isinstance(current_value, str) and isinstance(new_value, str):
                # String concatenation
                result = current_value + new_value
            else:
                # Numeric addition
                current_num = float(current_value) if current_value else 0.0
                new_num = float(new_value) if new_value else 0.0
                result = current_num + new_num
            target_scope.set(lvalue, result)
        elif operator == "-=":
            current_value = target_scope.get(lvalue) or 0
            result = float(current_value) - float(new_value)
            target_scope.set(lvalue, result)
        elif operator == "*=":
            current_value = target_scope.get(lvalue) or 0
            result = float(current_value) * float(new_value)
            target_scope.set(lvalue, result)
        elif operator == "/=":
            current_value = target_scope.get(lvalue) or 0
            result = float(current_value) / float(new_value) if new_value != 0 else 0
            target_scope.set(lvalue, result)
        elif operator == "%=":
            current_value = target_scope.get(lvalue) or 0
            result = float(current_value) % float(new_value) if new_value != 0 else 0
            target_scope.set(lvalue, result)
        
        return None

    def _execute_while_loop(self, while_node):
        while self._evaluate_expression(while_node["condition"]):
            result = self._execute_statements(while_node["body"])
            if result is not None:
                return result
        return None

    def _execute_for_loop(self, for_node):
        # Execute initialization
        if for_node.get("init"):
            init_stmt = for_node["init"]
            
            # Handle ANTLR4 structured format (dict) vs old string format
            if isinstance(init_stmt, dict):
                # New ANTLR4 format: {"type": "assignment", "lvalue": "i", "operator": "=", "expression": "0"}
                if init_stmt.get("type") == "assignment":
                    self._execute_assignment_statement(init_stmt)
                elif init_stmt.get("type") == "declaration":
                    self._execute_simple_statement(init_stmt)
                else:
                    # Generic statement execution
                    self._execute_statements([init_stmt])
            else:
                # Old string format handling
                # Check if it's a declaration (like "integer i = 1")
                decl_match = re.match(r"\s*(string|integer|key|float|vector|list|rotation)\s+(\w+)\s*=\s*(.*)", init_stmt, re.DOTALL)
                if decl_match:
                    var_type, var_name, var_val = decl_match.groups()
                    self._execute_simple_statement({
                        "type": "declaration",
                        "lsl_type": var_type,
                        "name": var_name,
                        "value": var_val.strip() if var_val else None
                    })
                else:
                    # It's a simple assignment
                    self._execute_simple_statement({"type": "simple", "statement": init_stmt})
        
        # Execute loop
        while self._evaluate_expression(for_node["condition"]):
            result = self._execute_statements(for_node["body"])
            if result is not None:
                return result
            
            # Execute increment
            if for_node.get("increment"):
                self._execute_simple_statement({"type": "simple", "statement": for_node["increment"]})
        
        return None

    def _call_user_function(self, func_name, args):
        func_def = self.user_functions[func_name]
        
        # Save current debug context before function call
        saved_statement_info = self.next_statement_info.copy() if isinstance(self.next_statement_info, dict) else None
        
        # Create new frame for function
        new_frame = Frame(parent_scope=self.call_stack.get_current_scope())
        
        # Set function arguments
        arg_names = func_def["args"]
        for i, arg_def in enumerate(arg_names):
            # Handle both old string format and new ANTLR4 dict format
            if isinstance(arg_def, dict) and "name" in arg_def:
                # New ANTLR4 format: {"type": "string", "name": "command"}
                arg_name = arg_def["name"]
            elif isinstance(arg_def, str) and arg_def.strip():
                # Old format: "string command"
                arg_name = arg_def.split()[-1]  # Get the variable name after the type
            else:
                continue
            
            if i < len(args):
                new_frame.set(arg_name, args[i])
        
        # Execute function body
        self.call_stack.push(new_frame)
        return_value = self._execute_statements(func_def["body"])
        self.call_stack.pop()
        
        # Restore debug context after function call
        if saved_statement_info and self.debug_mode:
            self.next_statement_info = saved_statement_info
        
        return return_value

    def _call_api_function(self, func_name, args):
        """Call an API function - either built-in LSL function or user-defined function."""
        # First check if it's a user-defined function
        if func_name in self.user_functions:
            return self._call_user_function(func_name, args)
        
        # Then check if it's a built-in LSL function
        # Try direct method name first (e.g., llSay)
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            if callable(func):
                print(f"[LSL API - HASATTR PATH]: {func_name} called with {args}")
                return func(*args)
        
        # Try with api_ prefix for extended API functions
        api_method_name = f"api_{func_name}"
        if hasattr(self, api_method_name):
            func = getattr(self, api_method_name)
            if callable(func):
                print(f"[LSL API]: {func_name} called with {args}")
                return func(*args)
        
        # Handle through the extended API if available
        if hasattr(self, 'lsl_api') and hasattr(self.lsl_api, func_name):
            func = getattr(self.lsl_api, func_name)
            if callable(func):
                print(f"[LSL API]: {func_name} called with {args}")
                return func(*args)
        
        # Function not found
        print(f"[LSL API]: Unknown function: {func_name}")
        return None

    def run(self):
        # Thread-safe event queue operations
        print("[SIMULATOR] 🚀 run() method called - Queueing state_entry event")
        self.event_queue.put(("state_entry", []))
        print("[SIMULATOR] ✅ state_entry event queued")
        
        print("[SIMULATOR] 🔄 Entering main event loop")
        while self._is_running:
            try:
                # Non-blocking get with timeout
                event_name, args = self.event_queue.get(timeout=0.1)
                print(f"[SIMULATOR] 📨 Processing event: {event_name}")
                self.trigger_event(event_name, *args)
                self.event_queue.task_done()
            except:
                # Queue is empty, continue the loop
                pass

    def trigger_event(self, event_name, *args):
        if event_name == "http_response":
            request_id = args[0] if args else "none"
            status = args[1] if len(args) > 1 else "unknown"
            current_http = self.global_scope.get("current_http_request")
            print(f"[HTTP] 📨 LSL EVENT TRIGGERED")
            print(f"[HTTP]    Request ID: {request_id}")
            print(f"[HTTP]    Status: {status}")
            print(f"[HTTP]    Current HTTP Request: {current_http}")
            print(f"[HTTP]    Match: {'✅ YES' if request_id == current_http else '❌ NO'}")
        elif event_name == "dataserver":
            print(f"[DATASERVER] 📨 EVENT TRIGGERED")
            print(f"[DATASERVER]    Query ID: {args[0] if args else 'none'}")
            print(f"[DATASERVER]    Data: {args[1] if len(args) > 1 else 'none'}")
        elif event_name == "sensor":
            print(f"[SENSOR_DEBUG] 📨 EVENT TRIGGERED")
            print(f"[SENSOR_DEBUG]    Detected: {args[0] if args else 'none'}")
        print(f"[EVENT DEBUG]: Triggering event '{event_name}' with args: {len(args)} args")
        state_events = self.states.get(self.current_state, {})
        event_handler = state_events.get(event_name)
        if event_handler:
            print(f"[EVENT DEBUG]: Found handler for '{event_name}', executing...")
            # Create a frame for the event handler (local variables)
            event_frame = Frame(parent_scope=self.global_scope)
            
            # Map event arguments to parameter names (same pattern as _call_user_function)
            event_args = event_handler.get("args", "")
            if event_name == "dataserver":
                print(f"[DATASERVER] Event args: {event_args}")
                print(f"[DATASERVER] Received args: {args}")
            elif event_name == "sensor":
                print(f"[SENSOR_DEBUG] Event args: {event_args}")
                print(f"[SENSOR_DEBUG] Received args: {args}")
            if event_args and args:
                if isinstance(event_args, list):
                    # New format: list of parameter objects
                    for i, arg_obj in enumerate(event_args):
                        if i < len(args) and isinstance(arg_obj, dict):
                            arg_name = arg_obj.get("name", f"arg_{i}")
                            event_frame.set(arg_name, args[i])
                            if event_name == "dataserver":
                                print(f"[DATASERVER] Set {arg_name} = {args[i]}")
                            elif event_name == "sensor":
                                print(f"[SENSOR_DEBUG] Set {arg_name} = {args[i]}")
                else:
                    # Old format: comma-separated string
                    arg_names = [arg.strip() for arg in event_args.split(",")]
                    for i, arg_name_str in enumerate(arg_names):
                        if i < len(args):
                            # Extract variable name from "type name" format
                            arg_name = arg_name_str.split()[-1]
                            event_frame.set(arg_name, args[i])
                            if event_name == "dataserver":
                                print(f"[DATASERVER] Set {arg_name} = {args[i]}")
                            elif event_name == "sensor":
                                print(f"[SENSOR_DEBUG] Set {arg_name} = {args[i]}")
            
            self.call_stack.push(event_frame)
            try:
                body_statements = event_handler.get("body", [])
                if event_name == "dataserver":
                    print(f"[DATASERVER] Executing handler with {len(body_statements)} statements")
                elif event_name == "sensor":
                    print(f"[SENSOR_DEBUG] Executing handler with {len(body_statements)} statements")
                self._execute_statements(body_statements)
            finally:
                self.call_stack.pop()

    def continue_execution(self):
        self.single_step = False
        self.debugger_ready.clear()
        self.execution_paused.set()

    def step(self):
        """Step over - execute next statement without entering function calls"""
        self.single_step = True
        self.step_mode = "over"
        self.call_depth = len(self.call_stack.frames)  # Track current depth
        self.debugger_ready.clear()
        self.execution_paused.set()
    
    def step_into(self):
        """Step into - execute next statement and enter function calls"""
        self.single_step = True
        self.step_mode = "into"
        self.call_depth = 0  # Reset call depth tracking
        self.debugger_ready.clear()
        self.execution_paused.set()

    def stop(self):
        self._is_running = False
        self.execution_paused.set()
        self.debugger_ready.set()

    def simulate_avatar_sense(self, avatar_name):
        """Simulate an avatar approaching and trigger NPC greeting via /hook endpoint"""
        print(f"[AVATAR_SENSE]: Avatar '{avatar_name}' approaching NPC")
        
        # Generate a sequential key for this avatar (like SL/OS) - thread-safe
        with self.counter_lock:
            self.avatar_counter += 1
            avatar_key = f"00000000-0000-0000-0000-{self.avatar_counter:012d}"
        
        # Store detected avatar data for llDetectedKey/llDetectedDist to access
        self.detected_avatars = [{
            "key": avatar_key,
            "name": avatar_name,
            "distance": 2.5  # Within conversation range
        }]
        
        # Set sensed avatar data for say_on_channel to use
        self.sensed_avatar_name = avatar_name
        self.sensed_avatar_key = avatar_key
        print(f"[AVATAR_SENSE]: Set sensed avatar: {avatar_name} (key: {avatar_key})")
        
        # Simulate the sensor detection by calling the sensor event
        self.event_queue.put(("sensor", [1]))  # 1 avatar detected
        
        print(f"[AVATAR_SENSE]: Sensor event queued for {avatar_name} (key: {avatar_key})")
        if hasattr(self, 'global_scope'):
            self.global_scope.set('current_avatar', avatar_key)

    def get_variables(self, scope):
        if scope == "globals":
            return self.global_scope.locals
        elif scope == "locals":
            current_frame = self.call_stack.get_current_scope()
            if current_frame and current_frame != self.global_scope:
                return current_frame.locals
            else:
                # If we're in global scope, show global variables as locals too
                return self.global_scope.locals
        return None
    
    def get_performance_stats(self):
        """Get basic performance statistics."""
        return {
            'expression_evaluator': {
                'evaluations': getattr(self.expression_evaluator, 'total_evaluations', 0)
            }
        }
    
    def reset_performance_stats(self):
        """Reset performance statistics."""
        pass  # Simple evaluator doesn't need stat reset
    
    def get_debug_info(self):
        """Get detailed debug information."""
        return {
            'architecture': 'simplified_antlr4',
            'optimizations': ['simple_evaluation'],
            'performance': self.get_performance_stats(),
            'active_features': {
                'debug_mode': self.debug_mode,
                'expression_evaluator': self.expression_evaluator is not None
            }
        }
    def __getattr__(self, name):
        """
        Delegate all API calls to the consolidated LSL API.
        This eliminates dangerous redundancy by ensuring single source of truth.
        """
        # Don't create placeholders for user-defined functions
        if hasattr(self, 'user_functions'):
            # Check both direct name and api_ prefixed name
            base_name = name[4:] if name.startswith('api_') else name
            if base_name in self.user_functions:
                raise AttributeError(f"'{base_name}' is a user-defined function, not an attribute")
        
        if name.startswith('api_'):
            # Remove 'api_' prefix and delegate to consolidated API
            func_name = name[4:]  # Remove 'api_' prefix
            
            # Special handling for simulator-specific functions
            if func_name in ['llSay']:
                # llSay should print to console for debugging
                def llSay_impl(channel, message):
                    print(f"[llSay]: {message}")
                    # Also call the comprehensive implementation if available
                    if hasattr(self.lsl_api, 'llSay'):
                        return self.lsl_api.llSay(channel, message)
                return llSay_impl
            
            elif func_name in ['llListen', 'llListenRemove']:
                # Listener functions need access to simulator state
                if func_name == 'llListen':
                    def llListen_impl(channel, name, key, message):
                        handle = None
                        with self.counter_lock:
                            handle = self.listener_handle_counter
                            self.listener_handle_counter += 1
                        
                        listener = {
                            'handle': handle,
                            'channel': int(channel),
                            'name': str(name) if name else "",
                            'key': str(key) if key != "" else "",
                            'message': str(message) if message else "",
                            'active': True
                        }
                        
                        with self.listeners_lock:
                            self.active_listeners.append(listener)
                        
                        return handle
                    return llListen_impl
                
                elif func_name == 'llListenRemove':
                    def llListenRemove_impl(handle):
                        with self.listeners_lock:
                            for listener in self.active_listeners:
                                if listener['handle'] == handle:
                                    listener['active'] = False
                                    break
                    return llListenRemove_impl
            
            elif func_name in ['llSetTimerEvent']:
                # Timer functions need access to simulator state
                def llSetTimerEvent_impl(time):
                    self.timer_active = True
                    
                    def timer_loop():
                        while self._is_running and self.timer_active:
                            time_module.sleep(float(time))
                            if self.timer_active:
                                self.event_queue.put(("timer",))
                    
                    threading.Thread(target=timer_loop, daemon=True).start()
                return llSetTimerEvent_impl
            
            elif func_name in ['llSensor', 'llSensorRepeat', 'llSensorRemove']:
                # Sensor functions need access to simulator state
                if func_name == 'llSensor':
                    def llSensor_impl(name, key, type_filter, range_val, arc):
                        self.sensor_ranges['single'] = {
                            'name': str(name),
                            'key': str(key),
                            'type': int(type_filter),
                            'range': float(range_val),
                            'arc': float(arc),
                            'repeat': False
                        }
                        
                        # Simulate detection of nearby avatars for testing
                        self.detected_avatars = [
                            {"key": f"test-avatar-{i}", "name": f"TestUser{i}", "distance": 2.5 + i}
                            for i in range(1, 3)  # Simulate 2 detected avatars
                        ]
                        
                        # Queue sensor event
                        self.event_queue.put(("sensor", len(self.detected_avatars)))
                    return llSensor_impl
                
                elif func_name == 'llSensorRepeat':
                    def llSensorRepeat_impl(name, key, type_filter, range_val, arc, rate):
                        self.sensor_ranges['repeat'] = {
                            'name': str(name),
                            'key': str(key),
                            'type': int(type_filter),
                            'range': float(range_val),
                            'arc': float(arc),
                            'rate': float(rate),
                            'repeat': True
                        }
                        
                        def sensor_loop():
                            while self._is_running and 'repeat' in self.sensor_ranges:
                                # Simulate detection
                                self.detected_avatars = [
                                    {"key": f"repeat-avatar-{i}", "name": f"RepeatingUser{i}", "distance": 1.5 + i}
                                    for i in range(1, 2)  # Simulate 1 detected avatar
                                ]
                                
                                self.event_queue.put(("sensor", len(self.detected_avatars)))
                                time_module.sleep(rate)
                        
                        threading.Thread(target=sensor_loop, daemon=True).start()
                    return llSensorRepeat_impl
                
                elif func_name == 'llSensorRemove':
                    def llSensorRemove_impl():
                        self.sensor_ranges.clear()
                        self.detected_avatars.clear()
                    return llSensorRemove_impl
            
            elif func_name in ['llDetectedKey', 'llDetectedDist', 'llDetectedName']:
                # Detection functions need access to simulator state
                if func_name == 'llDetectedKey':
                    def llDetectedKey_impl(index):
                        if 0 <= index < len(self.detected_avatars):
                            return self.detected_avatars[index]["key"]
                        return "00000000-0000-0000-0000-000000000000"
                    return llDetectedKey_impl
                
                elif func_name == 'llDetectedDist':
                    def llDetectedDist_impl(index):
                        if 0 <= index < len(self.detected_avatars):
                            return self.detected_avatars[index]["distance"]
                        return 0.0
                    return llDetectedDist_impl
                
                elif func_name == 'llDetectedName':
                    def llDetectedName_impl(index):
                        if 0 <= index < len(self.detected_avatars):
                            return self.detected_avatars[index]["name"]
                        return ""
                    return llDetectedName_impl
            
            elif func_name in ['llHTTPRequest']:
                # HTTP functions need access to simulator state
                def llHTTPRequest_impl(url, parameters, body):
                    def make_request():
                        try:
                            # Simulate HTTP request
                            time_module.sleep(0.5)  # Simulate network delay
                            
                            # Mock different responses based on URL
                            if "/register" in str(url):
                                status = 200
                                response_body = '{"status": "registered", "message": "NPC registered successfully"}'
                            elif "/hook" in str(url):
                                status = 200
                                response_body = '{"say": "Hello! How can I help you today?", "text_display": "Ready to assist"}'
                            elif "/talk" in str(url):
                                status = 200  
                                response_body = '{"say": "That\'s interesting! Tell me more.", "text_display": "Listening..."}'
                            else:
                                status = 404
                                response_body = '{"error": "Endpoint not found"}'
                            
                            # Queue http_response event
                            request_id = str(uuid.uuid4())
                            metadata = []
                            self.event_queue.put(("http_response", request_id, status, metadata, response_body))
                            
                        except Exception as e:
                            # Queue error response
                            request_id = str(uuid.uuid4())
                            self.event_queue.put(("http_response", request_id, 500, [], f'{{"error": "{str(e)}"}}'))
                    
                    threading.Thread(target=make_request, daemon=True).start()
                    return str(uuid.uuid4())  # Return request ID
                return llHTTPRequest_impl
            
            elif func_name in ['llGetNotecardLine']:
                # Notecard functions need access to simulator state
                def llGetNotecardLine_impl(name, line_number):
                    def read_notecard():
                        # Simulate reading notecard content
                        lines = [
                            "NPC Profile Data",
                            "Name: Test NPC",
                            "Role: Assistant", 
                            "Personality: Helpful and friendly"
                        ]
                        
                        line_num = int(line_number)
                        if line_num < len(lines):
                            data = lines[line_num]
                        else:
                            data = "EOF"
                        
                        # Queue dataserver event
                        time_module.sleep(0.1)  # Simulate async delay
                        query_id = str(uuid.uuid4())
                        self.event_queue.put(("dataserver", query_id, data))
                    
                    threading.Thread(target=read_notecard, daemon=True).start()
                    return str(uuid.uuid4())  # Return query ID
                return llGetNotecardLine_impl
            
            # For all other functions, delegate to consolidated API
            elif hasattr(self.lsl_api, func_name):
                return getattr(self.lsl_api, func_name)
            elif func_name in self.lsl_api.functions:
                return self.lsl_api.functions[func_name]
            else:
                # Return a placeholder for unimplemented functions
                def placeholder(*args, **kwargs):
                    print(f"[LSL API]: {func_name} called with {args}")
                    return None
                return placeholder
        
        # For non-API attributes, raise the normal AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
