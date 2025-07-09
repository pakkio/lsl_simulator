"""
LSL Statement Executor - Command Pattern implementation
Replaces the monolithic _execute_simple_statement with specialized command handlers.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List


class StatementCommand(ABC):
    """Abstract base class for statement commands."""
    
    @abstractmethod
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        """Check if this command can handle the given statement."""
        pass
    
    @abstractmethod
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        """Execute the statement and return the result."""
        pass


class DeclarationCommand(StatementCommand):
    """Handles variable declarations."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        return stmt.get("type") == "declaration"
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        var_name = stmt["name"]
        var_value = stmt.get("value")
        
        if var_value:
            evaluated_value = simulator._evaluate_expression(var_value)
        else:
            # Default values based on LSL type
            var_type = stmt.get("lsl_type", "string")
            evaluated_value = self._get_default_value(var_type)
        
        # Set the variable in the current scope
        current_scope = simulator.call_stack.get_current_scope()
        current_scope.set(var_name, evaluated_value)
        return None
    
    def _get_default_value(self, var_type: str) -> Any:
        """Get default value for LSL type."""
        defaults = {
            "string": "",
            "integer": 0,
            "float": 0.0,
            "vector": [0.0, 0.0, 0.0],
            "list": [],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "key": "00000000-0000-0000-0000-000000000000"
        }
        return defaults.get(var_type, "")


class IncrementCommand(StatementCommand):
    """Handles increment operations like variable++."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        if stmt.get("type") != "simple":
            return False
        statement_str = stmt.get("statement", "")
        return re.match(r"[\w\d_]+\+\+", statement_str) is not None
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        statement_str = stmt.get("statement", "")
        inc_match = re.match(r"([\w\d_]+)\+\+", statement_str)
        if not inc_match:
            return None
        
        var_name = inc_match.group(1)
        current_value = simulator.call_stack.find_variable(var_name)
        
        if current_value is not None:
            new_value = current_value + 1
            self._update_variable(var_name, new_value, simulator)
        
        return None
    
    def _update_variable(self, var_name: str, value: Any, simulator) -> None:
        """Update variable in the appropriate scope."""
        current_scope = simulator.call_stack.get_current_scope()
        found_scope = current_scope
        
        while found_scope:
            if found_scope.get(var_name) is not None:
                found_scope.set(var_name, value)
                return
            found_scope = getattr(found_scope, 'parent', None)
        
        # If not found in any scope, set in current scope
        current_scope.set(var_name, value)


class DecrementCommand(StatementCommand):
    """Handles decrement operations like variable--."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        if stmt.get("type") != "simple":
            return False
        statement_str = stmt.get("statement", "")
        return re.match(r"[\w\d_]+--", statement_str) is not None
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        statement_str = stmt.get("statement", "")
        dec_match = re.match(r"([\w\d_]+)--", statement_str)
        if not dec_match:
            return None
        
        var_name = dec_match.group(1)
        current_value = simulator.call_stack.find_variable(var_name)
        
        if current_value is not None:
            new_value = current_value - 1
            self._update_variable(var_name, new_value, simulator)
        
        return None
    
    def _update_variable(self, var_name: str, value: Any, simulator) -> None:
        """Update variable in the appropriate scope."""
        current_scope = simulator.call_stack.get_current_scope()
        found_scope = current_scope
        
        while found_scope:
            if found_scope.get(var_name) is not None:
                found_scope.set(var_name, value)
                return
            found_scope = getattr(found_scope, 'parent', None)
        
        # If not found in any scope, set in current scope
        current_scope.set(var_name, value)


class AssignmentCommand(StatementCommand):
    """Handles variable assignments."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        if stmt.get("type") != "simple":
            return False
        statement_str = stmt.get("statement", "")
        return re.match(r"(?:(?:string|integer|key|float|vector|list|rotation)\s+)?[\w\d_]+\s*=\s*.*", statement_str, re.DOTALL) is not None
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        statement_str = stmt.get("statement", "")
        match = re.match(r"(?:(?:string|integer|key|float|vector|list|rotation)\s+)?([\w\d_]+)\s*=\s*(.*)", statement_str, re.DOTALL)
        
        if not match:
            return None
        
        var_name, value_str = match.groups()
        value = simulator._evaluate_expression(value_str)
        
        # Update variable in the appropriate scope
        self._update_variable(var_name, value, simulator)
        return None
    
    def _update_variable(self, var_name: str, value: Any, simulator) -> None:
        """Update variable in the appropriate scope."""
        current_scope = simulator.call_stack.get_current_scope()
        found_scope = current_scope
        
        while found_scope:
            if found_scope.get(var_name) is not None:
                found_scope.set(var_name, value)
                return
            found_scope = getattr(found_scope, 'parent', None)
        
        # If not found in any scope, set in current scope
        current_scope.set(var_name, value)


class FunctionCallCommand(StatementCommand):
    """Handles function calls."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        if stmt.get("type") != "simple":
            return False
        statement_str = stmt.get("statement", "")
        return re.match(r"\w+\s*\(.*\)", statement_str, re.DOTALL) is not None
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        statement_str = stmt.get("statement", "")
        match = re.match(r"(\w+)\s*\((.*)\)", statement_str, re.DOTALL)
        
        if not match:
            return None
        
        function_name, args_str = match.groups()
        
        # Parse arguments
        args = self._parse_arguments(args_str)
        evaluated_args = [simulator._evaluate_expression(arg) for arg in args]
        
        # Try API functions first
        api_func = getattr(simulator, f"api_{function_name}", None)
        if api_func:
            return api_func(*evaluated_args)
        
        # Try user-defined functions
        if function_name in simulator.user_functions:
            return simulator._call_user_function(function_name, evaluated_args)
        
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


class EmptyStatementCommand(StatementCommand):
    """Handles empty statements and comments."""
    
    def can_execute(self, stmt: Dict[str, Any]) -> bool:
        if stmt.get("type") != "simple":
            return False
        statement_str = stmt.get("statement", "")
        return not statement_str or statement_str.startswith("//")
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        return None


class StatementExecutor:
    """Executes statements using the command pattern."""
    
    def __init__(self):
        self.commands = [
            DeclarationCommand(),
            EmptyStatementCommand(),
            IncrementCommand(),
            DecrementCommand(),
            AssignmentCommand(),
            FunctionCallCommand(),
        ]
    
    def execute(self, stmt: Dict[str, Any], simulator) -> Any:
        """Execute a statement using the appropriate command."""
        for command in self.commands:
            if command.can_execute(stmt):
                return command.execute(stmt, simulator)
        
        # If no command can handle it, return None
        return None