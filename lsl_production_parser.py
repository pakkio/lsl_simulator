#!/usr/bin/env python3
"""
LSL Production Parser - Simple, Fast, and Reliable
Replaces pyparsing with a lightweight ANTLR4-style parser for production use.
"""

import re
from typing import Any, Dict, List, Optional, Union


class LSLProductionParser:
    """
    Simple production parser for LSL that replaces pyparsing.
    Focuses on reliability and simplicity over complex features.
    """
    
    def __init__(self):
        self.errors = []
        
    def parse_script(self, script_content: str) -> Dict[str, Any]:
        """Parse LSL script into simulator-compatible format."""
        self.errors = []
        
        try:
            # Clean content
            content = self._clean_content(script_content)
            
            # Parse components
            globals_list = self._parse_globals(content)
            functions = self._parse_functions(content)
            states = self._parse_states(content)
            
            return {
                'globals': globals_list,
                'functions': functions,
                'states': states
            }
            
        except Exception as e:
            self.errors.append(f"Parse error: {str(e)}")
            return {'globals': [], 'functions': {}, 'states': {}}
    
    def parse_expression(self, expr_str: str) -> Any:
        """Parse a single expression - simple and fast."""
        expr_str = expr_str.strip()
        
        if not expr_str:
            return None
            
        # Handle common patterns quickly
        
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
                return parts
        
        # List literals
        if expr_str.startswith('[') and expr_str.endswith(']'):
            content = expr_str[1:-1].strip()
            if not content:
                return []
            return self._parse_list_elements(content)
        
        # Function calls
        if '(' in expr_str and expr_str.endswith(')'):
            return self._parse_function_call(expr_str)
        
        # Binary operations (simplified)
        for op in ['==', '!=', '<=', '>=', '<', '>', '&&', '||', '+', '-', '*', '/', '%']:
            if op in expr_str:
                return self._parse_binary_op(expr_str, op)
        
        # Variable/identifier
        return expr_str
    
    def _clean_content(self, content: str) -> str:
        """Remove comments and normalize whitespace."""
        # Remove single-line comments
        content = re.sub(r'//[^\r\n]*', '', content)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    
    def _parse_globals(self, content: str) -> List[Dict[str, Any]]:
        """Parse global variable declarations."""
        globals_list = []
        
        # Remove function/state blocks
        content_no_blocks = self._remove_blocks(content)
        
        # Find global declarations
        pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)\s*(?:=\s*([^;]+))?\s*;'
        
        for match in re.finditer(pattern, content_no_blocks):
            type_name = match.group(1)
            name = match.group(2)
            value_str = match.group(3)
            
            value = None
            if value_str:
                value = self.parse_expression(value_str.strip())
            
            globals_list.append({
                'name': name,
                'type': type_name,
                'value': value
            })
        
        return globals_list
    
    def _parse_functions(self, content: str) -> Dict[str, Any]:
        """Parse user-defined functions."""
        functions = {}
        
        # Match function definitions
        pattern = r'\b(integer|float|string|key|vector|rotation|list|void)\s+(\w+)\s*\(([^)]*)\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(pattern, content):
            return_type = match.group(1)
            name = match.group(2)
            params_str = match.group(3)
            body_str = match.group(4)
            
            # Skip known event handlers
            if name in ['state_entry', 'touch_start', 'touch_end', 'timer', 'http_response']:
                continue
            
            # Parse parameters
            args = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        args.append(param)
            
            # Parse body into statements
            statements = self._parse_statements(body_str)
            
            functions[name] = {
                'return_type': return_type,
                'args': args,
                'body': statements
            }
        
        return functions
    
    def _parse_states(self, content: str) -> Dict[str, Any]:
        """Parse state definitions."""
        states = {}
        
        # Find state blocks
        pattern = r'\b(default|state\s+\w+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(pattern, content):
            state_name = match.group(1).strip()
            if state_name.startswith('state '):
                state_name = state_name.split()[-1]
            
            state_body = match.group(2)
            events = self._parse_events(state_body)
            
            states[state_name] = events
        
        return states
    
    def _parse_events(self, state_body: str) -> Dict[str, Any]:
        """Parse event handlers within a state."""
        events = {}
        
        # Known LSL events
        event_names = [
            'state_entry', 'state_exit', 'touch_start', 'touch', 'touch_end',
            'collision_start', 'collision', 'collision_end', 'timer', 'listen',
            'sensor', 'no_sensor', 'http_response', 'dataserver', 'changed'
        ]
        
        for event_name in event_names:
            pattern = rf'\b{event_name}\s*\(([^)]*)\)\s*\{{([^}}]*(?:\{{[^}}]*\}}[^}}]*)*)\}}'
            match = re.search(pattern, state_body)
            
            if match:
                params_str = match.group(1)
                event_body = match.group(2)
                
                # Parse event parameters
                args = params_str.strip() if params_str.strip() else ""
                
                # Parse event body
                statements = self._parse_statements(event_body)
                
                events[event_name] = {
                    'args': args,
                    'body': statements
                }
        
        return events
    
    def _parse_statements(self, body_str: str) -> List[Dict[str, Any]]:
        """Parse statements from body string."""
        statements = []
        
        # Split by semicolons but respect braces and strings
        stmt_parts = self._split_statements(body_str)
        
        for part in stmt_parts:
            part = part.strip()
            if not part:
                continue
            
            stmt = self._parse_statement(part)
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _parse_statement(self, stmt_str: str) -> Optional[Dict[str, Any]]:
        """Parse a single statement."""
        stmt_str = stmt_str.strip()
        
        # Variable declarations
        var_pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)\s*(?:=\s*(.+))?'
        var_match = re.match(var_pattern, stmt_str)
        if var_match:
            return {
                'type': 'declaration',
                'lsl_type': var_match.group(1),
                'name': var_match.group(2),
                'value': var_match.group(3).strip() if var_match.group(3) else None
            }
        
        # If statements
        if_pattern = r'if\s*\(([^)]+)\)\s*\{([^}]*)\}(?:\s*else\s*\{([^}]*)\})?'
        if_match = re.match(if_pattern, stmt_str)
        if if_match:
            return {
                'type': 'if',
                'condition': if_match.group(1),
                'then_body': self._parse_statements(if_match.group(2)),
                'else_body': self._parse_statements(if_match.group(3)) if if_match.group(3) else None
            }
        
        # For loops
        for_pattern = r'for\s*\(([^;]*);([^;]*);([^)]*)\)\s*\{([^}]*)\}'
        for_match = re.match(for_pattern, stmt_str)
        if for_match:
            return {
                'type': 'for',
                'init': for_match.group(1).strip(),
                'condition': for_match.group(2).strip(),
                'increment': for_match.group(3).strip(),
                'body': self._parse_statements(for_match.group(4))
            }
        
        # While loops
        while_pattern = r'while\s*\(([^)]+)\)\s*\{([^}]*)\}'
        while_match = re.match(while_pattern, stmt_str)
        if while_match:
            return {
                'type': 'while',
                'condition': while_match.group(1),
                'body': self._parse_statements(while_match.group(2))
            }
        
        # Return statements
        if stmt_str.startswith('return'):
            return_pattern = r'return\s*(.+)?'
            return_match = re.match(return_pattern, stmt_str)
            if return_match:
                return {
                    'type': 'return',
                    'value': return_match.group(1).strip() if return_match.group(1) else None
                }
        
        # Default: simple statement
        return {
            'type': 'simple',
            'statement': stmt_str
        }
    
    def _split_statements(self, body_str: str) -> List[str]:
        """Split body into statements, respecting braces and strings."""
        statements = []
        current = ""
        brace_level = 0
        in_string = False
        
        for char in body_str:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                elif char == ';' and brace_level == 0:
                    if current.strip():
                        statements.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            statements.append(current.strip())
        
        return statements
    
    def _remove_blocks(self, content: str) -> str:
        """Remove content inside braces to find top-level declarations."""
        result = ""
        brace_level = 0
        
        for char in content:
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
            elif brace_level == 0:
                result += char
        
        return result
    
    def _parse_list_elements(self, content: str) -> List[Any]:
        """Parse list elements."""
        elements = []
        current = ""
        level = 0
        in_string = False
        
        for char in content:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char in '([<':
                    level += 1
                elif char in ')]>':
                    level -= 1
                elif char == ',' and level == 0:
                    if current.strip():
                        elements.append(self.parse_expression(current.strip()))
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            elements.append(self.parse_expression(current.strip()))
        
        return elements
    
    def _parse_function_call(self, expr_str: str) -> Dict[str, Any]:
        """Parse function call."""
        match = re.match(r'(\w+)\s*\((.*)\)', expr_str)
        if not match:
            return expr_str
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        # Parse arguments
        args = []
        if args_str.strip():
            args = self._parse_list_elements(args_str)
        
        return [func_name] + args
    
    def _parse_binary_op(self, expr_str: str, operator: str) -> List[Any]:
        """Parse binary operation."""
        # Find the operator not inside parentheses or strings
        pos = -1
        level = 0
        in_string = False
        
        for i, char in enumerate(expr_str):
            if char == '"' and (i == 0 or expr_str[i-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char == '(':
                    level += 1
                elif char == ')':
                    level -= 1
                elif level == 0 and expr_str[i:i+len(operator)] == operator:
                    pos = i
                    break
        
        if pos == -1:
            return expr_str
        
        left = expr_str[:pos].strip()
        right = expr_str[pos+len(operator):].strip()
        
        return [self.parse_expression(left), operator, self.parse_expression(right)]