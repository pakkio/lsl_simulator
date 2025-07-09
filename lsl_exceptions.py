"""
LSL Exception System - Enhanced Error Propagation with Exception Chains
Replaces silent failures with informative exception chains for better debugging.
"""

from typing import Any, Optional, List, Dict
import traceback
from dataclasses import dataclass
from enum import Enum


class LSLErrorType(Enum):
    """Types of LSL errors for better categorization."""
    PARSE_ERROR = "parse_error"
    EVALUATION_ERROR = "evaluation_error"
    STATEMENT_ERROR = "statement_error"
    FUNCTION_ERROR = "function_error"
    VARIABLE_ERROR = "variable_error"
    TYPE_ERROR = "type_error"
    RUNTIME_ERROR = "runtime_error"


@dataclass
class LSLErrorContext:
    """Context information for LSL errors."""
    expression: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    function_name: Optional[str] = None
    variable_name: Optional[str] = None
    operation: Optional[str] = None


class LSLException(Exception):
    """Base exception for all LSL-related errors."""
    
    def __init__(self, message: str, error_type: LSLErrorType, 
                 context: Optional[LSLErrorContext] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context
        self.original_error = original_error
        self.timestamp = self._get_timestamp()
        self.stack_trace = self._get_stack_trace()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error tracking."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _get_stack_trace(self) -> List[str]:
        """Get current stack trace for debugging."""
        return traceback.format_stack()
    
    def get_detailed_message(self) -> str:
        """Get detailed error message with context."""
        parts = [f"[{self.error_type.value.upper()}] {self.args[0]}"]
        
        if self.context:
            if self.context.expression:
                parts.append(f"Expression: {self.context.expression}")
            if self.context.line_number:
                parts.append(f"Line: {self.context.line_number}")
            if self.context.function_name:
                parts.append(f"Function: {self.context.function_name}")
            if self.context.variable_name:
                parts.append(f"Variable: {self.context.variable_name}")
            if self.context.operation:
                parts.append(f"Operation: {self.context.operation}")
        
        if self.original_error:
            parts.append(f"Caused by: {type(self.original_error).__name__}: {self.original_error}")
        
        return " | ".join(parts)


class LSLParseException(LSLException):
    """Exception for parsing errors."""
    
    def __init__(self, message: str, expression: str, 
                 original_error: Optional[Exception] = None):
        context = LSLErrorContext(expression=expression)
        super().__init__(message, LSLErrorType.PARSE_ERROR, context, original_error)


class LSLEvaluationException(LSLException):
    """Exception for expression evaluation errors."""
    
    def __init__(self, message: str, expression: str, operation: str,
                 original_error: Optional[Exception] = None):
        context = LSLErrorContext(expression=expression, operation=operation)
        super().__init__(message, LSLErrorType.EVALUATION_ERROR, context, original_error)


class LSLFunctionException(LSLException):
    """Exception for function call errors."""
    
    def __init__(self, message: str, function_name: str, 
                 args: Optional[List[Any]] = None,
                 original_error: Optional[Exception] = None):
        context = LSLErrorContext(
            expression=f"{function_name}({', '.join(map(str, args or []))})",
            function_name=function_name
        )
        super().__init__(message, LSLErrorType.FUNCTION_ERROR, context, original_error)


class LSLVariableException(LSLException):
    """Exception for variable-related errors."""
    
    def __init__(self, message: str, variable_name: str, operation: str,
                 original_error: Optional[Exception] = None):
        context = LSLErrorContext(
            expression=f"{operation} {variable_name}",
            variable_name=variable_name,
            operation=operation
        )
        super().__init__(message, LSLErrorType.VARIABLE_ERROR, context, original_error)


class LSLTypeException(LSLException):
    """Exception for type-related errors."""
    
    def __init__(self, message: str, expression: str, expected_type: str, 
                 actual_type: str, original_error: Optional[Exception] = None):
        context = LSLErrorContext(
            expression=expression,
            operation=f"type_cast_to_{expected_type}"
        )
        enhanced_message = f"{message} (expected: {expected_type}, got: {actual_type})"
        super().__init__(enhanced_message, LSLErrorType.TYPE_ERROR, context, original_error)


class LSLRuntimeException(LSLException):
    """Exception for runtime errors."""
    
    def __init__(self, message: str, operation: str, 
                 line_number: Optional[int] = None,
                 original_error: Optional[Exception] = None):
        context = LSLErrorContext(
            expression=operation,
            operation=operation,
            line_number=line_number
        )
        super().__init__(message, LSLErrorType.RUNTIME_ERROR, context, original_error)


class LSLErrorHandler:
    """Centralized error handling for LSL operations."""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.error_history: List[LSLException] = []
        self.max_history = 100
    
    def handle_parse_error(self, expression: str, original_error: Exception) -> Any:
        """Handle parsing errors with appropriate fallback."""
        error = LSLParseException(
            f"Failed to parse expression: {expression}",
            expression,
            original_error
        )
        
        if self.debug_mode:
            raise error
        else:
            self._log_error(error)
            # Return a safe default based on expression type
            return self._get_safe_default(expression)
    
    def handle_evaluation_error(self, expression: str, operation: str, 
                               original_error: Exception) -> Any:
        """Handle evaluation errors with appropriate fallback."""
        error = LSLEvaluationException(
            f"Failed to evaluate expression: {expression}",
            expression,
            operation,
            original_error
        )
        
        if self.debug_mode:
            raise error
        else:
            self._log_error(error)
            return self._get_safe_default(expression)
    
    def handle_function_error(self, function_name: str, args: List[Any], 
                            original_error: Exception) -> Any:
        """Handle function call errors with appropriate fallback."""
        error = LSLFunctionException(
            f"Function call failed: {function_name}",
            function_name,
            args,
            original_error
        )
        
        if self.debug_mode:
            raise error
        else:
            self._log_error(error)
            return self._get_function_default(function_name)
    
    def handle_variable_error(self, variable_name: str, operation: str, 
                            original_error: Exception) -> Any:
        """Handle variable errors with appropriate fallback."""
        error = LSLVariableException(
            f"Variable operation failed: {operation} {variable_name}",
            variable_name,
            operation,
            original_error
        )
        
        if self.debug_mode:
            raise error
        else:
            self._log_error(error)
            return self._get_variable_default(variable_name)
    
    def handle_type_error(self, expression: str, expected_type: str, 
                         actual_type: str, original_error: Exception) -> Any:
        """Handle type conversion errors with appropriate fallback."""
        error = LSLTypeException(
            f"Type conversion failed: {expression}",
            expression,
            expected_type,
            actual_type,
            original_error
        )
        
        if self.debug_mode:
            raise error
        else:
            self._log_error(error)
            return self._get_type_default(expected_type)
    
    def _log_error(self, error: LSLException) -> None:
        """Log error for debugging purposes."""
        self.error_history.append(error)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        if self.debug_mode:
            print(f"[LSL ERROR] {error.get_detailed_message()}")
    
    def _get_safe_default(self, expression: str) -> Any:
        """Get a safe default value based on expression characteristics."""
        if not expression:
            return None
        
        # Try to infer type from expression
        expr = expression.strip()
        
        if expr.startswith('[') and expr.endswith(']'):
            return []
        elif expr.startswith('<') and expr.endswith('>'):
            return [0.0, 0.0, 0.0]
        elif expr.startswith('"') and expr.endswith('"'):
            return ""
        elif expr.replace('.', '').replace('-', '').isdigit():
            return 0 if '.' not in expr else 0.0
        else:
            return expr  # Return as string literal
    
    def _get_function_default(self, function_name: str) -> Any:
        """Get default return value for failed function calls."""
        # Common LSL function return types
        if function_name.startswith('llList'):
            return []
        elif function_name.startswith('llVec') or function_name.startswith('llGet') and 'Pos' in function_name:
            return [0.0, 0.0, 0.0]
        elif function_name.startswith('llRot') or 'Rot' in function_name:
            return [0.0, 0.0, 0.0, 1.0]
        elif 'String' in function_name or function_name.startswith('llGet') and 'Name' in function_name:
            return ""
        elif 'Length' in function_name or 'Count' in function_name:
            return 0
        elif 'Float' in function_name or 'Mag' in function_name:
            return 0.0
        else:
            return None
    
    def _get_variable_default(self, variable_name: str) -> Any:
        """Get default value for failed variable operations."""
        return variable_name  # Return as string literal
    
    def _get_type_default(self, expected_type: str) -> Any:
        """Get default value for failed type conversions."""
        defaults = {
            'string': "",
            'integer': 0,
            'float': 0.0,
            'key': "00000000-0000-0000-0000-000000000000",
            'vector': [0.0, 0.0, 0.0],
            'rotation': [0.0, 0.0, 0.0, 1.0],
            'list': []
        }
        return defaults.get(expected_type, None)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors for debugging."""
        error_counts = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'error_types': error_counts,
            'recent_errors': [
                {
                    'type': error.error_type.value,
                    'message': str(error),
                    'context': error.context.__dict__ if error.context else None,
                    'timestamp': error.timestamp
                }
                for error in self.error_history[-10:]  # Last 10 errors
            ]
        }
    
    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()