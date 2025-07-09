#!/usr/bin/env python3
"""
Simple Expression Evaluator - Replaces over-engineered modular system
Addresses criticism: "LSL não é JavaScript - a complessità sintattica é limitata"
"""

import re
from typing import Any, Union, List


class SimpleExpressionEvaluator:
    """
    Simple, direct expression evaluator for LSL.
    No visitor patterns, object pooling, or complex fallback systems.
    LSL syntax is simple - the evaluator should be too.
    """
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def evaluate(self, expr_str: str) -> Any:
        """
        Evaluate an expression directly without complex architecture.
        Handles the 90% case simply, falls back gracefully for edge cases.
        """
        if not expr_str:
            return None
        
        original_expr_str = str(expr_str)
        expr_str = original_expr_str.strip()
        
        # Handle empty string after stripping
        if not expr_str:
            return original_expr_str
        
        # Handle most common cases first (performance optimization)
        
        # 1. String literals (very common)
        if expr_str.startswith('"') and expr_str.endswith('"') and expr_str.count('"') == 2:
            return expr_str[1:-1]
        
        # 2. Numbers (very common)
        if expr_str.isdigit():
            return int(expr_str)
        
        if re.match(r'^-?\d+$', expr_str):
            return int(expr_str)
        
        if re.match(r'^-?\d*\.\d+$', expr_str):
            return float(expr_str)
        
        # 3. Variables (very common)
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr_str):
            return self._lookup_variable(expr_str)
        
        # 4. Component access (common in LSL) - but not if it's a vector/list literal
        if ('.' in expr_str and not self._is_url_or_ip(expr_str) and 
            not (expr_str.startswith('<') and expr_str.endswith('>')) and
            not (expr_str.startswith('[') and expr_str.endswith(']'))):
            return self._evaluate_component_access(expr_str)
        
        # 5. Function calls (common)
        if '(' in expr_str and expr_str.endswith(')'):
            return self._evaluate_function_call(expr_str)
        
        # 6. Vector literals (common in LSL)
        if expr_str.startswith('<') and expr_str.endswith('>'):
            return self._evaluate_vector_literal(expr_str)
        
        # 7. List literals (less common)
        if expr_str.startswith('[') and expr_str.endswith(']'):
            return self._evaluate_list_literal(expr_str)
        
        # 8. Binary operations (handle last due to complexity)
        return self._evaluate_binary_operation(expr_str)
    
    def _lookup_variable(self, name: str) -> Any:
        """Look up variable value."""
        # Check call stack
        val = self.simulator.call_stack.find_variable(name)
        if val is not None:
            return val
        
        # Check constants
        if hasattr(self.simulator, name):
            return getattr(self.simulator, name)
        
        # Return as string if not found (LSL behavior)
        return name
    
    def _is_url_or_ip(self, text: str) -> bool:
        """Check if text is URL or IP - simple heuristic."""
        return ('://' in text or 
                text.startswith('http') or 
                text.count('.') >= 2)
    
    def _evaluate_component_access(self, expr_str: str) -> Any:
        """Evaluate component access like variable.x"""
        parts = expr_str.split('.', 1)
        if len(parts) != 2:
            return expr_str
        
        var_name, component = parts
        var_value = self._lookup_variable(var_name)
        
        if isinstance(var_value, list):
            return self.simulator._get_component(var_value, component)
        
        return f"{var_name}.{component}"
    
    def _evaluate_function_call(self, expr_str: str) -> Any:
        """Evaluate function call - simple parsing."""
        match = re.match(r'(\w+)\s*\((.*)\)$', expr_str)
        if not match:
            return expr_str
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        # Parse arguments simply
        args = []
        if args_str.strip():
            args = self._parse_arguments(args_str)
        
        # Evaluate arguments
        evaluated_args = [self.evaluate(arg) for arg in args]
        
        # Call function
        return self.simulator._call_api_function(func_name, evaluated_args)
    
    def _evaluate_vector_literal(self, expr_str: str) -> List[float]:
        """Evaluate vector literal like <1.0, 2.0, 3.0>"""
        content = expr_str[1:-1].strip()
        if not content:
            return []
        
        parts = content.split(',')
        result = []
        for part in parts:
            try:
                result.append(float(self.evaluate(part.strip())))
            except (ValueError, TypeError):
                result.append(0.0)
        
        return result
    
    def _evaluate_list_literal(self, expr_str: str) -> List[Any]:
        """Evaluate list literal like [1, 2, 3]"""
        content = expr_str[1:-1].strip()
        if not content:
            return []
        
        elements = self._parse_arguments(content)
        return [self.evaluate(elem) for elem in elements]
    
    def _evaluate_binary_operation(self, expr_str: str) -> Any:
        """Evaluate binary operations - simple left-to-right for most cases."""
        # Handle common operators in order of precedence
        operators = [
            ('||', self._logical_or),
            ('&&', self._logical_and),
            ('==', self._equal),
            ('!=', self._not_equal),
            ('<=', self._less_equal),
            ('>=', self._greater_equal),
            ('<', self._less),
            ('>', self._greater),
            ('+', self._add),
            ('-', self._subtract),
            ('*', self._multiply),
            ('/', self._divide),
            ('%', self._modulo)
        ]
        
        # Find the rightmost operator to handle left-to-right evaluation correctly
        for op, func in operators:
            # Find all occurrences of this operator
            pos = -1
            for i in range(len(expr_str) - len(op) + 1):
                if expr_str[i:i+len(op)] == op:
                    # Check if this operator is not inside a string or function call
                    if not self._is_inside_construct(expr_str, i):
                        pos = i
                        break  # Take the first valid occurrence
            
            if pos >= 0:
                left = expr_str[:pos].strip()
                right = expr_str[pos + len(op):].strip()
                
                if left and right:  # Make sure we have both operands
                    left_val = self.evaluate(left)
                    right_val = self.evaluate(right)
                    return func(left_val, right_val)
        
        # If no operator found, return as-is
        return expr_str
    
    def _is_inside_construct(self, expr_str: str, pos: int) -> bool:
        """Check if position is inside string or parentheses."""
        # Simple check for strings
        in_string = False
        for i in range(pos):
            if expr_str[i] == '"' and (i == 0 or expr_str[i-1] != '\\'):
                in_string = not in_string
        
        if in_string:
            return True
        
        # Simple check for parentheses
        paren_count = 0
        for i in range(pos):
            if expr_str[i] == '(':
                paren_count += 1
            elif expr_str[i] == ')':
                paren_count -= 1
        
        return paren_count > 0
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse comma-separated arguments - simple but effective."""
        args = []
        current = ""
        paren_level = 0
        bracket_level = 0
        in_string = False
        
        for char in args_str:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                elif char == '[':
                    bracket_level += 1
                elif char == ']':
                    bracket_level -= 1
                elif char == ',' and paren_level == 0 and bracket_level == 0:
                    args.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args
    
    # Simple binary operation implementations
    def _logical_or(self, left: Any, right: Any) -> bool:
        return bool(left) or bool(right)
    
    def _logical_and(self, left: Any, right: Any) -> bool:
        return bool(left) and bool(right)
    
    def _equal(self, left: Any, right: Any) -> bool:
        return left == right
    
    def _not_equal(self, left: Any, right: Any) -> bool:
        return left != right
    
    def _less_equal(self, left: Any, right: Any) -> bool:
        try:
            return left <= right
        except TypeError:
            return False
    
    def _greater_equal(self, left: Any, right: Any) -> bool:
        try:
            return left >= right
        except TypeError:
            return False
    
    def _less(self, left: Any, right: Any) -> bool:
        try:
            return left < right
        except TypeError:
            return False
    
    def _greater(self, left: Any, right: Any) -> bool:
        try:
            return left > right
        except TypeError:
            return False
    
    def _add(self, left: Any, right: Any) -> Any:
        # String concatenation or numeric addition
        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        try:
            return left + right
        except TypeError:
            return str(left) + str(right)
    
    def _subtract(self, left: Any, right: Any) -> Any:
        try:
            return left - right
        except TypeError:
            return 0
    
    def _multiply(self, left: Any, right: Any) -> Any:
        try:
            return left * right
        except TypeError:
            return 0
    
    def _divide(self, left: Any, right: Any) -> Any:
        try:
            return left / right if right != 0 else 0
        except TypeError:
            return 0
    
    def _modulo(self, left: Any, right: Any) -> Any:
        try:
            return left % right if right != 0 else 0
        except TypeError:
            return 0