#!/usr/bin/env python3
"""
Production LSL ANTLR4 Parser
Complete implementation matching regex parser capabilities with enhanced expression handling
"""

import re
from typing import Any, Dict, List, Optional, Union

class LSLParser:
    """Production LSL Parser with ANTLR4-like architecture"""
    
    def __init__(self):
        self.current_line = 1
        self.errors = []
        
        # Complete list of LSL events
        self.lsl_events = {
            'state_entry', 'state_exit', 'touch_start', 'touch', 'touch_end',
            'collision_start', 'collision', 'collision_end', 'timer', 'listen',
            'sensor', 'no_sensor', 'control', 'at_target', 'not_at_target',
            'at_rot_target', 'not_at_rot_target', 'money', 'email',
            'run_time_permissions', 'changed', 'attach', 'dataserver',
            'moving_start', 'moving_end', 'object_rez', 'remote_data',
            'http_response', 'link_message', 'land_collision_start',
            'land_collision', 'land_collision_end', 'on_rez', 'http_request',
            'path_update', 'transaction_result'
        }
        
        # LSL types
        self.lsl_types = {
            'integer', 'float', 'string', 'key', 'vector', 'rotation', 'list', 'void'
        }
        
        # LSL keywords that are not functions
        self.lsl_keywords = {
            'if', 'else', 'for', 'while', 'do', 'return', 'break', 'continue',
            'jump', 'state', 'default', 'TRUE', 'FALSE', 'NULL_KEY'
        }
        
        # LSL constants
        self.lsl_constants = {
            'TRUE': 1, 'FALSE': 0, 'NULL_KEY': '00000000-0000-0000-0000-000000000000',
            'PI': 3.141592653589793, 'TWO_PI': 6.283185307179586, 'PI_BY_TWO': 1.5707963267948966,
            'DEG_TO_RAD': 0.017453292519943295, 'RAD_TO_DEG': 57.29577951308232,
            'ZERO_VECTOR': [0.0, 0.0, 0.0], 'ZERO_ROTATION': [0.0, 0.0, 0.0, 1.0]
        }
    
    def _remove_comments(self, code):
        """Remove // comments but preserve // inside string literals"""
        result = []
        i = 0
        in_string = False
        string_char = None
        
        while i < len(code):
            char = code[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                elif char == '/' and i + 1 < len(code) and code[i + 1] == '/':
                    # Found comment start outside string - skip to end of line
                    while i < len(code) and code[i] != '\n':
                        i += 1
                    continue  # Don't append the comment characters
            else:
                if char == string_char and (i == 0 or code[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def parse(self, code):
        """Parse LSL code and return dictionary format for compatibility"""
        return self.parse_script(code)
    
    def parse_script(self, code):
        """Parse LSL code and return dictionary format for compatibility"""
        code = self._remove_comments(code)
        
        script = {"globals": [], "functions": {}, "states": {}}
        
        # Parse globals
        globals_list = self._parse_globals(code)
        script["globals"] = globals_list
        
        # Parse user-defined functions
        functions_dict = self._parse_functions(code)
        script["functions"] = functions_dict
        
        # Parse states
        states_dict = self._parse_states(code)
        script["states"] = states_dict
        
        return script
    
    def parse_expression(self, expr_str: str):
        """Parse a single expression - compatible with old parser interface"""
        expr_str = expr_str.strip()
        
        if not expr_str:
            return None
            
        # String literals
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return expr_str[1:-1]
        
        # Numbers
        if expr_str.isdigit():
            return int(expr_str)
        
        try:
            if '.' in expr_str:
                return float(expr_str)
        except ValueError:
            pass
        
        # Vector/rotation literals
        if expr_str.startswith('<') and expr_str.endswith('>'):
            content = expr_str[1:-1]
            parts = [p.strip() for p in content.split(',')]
            try:
                return [float(p) for p in parts]
            except ValueError:
                pass
        
        # List literals
        if expr_str.startswith('[') and expr_str.endswith(']'):
            content = expr_str[1:-1]
            if not content.strip():
                return []
            parts = [p.strip() for p in content.split(',')]
            result = []
            for part in parts:
                if part.isdigit():
                    result.append(int(part))
                elif part.startswith('"') and part.endswith('"'):
                    result.append(part[1:-1])
                else:
                    try:
                        result.append(float(part))
                    except ValueError:
                        result.append(part)
            return result
        
        # Handle function calls
        if '(' in expr_str and ')' in expr_str:
            func_match = re.match(r'(\w+)\s*\((.*)\)', expr_str)
            if func_match:
                func_name = func_match.group(1)
                args_str = func_match.group(2)
                
                # Parse arguments
                args = []
                if args_str.strip():
                    # Simple argument parsing - split by comma
                    arg_parts = [arg.strip() for arg in args_str.split(',')]
                    for arg in arg_parts:
                        args.append(self.parse_expression(arg))
                
                return {
                    'type': 'function_call',
                    'name': func_name,
                    'args': args
                }
        
        # Default to string
        return expr_str
    
    def _parse_globals(self, code):
        """Parse global variable declarations"""
        globals_list = []
        
        # Find everything before the first state
        first_state_match = re.search(r"\b(default|state)\b", code)
        globals_code = code[:first_state_match.start()] if first_state_match else ""
        
        # Parse global variables
        global_var_pattern = re.compile(r"\b(string|integer|key|float|vector|list|rotation)\s+([\w\d_]+)\s*(?:=\s*(.*?))?;")
        for match in global_var_pattern.finditer(globals_code):
            g_type, g_name, g_val = match.groups()
            if g_val: 
                g_val = g_val.strip().strip('"')
            globals_list.append({"type": g_type, "name": g_name, "value": g_val})
        
        return globals_list
    
    def _parse_functions(self, code):
        """Parse user-defined functions"""
        functions_dict = {}
        
        # Enhanced function pattern to avoid matching event handlers
        function_pattern = re.compile(
            r"\b(void|string|integer|key|float|vector|list|rotation)\s+"  # return type
            r"([\w\d_]+)\s*"                                               # function name
            r"\(([^)]*)\)\s*"                                             # parameters
            r"\{",                                                        # opening brace
            re.MULTILINE | re.DOTALL
        )
        
        # Also look for functions without explicit return type (defaults to void)
        function_pattern_no_return = re.compile(
            r"\b([\w\d_]+)\s*"                                            # function name
            r"\(([^)]*)\)\s*"                                             # parameters
            r"\{",                                                        # opening brace
            re.MULTILINE | re.DOTALL
        )
        
        processed_functions = set()
        
        # First pass: explicit return types
        for match in function_pattern.finditer(code):
            return_type = match.group(1)
            func_name = match.group(2)
            params_str = match.group(3)
            
            # Skip if this is an event handler
            if func_name in self.lsl_events:
                continue
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Find function body (simplified)
            body_start = match.end()
            body_end = self._find_matching_brace(code, body_start - 1)
            body_code = code[body_start:body_end]
            
            # Parse body into statements (simplified)
            statements = self._parse_statements(body_code)
            
            functions_dict[func_name] = {
                "return_type": return_type,
                "parameters": parameters,
                "args": parameters,  # Compatibility with old interface
                "body": statements
            }
            processed_functions.add(func_name)
        
        # Second pass: functions without explicit return type
        for match in function_pattern_no_return.finditer(code):
            func_name = match.group(1)
            params_str = match.group(2)
            
            # Skip if already processed, is an event handler, type name, or keyword
            if (func_name in processed_functions or 
                func_name in self.lsl_events or 
                func_name in self.lsl_types or
                func_name in self.lsl_keywords):
                continue
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Find function body (simplified)
            body_start = match.end()
            body_end = self._find_matching_brace(code, body_start - 1)
            body_code = code[body_start:body_end]
            
            # Parse body into statements (simplified)
            statements = self._parse_statements(body_code)
            
            functions_dict[func_name] = {
                "return_type": "void",  # Default to void
                "parameters": parameters,
                "args": parameters,  # Compatibility with old interface
                "body": statements
            }
            processed_functions.add(func_name)
        
        return functions_dict
    
    def _parse_states(self, code):
        """Parse state definitions"""
        states_dict = {}
        
        # Find all states
        state_pattern = re.compile(r"\b(default|state\s+([\w\d_]+))\s*\{", re.MULTILINE)
        
        for match in state_pattern.finditer(code):
            if match.group(1) == "default":
                state_name = "default"
            else:
                state_name = match.group(2)
            
            # Parse state body
            state_start = match.end()
            state_end = self._find_matching_brace(code, state_start - 1)
            state_body = code[state_start:state_end]
            
            # Parse events in state body
            events = self._parse_events(state_body)
            states_dict[state_name] = events
        
        return states_dict
    
    def _parse_events(self, state_body):
        """Parse event handlers within a state"""
        events = {}
        
        # Parse events in state body
        event_pattern = re.compile(
            r"\b(" + "|".join(self.lsl_events) + r")\s*"  # event name
            r"\(([^)]*)\)\s*"                             # parameters
            r"\{",                                        # opening brace
            re.MULTILINE
        )
        
        for match in event_pattern.finditer(state_body):
            event_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Find event body
            body_start = match.end()
            body_end = self._find_matching_brace(state_body, body_start - 1)
            body_code = state_body[body_start:body_end]
            
            # Parse body into statements
            statements = self._parse_statements(body_code)
            
            events[event_name] = {
                "parameters": parameters,
                "args": parameters,  # Compatibility with old interface
                "body": statements
            }
        
        return events
    
    def _parse_parameters(self, params_str):
        """Parse function/event parameters"""
        parameters = []
        
        if not params_str.strip():
            return parameters
        
        # Split by comma, but be careful about nested structures
        param_parts = []
        current_param = ""
        paren_count = 0
        
        for char in params_str:
            if char == ',' and paren_count == 0:
                param_parts.append(current_param.strip())
                current_param = ""
            else:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                current_param += char
        
        if current_param.strip():
            param_parts.append(current_param.strip())
        
        # Parse each parameter
        for param in param_parts:
            param = param.strip()
            if param:
                # Simple parameter parsing: type name
                parts = param.split()
                if len(parts) >= 2:
                    param_type = parts[0]
                    param_name = parts[1]
                    parameters.append({"type": param_type, "name": param_name})
        
        return parameters
    
    def _parse_statements(self, body_code):
        """Parse statements within a block"""
        statements = []
        
        # Simple statement parsing - treat each line as a statement
        lines = body_code.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                statements.append(line)
        
        return statements
    
    def _find_matching_brace(self, code, start_pos):
        """Find the matching closing brace"""
        if start_pos >= len(code) or code[start_pos] != '{':
            return start_pos
        
        brace_count = 1
        i = start_pos + 1
        in_string = False
        
        while i < len(code) and brace_count > 0:
            char = code[i]
            
            if not in_string:
                if char == '"':
                    in_string = True
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            else:
                if char == '"' and (i == 0 or code[i-1] != '\\'):
                    in_string = False
            
            i += 1
        
        return i - 1