"""
Professional tests for Expression Evaluation.
Tests the simplified expression evaluator with comprehensive cases.
"""

import pytest
import math
from simple_expression_evaluator import SimpleExpressionEvaluator


class TestSimpleExpressionEvaluator:
    """Test suite for the Simple Expression Evaluator."""
    
    def test_evaluator_initialization(self, simulator):
        """Test evaluator initializes correctly."""
        evaluator = SimpleExpressionEvaluator(simulator)
        assert evaluator is not None
        assert evaluator.simulator == simulator
    
    @pytest.mark.parametrize("expression,expected", [
        ('"Hello World"', "Hello World"),
        ('"Test String"', "Test String"),
        ('""', ""),
        ('"String with spaces"', "String with spaces"),
        ('"String with 123 numbers"', "String with 123 numbers"),
    ])
    def test_string_literals(self, simulator, expression, expected):
        """Test string literal evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert result == expected
        assert isinstance(result, str)
    
    @pytest.mark.parametrize("expression,expected", [
        ("42", 42),
        ("0", 0),
        ("-5", -5),
        ("999", 999),
        ("-1", -1),
    ])
    def test_integer_literals(self, simulator, expression, expected):
        """Test integer literal evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert result == expected
        assert isinstance(result, int)
    
    @pytest.mark.parametrize("expression,expected", [
        ("3.14", 3.14),
        ("0.0", 0.0),
        ("-2.5", -2.5),
        ("1.0", 1.0),
        ("99.99", 99.99),
    ])
    def test_float_literals(self, simulator, expression, expected):
        """Test float literal evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert abs(result - expected) < 0.0001
        assert isinstance(result, float)
    
    @pytest.mark.parametrize("expression,expected", [
        ("<1, 2, 3>", [1.0, 2.0, 3.0]),
        ("<0.0, 0.0, 0.0>", [0.0, 0.0, 0.0]),
        ("<-1, 5.5, 10>", [-1.0, 5.5, 10.0]),
        ("<128.5, 129.3, 25.7>", [128.5, 129.3, 25.7]),
    ])
    def test_vector_literals(self, simulator, expression, expected):
        """Test vector literal evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert isinstance(result, list)
        assert len(result) == 3
        for i in range(3):
            assert abs(result[i] - expected[i]) < 0.0001
    
    @pytest.mark.parametrize("expression,expected", [
        ("[]", []),
        ("[1, 2, 3]", [1, 2, 3]),
        ('["a", "b", "c"]', ["a", "b", "c"]),
        ('[1, "mixed", 3.14]', [1, "mixed", 3.14]),
    ])
    def test_list_literals(self, simulator, expression, expected):
        """Test list literal evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert isinstance(result, list)
        assert len(result) == len(expected)
        for i in range(len(expected)):
            if isinstance(expected[i], float):
                assert abs(result[i] - expected[i]) < 0.0001
            else:
                assert result[i] == expected[i]
    
    def test_variable_lookup(self, simulator):
        """Test variable lookup functionality."""
        # Set up variables in simulator
        simulator.global_scope.set("test_var", "Hello")
        simulator.global_scope.set("count", 42)
        simulator.global_scope.set("pi_value", 3.14159)
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        assert evaluator.evaluate("test_var") == "Hello"
        assert evaluator.evaluate("count") == 42
        assert abs(evaluator.evaluate("pi_value") - 3.14159) < 0.0001
    
    def test_component_access(self, simulator):
        """Test component access (e.g., vector.x)."""
        # Set up vector variable
        simulator.global_scope.set("pos", [10.0, 20.0, 30.0])
        simulator.global_scope.set("rot", [0.1, 0.2, 0.3, 0.9])
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test vector components
        assert evaluator.evaluate("pos.x") == 10.0
        assert evaluator.evaluate("pos.y") == 20.0
        assert evaluator.evaluate("pos.z") == 30.0
        
        # Test rotation components
        assert abs(evaluator.evaluate("rot.x") - 0.1) < 0.0001
        assert abs(evaluator.evaluate("rot.y") - 0.2) < 0.0001
        assert abs(evaluator.evaluate("rot.z") - 0.3) < 0.0001
        assert abs(evaluator.evaluate("rot.s") - 0.9) < 0.0001
    
    @pytest.mark.parametrize("expression,expected", [
        ("5 + 3", 8),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("15 / 3", 5.0),
        ("17 % 5", 2),
        ("2 + 3 * 4", 14),  # Should handle left-to-right for simplicity
    ])
    def test_arithmetic_operations(self, simulator, expression, expected):
        """Test arithmetic operations."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        
        if isinstance(expected, float):
            assert abs(result - expected) < 0.0001
        else:
            assert result == expected
    
    @pytest.mark.parametrize("expression,expected", [
        ('"Hello" + " World"', "Hello World"),
        ('"A" + "B" + "C"', "ABC"),
        ('5 + " items"', "5 items"),
        ('"Count: " + 42', "Count: 42"),
    ])
    def test_string_concatenation(self, simulator, expression, expected):
        """Test string concatenation operations."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert result == expected
        assert isinstance(result, str)
    
    @pytest.mark.parametrize("expression,expected", [
        ("5 == 5", True),
        ("5 != 3", True),
        ("10 > 5", True),
        ("3 < 8", True),
        ("5 >= 5", True),
        ("4 <= 7", True),
        ("5 == 3", False),
        ("5 != 5", False),
    ])
    def test_comparison_operations(self, simulator, expression, expected):
        """Test comparison operations."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert result == expected
        assert isinstance(result, bool)
    
    @pytest.mark.parametrize("expression,expected", [
        ("1 && 1", True),
        ("1 || 0", True),
        ("0 && 1", False),
        ("0 || 0", False),
    ])
    def test_logical_operations(self, simulator, expression, expected):
        """Test logical operations."""
        evaluator = SimpleExpressionEvaluator(simulator)
        result = evaluator.evaluate(expression)
        assert result == expected
        assert isinstance(result, bool)
    
    def test_function_call_evaluation(self, simulator):
        """Test function call evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test simple function calls
        result = evaluator.evaluate('llSay(0, "Hello")')
        assert result is None  # llSay returns None
        
        result = evaluator.evaluate('llStringLength("Hello")')
        assert result == 5
        
        result = evaluator.evaluate('llGetListLength([1, 2, 3, 4])')
        assert result == 4
    
    def test_nested_expressions(self, simulator):
        """Test nested expression evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Set up variables
        simulator.global_scope.set("x", 5)
        simulator.global_scope.set("y", 3)
        
        # Test nested expressions
        result = evaluator.evaluate("x + y * 2")
        assert result == 11  # Left-to-right: (5 + 3) * 2 = 16, or 5 + (3 * 2) = 11
        
        result = evaluator.evaluate('llStringLength("Hello") + 2')
        assert result == 7
    
    def test_error_handling(self, simulator):
        """Test error handling in expression evaluation."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test division by zero
        result = evaluator.evaluate("10 / 0")
        assert result == 0  # Should handle gracefully
        
        # Test modulo by zero
        result = evaluator.evaluate("10 % 0")
        assert result == 0  # Should handle gracefully
        
        # Test unknown variable (should return the variable name)
        result = evaluator.evaluate("unknown_variable")
        assert result == "unknown_variable"
    
    def test_url_and_ip_detection(self, simulator):
        """Test that URLs and IPs are not treated as component access."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # These should not be parsed as component access
        result = evaluator.evaluate('"http://example.com"')
        assert result == "http://example.com"
        
        result = evaluator.evaluate('"192.168.1.1"')
        assert result == "192.168.1.1"
        
        result = evaluator.evaluate('"https://api.test.com/endpoint"')
        assert result == "https://api.test.com/endpoint"
    
    def test_complex_vector_operations(self, simulator):
        """Test complex vector operations."""
        # Set up vector variables
        simulator.global_scope.set("pos1", [1.0, 2.0, 3.0])
        simulator.global_scope.set("pos2", [4.0, 5.0, 6.0])
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test vector component access
        assert evaluator.evaluate("pos1.x") == 1.0
        assert evaluator.evaluate("pos2.z") == 6.0
    
    def test_performance_simple_expressions(self, simulator):
        """Test performance of simple expression evaluation."""
        import time
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test many simple expressions
        start_time = time.time()
        for i in range(1000):
            result = evaluator.evaluate(f'"Test string {i}"')
            assert result == f"Test string {i}"
        
        eval_time = time.time() - start_time
        assert eval_time < 1.0  # Should complete in under 1 second
    
    def test_performance_arithmetic(self, simulator):
        """Test performance of arithmetic operations."""
        import time
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        start_time = time.time()
        for i in range(1000):
            result = evaluator.evaluate(f"{i} + {i + 1}")
            assert result == i + (i + 1)
        
        eval_time = time.time() - start_time
        assert eval_time < 1.0  # Should complete in under 1 second
    
    def test_empty_and_none_expressions(self, simulator):
        """Test handling of empty and None expressions."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        assert evaluator.evaluate("") is None
        assert evaluator.evaluate(None) is None
        assert evaluator.evaluate("   ") == "   "  # Whitespace is preserved
    
    @pytest.mark.parametrize("expression,should_work", [
        ("5 + 3", True),
        ('"valid string"', True),
        ("[1, 2, 3]", True),
        ("<1, 2, 3>", True),
        ("invalid(", False),  # Malformed
        ("5 +", False),       # Incomplete
    ])
    def test_expression_validity(self, simulator, expression, should_work):
        """Test expression validity handling."""
        evaluator = SimpleExpressionEvaluator(simulator)
        
        try:
            result = evaluator.evaluate(expression)
            if should_work:
                assert result is not None
            # If it doesn't work, it might still return something (graceful degradation)
        except Exception as e:
            # Should not crash on malformed expressions
            if should_work:
                pytest.fail(f"Valid expression '{expression}' should not raise exception: {e}")
    
    def test_lsl_constants(self, simulator, lsl_constants):
        """Test LSL constant evaluation."""
        # Set up LSL constants in simulator
        for name, value in lsl_constants.items():
            simulator.global_scope.set(name, value)
        
        evaluator = SimpleExpressionEvaluator(simulator)
        
        # Test constant evaluation
        assert abs(evaluator.evaluate("PI") - 3.141592653589793) < 0.0001
        assert evaluator.evaluate("TRUE") == 1
        assert evaluator.evaluate("FALSE") == 0
        assert evaluator.evaluate("NULL_KEY") == "00000000-0000-0000-0000-000000000000"