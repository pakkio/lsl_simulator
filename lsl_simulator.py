import re
import time as time_module
import threading
import requests
import math
import random
import uuid
from queue import Queue
from expression_parser import ExpressionParser
from lsl_expression_evaluator import ExpressionEvaluator, TreeToNodeConverter
from lsl_expression_fallback import ExpressionFallbackSystem
from lsl_statement_executor import StatementExecutor
from lsl_expression_pool import get_global_node_pool, PooledTreeToNodeConverter
from lsl_exceptions import LSLErrorHandler

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
        self.expression_parser = ExpressionParser()
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
        
        # Initialize new modular expression evaluation system with optimizations
        self.node_pool = get_global_node_pool()
        self.error_handler = LSLErrorHandler(debug_mode=debug_mode)
        self.expression_evaluator = ExpressionEvaluator(self)
        self.tree_converter = PooledTreeToNodeConverter(self, self.node_pool)
        self.fallback_system = ExpressionFallbackSystem()
        self.statement_executor = StatementExecutor()
        
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

    def _evaluate_tree(self, parsed_tree):
        """
        Evaluate a parsed tree using the new modular expression system.
        This replaces the monolithic 118-line implementation with a clean, extensible architecture.
        """
        # Debug output for function calls
        if hasattr(parsed_tree, 'asList') or isinstance(parsed_tree, list):
            items = parsed_tree.asList() if hasattr(parsed_tree, 'asList') else parsed_tree
            if isinstance(items, list) and len(items) >= 1 and isinstance(items[0], str):
                if items[0].startswith('ll') or items[0].startswith('os'):
                    print(f"\033[92m[DEBUG] _evaluate_tree: Processing function call: {items}\033[0m")
        
        # Convert pyparsing tree to expression node
        expression_node = self.tree_converter.convert(parsed_tree)
        
        # Evaluate using the visitor pattern
        return self.expression_evaluator.evaluate(expression_node)

    def _evaluate_expression(self, expr_str):
        """
        Evaluate an expression using the optimized modular system.
        Features object pooling, enhanced error handling, and performance monitoring.
        """
        if not expr_str:
            return None
        
        try:
            # First try pyparsing with the pooled tree evaluator
            parsed = self.expression_parser.parse(expr_str)
            result = self._evaluate_tree(parsed)
            # Return nodes to pool after evaluation
            self.tree_converter.cleanup()
            return result
        except Exception as e:
            # If parsing fails, use the enhanced fallback system
            try:
                return self.fallback_system.evaluate(expr_str, self)
            except Exception as fallback_error:
                # Use error handler for graceful degradation
                return self.error_handler.handle_parse_error(expr_str, fallback_error)

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

            if not self._is_running:
                break

            return_value = None
            if isinstance(stmt, dict):
                stmt_type = stmt.get("type")
                if stmt_type == "simple" or stmt_type == "declaration":
                    return_value = self._execute_simple_statement(stmt)
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
                    
                    # Handle if statements with proper control flow
                    if stmt_str.startswith("if (") and stmt_str.endswith(") {"):
                        # Extract condition
                        condition = stmt_str[4:-3]  # Remove "if (" and ") {"
                        condition_result = self._evaluate_expression(condition)
                        
                        # Find the if body and optional else body
                        if_body = []
                        else_body = []
                        j = i + 1
                        brace_count = 1
                        
                        # Collect if body
                        while j < len(statements) and brace_count > 0:
                            next_stmt = statements[j].strip() if isinstance(statements[j], str) else str(statements[j])
                            
                            if next_stmt == "{":
                                brace_count += 1
                            elif next_stmt == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    break
                            elif next_stmt == "} else {":
                                # Found else clause immediately after if body
                                j += 1
                                brace_count = 1
                                # Collect else body
                                while j < len(statements) and brace_count > 0:
                                    else_stmt = statements[j].strip() if isinstance(statements[j], str) else str(statements[j])
                                    if else_stmt == "{":
                                        brace_count += 1
                                    elif else_stmt == "}":
                                        brace_count -= 1
                                        if brace_count == 0:
                                            break
                                    elif else_stmt and not else_stmt.startswith("//") and else_stmt not in ["{", "}"]:
                                        else_body.append(statements[j])
                                    j += 1
                                break
                            elif next_stmt and not next_stmt.startswith("//") and next_stmt not in ["{", "}"]:
                                if_body.append(statements[j])
                            j += 1
                        
                        # Execute the appropriate body
                        if condition_result:
                            if if_body:
                                return_value = self._execute_statements(if_body)
                        else:
                            if else_body:
                                return_value = self._execute_statements(else_body)
                        
                        # Skip to after the if/else block
                        i = j
                        if return_value is not None:
                            return return_value
                        i += 1
                        continue
                    
                    # Handle else statements (standalone)
                    if stmt_str == "} else {" or stmt_str.startswith("else"):
                        # This should be handled by if statement logic above
                        i += 1
                        continue
                    
                    # Skip braces (they're structural, not executable)
                    if stmt_str in ["{", "}"]:
                        i += 1
                        continue
                        
                    # Handle regular statements
                    if stmt_str.endswith(";"):
                        stmt_str = stmt_str[:-1]
                    
                    # Create structured statement
                    structured_stmt = {
                        "type": "simple",
                        "statement": stmt_str
                    }
                    return_value = self._execute_simple_statement(structured_stmt)
            
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

    def _execute_if_statement(self, if_node):
        condition = self._evaluate_expression(if_node["condition"])
        if condition:
            return self._execute_statements(if_node["then_body"])
        elif if_node.get("else_body"):
            return self._execute_statements(if_node["else_body"])
        return None

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
        
        return return_value

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
        """Get comprehensive performance statistics."""
        return {
            'memory_pool': self.node_pool.get_stats(),
            'error_handler': self.error_handler.get_error_summary(),
            'fallback_system': self.fallback_system.get_performance_stats(),
            'expression_evaluator': {
                'total_evaluations': getattr(self.expression_evaluator, 'total_evaluations', 0),
                'pool_hits': getattr(self.expression_evaluator, 'pool_hits', 0),
                'pool_misses': getattr(self.expression_evaluator, 'pool_misses', 0)
            }
        }
    
    def reset_performance_stats(self):
        """Reset all performance statistics."""
        if hasattr(self.node_pool, 'clear_pools'):
            self.node_pool.clear_pools()
        if hasattr(self.error_handler, 'clear_history'):
            self.error_handler.clear_history()
        if hasattr(self.fallback_system, 'reset_stats'):
            self.fallback_system.reset_stats()
    
    def get_debug_info(self):
        """Get detailed debug information."""
        return {
            'architecture': 'modular_refactored',
            'optimizations': ['object_pooling', 'exception_chaining', 'handler_prioritization'],
            'performance': self.get_performance_stats(),
            'active_features': {
                'debug_mode': self.debug_mode,
                'object_pool': self.node_pool is not None,
                'error_handler': self.error_handler is not None,
                'fallback_system': self.fallback_system is not None
            }
        }
    def api_llSay(self, channel, message): print(f"[llSay]: {message}")
    
    def api_llGetListLength(self, lst):
        return len(lst) if isinstance(lst, list) else 0
    
    def api_llList2String(self, lst, index):
        if isinstance(lst, list) and 0 <= index < len(lst):
            return str(lst[index])
        return ""
    
    def api_llDetectedKey(self, index):
        """Return the key of the detected avatar at the given index"""
        if 0 <= index < len(self.detected_avatars):
            return self.detected_avatars[index]["key"]
        return "00000000-0000-0000-0000-000000000000"  # NULL_KEY
    
    def api_llDetectedDist(self, index):
        """Return the distance to the detected avatar at the given index"""
        if 0 <= index < len(self.detected_avatars):
            return self.detected_avatars[index]["distance"]
        return 0.0
    
    def api_llDetectedName(self, index):
        """Return the name of the detected avatar at the given index"""
        if 0 <= index < len(self.detected_avatars):
            return self.detected_avatars[index]["name"]
        return ""
    
    def api_llListFindList(self, lst, sub):
        if not isinstance(lst, list) or not isinstance(sub, list):
            return -1
        # Find sublist in list
        for i in range(len(lst) - len(sub) + 1):
            if lst[i:i+len(sub)] == sub:
                return i
        return -1
    
    def api_llListSort(self, lst, stride, ascending):
        if not isinstance(lst, list) or stride <= 0:
            return lst
        
        # Group elements by stride
        groups = []
        for i in range(0, len(lst), stride):
            groups.append(lst[i:i+stride])
        
        # Sort groups by first element
        groups.sort(key=lambda x: x[0], reverse=not ascending)
        
        # Flatten back to list
        result = []
        for group in groups:
            result.extend(group)
        return result
    
    def api_llVecMag(self, vec):
        """Calculate the magnitude of a vector"""
        if not isinstance(vec, list) or len(vec) < 3:
            return 0.0
        import math
        return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    
    def api_llVecNorm(self, vec):
        """Normalize a vector to unit length"""
        if not isinstance(vec, list) or len(vec) < 3:
            return [0.0, 0.0, 0.0]
        
        mag = self.api_llVecMag(vec)
        if mag == 0.0:
            return [0.0, 0.0, 0.0]
        
        return [vec[0]/mag, vec[1]/mag, vec[2]/mag]
    
    def api_llRot2Euler(self, rot):
        """Convert rotation to euler angles"""
        if not isinstance(rot, list) or len(rot) < 4:
            return [0.0, 0.0, 0.0]
        
        import math
        x, y, z, w = rot[0], rot[1], rot[2], rot[3]
        
        # Convert quaternion to euler angles
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return [roll, pitch, yaw]
    
    def api_llGetPos(self):
        """Get current position (simulated)"""
        return [128.5, 129.3, 25.7]
    
    def api_llSetText(self, text, color, alpha):
        """Set text display (simulated)"""
        print(f"[TEXT DISPLAY]: {text}")
        return None
    
    def api_llSetAlpha(self, alpha, face):
        """Set object transparency"""
        print(f"[SET ALPHA]: {alpha} on face {face}")
        return None
    
    def api_llSetScale(self, scale):
        """Set object scale"""
        print(f"[SET SCALE]: {scale}")
        return None
    
    def api_llEuler2Rot(self, euler):
        """Convert euler angles to rotation"""
        if not isinstance(euler, list) or len(euler) < 3:
            return [0.0, 0.0, 0.0, 1.0]
        
        import math
        roll, pitch, yaw = euler[0], euler[1], euler[2]
        
        # Convert euler to quaternion
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return [x, y, z, w]
    
    def api_llDumpList2String(self, lst, separator):
        """Convert list to string with separator"""
        if not isinstance(lst, list):
            return ""
        return separator.join(str(item) for item in lst)
    
    def api_llHTTPRequest(self, url, options, body):
        """Make HTTP request (with actual HTTP call for testing)"""
        print(f"[HTTP] 🚀 REQUEST STARTING")
        print(f"[HTTP]    URL: {url}")
        print(f"[HTTP]    Options: {options}")
        print(f"[HTTP]    Body: {body[:100]}...")
        
        request_key = f"http-key-{int(time_module.time())}"
        print(f"[HTTP]    Request Key: {request_key}")
        
        # Try to determine endpoint type
        endpoint_type = "UNKNOWN"
        if isinstance(url, str):
            if "/register" in url:
                endpoint_type = "REGISTRATION"
            elif "/hook" in url:
                endpoint_type = "GREETING/HOOK"
            elif "/talk" in url:
                endpoint_type = "CONVERSATION"
        print(f"[HTTP] 🎯 Endpoint Type: {endpoint_type}")
        
        # Ensure URL is a string
        if isinstance(url, list):
            # If it's a list, it might be a binary expression that wasn't evaluated
            url = self._evaluate_tree(url)
        
        # Ensure body is evaluated if it's an expression
        if isinstance(body, list):
            # If it's a list, it might be a function call or expression that wasn't evaluated
            body = self._evaluate_tree(body)
        elif isinstance(body, str) and body.startswith('llList2Json('):
            # If it's a string that looks like a function call, manually construct and evaluate it
            print(f"[HTTP DEBUG]: Attempting to evaluate body expression: {body[:100]}...")
            try:
                # For the specific case of registration payload, manually construct the function call
                if 'npc_profile_data' in body and 'llGetRegionName' in body:
                    # This is the registration payload - construct it manually
                    profile_data = self.call_stack.find_variable('npc_profile_data') or ""
                    region_name = self.api_llGetRegionName()
                    pos = self.api_llGetPos()
                    position_json = self.api_llList2Json(self.JSON_ARRAY, [pos[0], pos[1], pos[2]])
                    owner = self.api_llGetOwner()
                    object_key = self.api_llGetKey()
                    timestamp = self.api_llGetUnixTime()
                    
                    # Construct the JSON object
                    json_data = self.api_llList2Json(self.JSON_OBJECT, [
                        "profile", profile_data,
                        "region", region_name,
                        "position", position_json,
                        "owner", owner,
                        "object_key", object_key,
                        "timestamp", timestamp
                    ])
                    
                    print(f"[HTTP DEBUG]: Successfully evaluated body to: {json_data[:100]}...")
                    body = json_data
                else:
                    print(f"[HTTP DEBUG]: Unknown llList2Json call pattern")
            except Exception as e:
                print(f"[HTTP DEBUG]: Failed to evaluate body expression: {e}")
                # Fall back to treating it as a literal string
        
        # Try to make actual HTTP request for testing
        try:
            import requests
            # Parse options
            method = "GET"
            headers = {}
            
            if isinstance(options, list):
                i = 0
                while i < len(options):
                    if i + 1 < len(options):
                        key = options[i]
                        value = options[i + 1]
                        if key == "method":
                            method = value
                            i += 2
                        elif key == "mimetype":
                            headers["Content-Type"] = value
                            i += 2
                        elif key == "header":
                            # Custom header - value is header name, next option is header value
                            header_name = value
                            if i + 2 < len(options):
                                header_value = options[i + 2]
                                headers[header_name] = header_value
                                i += 3  # Skip 3 values: key, header_name, header_value
                            else:
                                i += 2
                        else:
                            i += 2
                    else:
                        break
            
            # Debug output
            print(f"[HTTP DEBUG]: Method={method}, Headers={headers}")
            print(f"[HTTP DEBUG]: Body={body[:200]}...")
            
            # Make the request synchronously for now
            if method.upper() == "POST":
                if headers.get("Content-Type") == "application/json":
                    # Parse JSON string if it's a string, otherwise send as JSON object
                    if isinstance(body, str):
                        try:
                            import json
                            json_body = json.loads(body)
                            response = requests.post(url, json=json_body, headers=headers, timeout=5)
                        except json.JSONDecodeError:
                            # If it's not valid JSON, send as raw data
                            response = requests.post(url, data=body, headers=headers, timeout=5)
                    else:
                        response = requests.post(url, json=body, headers=headers, timeout=5)
                else:
                    response = requests.post(url, data=body, headers=headers, timeout=5)
            else:
                response = requests.get(url, headers=headers, timeout=5)
            
            # Simulate http_response event
            print(f"[HTTP] ✅ RESPONSE RECEIVED")
            print(f"[HTTP]    Status: {response.status_code}")
            print(f"[HTTP]    Request Key: {request_key}")
            print(f"[HTTP]    Response: {response.text[:200]}...")
            
            # Queue http_response event
            metadata = [f"status:{response.status_code}"]
            print(f"[HTTP] 📨 Queueing http_response event for LSL handler")
            self.event_queue.put(("http_response", [request_key, response.status_code, metadata, response.text]))
            
        except Exception as e:
            print(f"[HTTP ERROR]: {e}")
        
        return request_key
    
    def api_llGetInventoryType(self, name):
        """Get inventory item type (simulated)"""
        print(f"[INVENTORY CHECK]: {name} -> INVENTORY_NOTECARD (7)")
        return 7  # INVENTORY_NOTECARD
    
    def api_llGetNotecardLine(self, name, line):
        """Read notecard line (with actual file reading)"""
        print(f"[NOTECARD READ]: {name} line {line}")
        import uuid
        request_key = f"notecard-key-{uuid.uuid4().hex[:8]}"
        
        # Try to read actual file
        try:
            import threading
            import time
            def read_notecard():
                try:
                    # Look for the file in current directory
                    import os
                    filename = f"{name}.txt"
                    if os.path.exists(filename):
                        with open(filename, 'r') as f:
                            lines = f.readlines()
                            if line < len(lines):
                                content = lines[line].rstrip('\n')
                                print(f"[NOTECARD CONTENT]: Line {line}: {content}")
                                # Queue dataserver event with the content
                                print(f"[DEBUG] Queuing dataserver event for line {line}")
                                self.event_queue.put(("dataserver", [request_key, content]))
                            else:
                                print(f"[NOTECARD EOF]: Reached end of file {filename}")
                                # Queue dataserver event with EOF
                                self.event_queue.put(("dataserver", [request_key, "EOF"]))
                    else:
                        print(f"[NOTECARD ERROR]: File {filename} not found")
                        # Queue dataserver event with EOF for missing file
                        self.event_queue.put(("dataserver", [request_key, "EOF"]))
                except Exception as e:
                    print(f"[NOTECARD READ ERROR]: {e}")
                    # Queue dataserver event with EOF on error
                    self.event_queue.put(("dataserver", [request_key, "EOF"]))
            
            # Execute synchronously to ensure event is queued before returning
            read_notecard()
            
        except Exception as e:
            print(f"[NOTECARD SETUP ERROR]: {e}")
        
        return request_key
    
    def api_llSetTimerEvent(self, time):
        """Set timer event (simulated)"""
        print(f"[TIMER SET]: {time} seconds")
        if time == 5.0:
            print(f"[TIMER DEBUG]: 5-second timer set - likely from http throttle check")
        if time > 0:
            # Simulate timer event after delay
            import threading
            def fire_timer():
                import time as time_module
                time_module.sleep(float(time))
                print(f"[TIMER FIRE]: Timer firing after {time} seconds")
                self.event_queue.put(("timer", []))
            thread = threading.Thread(target=fire_timer)
            thread.daemon = True
            thread.start()
        return None
    
    def api_llStringLength(self, string):
        """Get string length"""
        return len(str(string))
    
    def api_llSubStringIndex(self, string, pattern):
        """Find substring index"""
        string_str = str(string)
        pattern_str = str(pattern)
        index = string_str.find(pattern_str)
        return index if index != -1 else -1
    
    def api_llStringTrim(self, string, trim_type):
        """Trim string"""
        string_str = str(string)
        return string_str.strip()
    
    def api_llGetSubString(self, string, start, end):
        """Get substring"""
        string_str = str(string)
        if start < 0:
            start = len(string_str) + start
        if end < 0:
            end = len(string_str) + end
        return string_str[start:end+1]
    
    # Constants moved to _initialize_lsl_constants method to ensure they're in global scope
    # But keep class attributes for API functions that need them
    JSON_OBJECT = "object"
    JSON_ARRAY = "array"
    JSON_INVALID = "invalid"
    OBJECT_POS = 1
    
    # Communication Functions
    def api_llListen(self, channel, name, key, message):
        """Listen on channel"""
        print(f"\033[92m🚨 [DEBUG] api_llListen CALLED: channel={channel}, name='{name}', key='{key}', message='{message}'\033[0m")
        # Thread-safe counter increment
        with self.counter_lock:
            handle = f"listen-handle-{self.listener_handle_counter}"
            self.listener_handle_counter += 1
        
        listener = {
            'handle': handle,
            'channel': channel,
            'name': name,
            'key': key, 
            'message': message,
            'active': True
        }
        
        # Thread-safe list append
        with self.listeners_lock:
            self.active_listeners.append(listener)
            total_listeners = len(self.active_listeners)
        
        print(f"[LISTEN]: ✅ Created listener on channel {channel} for '{message}' from {name} (key: {key})")
        print(f"[LISTEN]: Handle: {handle}, Total active listeners: {total_listeners}")
        print(f"[LISTEN]: 🔄 Returning handle: {handle}")
        return handle
    
    def api_llRegionSay(self, channel, message):
        """Say to entire region"""
        print(f"[REGION SAY]: Channel {channel}: {message}")
        return None
    
    def api_llInstantMessage(self, avatar, message):
        """Send instant message"""
        print(f"[IM]: To {avatar}: {message}")
        return None
    
    def say_on_channel(self, channel, message, speaker_name="Unknown", speaker_key="00000000-0000-0000-0000-000000000000"):
        """Simulate someone speaking on a channel and trigger matching listen events"""
        
        # For channel 0, use the sensed avatar as the speaker if available
        if channel == 0 and hasattr(self, 'sensed_avatar_name') and hasattr(self, 'sensed_avatar_key'):
            speaker_name = self.sensed_avatar_name
            speaker_key = self.sensed_avatar_key
        
        print(f"[SAY_ON_CHANNEL]: Channel {channel}: {speaker_name} says '{message}'")
        
        # Check all active listeners - thread-safe
        with self.listeners_lock:
            listeners_copy = self.active_listeners.copy()
        
        print(f"[LISTEN_DEBUG]: Found {len(listeners_copy)} active listeners")
        for i, listener in enumerate(listeners_copy):
            print(f"[LISTEN_DEBUG]: Listener {i}: channel={listener['channel']}, active={listener['active']}, handle={listener['handle']}")
        
        for listener in listeners_copy:
            if listener['active'] and self._listener_matches(listener, channel, message, speaker_name, speaker_key):
                # Queue a listen event
                self.event_queue.put(("listen", [channel, speaker_name, speaker_key, message]))
                print(f"[LISTEN_TRIGGER]: Triggering listen event for handle {listener['handle']}")
            else:
                match_result = self._listener_matches(listener, channel, message, speaker_name, speaker_key)
                print(f"[LISTEN_DEBUG]: Listener {listener['handle']} no match: active={listener['active']}, match={match_result}")

    def _listener_matches(self, listener, channel, message, speaker_name, speaker_key):
        """Check if a listener matches the given message"""
        # Channel must match
        if listener['channel'] != channel:
            return False
        
        # Check name filter (empty string means accept all)
        if listener['name'] != "" and listener['name'] != speaker_name:
            return False
            
        # Check key filter (empty string or NULL_KEY means accept all)
        if listener['key'] != "" and listener['key'] != "00000000-0000-0000-0000-000000000000" and listener['key'] != speaker_key:
            return False
            
        # Check message filter (empty string means accept all)
        if listener['message'] != "" and listener['message'] != message:
            return False
            
        return True
    
    def api_llListenRemove(self, handle):
        """Remove a listener by handle"""
        with self.listeners_lock:
            self.active_listeners = [l for l in self.active_listeners if l['handle'] != handle]
        print(f"[LISTEN_REMOVE]: Removed listener {handle}")

    def api_llListenControl(self, handle, active):
        """Enable/disable a listener"""
        with self.listeners_lock:
            for listener in self.active_listeners:
                if listener['handle'] == handle:
                    listener['active'] = bool(active)
                    print(f"[LISTEN_CONTROL]: Listener {handle} {'enabled' if active else 'disabled'}")
                    return
    
    def api_llGetOwner(self):
        """Get object owner"""
        result = "npc-owner-uuid-12345"
        print(f"[OWNER DEBUG]: llGetOwner() called, returning: {result}")
        return result
    
    def api_llGetKey(self):
        """Get object key"""
        return "object-uuid-67890"
    
    def api_llGetRegionName(self):
        """Get region name"""
        return "Test Region"
    
    def api_llGetTime(self):
        """Get elapsed time"""
        return time_module.time() % 86400  # Time since midnight
    
    def api_llGetUnixTime(self):
        """Get Unix timestamp"""
        return int(time_module.time())
    
    def api_llResetScript(self):
        """Reset script"""
        print("[RESET]: Script reset requested")
        return None
    
    # Sensor Functions
    def api_llSensorRepeat(self, name, key, type_mask, range_val, arc, rate):
        """Repeat sensor scanning"""
        print(f"[SENSOR]: Repeating scan for {name} every {rate}s in {range_val}m range")
        return None
    
    def api_llSensorRemove(self):
        """Remove sensor"""
        print("[SENSOR]: Sensor removed")
        return None
    
    
    # JSON Functions
    def api_llJsonGetValue(self, json_str, path):
        """Get value from JSON"""
        try:
            import json
            data = json.loads(json_str)
            if isinstance(path, list):
                current = data
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                        current = current[key]
                    else:
                        return self.JSON_INVALID
                return str(current)
            else:
                return str(data.get(path, self.JSON_INVALID))
        except:
            return self.JSON_INVALID
    
    def api_llList2Json(self, type_hint, lst):
        """Convert list to JSON"""
        try:
            import json
            if type_hint == self.JSON_OBJECT:
                # Convert list to object (key-value pairs)
                if len(lst) % 2 != 0:
                    return self.JSON_INVALID
                obj = {}
                for i in range(0, len(lst), 2):
                    obj[str(lst[i])] = lst[i+1]
                return json.dumps(obj)
            elif type_hint == self.JSON_ARRAY:
                return json.dumps(lst)
            else:
                return self.JSON_INVALID
        except:
            return self.JSON_INVALID
    
    # Utility Functions
    def api_llKey2Name(self, key):
        """Convert key to name"""
        if key == self.api_llGetOwner():
            return "Test User"
        # If we have a sensed avatar, return its name
        if hasattr(self, 'sensed_avatar_key') and key == self.sensed_avatar_key:
            return self.sensed_avatar_name
        return "Unknown User"
    
    def api_llGetObjectDetails(self, key, params):
        """Get object details"""
        details = []
        for param in params:
            if param == self.OBJECT_POS:
                details.append([125.0, 130.0, 25.0])
            else:
                details.append(0)
        return details
    
    def api_llRotBetween(self, start, end):
        """Calculate rotation between vectors"""
        import math
        # Simplified rotation calculation
        return [0.0, 0.0, 0.0, 1.0]
    
    def api_llParseString2List(self, string, separators, spacers):
        """Parse string to list"""
        string_str = str(string)
        if not separators:
            return [string_str]
        
        # Simple implementation - split by first separator
        if isinstance(separators, list) and len(separators) > 0:
            return string_str.split(separators[0])
        else:
            return string_str.split(str(separators))
    
    def api_llList2Vector(self, lst, index=0):
        """Convert list to vector"""
        if isinstance(lst, list) and len(lst) >= 3:
            return [float(lst[0]), float(lst[1]), float(lst[2])]
        return [0.0, 0.0, 0.0]
    
    # OpenSimulator NPC Functions
    def api_osIsNpc(self, key):
        """Check if target is an NPC"""
        # For testing, always return True to ensure consistent NPC behavior.
        print(f"[NPC CHECK]: osIsNpc({key}) -> True (forced for simulation)")
        return True
    
    def api_osNpcCreate(self, firstname, lastname, position, owner):
        """Create an NPC"""
        npc_key = f"npc-{firstname}-{lastname}-{int(time_module.time())}"
        print(f"[NPC CREATE]: Created NPC {firstname} {lastname} at {position}")
        return npc_key
    
    def api_osNpcSay(self, npc, message):
        """Make NPC speak"""
        print(f"[NPC SAY]: {npc}: {message}")
        return None
    
    def api_osNpcGetPos(self, npc):
        """Get NPC position"""
        return [128.0, 128.0, 25.0]
    
    def api_osNpcSetRot(self, npc, rotation):
        """Set NPC rotation"""
        print(f"[NPC ROTATE]: {npc} rotated to {rotation}")
        return None
    
    def api_osNpcPlayAnimation(self, npc, animation):
        """Play animation on NPC"""
        print(f"[NPC ANIMATE]: {npc} playing {animation}")
        return None
    
    def api_osSetDynamicTextureURL(self, *args):
        """Set dynamic texture"""
        print(f"[TEXTURE]: Dynamic texture set")
        return None
    
    # Constants moved to _initialize_lsl_constants method
    
    # ... all other api functions ...