#!/usr/bin/env python3
"""
LSL ANTLR4 Parser - Simplified production implementation
Replaces pyparsing with visitor pattern for better performance
"""

import re
from typing import Any, Dict, List, Optional, Union

class LSLASTNode:
    """Base class for all AST nodes"""
    def __init__(self, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column

class LSLScript(LSLASTNode):
    """Root AST node"""
    def __init__(self, globals: List['LSLGlobalDeclaration'] = None, 
                 functions: List['LSLFunctionDefinition'] = None, 
                 states: List['LSLState'] = None):
        super().__init__()
        self.globals = globals or []
        self.functions = functions or []
        self.states = states or []

class LSLGlobalDeclaration(LSLASTNode):
    def __init__(self, type_name: str, name: str, init_value: Optional['LSLExpression'] = None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.init_value = init_value

class LSLFunctionDefinition(LSLASTNode):
    def __init__(self, return_type: str, name: str, 
                 parameters: List['LSLParameter'], body: List['LSLStatement']):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

class LSLParameter(LSLASTNode):
    def __init__(self, type_name: str, name: str):
        super().__init__()
        self.type_name = type_name
        self.name = name

class LSLState(LSLASTNode):
    def __init__(self, name: str, events: List['LSLEventHandler']):
        super().__init__()
        self.name = name
        self.events = events

class LSLEventHandler(LSLASTNode):
    def __init__(self, event_name: str, parameters: List['LSLParameter'], 
                 body: List['LSLStatement']):
        super().__init__()
        self.event_name = event_name
        self.parameters = parameters
        self.body = body

class LSLStatement(LSLASTNode):
    pass

class LSLExpressionStatement(LSLStatement):
    def __init__(self, expression: 'LSLExpression'):
        super().__init__()
        self.expression = expression

class LSLVariableDeclaration(LSLStatement):
    def __init__(self, type_name: str, name: str, init_value: Optional['LSLExpression'] = None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.init_value = init_value

class LSLAssignmentStatement(LSLStatement):
    def __init__(self, lvalue: 'LSLExpression', operator: str, rvalue: 'LSLExpression'):
        super().__init__()
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

class LSLIfStatement(LSLStatement):
    def __init__(self, condition: 'LSLExpression', then_stmt: 'LSLStatement', 
                 else_stmt: Optional['LSLStatement'] = None):
        super().__init__()
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class LSLWhileStatement(LSLStatement):
    def __init__(self, condition: 'LSLExpression', body: 'LSLStatement'):
        super().__init__()
        self.condition = condition
        self.body = body

class LSLForStatement(LSLStatement):
    def __init__(self, init: Optional['LSLStatement'], condition: Optional['LSLExpression'],
                 increment: Optional['LSLExpression'], body: 'LSLStatement'):
        super().__init__()
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

class LSLReturnStatement(LSLStatement):
    def __init__(self, value: Optional['LSLExpression'] = None):
        super().__init__()
        self.value = value

class LSLStateChangeStatement(LSLStatement):
    def __init__(self, state_name: str):
        super().__init__()
        self.state_name = state_name

class LSLCompoundStatement(LSLStatement):
    def __init__(self, statements: List['LSLStatement']):
        super().__init__()
        self.statements = statements

class LSLExpression(LSLASTNode):
    pass

class LSLBinaryOp(LSLExpression):
    def __init__(self, left: 'LSLExpression', operator: str, right: 'LSLExpression'):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

class LSLUnaryOp(LSLExpression):
    def __init__(self, operator: str, operand: 'LSLExpression'):
        super().__init__()
        self.operator = operator
        self.operand = operand

class LSLFunctionCall(LSLExpression):
    def __init__(self, function_name: str, arguments: List['LSLExpression']):
        super().__init__()
        self.function_name = function_name
        self.arguments = arguments

class LSLIdentifier(LSLExpression):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class LSLMemberAccess(LSLExpression):
    def __init__(self, object: 'LSLExpression', member: str):
        super().__init__()
        self.object = object
        self.member = member

class LSLLiteral(LSLExpression):
    def __init__(self, value: Any, type_name: str):
        super().__init__()
        self.value = value
        self.type_name = type_name

class LSLVectorLiteral(LSLExpression):
    def __init__(self, x: 'LSLExpression', y: 'LSLExpression', z: 'LSLExpression'):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

class LSLRotationLiteral(LSLExpression):
    def __init__(self, x: 'LSLExpression', y: 'LSLExpression', 
                 z: 'LSLExpression', s: 'LSLExpression'):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.s = s

class LSLListLiteral(LSLExpression):
    def __init__(self, elements: List['LSLExpression']):
        super().__init__()
        self.elements = elements

class LSLTypeCast(LSLExpression):
    def __init__(self, type_name: str, expression: 'LSLExpression'):
        super().__init__()
        self.type_name = type_name
        self.expression = expression

class LSLParseError(Exception):
    """LSL parse error with location info"""
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}: {message}" if line else message)

class LSLParser:
    """Simplified LSL parser with ANTLR4-style visitor pattern"""
    
    def __init__(self):
        self.precedence = {
            '||': 1, '&&': 2, '|': 3, '^': 4, '&': 5,
            '==': 6, '!=': 6, '<': 7, '>': 7, '<=': 7, '>=': 7,
            '<<': 8, '>>': 8, '+': 9, '-': 9, '*': 10, '/': 10, '%': 10,
            '.': 15
        }
    
    def parse(self, script_content: str) -> LSLScript:
        """Parse LSL script content into AST"""
        content = self._clean_content(script_content)
        
        globals = self._parse_globals(content)
        functions = self._parse_functions(content)
        states = self._parse_states(content)
        
        return LSLScript(globals, functions, states)
    
    def _clean_content(self, content: str) -> str:
        """Remove comments and normalize whitespace"""
        # Remove comments
        content = re.sub(r'//[^\r\n]*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\{', ' { ', content)
        content = re.sub(r'\}', ' } ', content)
        return content.strip()
    
    def _parse_globals(self, content: str) -> List[LSLGlobalDeclaration]:
        """Parse global variables"""
        globals = []
        
        # Remove function/state blocks to find globals
        content_no_blocks = self._remove_blocks(content)
        
        pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)\s*(?:=\s*([^;]+))?\s*;'
        for match in re.finditer(pattern, content_no_blocks):
            type_name = match.group(1)
            name = match.group(2)
            init_str = match.group(3)
            
            init_value = None
            if init_str:
                init_value = self._parse_expression(init_str.strip())
            
            globals.append(LSLGlobalDeclaration(type_name, name, init_value))
        
        return globals
    
    def _remove_blocks(self, content: str) -> str:
        """Remove content inside braces"""
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
    
    def _parse_functions(self, content: str) -> List[LSLFunctionDefinition]:
        """Parse user-defined functions"""
        functions = []
        
        # Skip built-in LSL functions and event handlers
        pattern = r'\b(integer|float|string|key|vector|rotation|list|void)\s+(\w+)\s*\(([^)]*)\)\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})'
        
        for match in re.finditer(pattern, content):
            return_type = match.group(1)
            name = match.group(2)
            params_str = match.group(3)
            body_str = match.group(4)
            
            # Skip LSL event handlers
            if name in ['state_entry', 'touch_start', 'timer', 'http_response']:
                continue
            
            parameters = self._parse_parameters(params_str)
            body = self._parse_statements(body_str[1:-1])  # Remove braces
            
            functions.append(LSLFunctionDefinition(return_type, name, parameters, body))
        
        return functions
    
    def _parse_states(self, content: str) -> List[LSLState]:
        """Parse state definitions"""
        states = []
        
        # Find state blocks
        pattern = r'\b(default|state\s+\w+)\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})'
        
        for match in re.finditer(pattern, content):
            state_name = match.group(1).strip()
            if state_name.startswith('state '):
                state_name = state_name.split()[-1]
            
            state_body = match.group(2)[1:-1]  # Remove braces
            events = self._parse_events(state_body)
            
            states.append(LSLState(state_name, events))
        
        return states
    
    def _parse_events(self, state_body: str) -> List[LSLEventHandler]:
        """Parse event handlers within state"""
        events = []
        
        # Known LSL events
        event_names = [
            'state_entry', 'touch_start', 'touch_end', 'timer', 'collision_start',
            'http_response', 'listen', 'sensor', 'no_sensor', 'changed'
        ]
        
        for event_name in event_names:
            pattern = rf'\b{event_name}\s*\(([^)]*)\)\s*(\{{[^}}]*(?:\{{[^}}]*\}}[^}}]*)*\}})'
            match = re.search(pattern, state_body)
            
            if match:
                params_str = match.group(1)
                event_body = match.group(2)[1:-1]  # Remove braces
                
                parameters = self._parse_parameters(params_str)
                body = self._parse_statements(event_body)
                
                events.append(LSLEventHandler(event_name, parameters, body))
        
        return events
    
    def _parse_parameters(self, params_str: str) -> List[LSLParameter]:
        """Parse function parameters"""
        parameters = []
        
        if params_str.strip():
            pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)'
            for match in re.finditer(pattern, params_str):
                type_name = match.group(1)
                name = match.group(2)
                parameters.append(LSLParameter(type_name, name))
        
        return parameters
    
    def _parse_statements(self, body_str: str) -> List[LSLStatement]:
        """Parse statements in body"""
        statements = []
        
        # Split by semicolons, respecting braces
        stmt_parts = self._split_statements(body_str)
        
        for part in stmt_parts:
            part = part.strip()
            if not part:
                continue
            
            stmt = self._parse_statement(part)
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _split_statements(self, body_str: str) -> List[str]:
        """Split body into statements"""
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
    
    def _parse_statement(self, stmt_str: str) -> Optional[LSLStatement]:
        """Parse single statement"""
        stmt_str = stmt_str.strip()
        
        # Variable declarations
        var_pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)(?:\s*=\s*(.+))?'
        var_match = re.match(var_pattern, stmt_str)
        if var_match:
            type_name = var_match.group(1)
            name = var_match.group(2)
            init_str = var_match.group(3)
            
            init_value = None
            if init_str:
                init_value = self._parse_expression(init_str.strip())
            
            return LSLVariableDeclaration(type_name, name, init_value)
        
        # Assignment
        assign_pattern = r'(\w+)\s*=\s*(.+)'
        assign_match = re.match(assign_pattern, stmt_str)
        if assign_match:
            var_name = assign_match.group(1)
            value_str = assign_match.group(2)
            
            lvalue = LSLIdentifier(var_name)
            rvalue = self._parse_expression(value_str.strip())
            return LSLAssignmentStatement(lvalue, '=', rvalue)
        
        # If statement
        if_pattern = r'if\s*\(([^)]+)\)\s*\{([^}]*)\}(?:\s*else\s*\{([^}]*)\})?'
        if_match = re.match(if_pattern, stmt_str)
        if if_match:
            condition = self._parse_expression(if_match.group(1))
            then_body = self._parse_statements(if_match.group(2))
            then_stmt = LSLCompoundStatement(then_body)
            
            else_stmt = None
            if if_match.group(3):
                else_body = self._parse_statements(if_match.group(3))
                else_stmt = LSLCompoundStatement(else_body)
            
            return LSLIfStatement(condition, then_stmt, else_stmt)
        
        # For loop
        for_pattern = r'for\s*\(([^;]*);([^;]*);([^)]*)\)\s*\{([^}]*)\}'
        for_match = re.match(for_pattern, stmt_str)
        if for_match:
            init_str = for_match.group(1).strip()
            condition_str = for_match.group(2).strip()
            increment_str = for_match.group(3).strip()
            body_str = for_match.group(4)
            
            init_stmt = None
            if init_str:
                init_stmt = self._parse_statement(init_str)
            
            condition = None
            if condition_str:
                condition = self._parse_expression(condition_str)
            
            increment = None
            if increment_str:
                increment = self._parse_expression(increment_str)
            
            body = self._parse_statements(body_str)
            body_stmt = LSLCompoundStatement(body)
            
            return LSLForStatement(init_stmt, condition, increment, body_stmt)
        
        # Return statement
        if stmt_str.startswith('return'):
            return_pattern = r'return\s*(.+)?'
            return_match = re.match(return_pattern, stmt_str)
            if return_match:
                value_str = return_match.group(1)
                value = None
                if value_str and value_str.strip():
                    value = self._parse_expression(value_str.strip())
                return LSLReturnStatement(value)
        
        # Function call (expression statement)
        if re.match(r'\w+\s*\(', stmt_str):
            expr = self._parse_expression(stmt_str)
            return LSLExpressionStatement(expr)
        
        return None
    
    def _parse_expression(self, expr_str: str) -> LSLExpression:
        """Parse expression with proper precedence"""
        expr_str = expr_str.strip()
        
        # Vector literals
        vector_pattern = r'^<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>$'
        vector_match = re.match(vector_pattern, expr_str)
        if vector_match:
            x = self._parse_expression(vector_match.group(1).strip())
            y = self._parse_expression(vector_match.group(2).strip())
            z = self._parse_expression(vector_match.group(3).strip())
            return LSLVectorLiteral(x, y, z)
        
        # Rotation literals
        rotation_pattern = r'^<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>$'
        rotation_match = re.match(rotation_pattern, expr_str)
        if rotation_match:
            x = self._parse_expression(rotation_match.group(1).strip())
            y = self._parse_expression(rotation_match.group(2).strip())
            z = self._parse_expression(rotation_match.group(3).strip())
            s = self._parse_expression(rotation_match.group(4).strip())
            return LSLRotationLiteral(x, y, z, s)
        
        # List literals
        if expr_str.startswith('[') and expr_str.endswith(']'):
            list_content = expr_str[1:-1].strip()
            elements = []
            if list_content:
                elem_parts = self._split_arguments(list_content)
                elements = [self._parse_expression(part.strip()) for part in elem_parts]
            return LSLListLiteral(elements)
        
        # Type casting
        cast_pattern = r'^\((integer|float|string|key|vector|rotation|list)\)\s*(.+)$'
        cast_match = re.match(cast_pattern, expr_str)
        if cast_match:
            type_name = cast_match.group(1)
            expr = cast_match.group(2)
            return LSLTypeCast(type_name, self._parse_expression(expr))
        
        # Function calls
        func_pattern = r'^(\w+)\s*\(([^)]*)\)$'
        func_match = re.match(func_pattern, expr_str)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            
            arguments = []
            if args_str.strip():
                arg_parts = self._split_arguments(args_str)
                arguments = [self._parse_expression(part.strip()) for part in arg_parts]
            
            return LSLFunctionCall(func_name, arguments)
        
        # Binary operations
        return self._parse_binary_expression(expr_str)
    
    def _parse_binary_expression(self, expr_str: str) -> LSLExpression:
        """Parse binary expressions with precedence"""
        best_op = None
        best_pos = -1
        best_precedence = float('inf')
        
        paren_level = 0
        in_string = False
        
        # Scan right to left for lowest precedence operator
        for i in range(len(expr_str) - 1, -1, -1):
            char = expr_str[i]
            
            if char == '"' and (i == 0 or expr_str[i-1] != '\\'):
                in_string = not in_string
                continue
            
            if in_string:
                continue
            
            if char == ')':
                paren_level += 1
            elif char == '(':
                paren_level -= 1
            elif paren_level == 0:
                for op in sorted(self.precedence.keys(), key=len, reverse=True):
                    if i >= len(op) - 1 and expr_str[i-len(op)+1:i+1] == op:
                        precedence = self.precedence[op]
                        if precedence <= best_precedence:
                            best_op = op
                            best_pos = i - len(op) + 1
                            best_precedence = precedence
                        break
        
        if best_op and best_pos > 0 and best_pos + len(best_op) < len(expr_str):
            left_str = expr_str[:best_pos].strip()
            right_str = expr_str[best_pos + len(best_op):].strip()
            
            if best_op == '.':
                left = self._parse_expression(left_str)
                return LSLMemberAccess(left, right_str)
            else:
                left = self._parse_expression(left_str)
                right = self._parse_expression(right_str)
                return LSLBinaryOp(left, best_op, right)
        
        return self._parse_atomic_expression(expr_str)
    
    def _parse_atomic_expression(self, expr_str: str) -> LSLExpression:
        """Parse atomic expressions"""
        expr_str = expr_str.strip()
        
        # Parenthesized
        if expr_str.startswith('(') and expr_str.endswith(')'):
            return self._parse_expression(expr_str[1:-1])
        
        # String literals
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return LSLLiteral(expr_str[1:-1], 'string')
        
        # Numbers
        if expr_str.isdigit() or (expr_str.startswith('-') and expr_str[1:].isdigit()):
            return LSLLiteral(int(expr_str), 'integer')
        
        if '.' in expr_str:
            try:
                return LSLLiteral(float(expr_str), 'float')
            except ValueError:
                pass
        
        # LSL constants
        constants = {
            'TRUE': (1, 'integer'),
            'FALSE': (0, 'integer'),
            'NULL_KEY': ("00000000-0000-0000-0000-000000000000", 'key'),
            'PI': (3.14159265359, 'float'),
            'ZERO_VECTOR': ((0.0, 0.0, 0.0), 'vector'),
        }
        
        if expr_str in constants:
            value, type_name = constants[expr_str]
            return LSLLiteral(value, type_name)
        
        # Identifiers
        if re.match(r'^[a-zA-Z_]\w*$', expr_str):
            return LSLIdentifier(expr_str)
        
        return LSLLiteral(expr_str, 'unknown')
    
    def _split_arguments(self, args_str: str) -> List[str]:
        """Split function arguments"""
        args = []
        current = ""
        paren_level = 0
        in_string = False
        
        for char in args_str:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                elif char == ',' and paren_level == 0:
                    if current.strip():
                        args.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args

class LSLVisitor:
    """Visitor for LSL AST nodes"""
    
    def visit(self, node: LSLASTNode) -> Any:
        """Visit an AST node"""
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node: LSLASTNode) -> Any:
        """Default visitor for unknown nodes"""
        return None

class LSLEvaluator(LSLVisitor):
    """Evaluator for LSL AST using visitor pattern"""
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def visit_LSLLiteral(self, node: LSLLiteral) -> Any:
        return node.value
    
    def visit_LSLIdentifier(self, node: LSLIdentifier) -> Any:
        # Look up variable in simulator
        value = self.simulator.call_stack.find_variable(node.name)
        return value if value is not None else 0
    
    def visit_LSLBinaryOp(self, node: LSLBinaryOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        try:
            if node.operator == '+':
                return left + right
            elif node.operator == '-':
                return left - right
            elif node.operator == '*':
                return left * right
            elif node.operator == '/':
                return left / right if right != 0 else 0
            elif node.operator == '==':
                return left == right
            elif node.operator == '!=':
                return left != right
            elif node.operator == '<':
                return left < right
            elif node.operator == '>':
                return left > right
            elif node.operator == '&&':
                return bool(left) and bool(right)
            elif node.operator == '||':
                return bool(left) or bool(right)
            else:
                return 0
        except:
            return 0
    
    def visit_LSLFunctionCall(self, node: LSLFunctionCall) -> Any:
        args = [self.visit(arg) for arg in node.arguments]
        return self.simulator.call_function(node.function_name, args)
    
    def visit_LSLVectorLiteral(self, node: LSLVectorLiteral) -> tuple:
        x = self.visit(node.x)
        y = self.visit(node.y)
        z = self.visit(node.z)
        return (float(x), float(y), float(z))
    
    def visit_LSLListLiteral(self, node: LSLListLiteral) -> list:
        return [self.visit(elem) for elem in node.elements]
    
    def visit_LSLTypeCast(self, node: LSLTypeCast) -> Any:
        value = self.visit(node.expression)
        
        if node.type_name == 'string':
            return str(value)
        elif node.type_name == 'integer':
            return int(value) if isinstance(value, (int, float)) else 0
        elif node.type_name == 'float':
            return float(value) if isinstance(value, (int, float)) else 0.0
        
        return value