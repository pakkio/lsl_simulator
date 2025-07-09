#!/usr/bin/env python3
"""
Simplified LSL Expression Evaluator
Replaces the complex modular architecture with a simple visitor pattern
"""

import re
from typing import Any, Dict, List, Optional
from .lsl_antlr_parser import LSLASTNode, LSLExpression, LSLVisitor
from .lsl_antlr_parser import (
    LSLBinaryOp, LSLUnaryOp, LSLFunctionCall, LSLIdentifier, LSLLiteral,
    LSLVectorLiteral, LSLRotationLiteral, LSLListLiteral, LSLTypeCast,
    LSLMemberAccess
)

class LSLSimpleEvaluator(LSLVisitor):
    """Simple expression evaluator using visitor pattern"""
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def evaluate(self, expr: LSLExpression) -> Any:
        """Evaluate an expression"""
        return self.visit(expr)
    
    def visit_LSLLiteral(self, node: LSLLiteral) -> Any:
        """Evaluate literal value"""
        return node.value
    
    def visit_LSLIdentifier(self, node: LSLIdentifier) -> Any:
        """Evaluate identifier (variable lookup)"""
        # Look up in call stack
        value = self.simulator.call_stack.find_variable(node.name)
        if value is not None:
            return value
        
        # Look up in global scope
        value = self.simulator.global_scope.get(node.name)
        if value is not None:
            return value
        
        # Return default for unknown variables
        return self._get_default_value('unknown')
    
    def visit_LSLBinaryOp(self, node: LSLBinaryOp) -> Any:
        """Evaluate binary operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        try:
            if node.operator == '+':
                return self._add_values(left, right)
            elif node.operator == '-':
                return self._subtract_values(left, right)
            elif node.operator == '*':
                return self._multiply_values(left, right)
            elif node.operator == '/':
                return self._divide_values(left, right)
            elif node.operator == '%':
                return self._modulo_values(left, right)
            elif node.operator == '==':
                return self._equals_values(left, right)
            elif node.operator == '!=':
                return not self._equals_values(left, right)
            elif node.operator == '<':
                return self._less_than_values(left, right)
            elif node.operator == '>':
                return self._greater_than_values(left, right)
            elif node.operator == '<=':
                return self._less_equal_values(left, right)
            elif node.operator == '>=':
                return self._greater_equal_values(left, right)
            elif node.operator == '&&':
                return self._logical_and_values(left, right)
            elif node.operator == '||':
                return self._logical_or_values(left, right)
            elif node.operator == '&':
                return self._bitwise_and_values(left, right)
            elif node.operator == '|':
                return self._bitwise_or_values(left, right)
            elif node.operator == '^':
                return self._bitwise_xor_values(left, right)
            elif node.operator == '<<':
                return self._shift_left_values(left, right)
            elif node.operator == '>>':
                return self._shift_right_values(left, right)
            else:
                return 0
        except Exception:
            return 0
    
    def visit_LSLUnaryOp(self, node: LSLUnaryOp) -> Any:
        """Evaluate unary operation"""
        operand = self.visit(node.operand)
        
        try:
            if node.operator == '!':
                return not self._is_truthy(operand)
            elif node.operator == '-':
                return -self._to_number(operand)
            elif node.operator == '+':
                return +self._to_number(operand)
            elif node.operator == '~':
                return ~self._to_integer(operand)
            else:
                return 0
        except Exception:
            return 0
    
    def visit_LSLFunctionCall(self, node: LSLFunctionCall) -> Any:
        """Evaluate function call"""
        args = [self.visit(arg) for arg in node.arguments]
        
        # Call function through simulator
        return self.simulator.call_function(node.function_name, args)
    
    def visit_LSLVectorLiteral(self, node: LSLVectorLiteral) -> List[float]:
        """Evaluate vector literal"""
        x = self._to_float(self.visit(node.x))
        y = self._to_float(self.visit(node.y))
        z = self._to_float(self.visit(node.z))
        return [x, y, z]
    
    def visit_LSLRotationLiteral(self, node: LSLRotationLiteral) -> List[float]:
        """Evaluate rotation literal"""
        x = self._to_float(self.visit(node.x))
        y = self._to_float(self.visit(node.y))
        z = self._to_float(self.visit(node.z))
        s = self._to_float(self.visit(node.s))
        return [x, y, z, s]
    
    def visit_LSLListLiteral(self, node: LSLListLiteral) -> List[Any]:
        """Evaluate list literal"""
        return [self.visit(elem) for elem in node.elements]
    
    def visit_LSLTypeCast(self, node: LSLTypeCast) -> Any:
        """Evaluate type cast"""
        value = self.visit(node.expression)
        
        if node.type_name == 'string':
            return self._to_string(value)
        elif node.type_name == 'integer':
            return self._to_integer(value)
        elif node.type_name == 'float':
            return self._to_float(value)
        elif node.type_name == 'key':
            return self._to_string(value)
        elif node.type_name == 'vector':
            return self._to_vector(value)
        elif node.type_name == 'rotation':
            return self._to_rotation(value)
        elif node.type_name == 'list':
            return self._to_list(value)
        else:
            return value
    
    def visit_LSLMemberAccess(self, node: LSLMemberAccess) -> Any:
        """Evaluate member access (e.g., vector.x)"""
        obj = self.visit(node.object)
        
        # Handle vector component access
        if isinstance(obj, list) and len(obj) == 3:
            if node.member == 'x':
                return obj[0]
            elif node.member == 'y':
                return obj[1]
            elif node.member == 'z':
                return obj[2]
        
        # Handle rotation component access
        if isinstance(obj, list) and len(obj) == 4:
            if node.member == 'x':
                return obj[0]
            elif node.member == 'y':
                return obj[1]
            elif node.member == 'z':
                return obj[2]
            elif node.member == 's':
                return obj[3]
        
        return 0.0
    
    # Helper methods for type conversion and operations
    
    def _add_values(self, left: Any, right: Any) -> Any:
        """Add two values with LSL semantics"""
        if isinstance(left, str) or isinstance(right, str):
            return self._to_string(left) + self._to_string(right)
        elif isinstance(left, list) and isinstance(right, list):
            return left + right  # List concatenation
        elif isinstance(left, list) and len(left) == 3 and isinstance(right, list) and len(right) == 3:
            return [left[0] + right[0], left[1] + right[1], left[2] + right[2]]  # Vector addition
        else:
            return self._to_number(left) + self._to_number(right)
    
    def _subtract_values(self, left: Any, right: Any) -> Any:
        """Subtract two values with LSL semantics"""
        if isinstance(left, list) and len(left) == 3 and isinstance(right, list) and len(right) == 3:
            return [left[0] - right[0], left[1] - right[1], left[2] - right[2]]  # Vector subtraction
        else:
            return self._to_number(left) - self._to_number(right)
    
    def _multiply_values(self, left: Any, right: Any) -> Any:
        """Multiply two values with LSL semantics"""
        if isinstance(left, list) and len(left) == 3 and isinstance(right, (int, float)):
            return [left[0] * right, left[1] * right, left[2] * right]  # Vector scaling
        elif isinstance(left, (int, float)) and isinstance(right, list) and len(right) == 3:
            return [left * right[0], left * right[1], left * right[2]]  # Vector scaling
        else:
            return self._to_number(left) * self._to_number(right)
    
    def _divide_values(self, left: Any, right: Any) -> Any:
        """Divide two values with LSL semantics"""
        right_num = self._to_number(right)
        if right_num == 0:
            return 0
        
        if isinstance(left, list) and len(left) == 3:
            return [left[0] / right_num, left[1] / right_num, left[2] / right_num]  # Vector division
        else:
            return self._to_number(left) / right_num
    
    def _modulo_values(self, left: Any, right: Any) -> Any:
        """Modulo operation with LSL semantics"""
        right_num = self._to_number(right)
        if right_num == 0:
            return 0
        return self._to_number(left) % right_num
    
    def _equals_values(self, left: Any, right: Any) -> bool:
        """Compare two values for equality with LSL semantics"""
        return left == right
    
    def _less_than_values(self, left: Any, right: Any) -> bool:
        """Compare two values with LSL semantics"""
        try:
            return self._to_number(left) < self._to_number(right)
        except:
            return False
    
    def _greater_than_values(self, left: Any, right: Any) -> bool:
        """Compare two values with LSL semantics"""
        try:
            return self._to_number(left) > self._to_number(right)
        except:
            return False
    
    def _less_equal_values(self, left: Any, right: Any) -> bool:
        """Compare two values with LSL semantics"""
        try:
            return self._to_number(left) <= self._to_number(right)
        except:
            return False
    
    def _greater_equal_values(self, left: Any, right: Any) -> bool:
        """Compare two values with LSL semantics"""
        try:
            return self._to_number(left) >= self._to_number(right)
        except:
            return False
    
    def _logical_and_values(self, left: Any, right: Any) -> bool:
        """Logical AND with LSL semantics"""
        return self._is_truthy(left) and self._is_truthy(right)
    
    def _logical_or_values(self, left: Any, right: Any) -> bool:
        """Logical OR with LSL semantics"""
        return self._is_truthy(left) or self._is_truthy(right)
    
    def _bitwise_and_values(self, left: Any, right: Any) -> int:
        """Bitwise AND with LSL semantics"""
        return self._to_integer(left) & self._to_integer(right)
    
    def _bitwise_or_values(self, left: Any, right: Any) -> int:
        """Bitwise OR with LSL semantics"""
        return self._to_integer(left) | self._to_integer(right)
    
    def _bitwise_xor_values(self, left: Any, right: Any) -> int:
        """Bitwise XOR with LSL semantics"""
        return self._to_integer(left) ^ self._to_integer(right)
    
    def _shift_left_values(self, left: Any, right: Any) -> int:
        """Shift left with LSL semantics"""
        return self._to_integer(left) << self._to_integer(right)
    
    def _shift_right_values(self, left: Any, right: Any) -> int:
        """Shift right with LSL semantics"""
        return self._to_integer(left) >> self._to_integer(right)
    
    def _is_truthy(self, value: Any) -> bool:
        """Check if value is truthy in LSL"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return value != ""
        elif isinstance(value, list):
            return len(value) > 0
        else:
            return bool(value)
    
    def _to_number(self, value: Any) -> float:
        """Convert value to number (float)"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        elif isinstance(value, bool):
            return 1.0 if value else 0.0
        else:
            return 0.0
    
    def _to_integer(self, value: Any) -> int:
        """Convert value to integer"""
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return int(value)
        elif isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return 0
        elif isinstance(value, bool):
            return 1 if value else 0
        else:
            return 0
    
    def _to_float(self, value: Any) -> float:
        """Convert value to float"""
        return self._to_number(value)
    
    def _to_string(self, value: Any) -> str:
        """Convert value to string with LSL semantics"""
        if isinstance(value, str):
            return value
        elif isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, list) and len(value) == 3:
            return f"<{value[0]}, {value[1]}, {value[2]}>"
        elif isinstance(value, list) and len(value) == 4:
            return f"<{value[0]}, {value[1]}, {value[2]}, {value[3]}>"
        else:
            return str(value)
    
    def _to_vector(self, value: Any) -> List[float]:
        """Convert value to vector"""
        if isinstance(value, list) and len(value) == 3:
            return [self._to_float(v) for v in value]
        elif isinstance(value, str):
            # Parse vector string like "<1.0, 2.0, 3.0>"
            match = re.match(r'<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>', value)
            if match:
                return [self._to_float(match.group(1)), 
                       self._to_float(match.group(2)), 
                       self._to_float(match.group(3))]
        return [0.0, 0.0, 0.0]
    
    def _to_rotation(self, value: Any) -> List[float]:
        """Convert value to rotation"""
        if isinstance(value, list) and len(value) == 4:
            return [self._to_float(v) for v in value]
        elif isinstance(value, str):
            # Parse rotation string like "<1.0, 2.0, 3.0, 4.0>"
            match = re.match(r'<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>', value)
            if match:
                return [self._to_float(match.group(1)), 
                       self._to_float(match.group(2)), 
                       self._to_float(match.group(3)), 
                       self._to_float(match.group(4))]
        return [0.0, 0.0, 0.0, 1.0]
    
    def _to_list(self, value: Any) -> List[Any]:
        """Convert value to list"""
        if isinstance(value, list):
            return value
        else:
            return [value]
    
    def _get_default_value(self, type_name: str) -> Any:
        """Get default value for LSL type"""
        defaults = {
            'integer': 0,
            'float': 0.0,
            'string': "",
            'key': "00000000-0000-0000-0000-000000000000",
            'vector': [0.0, 0.0, 0.0],
            'rotation': [0.0, 0.0, 0.0, 1.0],
            'list': []
        }
        return defaults.get(type_name, 0)