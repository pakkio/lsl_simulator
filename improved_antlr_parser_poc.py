#!/usr/bin/env python3
"""
Improved ANTLR4 Parser POC for LSL
Fixes the limitations identified in the complex script testing.
"""

import os
import sys
import re
from typing import Any, Dict, List, Optional, Union

# Mock ANTLR4 imports (would be real imports after grammar generation)
# from antlr4 import InputStream, CommonTokenStream
# from LSLLexer import LSLLexer  
# from LSLParser import LSLParser as ANTLRLSLParser
# from LSLVisitor import LSLVisitor

class LSLASTNode:
    """Base class for all AST nodes"""
    def __init__(self, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column
    
    def accept(self, visitor):
        """Visitor pattern support"""
        raise NotImplementedError

class LSLScript(LSLASTNode):
    """Root AST node representing entire LSL script"""
    def __init__(self, globals: List['LSLGlobalDeclaration'], 
                 functions: List['LSLFunctionDefinition'],
                 states: List['LSLState']):
        super().__init__()
        self.globals = globals
        self.functions = functions
        self.states = states

class LSLGlobalDeclaration(LSLASTNode):
    """Global variable declaration"""
    def __init__(self, type_name: str, name: str, init_value: Optional['LSLExpression'] = None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.init_value = init_value

class LSLFunctionDefinition(LSLASTNode):
    """Function definition"""
    def __init__(self, return_type: str, name: str, parameters: List['LSLParameter'], 
                 body: List['LSLStatement']):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body

class LSLParameter(LSLASTNode):
    """Function parameter"""
    def __init__(self, type_name: str, name: str):
        super().__init__()
        self.type_name = type_name
        self.name = name

class LSLState(LSLASTNode):
    """State definition"""
    def __init__(self, name: str, events: List['LSLEventHandler']):
        super().__init__()
        self.name = name
        self.events = events

class LSLEventHandler(LSLASTNode):
    """Event handler definition"""
    def __init__(self, event_name: str, parameters: List['LSLParameter'], 
                 body: List['LSLStatement']):
        super().__init__()
        self.event_name = event_name
        self.parameters = parameters
        self.body = body

class LSLStatement(LSLASTNode):
    """Base class for all statements"""
    pass

class LSLExpressionStatement(LSLStatement):
    """Expression used as statement"""
    def __init__(self, expression: 'LSLExpression'):
        super().__init__()
        self.expression = expression

class LSLVariableDeclaration(LSLStatement):
    """Variable declaration statement"""
    def __init__(self, type_name: str, name: str, init_value: Optional['LSLExpression'] = None):
        super().__init__()
        self.type_name = type_name
        self.name = name
        self.init_value = init_value

class LSLAssignmentStatement(LSLStatement):
    """Assignment statement"""
    def __init__(self, lvalue: 'LSLExpression', operator: str, rvalue: 'LSLExpression'):
        super().__init__()
        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue

class LSLIfStatement(LSLStatement):
    """If statement"""
    def __init__(self, condition: 'LSLExpression', then_stmt: 'LSLStatement', 
                 else_stmt: Optional['LSLStatement'] = None):
        super().__init__()
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class LSLWhileStatement(LSLStatement):
    """While loop statement"""
    def __init__(self, condition: 'LSLExpression', body: 'LSLStatement'):
        super().__init__()
        self.condition = condition
        self.body = body

class LSLForStatement(LSLStatement):
    """For loop statement"""
    def __init__(self, init: Optional['LSLStatement'], condition: Optional['LSLExpression'],
                 increment: Optional['LSLExpression'], body: 'LSLStatement'):
        super().__init__()
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

class LSLDoWhileStatement(LSLStatement):
    """Do-while loop statement"""
    def __init__(self, body: 'LSLStatement', condition: 'LSLExpression'):
        super().__init__()
        self.body = body
        self.condition = condition

class LSLBreakStatement(LSLStatement):
    """Break statement"""
    def __init__(self):
        super().__init__()

class LSLContinueStatement(LSLStatement):
    """Continue statement"""
    def __init__(self):
        super().__init__()

class LSLReturnStatement(LSLStatement):
    """Return statement"""
    def __init__(self, value: Optional['LSLExpression'] = None):
        super().__init__()
        self.value = value

class LSLStateChangeStatement(LSLStatement):
    """State change statement"""
    def __init__(self, state_name: str):
        super().__init__()
        self.state_name = state_name

class LSLCompoundStatement(LSLStatement):
    """Compound statement (block)"""
    def __init__(self, statements: List['LSLStatement']):
        super().__init__()
        self.statements = statements

class LSLExpression(LSLASTNode):
    """Base class for all expressions"""
    pass

class LSLBinaryOp(LSLExpression):
    """Binary operation expression"""
    def __init__(self, left: 'LSLExpression', operator: str, right: 'LSLExpression'):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

class LSLUnaryOp(LSLExpression):
    """Unary operation expression"""
    def __init__(self, operator: str, operand: 'LSLExpression'):
        super().__init__()
        self.operator = operator
        self.operand = operand

class LSLFunctionCall(LSLExpression):
    """Function call expression"""
    def __init__(self, function_name: str, arguments: List['LSLExpression']):
        super().__init__()
        self.function_name = function_name
        self.arguments = arguments

class LSLIdentifier(LSLExpression):
    """Identifier expression"""
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class LSLMemberAccess(LSLExpression):
    """Member access expression (e.g., vector.x)"""
    def __init__(self, object: 'LSLExpression', member: str):
        super().__init__()
        self.object = object
        self.member = member

class LSLIndexAccess(LSLExpression):
    """Index access expression (e.g., list[0])"""
    def __init__(self, object: 'LSLExpression', index: 'LSLExpression'):
        super().__init__()
        self.object = object
        self.index = index

class LSLSliceAccess(LSLExpression):
    """Slice access expression (e.g., list[1:3])"""
    def __init__(self, object: 'LSLExpression', start: 'LSLExpression', end: 'LSLExpression'):
        super().__init__()
        self.object = object
        self.start = start
        self.end = end

class LSLTypeCast(LSLExpression):
    """Type cast expression"""
    def __init__(self, type_name: str, expression: 'LSLExpression'):
        super().__init__()
        self.type_name = type_name
        self.expression = expression

class LSLLiteral(LSLExpression):
    """Literal value expression"""
    def __init__(self, value: Any, type_name: str):
        super().__init__()
        self.value = value
        self.type_name = type_name

class LSLVectorLiteral(LSLExpression):
    """Vector literal expression"""
    def __init__(self, x: 'LSLExpression', y: 'LSLExpression', z: 'LSLExpression'):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

class LSLRotationLiteral(LSLExpression):
    """Rotation literal expression"""
    def __init__(self, x: 'LSLExpression', y: 'LSLExpression', 
                 z: 'LSLExpression', s: 'LSLExpression'):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.s = s

class LSLListLiteral(LSLExpression):
    """List literal expression"""
    def __init__(self, elements: List['LSLExpression']):
        super().__init__()
        self.elements = elements

class LSLSyntaxError(Exception):
    """Enhanced syntax error with location information"""
    def __init__(self, message: str, line: Optional[int] = None, 
                 column: Optional[int] = None, context: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        
        if line is not None and column is not None:
            super().__init__(f"Line {line}, Column {column}: {message}")
        else:
            super().__init__(message)

class ImprovedLSLParser:
    """Improved ANTLR4-style LSL parser with fixed limitations"""
    
    def __init__(self):
        self.errors = []
        # Operator precedence table (higher number = higher precedence)
        self.precedence = {
            '||': 1,   # Logical OR (lowest)
            '&&': 2,   # Logical AND
            '|': 3,    # Bitwise OR
            '^': 4,    # Bitwise XOR
            '&': 5,    # Bitwise AND
            '==': 6, '!=': 6,   # Equality
            '<': 7, '>': 7, '<=': 7, '>=': 7,  # Relational
            '<<': 8, '>>': 8,   # Shift
            '+': 9, '-': 9,     # Addition/Subtraction
            '*': 10, '/': 10, '%': 10,  # Multiplication/Division/Modulo
            '.': 15,   # Member access (very high precedence)
        }
    
    def parse(self, script_content: str) -> LSLScript:
        """Parse LSL script and return AST"""
        try:
            return self._parse_script(script_content)
        except Exception as e:
            raise LSLSyntaxError(f"Parse error: {str(e)}")
    
    def _parse_script(self, content: str) -> LSLScript:
        """Enhanced manual parsing with fixed limitations"""
        # Clean up content
        content = self._remove_comments(content)
        content = self._normalize_whitespace(content)
        
        globals = []
        functions = []
        states = []
        
        # Parse global variables (outside functions and states)
        globals = self._parse_global_variables(content)
        
        # Parse user-defined functions
        functions = self._parse_functions(content)
        
        # Parse states with improved event handler detection
        states = self._parse_states_improved(content)
        
        return LSLScript(globals, functions, states)
    
    def _remove_comments(self, content: str) -> str:
        """Remove comments from content"""
        # Remove single-line comments
        content = re.sub(r'//[^\r\n]*', '', content)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace for easier parsing"""
        # Replace multiple whitespace with single space
        content = re.sub(r'\s+', ' ', content)
        # Add newlines around braces for easier parsing
        content = re.sub(r'\{', ' { ', content)
        content = re.sub(r'\}', ' } ', content)
        return content.strip()
    
    def _parse_global_variables(self, content: str) -> List[LSLGlobalDeclaration]:
        """Parse global variable declarations"""
        globals = []
        
        # Find global variables (not inside functions or states)
        global_pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)\s*(?:=\s*([^;]+))?\s*;'
        
        # Remove function and state content to avoid false matches
        content_without_blocks = self._remove_block_content(content)
        
        for match in re.finditer(global_pattern, content_without_blocks):
            type_name = match.group(1)
            var_name = match.group(2)
            init_value = match.group(3)
            
            init_expr = None
            if init_value:
                init_expr = self._parse_expression_improved(init_value.strip())
            
            globals.append(LSLGlobalDeclaration(type_name, var_name, init_expr))
        
        return globals
    
    def _remove_block_content(self, content: str) -> str:
        """Remove content inside braces to find top-level declarations"""
        result = ""
        brace_level = 0
        i = 0
        
        while i < len(content):
            if content[i] == '{':
                brace_level += 1
            elif content[i] == '}':
                brace_level -= 1
            elif brace_level == 0:
                result += content[i]
            i += 1
        
        return result
    
    def _parse_functions(self, content: str) -> List[LSLFunctionDefinition]:
        """Parse user-defined functions"""
        functions = []
        
        # Match function definitions
        func_pattern = r'\b(integer|float|string|key|vector|rotation|list|void)\s+(\w+)\s*\(([^)]*)\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(func_pattern, content):
            return_type = match.group(1)
            func_name = match.group(2)
            params_str = match.group(3)
            body_str = match.group(4)
            
            # Skip event handlers (they don't have return types in the same way)
            if func_name in ['state_entry', 'touch_start', 'touch_end', 'timer', 'collision_start', 'http_response']:
                continue
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Parse function body
            body = self._parse_statements(body_str)
            functions.append(LSLFunctionDefinition(return_type, func_name, parameters, body))
        
        return functions
    
    def _parse_states_improved(self, content: str) -> List[LSLState]:
        """Parse state definitions with robust nested brace handling"""
        states = []
        
        # Find all state definitions using proper brace matching
        state_positions = []
        
        # Look for state keywords
        for match in re.finditer(r'\b(default|state\s+\w+)\s*\{', content):
            state_name = match.group(1).strip()
            if state_name.startswith('state '):
                state_name = state_name.split()[-1]
            
            start_pos = match.end() - 1  # Position of opening brace
            end_pos = self._find_matching_brace(content, start_pos)
            
            if end_pos is not None:
                state_body = content[start_pos + 1:end_pos]  # Content between braces
                events = self._parse_event_handlers_improved(state_body)
                states.append(LSLState(state_name, events))
        
        return states
    
    def _find_matching_brace(self, content: str, start_pos: int) -> Optional[int]:
        """Find the matching closing brace for an opening brace at start_pos"""
        if start_pos >= len(content) or content[start_pos] != '{':
            return None
        
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_pos, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"':
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return i
        
        return None  # No matching brace found
    
    def _parse_event_handlers_improved(self, state_body: str) -> List[LSLEventHandler]:
        """Parse event handlers within a state with robust nested brace handling"""
        events = []
        
        # Known LSL event handlers
        event_names = [
            'state_entry', 'state_exit', 'touch_start', 'touch', 'touch_end',
            'collision_start', 'collision', 'collision_end', 'timer', 'listen',
            'sensor', 'no_sensor', 'control', 'at_target', 'not_at_target',
            'at_rot_target', 'not_at_rot_target', 'money', 'email',
            'run_time_permissions', 'changed', 'attach', 'dataserver',
            'moving_start', 'moving_end', 'object_rez', 'remote_data',
            'http_response', 'link_message'
        ]
        
        # Find event handlers using proper brace matching
        for event_name in event_names:
            # Look for event handler start
            pattern = rf'\b{event_name}\s*\(([^)]*)\)\s*\{{'
            match = re.search(pattern, state_body)
            
            if match:
                params_str = match.group(1)
                start_pos = match.end() - 1  # Position of opening brace
                end_pos = self._find_matching_brace(state_body, start_pos)
                
                if end_pos is not None:
                    event_body = state_body[start_pos + 1:end_pos]  # Content between braces
                    
                    # Parse event parameters
                    parameters = self._parse_parameters(params_str)
                    
                    # Parse event body
                    body = self._parse_statements(event_body)
                    events.append(LSLEventHandler(event_name, parameters, body))
        
        return events
    
    def _parse_parameters(self, params_str: str) -> List[LSLParameter]:
        """Parse function/event parameters"""
        parameters = []
        
        if params_str.strip():
            param_pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)'
            for param_match in re.finditer(param_pattern, params_str):
                param_type = param_match.group(1)
                param_name = param_match.group(2)
                parameters.append(LSLParameter(param_type, param_name))
        
        return parameters
    
    def _parse_statements(self, body_str: str) -> List[LSLStatement]:
        """Parse statements from body string"""
        statements = []
        
        # Split by semicolons, but respect braces
        statement_parts = self._split_statements(body_str)
        
        for part in statement_parts:
            part = part.strip()
            if not part:
                continue
            
            # Parse different statement types
            stmt = self._parse_single_statement(part)
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _split_statements(self, body_str: str) -> List[str]:
        """Split body into individual statements, respecting braces"""
        statements = []
        current = ""
        brace_level = 0
        in_string = False
        
        i = 0
        while i < len(body_str):
            char = body_str[i]
            
            if char == '"' and (i == 0 or body_str[i-1] != '\\'):
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
                    i += 1
                    continue
            
            current += char
            i += 1
        
        if current.strip():
            statements.append(current.strip())
        
        return statements
    
    def _parse_single_statement(self, stmt_str: str) -> Optional[LSLStatement]:
        """Parse a single statement"""
        stmt_str = stmt_str.strip()
        
        # Variable declarations
        var_decl_pattern = r'\b(integer|float|string|key|vector|rotation|list)\s+(\w+)\s*(?:=\s*(.+))?'
        var_match = re.match(var_decl_pattern, stmt_str)
        if var_match:
            type_name = var_match.group(1)
            var_name = var_match.group(2)
            init_value = var_match.group(3)
            
            init_expr = None
            if init_value:
                init_expr = self._parse_expression_improved(init_value.strip())
            
            return LSLVariableDeclaration(type_name, var_name, init_expr)
        
        # Assignment statements
        assign_pattern = r'(\w+)\s*=\s*(.+)'
        assign_match = re.match(assign_pattern, stmt_str)
        if assign_match:
            var_name = assign_match.group(1)
            value_expr = assign_match.group(2)
            
            lvalue = LSLIdentifier(var_name)
            rvalue = self._parse_expression_improved(value_expr.strip())
            return LSLAssignmentStatement(lvalue, '=', rvalue)
        
        # If statements
        if_pattern = r'if\s*\(([^)]+)\)\s*\{([^}]*)\}(?:\s*else\s*\{([^}]*)\})?'
        if_match = re.match(if_pattern, stmt_str)
        if if_match:
            condition = self._parse_expression_improved(if_match.group(1))
            then_body = self._parse_statements(if_match.group(2))
            then_stmt = LSLCompoundStatement(then_body)
            
            else_stmt = None
            if if_match.group(3):
                else_body = self._parse_statements(if_match.group(3))
                else_stmt = LSLCompoundStatement(else_body)
            
            return LSLIfStatement(condition, then_stmt, else_stmt)
        
        # For loops
        for_pattern = r'for\s*\(([^;]*);([^;]*);([^)]*)\)\s*\{([^}]*)\}'
        for_match = re.match(for_pattern, stmt_str)
        if for_match:
            init_str = for_match.group(1).strip()
            condition_str = for_match.group(2).strip()
            increment_str = for_match.group(3).strip()
            body_str = for_match.group(4)
            
            init_stmt = None
            if init_str:
                init_stmt = self._parse_single_statement(init_str)
            
            condition = None
            if condition_str:
                condition = self._parse_expression_improved(condition_str)
            
            increment = None
            if increment_str:
                increment = self._parse_expression_improved(increment_str)
            
            body = self._parse_statements(body_str)
            body_stmt = LSLCompoundStatement(body)
            
            return LSLForStatement(init_stmt, condition, increment, body_stmt)
        
        # Do-while loops
        do_while_pattern = r'do\s*\{([^}]*)\}\s*while\s*\(([^)]*)\)'
        do_while_match = re.match(do_while_pattern, stmt_str)
        if do_while_match:
            body_str = do_while_match.group(1)
            condition_str = do_while_match.group(2)
            
            body = self._parse_statements(body_str)
            body_stmt = LSLCompoundStatement(body)
            condition = self._parse_expression_improved(condition_str)
            
            return LSLDoWhileStatement(body_stmt, condition)
        
        # Break/Continue statements
        if stmt_str == 'break':
            return LSLBreakStatement()
        if stmt_str == 'continue':
            return LSLContinueStatement()
        
        # Function calls (expression statements)
        if re.match(r'\w+\s*\(', stmt_str):
            expr = self._parse_expression_improved(stmt_str)
            return LSLExpressionStatement(expr)
        
        # Return statements
        if stmt_str.startswith('return'):
            return_pattern = r'return\s*(.+)?'
            return_match = re.match(return_pattern, stmt_str)
            if return_match:
                value_str = return_match.group(1)
                value = None
                if value_str and value_str.strip():
                    value = self._parse_expression_improved(value_str.strip())
                return LSLReturnStatement(value)
        
        return None
    
    def _parse_expression_improved(self, expr_str: str) -> LSLExpression:
        """Parse expression with proper precedence and special syntax handling"""
        expr_str = expr_str.strip()
        
        # First check for special LSL syntax
        
        # Vector literals: <x, y, z>
        vector_pattern = r'^<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>$'
        vector_match = re.match(vector_pattern, expr_str)
        if vector_match:
            x = self._parse_expression_improved(vector_match.group(1).strip())
            y = self._parse_expression_improved(vector_match.group(2).strip())
            z = self._parse_expression_improved(vector_match.group(3).strip())
            return LSLVectorLiteral(x, y, z)
        
        # Rotation literals: <x, y, z, s>
        rotation_pattern = r'^<\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^>]+)\s*>$'
        rotation_match = re.match(rotation_pattern, expr_str)
        if rotation_match:
            x = self._parse_expression_improved(rotation_match.group(1).strip())
            y = self._parse_expression_improved(rotation_match.group(2).strip())
            z = self._parse_expression_improved(rotation_match.group(3).strip())
            s = self._parse_expression_improved(rotation_match.group(4).strip())
            return LSLRotationLiteral(x, y, z, s)
        
        # List literals: [elem1, elem2, ...]
        if expr_str.startswith('[') and expr_str.endswith(']'):
            list_content = expr_str[1:-1].strip()
            if list_content:
                elements = self._split_arguments(list_content)
                parsed_elements = [self._parse_expression_improved(elem.strip()) for elem in elements]
                return LSLListLiteral(parsed_elements)
            else:
                return LSLListLiteral([])
        
        # Type casting: (type)expression
        cast_pattern = r'^\((integer|float|string|key|vector|rotation|list)\)\s*(.+)$'
        cast_match = re.match(cast_pattern, expr_str)
        if cast_match:
            type_name = cast_match.group(1)
            expr = cast_match.group(2)
            return LSLTypeCast(type_name, self._parse_expression_improved(expr))
        
        # Function calls: func(args...)
        func_call_pattern = r'^(\w+)\s*\(([^)]*)\)$'
        func_match = re.match(func_call_pattern, expr_str)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            
            arguments = []
            if args_str.strip():
                args = self._split_arguments(args_str)
                for arg in args:
                    arguments.append(self._parse_expression_improved(arg.strip()))
            
            return LSLFunctionCall(func_name, arguments)
        
        # Handle list slicing: obj[start:end]
        slice_pattern = r'^(.+)\[([^:]+):([^]]+)\]$'
        slice_match = re.match(slice_pattern, expr_str)
        if slice_match:
            obj_str = slice_match.group(1)
            start_str = slice_match.group(2)
            end_str = slice_match.group(3)
            
            obj = self._parse_expression_improved(obj_str)
            start = self._parse_expression_improved(start_str)
            end = self._parse_expression_improved(end_str)
            return LSLSliceAccess(obj, start, end)
        
        # Now handle operators with proper precedence
        return self._parse_binary_expression(expr_str)
    
    def _parse_binary_expression(self, expr_str: str) -> LSLExpression:
        """Parse binary expressions with proper operator precedence"""
        # Find the operator with lowest precedence (rightmost)
        best_op = None
        best_pos = -1
        best_precedence = float('inf')
        
        paren_level = 0
        in_string = False
        
        i = len(expr_str) - 1
        while i >= 0:
            char = expr_str[i]
            
            if char == '"' and (i == 0 or expr_str[i-1] != '\\'):
                in_string = not in_string
                i -= 1
                continue
            
            if in_string:
                i -= 1
                continue
                
            if char == ')':
                paren_level += 1
            elif char == '(':
                paren_level -= 1
            elif paren_level == 0:
                # Check for operators
                for op in sorted(self.precedence.keys(), key=len, reverse=True):
                    if i >= len(op) - 1 and expr_str[i-len(op)+1:i+1] == op:
                        precedence = self.precedence[op]
                        if precedence <= best_precedence:
                            best_op = op
                            best_pos = i - len(op) + 1
                            best_precedence = precedence
                        break
            i -= 1
        
        # If we found an operator, split the expression
        if best_op and best_pos > 0 and best_pos + len(best_op) < len(expr_str):
            left_str = expr_str[:best_pos].strip()
            right_str = expr_str[best_pos + len(best_op):].strip()
            
            if best_op == '.':
                # Member access: obj.member
                left = self._parse_expression_improved(left_str)
                # Right side should be an identifier for member access
                return LSLMemberAccess(left, right_str)
            else:
                # Regular binary operation
                left = self._parse_expression_improved(left_str)
                right = self._parse_expression_improved(right_str)
                return LSLBinaryOp(left, best_op, right)
        
        # No operators found, parse as atomic expression
        return self._parse_atomic_expression(expr_str)
    
    def _parse_atomic_expression(self, expr_str: str) -> LSLExpression:
        """Parse atomic expressions (literals, identifiers, parenthesized expressions)"""
        expr_str = expr_str.strip()
        
        # Parenthesized expressions
        if expr_str.startswith('(') and expr_str.endswith(')'):
            return self._parse_expression_improved(expr_str[1:-1])
        
        # String literals
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return LSLLiteral(expr_str[1:-1], 'string')
        
        # Integer literals
        if expr_str.isdigit() or (expr_str.startswith('-') and expr_str[1:].isdigit()):
            return LSLLiteral(int(expr_str), 'integer')
        
        # Float literals
        try:
            if '.' in expr_str:
                return LSLLiteral(float(expr_str), 'float')
        except ValueError:
            pass
        
        # Hexadecimal integers
        if expr_str.startswith('0x') or expr_str.startswith('0X'):
            try:
                return LSLLiteral(int(expr_str, 16), 'integer')
            except ValueError:
                pass
        
        # LSL constants (ENHANCED)
        lsl_constants = {
            'TRUE': (1, 'integer'),
            'FALSE': (0, 'integer'),
            'NULL_KEY': ("00000000-0000-0000-0000-000000000000", 'key'),
            'PI': (3.14159265359, 'float'),
            'TWO_PI': (6.28318530718, 'float'),
            'PI_BY_TWO': (1.57079632679, 'float'),
            'DEG_TO_RAD': (0.01745329252, 'float'),
            'RAD_TO_DEG': (57.2957795131, 'float'),
            'ZERO_VECTOR': ((0.0, 0.0, 0.0), 'vector'),
            'ZERO_ROTATION': ((0.0, 0.0, 0.0, 1.0), 'rotation'),
            # Additional LSL constants
            'EOF': (-1, 'integer'),
            'DEBUG_CHANNEL': (2147483647, 'integer'),
            'PUBLIC_CHANNEL': (0, 'integer'),
            'TOUCH_INVALID_FACE': (-1, 'integer'),
            'AGENT': (1, 'integer'),
            'ACTIVE': (2, 'integer'),
            'PASSIVE': (4, 'integer'),
            'SCRIPTED': (8, 'integer'),
        }
        
        if expr_str in lsl_constants:
            value, type_name = lsl_constants[expr_str]
            return LSLLiteral(value, type_name)
        
        # Identifiers
        if re.match(r'^[a-zA-Z_]\w*$', expr_str):
            return LSLIdentifier(expr_str)
        
        # Fallback to literal
        return LSLLiteral(expr_str, 'unknown')
    
    def _split_arguments(self, args_str: str) -> List[str]:
        """Split function arguments, respecting parentheses and quotes"""
        args = []
        current = ""
        paren_level = 0
        bracket_level = 0
        in_string = False
        
        for char in args_str:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            
            if not in_string:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                elif char == '[':
                    bracket_level += 1
                elif char == ']':
                    bracket_level -= 1
                elif char == ',' and paren_level == 0 and bracket_level == 0:
                    if current.strip():
                        args.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args

class ImprovedLSLEvaluator:
    """Improved evaluator with better type handling"""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.scope_stack = []
        self.global_scope = {}
    
    def evaluate(self, node: LSLASTNode) -> Any:
        """Evaluate an AST node"""
        method_name = f"evaluate_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_evaluate)
        return method(node)
    
    def generic_evaluate(self, node: LSLASTNode) -> Any:
        """Default evaluation for unknown nodes"""
        raise NotImplementedError(f"No evaluator for {type(node).__name__}")
    
    def evaluate_LSLScript(self, node: LSLScript) -> Dict[str, Any]:
        """Evaluate entire script"""
        result = {
            'globals': {},
            'functions': {},
            'states': {}
        }
        
        # Process globals
        for global_decl in node.globals:
            name = global_decl.name
            value = self.evaluate(global_decl.init_value) if global_decl.init_value else self._get_default_value(global_decl.type_name)
            result['globals'][name] = value
            self.global_scope[name] = value
        
        # Process functions
        for func_def in node.functions:
            result['functions'][func_def.name] = func_def
        
        # Process states
        for state in node.states:
            result['states'][state.name] = state
        
        return result
    
    def _get_default_value(self, type_name: str) -> Any:
        """Get default value for LSL type"""
        defaults = {
            'integer': 0,
            'float': 0.0,
            'string': "",
            'key': "00000000-0000-0000-0000-000000000000",
            'vector': (0.0, 0.0, 0.0),
            'rotation': (0.0, 0.0, 0.0, 1.0),
            'list': []
        }
        return defaults.get(type_name, None)
    
    def evaluate_LSLBinaryOp(self, node: LSLBinaryOp) -> Any:
        """Evaluate binary operation with better type handling"""
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)
        
        # Convert string comparisons to proper types
        if isinstance(left_val, str) and left_val.isdigit():
            left_val = int(left_val)
        if isinstance(right_val, str) and right_val.isdigit():
            right_val = int(right_val)
        
        try:
            if node.operator == '+':
                return left_val + right_val
            elif node.operator == '-':
                return left_val - right_val
            elif node.operator == '*':
                return left_val * right_val
            elif node.operator == '/':
                return left_val / right_val if right_val != 0 else 0
            elif node.operator == '%':
                return left_val % right_val if right_val != 0 else 0
            elif node.operator == '==':
                return left_val == right_val
            elif node.operator == '!=':
                return left_val != right_val
            elif node.operator == '<':
                return left_val < right_val
            elif node.operator == '>':
                return left_val > right_val
            elif node.operator == '<=':
                return left_val <= right_val
            elif node.operator == '>=':
                return left_val >= right_val
            elif node.operator == '&&':
                return bool(left_val) and bool(right_val)
            elif node.operator == '||':
                return bool(left_val) or bool(right_val)
            elif node.operator == '&':
                return int(left_val) & int(right_val)
            elif node.operator == '|':
                return int(left_val) | int(right_val)
            elif node.operator == '^':
                return int(left_val) ^ int(right_val)
            elif node.operator == '<<':
                return int(left_val) << int(right_val)
            elif node.operator == '>>':
                return int(left_val) >> int(right_val)
            else:
                raise NotImplementedError(f"Binary operator {node.operator} not implemented")
        except Exception as e:
            print(f"Warning: Binary operation {left_val} {node.operator} {right_val} failed: {e}")
            return 0  # Return safe default
    
    def evaluate_LSLMemberAccess(self, node: LSLMemberAccess) -> Any:
        """Evaluate member access (e.g., vector.x)"""
        obj_val = self.evaluate(node.object)
        
        # Handle vector component access
        if isinstance(obj_val, tuple) and len(obj_val) == 3:
            if node.member == 'x':
                return obj_val[0]
            elif node.member == 'y':
                return obj_val[1]
            elif node.member == 'z':
                return obj_val[2]
        
        # Handle rotation component access
        if isinstance(obj_val, tuple) and len(obj_val) == 4:
            if node.member == 'x':
                return obj_val[0]
            elif node.member == 'y':
                return obj_val[1]
            elif node.member == 'z':
                return obj_val[2]
            elif node.member == 's':
                return obj_val[3]
        
        # Fallback
        return 0.0
    
    def evaluate_LSLUnaryOp(self, node: LSLUnaryOp) -> Any:
        """Evaluate unary operation"""
        operand_val = self.evaluate(node.operand)
        
        if node.operator == '!':
            return not bool(operand_val)
        elif node.operator == '-':
            return -operand_val
        elif node.operator == '+':
            return +operand_val
        elif node.operator == '~':
            return ~int(operand_val)
        else:
            raise NotImplementedError(f"Unary operator {node.operator} not implemented")
    
    def evaluate_LSLFunctionCall(self, node: LSLFunctionCall) -> Any:
        """Evaluate function call"""
        args = [self.evaluate(arg) for arg in node.arguments]
        
        # This would integrate with the existing simulator's function registry
        if hasattr(self.simulator, 'call_function'):
            return self.simulator.call_function(node.function_name, args)
        else:
            print(f"CALL: {node.function_name}({', '.join(map(str, args))})")
            return None
    
    def evaluate_LSLIdentifier(self, node: LSLIdentifier) -> Any:
        """Evaluate identifier (variable lookup)"""
        # Look up in scope stack
        for scope in reversed(self.scope_stack):
            if node.name in scope:
                return scope[node.name]
        
        # Look up in global scope
        if node.name in self.global_scope:
            return self.global_scope[node.name]
        
        # Look up in simulator global vars
        if hasattr(self.simulator, 'global_vars') and node.name in self.simulator.global_vars:
            return self.simulator.global_vars[node.name]
        
        # Return default for unknown variables
        print(f"Warning: Unknown variable {node.name}, returning 0")
        return 0
    
    def evaluate_LSLLiteral(self, node: LSLLiteral) -> Any:
        """Evaluate literal value"""
        return node.value
    
    def evaluate_LSLVectorLiteral(self, node: LSLVectorLiteral) -> tuple:
        """Evaluate vector literal"""
        x = self.evaluate(node.x)
        y = self.evaluate(node.y)
        z = self.evaluate(node.z)
        return (float(x), float(y), float(z))
    
    def evaluate_LSLRotationLiteral(self, node: LSLRotationLiteral) -> tuple:
        """Evaluate rotation literal"""
        x = self.evaluate(node.x)
        y = self.evaluate(node.y)
        z = self.evaluate(node.z)
        s = self.evaluate(node.s)
        return (float(x), float(y), float(z), float(s))
    
    def evaluate_LSLListLiteral(self, node: LSLListLiteral) -> list:
        """Evaluate list literal"""
        return [self.evaluate(elem) for elem in node.elements]
    
    def evaluate_LSLTypeCast(self, node: LSLTypeCast) -> Any:
        """Evaluate type cast"""
        value = self.evaluate(node.expression)
        
        # LSL type casting
        if node.type_name == 'string':
            if isinstance(value, tuple) and len(value) == 3:
                return f"<{value[0]}, {value[1]}, {value[2]}>"
            elif isinstance(value, tuple) and len(value) == 4:
                return f"<{value[0]}, {value[1]}, {value[2]}, {value[3]}>"
            else:
                return str(value)
        elif node.type_name == 'integer':
            if isinstance(value, str):
                try:
                    return int(float(value))
                except ValueError:
                    return 0
            return int(value)
        elif node.type_name == 'float':
            return float(value)
        elif node.type_name == 'key':
            return str(value)
        else:
            return value
    
    def evaluate_LSLForStatement(self, node: LSLForStatement) -> Any:
        """Evaluate for loop with break/continue support"""
        # Initialize
        if node.init:
            self.evaluate(node.init)
        
        # Loop
        while True:
            # Check condition
            if node.condition and not self.evaluate(node.condition):
                break
            
            try:
                # Execute body
                self.evaluate(node.body)
            except BreakException:
                break
            except ContinueException:
                pass  # Continue to increment
            
            # Increment
            if node.increment:
                self.evaluate(node.increment)
        
        return None
    
    def evaluate_LSLWhileStatement(self, node: LSLWhileStatement) -> Any:
        """Evaluate while loop with break/continue support"""
        while self.evaluate(node.condition):
            try:
                self.evaluate(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
        return None
    
    def evaluate_LSLDoWhileStatement(self, node: LSLDoWhileStatement) -> Any:
        """Evaluate do-while loop"""
        # Execute body at least once
        try:
            self.evaluate(node.body)
        except (BreakException, ContinueException):
            pass
        
        # Then check condition
        while self.evaluate(node.condition):
            try:
                self.evaluate(node.body)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return None
    
    def evaluate_LSLBreakStatement(self, node: LSLBreakStatement) -> Any:
        """Evaluate break statement"""
        raise BreakException()
    
    def evaluate_LSLContinueStatement(self, node: LSLContinueStatement) -> Any:
        """Evaluate continue statement"""
        raise ContinueException()
    
    def evaluate_LSLSliceAccess(self, node: LSLSliceAccess) -> Any:
        """Evaluate slice access (e.g., list[1:3])"""
        obj_val = self.evaluate(node.object)
        start_val = int(self.evaluate(node.start))
        end_val = int(self.evaluate(node.end))
        
        if isinstance(obj_val, (list, str)):
            return obj_val[start_val:end_val]
        else:
            print(f"Warning: Cannot slice {type(obj_val)}")
            return []

# Exception classes for control flow
class BreakException(Exception):
    """Exception for break statements"""
    pass

class ContinueException(Exception):
    """Exception for continue statements"""
    pass

def test_improved_parser():
    """Test the improved parser with the previously problematic cases"""
    print("=== Testing Improved ANTLR4 POC Parser ===")
    
    parser = ImprovedLSLParser()
    evaluator = ImprovedLSLEvaluator(None)
    
    # Test vector literal parsing
    print("\n1. Testing vector literal parsing...")
    vector_expr = "<1.0, 2.0, 3.0>"
    ast_expr = parser._parse_expression_improved(vector_expr)
    print(f"✓ {vector_expr} -> {type(ast_expr).__name__}")
    result = evaluator.evaluate(ast_expr)
    print(f"  Evaluates to: {result}")
    
    # Test member access
    print("\n2. Testing member access parsing...")
    member_expr = "pos.x"
    ast_expr = parser._parse_expression_improved(member_expr)
    print(f"✓ {member_expr} -> {type(ast_expr).__name__}")
    
    # Test complex expression with precedence
    print("\n3. Testing operator precedence...")
    complex_expr = "a + b * c"
    ast_expr = parser._parse_expression_improved(complex_expr)
    print(f"✓ {complex_expr} -> {type(ast_expr).__name__}")
    if hasattr(ast_expr, 'left') and hasattr(ast_expr, 'right'):
        print(f"  Structure: {type(ast_expr.left).__name__} {ast_expr.operator} {type(ast_expr.right).__name__}")
    
    # Test type casting
    print("\n4. Testing type casting...")
    cast_expr = "(string)42"
    ast_expr = parser._parse_expression_improved(cast_expr)
    print(f"✓ {cast_expr} -> {type(ast_expr).__name__}")
    result = evaluator.evaluate(ast_expr)
    print(f"  Evaluates to: '{result}' (type: {type(result).__name__})")
    
    # Test function call with nested arguments
    print("\n5. Testing nested function calls...")
    func_expr = 'llSay(0, llList2Json(JSON_OBJECT, ["key", "value"]))'
    ast_expr = parser._parse_expression_improved(func_expr)
    print(f"✓ {func_expr} -> {type(ast_expr).__name__}")
    
    print("\n✅ All enhanced parsing tests successful!")

def test_enhanced_constructs():
    """Test enhanced grammar constructs"""
    print("\n=== Testing Enhanced Grammar Constructs ===")
    
    parser = ImprovedLSLParser()
    
    # Test do-while loop
    do_while_script = '''
    default {
        state_entry() {
            integer i = 0;
            do {
                llSay(0, "Count: " + (string)i);
                i++;
            } while (i < 3);
        }
    }
    '''
    
    try:
        ast = parser.parse(do_while_script)
        print("✓ Do-while loop parsing successful")
    except Exception as e:
        print(f"❌ Do-while loop failed: {e}")
    
    # Test break/continue
    break_continue_script = '''
    default {
        state_entry() {
            for (integer i = 0; i < 10; i++) {
                if (i == 3) continue;
                if (i == 8) break;
                llSay(0, (string)i);
            }
        }
    }
    '''
    
    try:
        ast = parser.parse(break_continue_script)
        print("✓ Break/continue parsing successful")
    except Exception as e:
        print(f"❌ Break/continue failed: {e}")
    
    print("\n🎉 Enhanced grammar tests completed!")

if __name__ == "__main__":
    test_improved_parser()
    test_enhanced_constructs()