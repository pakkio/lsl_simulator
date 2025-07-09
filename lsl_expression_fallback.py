"""
LSL Expression Fallback System - Manual parsing for expressions that pyparsing cannot handle
Replaces the monolithic _evaluate_expression fallback logic with specialized handlers.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict


class ExpressionHandler(ABC):
    """Abstract base class for expression handlers."""
    
    @abstractmethod
    def can_handle(self, expr_str: str) -> bool:
        """Check if this handler can process the given expression."""
        pass
    
    @abstractmethod
    def handle(self, expr_str: str, simulator) -> Any:
        """Process the expression and return the result."""
        pass


class ListLiteralHandler(ExpressionHandler):
    """Handles list literals like [1, 2, 3]."""
    
    def can_handle(self, expr_str: str) -> bool:
        return expr_str.startswith('[') and expr_str.endswith(']')
    
    def handle(self, expr_str: str, simulator) -> List[Any]:
        content = expr_str[1:-1].strip()
        if not content:
            return []
        
        # Split by comma but handle nested structures
        elements = []
        level = 0
        current = ""
        for char in content:
            if char in '[(':
                level += 1
            elif char in '])':
                level -= 1
            elif char == ',' and level == 0:
                elements.append(simulator._evaluate_expression(current.strip()))
                current = ""
                continue
            current += char
        
        if current:
            elements.append(simulator._evaluate_expression(current.strip()))
        
        return elements


class VectorLiteralHandler(ExpressionHandler):
    """Handles vector/rotation literals like <x, y, z> or <x, y, z, w>."""
    
    def can_handle(self, expr_str: str) -> bool:
        return expr_str.startswith('<') and expr_str.endswith('>')
    
    def handle(self, expr_str: str, simulator) -> List[Any]:
        content = expr_str[1:-1].strip()
        if not content:
            return []
        
        # Split by comma
        components = [comp.strip() for comp in content.split(',')]
        evaluated_components = [simulator._evaluate_expression(comp) for comp in components]
        return evaluated_components


class FunctionCallHandler(ExpressionHandler):
    """Handles function calls like llSay(0, "hello")."""
    
    def can_handle(self, expr_str: str) -> bool:
        return '(' in expr_str and expr_str.endswith(')')
    
    def handle(self, expr_str: str, simulator) -> Any:
        func_match = re.match(r'(\w+)\s*\((.*)\)', expr_str)
        if not func_match:
            return None
        
        func_name, args_str = func_match.groups()
        
        # Parse arguments properly handling nested structures
        args = self._parse_arguments(args_str)
        evaluated_args = [simulator._evaluate_expression(arg) for arg in args]
        
        # Try API functions
        api_func = getattr(simulator, f"api_{func_name}", None)
        if api_func:
            return api_func(*evaluated_args)
        
        # Try user-defined functions
        if func_name in simulator.user_functions:
            return simulator._call_user_function(func_name, evaluated_args)
        
        return None
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse function arguments handling nested structures and quotes."""
        args = []
        if not args_str:
            return args
        
        level = 0
        in_quotes = False
        quote_char = None
        current_arg = ""
        
        for char in args_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                if char == '(' or char == '[' or char == '<':
                    level += 1
                elif char == ')' or char == ']' or char == '>':
                    level -= 1
                elif char == ',' and level == 0:
                    args.append(current_arg.strip())
                    current_arg = ""
                    continue
            current_arg += char
        
        if current_arg:
            args.append(current_arg.strip())
        
        return args


class StringLiteralHandler(ExpressionHandler):
    """Handles quoted strings."""
    
    def can_handle(self, expr_str: str) -> bool:
        return ((expr_str.startswith('"') and expr_str.endswith('"')) or
                (expr_str.startswith("'") and expr_str.endswith("'")))
    
    def handle(self, expr_str: str, simulator) -> str:
        return expr_str[1:-1]


class NumberLiteralHandler(ExpressionHandler):
    """Handles numeric literals."""
    
    def can_handle(self, expr_str: str) -> bool:
        try:
            float(expr_str)
            return True
        except ValueError:
            return False
    
    def handle(self, expr_str: str, simulator) -> Any:
        try:
            if '.' in expr_str:
                return float(expr_str)
            else:
                return int(expr_str)
        except ValueError:
            return None


class ComponentAccessHandler(ExpressionHandler):
    """Handles component access like variable.x."""
    
    def can_handle(self, expr_str: str) -> bool:
        return ('.' in expr_str and 
                not expr_str.startswith('(') and
                not self._is_url_or_ip(expr_str))
    
    def handle(self, expr_str: str, simulator) -> Any:
        var_name, component = expr_str.split('.', 1)
        val = simulator.call_stack.find_variable(var_name)
        if val is not None:
            return simulator._get_component(val, component)
        return None
    
    def _is_url_or_ip(self, text: str) -> bool:
        """Check if text is a URL or IP address."""
        return ('://' in text or text.startswith('http') or 
                text.replace('.', '').replace(':', '').isdigit())


class VariableHandler(ExpressionHandler):
    """Handles variable references."""
    
    def can_handle(self, expr_str: str) -> bool:
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr_str) is not None
    
    def handle(self, expr_str: str, simulator) -> Any:
        # Check for constants first
        if hasattr(simulator, expr_str):
            return getattr(simulator, expr_str)
        
        val = simulator.call_stack.find_variable(expr_str)
        return val if val is not None else expr_str


class StringConcatenationHandler(ExpressionHandler):
    """Handles string concatenation with +."""
    
    def can_handle(self, expr_str: str) -> bool:
        return '+' in expr_str
    
    def handle(self, expr_str: str, simulator) -> str:
        parts = self._split_by_plus(expr_str)
        
        if len(parts) <= 1:
            return None
        
        # Evaluate each part and concatenate
        result = ""
        for part in parts:
            part = part.strip()
            if not part:
                continue
            part_result = simulator._evaluate_expression(part)
            if part_result is not None:
                result += str(part_result)
            else:
                result += str(part)
        
        return result
    
    def _split_by_plus(self, expr_str: str) -> List[str]:
        """Split by + but handle nested expressions and quotes."""
        parts = []
        level = 0
        in_quotes = False
        quote_char = None
        current = ""
        
        for char in expr_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                if char in '([<':
                    level += 1
                elif char in ')]>':
                    level -= 1
                elif char == '+' and level == 0:
                    parts.append(current.strip())
                    current = ""
                    continue
            current += char
        
        if current:
            parts.append(current.strip())
        
        return parts


class TypeCastHandler(ExpressionHandler):
    """Handles type casting like (string)expression."""
    
    def can_handle(self, expr_str: str) -> bool:
        return re.match(r'\((string|integer|float|key)\)\s*(.+)', expr_str) is not None
    
    def handle(self, expr_str: str, simulator) -> Any:
        cast_match = re.match(r'\((string|integer|float|key)\)\s*(.+)', expr_str)
        if not cast_match:
            return None
        
        cast_type, inner_expr = cast_match.groups()
        inner_result = simulator._evaluate_expression(inner_expr)
        
        if cast_type == 'string':
            return str(inner_result)
        elif cast_type == 'integer':
            try:
                return int(inner_result)
            except (ValueError, TypeError):
                return 0
        elif cast_type == 'float':
            try:
                return float(inner_result)
            except (ValueError, TypeError):
                return 0.0
        else:  # key
            return str(inner_result)


class ExpressionFallbackSystem:
    """Manages fallback expression evaluation using specialized handlers.
    
    CRITICAL: Handler order matters! Handlers are tried in sequence until one matches.
    Current priority (HIGH to LOW specificity):
    
    1. ListLiteralHandler - [1,2,3] - Most specific syntax
    2. VectorLiteralHandler - <1,2,3> - Specific syntax
    3. FunctionCallHandler - func(...) - Specific syntax with parens
    4. StringLiteralHandler - "..." or '...' - Specific quotes
    5. NumberLiteralHandler - 123 or 123.45 - Specific numeric format
    6. TypeCastHandler - (type)expr - Specific cast syntax
    7. ComponentAccessHandler - var.component - Specific dot access
    8. VariableHandler - identifier - Simple identifiers
    9. StringConcatenationHandler - expr+expr - LOWEST priority (most generic)
    
    WARNING: StringConcatenationHandler MUST be last as it's most aggressive!
    """
    
    def __init__(self):
        # ORDER IS CRITICAL - DO NOT CHANGE WITHOUT REVIEWING EACH HANDLER
        self.handlers = [
            # High specificity - exact syntax matches
            ListLiteralHandler(),           # [...]
            VectorLiteralHandler(),         # <...>
            TypeCastHandler(),              # (type)expr - moved up to avoid + conflicts
            FunctionCallHandler(),          # func(...)
            StringLiteralHandler(),         # "..." or '...'
            NumberLiteralHandler(),         # 123 or 123.45
            
            # Medium specificity - pattern matches
            ComponentAccessHandler(),       # var.component
            VariableHandler(),              # identifier
            
            # Low specificity - MUST BE LAST
            StringConcatenationHandler(),   # expr+expr (most generic!)
        ]
        
        # Handler performance metrics
        self.handler_stats = {
            handler.__class__.__name__: {
                'attempted': 0,
                'successful': 0,
                'failed': 0
            }
            for handler in self.handlers
        }
    
    def evaluate(self, expr_str: str, simulator) -> Any:
        """Evaluate an expression using the appropriate handler."""
        expr_str = expr_str.strip()
        
        # Try each handler in order (priority-based)
        for handler in self.handlers:
            handler_name = handler.__class__.__name__
            self.handler_stats[handler_name]['attempted'] += 1
            
            if handler.can_handle(expr_str):
                try:
                    result = handler.handle(expr_str, simulator)
                    if result is not None:
                        self.handler_stats[handler_name]['successful'] += 1
                        return result
                except Exception as e:
                    self.handler_stats[handler_name]['failed'] += 1
                    # Log error but continue to next handler
                    if hasattr(simulator, 'debug_mode') and simulator.debug_mode:
                        print(f"[HANDLER ERROR] {handler_name}: {e}")
                    continue
        
        # If no handler can process it, return as-is
        return expr_str
    
    def get_performance_stats(self) -> dict:
        """Get handler performance statistics."""
        return {
            'handler_stats': self.handler_stats.copy(),
            'total_attempts': sum(stats['attempted'] for stats in self.handler_stats.values()),
            'success_rate': sum(stats['successful'] for stats in self.handler_stats.values()) / 
                           max(1, sum(stats['attempted'] for stats in self.handler_stats.values())),
            'handler_efficiency': {
                name: {
                    'success_rate': stats['successful'] / max(1, stats['attempted']),
                    'usage_rate': stats['attempted'] / max(1, sum(s['attempted'] for s in self.handler_stats.values()))
                }
                for name, stats in self.handler_stats.items()
            }
        }
    
    def reset_stats(self) -> None:
        """Reset performance statistics."""
        for stats in self.handler_stats.values():
            stats['attempted'] = 0
            stats['successful'] = 0
            stats['failed'] = 0