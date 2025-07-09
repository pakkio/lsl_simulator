"""
LSL Expression Evaluator - Modular implementation with Visitor Pattern
Replaces the monolithic _evaluate_tree function with a clean, extensible architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Union, List, Dict, Optional


class ExpressionNode(ABC):
    """Base class for all expression nodes in the AST."""
    pass


class LiteralNode(ExpressionNode):
    """Represents literal values (strings, numbers, etc.)."""
    def __init__(self, value: Any):
        self.value = value


class VariableNode(ExpressionNode):
    """Represents variable references."""
    def __init__(self, name: str):
        self.name = name


class ComponentAccessNode(ExpressionNode):
    """Represents component access like variable.x or vector.z."""
    def __init__(self, variable: str, component: str):
        self.variable = variable
        self.component = component


class UnaryOperatorNode(ExpressionNode):
    """Represents unary operations like !expression."""
    def __init__(self, operator: str, operand: ExpressionNode):
        self.operator = operator
        self.operand = operand


class BinaryOperatorNode(ExpressionNode):
    """Represents binary operations like a + b."""
    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode):
        self.left = left
        self.operator = operator
        self.right = right


class FunctionCallNode(ExpressionNode):
    """Represents function calls like llSay(0, "hello")."""
    def __init__(self, name: str, args: List[ExpressionNode]):
        self.name = name
        self.args = args


class TypeCastNode(ExpressionNode):
    """Represents type casting like (string)variable."""
    def __init__(self, target_type: str, expression: ExpressionNode):
        self.target_type = target_type
        self.expression = expression


class ListLiteralNode(ExpressionNode):
    """Represents list literals like [1, 2, 3]."""
    def __init__(self, elements: List[ExpressionNode]):
        self.elements = elements


class ExpressionVisitor(ABC):
    """Abstract base class for expression visitors."""
    
    @abstractmethod
    def visit_literal(self, node: LiteralNode) -> Any:
        pass
    
    @abstractmethod
    def visit_variable(self, node: VariableNode) -> Any:
        pass
    
    @abstractmethod
    def visit_component_access(self, node: ComponentAccessNode) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_operator(self, node: UnaryOperatorNode) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_operator(self, node: BinaryOperatorNode) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        pass
    
    @abstractmethod
    def visit_type_cast(self, node: TypeCastNode) -> Any:
        pass
    
    @abstractmethod
    def visit_list_literal(self, node: ListLiteralNode) -> Any:
        pass


class ExpressionEvaluator(ExpressionVisitor):
    """Concrete evaluator that executes expressions using the visitor pattern."""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.call_stack = simulator.call_stack
    
    def evaluate(self, node: ExpressionNode) -> Any:
        """Main entry point for expression evaluation."""
        return self._dispatch(node)
    
    def _dispatch(self, node: ExpressionNode) -> Any:
        """Dispatch to appropriate visitor method based on node type."""
        if isinstance(node, LiteralNode):
            return self.visit_literal(node)
        elif isinstance(node, VariableNode):
            return self.visit_variable(node)
        elif isinstance(node, ComponentAccessNode):
            return self.visit_component_access(node)
        elif isinstance(node, UnaryOperatorNode):
            return self.visit_unary_operator(node)
        elif isinstance(node, BinaryOperatorNode):
            return self.visit_binary_operator(node)
        elif isinstance(node, FunctionCallNode):
            return self.visit_function_call(node)
        elif isinstance(node, TypeCastNode):
            return self.visit_type_cast(node)
        elif isinstance(node, ListLiteralNode):
            return self.visit_list_literal(node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")
    
    def visit_literal(self, node: LiteralNode) -> Any:
        """Handle literal values."""
        return node.value
    
    def visit_variable(self, node: VariableNode) -> Any:
        """Handle variable lookups."""
        val = self.call_stack.find_variable(node.name)
        if val is not None:
            return val
        # If not found, return as string literal (LSL behavior)
        return node.name
    
    def visit_component_access(self, node: ComponentAccessNode) -> Any:
        """Handle component access like variable.x."""
        var_val = self.call_stack.find_variable(node.variable)
        if var_val is not None:
            return self.simulator._get_component(var_val, node.component)
        return f"{node.variable}.{node.component}"
    
    def visit_unary_operator(self, node: UnaryOperatorNode) -> Any:
        """Handle unary operations."""
        operand = self._dispatch(node.operand)
        
        if node.operator == '!':
            return not operand
        elif node.operator == '-':
            return -operand
        elif node.operator == '+':
            return +operand
        else:
            raise ValueError(f"Unknown unary operator: {node.operator}")
    
    def visit_binary_operator(self, node: BinaryOperatorNode) -> Any:
        """Handle binary operations."""
        left = self._dispatch(node.left)
        right = self._dispatch(node.right)
        
        op = node.operator
        
        # Arithmetic operators
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        elif op == '%':
            return left % right
        
        # Comparison operators
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right
        
        # Logical operators
        elif op == '&&':
            return left and right
        elif op == '||':
            return left or right
        
        # Bitwise operators
        elif op == '&':
            return left & right
        elif op == '|':
            return left | right
        elif op == '^':
            return left ^ right
        elif op == '<<':
            return left << right
        elif op == '>>':
            return left >> right
        
        else:
            raise ValueError(f"Unknown binary operator: {op}")
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        """Handle function calls."""
        # Evaluate arguments
        evaluated_args = [self._dispatch(arg) for arg in node.args]
        
        # Debug output for specific functions
        if node.name == "llHTTPRequest":
            print(f"[DEBUG] llHTTPRequest evaluated args: {evaluated_args}")
        
        # Try API functions
        api_func = getattr(self.simulator, f"api_{node.name}", None)
        if api_func:
            return api_func(*evaluated_args)
        
        # Try user-defined functions
        if node.name in self.simulator.user_functions:
            return self.simulator._call_user_function(node.name, evaluated_args)
        
        raise ValueError(f"Unknown function: {node.name}")
    
    def visit_type_cast(self, node: TypeCastNode) -> Any:
        """Handle type casting."""
        value = self._dispatch(node.expression)
        
        if node.target_type == 'string':
            return str(value)
        elif node.target_type == 'integer':
            return int(value)
        elif node.target_type == 'float':
            return float(value)
        elif node.target_type == 'key':
            return value  # Keys are treated as strings in LSL
        else:
            raise ValueError(f"Unknown cast type: {node.target_type}")
    
    def visit_list_literal(self, node: ListLiteralNode) -> Any:
        """Handle list literals."""
        return [self._dispatch(element) for element in node.elements]


class TreeToNodeConverter:
    """Converts pyparsing tree structures to ExpressionNode objects."""
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def convert(self, parsed_tree) -> ExpressionNode:
        """Convert a pyparsing tree to an ExpressionNode."""
        return self._convert_tree(parsed_tree)
    
    def _convert_tree(self, tree) -> ExpressionNode:
        """Internal conversion method."""
        # Handle simple values
        if not isinstance(tree, list) and not hasattr(tree, 'asList'):
            if isinstance(tree, str):
                # Check if it's a component access
                if '.' in tree and not self._is_url_or_ip(tree):
                    var_name, component = tree.split('.', 1)
                    # Only treat as component access if variable exists
                    if self.simulator.call_stack.find_variable(var_name) is not None:
                        return ComponentAccessNode(var_name, component)
                # Return as variable reference
                return VariableNode(tree)
            else:
                # Literal value
                return LiteralNode(tree)
        
        # Convert to list format
        if hasattr(tree, 'asList'):
            items = tree.asList()
        else:
            items = tree
        
        # Handle nested structures
        if isinstance(items, list) and len(items) == 1 and isinstance(items[0], list):
            return ListLiteralNode([self._convert_tree(item) for item in items[0]])
        
        # Handle vector/rotation literals
        if isinstance(items, list) and len(items) in [3, 4]:
            if all(isinstance(item, (int, float)) for item in items):
                return ListLiteralNode([LiteralNode(item) for item in items])
        
        # Handle unary operators
        if len(items) == 2 and items[0] in ['!', '-', '+']:
            return UnaryOperatorNode(items[0], self._convert_tree(items[1]))
        
        # Handle type casting
        if len(items) == 2 and items[0] in ["integer", "string", "float", "key"]:
            return TypeCastNode(items[0], self._convert_tree(items[1]))
        
        # Handle function calls
        if isinstance(items, list) and len(items) >= 1 and isinstance(items[0], str):
            func_name = items[0]
            if (func_name.startswith('ll') or func_name.startswith('os') or 
                func_name in self.simulator.user_functions):
                args = [self._convert_tree(arg) for arg in items[1:]]
                return FunctionCallNode(func_name, args)
        
        # Handle binary operators
        if len(items) >= 3 and len(items) % 2 == 1:
            if self._is_binary_expression(items):
                return self._build_binary_expression(items)
        
        # Default: treat as list literal
        return ListLiteralNode([self._convert_tree(item) for item in items])
    
    def _is_url_or_ip(self, text: str) -> bool:
        """Check if text is a URL or IP address."""
        return ('://' in text or text.startswith('http') or 
                text.replace('.', '').replace(':', '').isdigit())
    
    def _is_binary_expression(self, items: List) -> bool:
        """Check if items represent a binary expression."""
        operators = ['+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '&', '|', '^', '<<', '>>']
        for i in range(1, len(items), 2):
            if i >= len(items) or not isinstance(items[i], str) or items[i] not in operators:
                return False
        return True
    
    def _build_binary_expression(self, items: List) -> ExpressionNode:
        """Build a binary expression tree from items."""
        left = self._convert_tree(items[0])
        
        for i in range(1, len(items), 2):
            if i + 1 >= len(items):
                break
            operator = items[i]
            right = self._convert_tree(items[i + 1])
            left = BinaryOperatorNode(left, operator, right)
        
        return left