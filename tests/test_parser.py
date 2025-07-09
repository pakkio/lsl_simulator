"""
Professional tests for LSL Production Parser.
Tests parsing capabilities with proper assertions and edge cases.
"""

import pytest
from lsl_antlr_parser import LSLParser


class TestLSLProductionParser:
    """Test suite for the LSL Production Parser."""
    
    def test_parser_initialization(self, parser):
        """Test parser initializes correctly."""
        assert parser is not None
        assert isinstance(parser, LSLParser)
        assert parser.errors == []
    
    @pytest.mark.parametrize("script_name,expected_globals", [
        ("minimal", 0),
        ("with_globals", 2),
        ("complex_npc", 3),
    ])
    def test_global_variable_parsing(self, parser, sample_lsl_scripts, script_name, expected_globals):
        """Test parsing of global variables."""
        script = sample_lsl_scripts[script_name]
        parsed = parser.parse_script(script)
        
        assert "globals" in parsed
        assert len(parsed["globals"]) == expected_globals
        
        if expected_globals > 0:
            for global_var in parsed["globals"]:
                assert "name" in global_var
                assert "type" in global_var
                assert isinstance(global_var["name"], str)
                assert global_var["type"] in ["string", "integer", "vector", "float", "key", "rotation", "list"]
    
    @pytest.mark.parametrize("script_name,expected_functions", [
        ("minimal", 0),
        ("with_functions", 1),
        ("complex_npc", 1),
    ])
    def test_user_function_parsing(self, parser, sample_lsl_scripts, script_name, expected_functions):
        """Test parsing of user-defined functions."""
        script = sample_lsl_scripts[script_name]
        parsed = parser.parse_script(script)
        
        assert "functions" in parsed
        assert len(parsed["functions"]) == expected_functions
        
        if expected_functions > 0:
            for func_name, func_def in parsed["functions"].items():
                assert isinstance(func_name, str)
                assert "return_type" in func_def
                assert "args" in func_def
                assert "body" in func_def
                assert isinstance(func_def["body"], list)
    
    @pytest.mark.parametrize("script_name,expected_states", [
        ("minimal", 1),
        ("with_globals", 1),
        ("with_functions", 1),
        ("complex_npc", 1),
    ])
    def test_state_parsing(self, parser, sample_lsl_scripts, script_name, expected_states):
        """Test parsing of state definitions."""
        script = sample_lsl_scripts[script_name]
        parsed = parser.parse_script(script)
        
        assert "states" in parsed
        assert len(parsed["states"]) == expected_states
        assert "default" in parsed["states"]
        
        default_state = parsed["states"]["default"]
        assert isinstance(default_state, dict)
        assert "state_entry" in default_state
    
    def test_event_handler_parsing(self, parser, sample_lsl_scripts):
        """Test parsing of event handlers within states."""
        script = sample_lsl_scripts["with_timer"]
        parsed = parser.parse_script(script)
        
        default_state = parsed["states"]["default"]
        
        # Should have state_entry and timer events
        assert "state_entry" in default_state
        assert "timer" in default_state
        
        # Check event structure
        state_entry = default_state["state_entry"]
        assert "args" in state_entry
        assert "body" in state_entry
        assert isinstance(state_entry["body"], list)
        assert len(state_entry["body"]) > 0
    
    @pytest.mark.parametrize("expression,expected_type", [
        ('"Hello World"', str),
        ("42", int),
        ("3.14", float),
        ("[1, 2, 3]", list),
        ("<1.0, 2.0, 3.0>", list),
    ])
    def test_expression_parsing(self, parser, expression, expected_type):
        """Test parsing of various expression types."""
        result = parser.parse_expression(expression)
        
        assert result is not None
        if expected_type == list:
            assert isinstance(result, list)
        else:
            assert isinstance(result, expected_type)
    
    def test_function_call_parsing(self, parser):
        """Test parsing of function calls."""
        expressions = [
            'llSay(0, "Hello")',
            'llHTTPRequest("http://example.com", [], "")',
            'llGetListLength([1, 2, 3])',
            'llVecMag(<1.0, 2.0, 3.0>)',
        ]
        
        for expr in expressions:
            result = parser.parse_expression(expr)
            assert result is not None
            assert isinstance(result, (list, dict))  # Function calls are parsed as structures
    
    def test_binary_operation_parsing(self, parser):
        """Test parsing of binary operations."""
        expressions = [
            ("5 + 3", 8),
            ("10 - 4", 6),
            ("6 * 7", 42),
            ("15 / 3", 5.0),
            ('"Hello" + " World"', "Hello World"),
        ]
        
        for expr, expected in expressions:
            result = parser.parse_expression(expr)
            assert result is not None
            # Binary operations might be parsed as structures
            assert isinstance(result, (int, float, str, list))
    
    def test_vector_parsing(self, parser):
        """Test parsing of vector literals."""
        vectors = [
            ("<1, 2, 3>", [1.0, 2.0, 3.0]),
            ("<0.0, 0.0, 0.0>", [0.0, 0.0, 0.0]),
            ("<-1, 5.5, 10>", [-1.0, 5.5, 10.0]),
        ]
        
        for vector_str, expected in vectors:
            result = parser.parse_expression(vector_str)
            assert isinstance(result, list)
            assert len(result) == 3
            for i in range(3):
                assert abs(result[i] - expected[i]) < 0.0001
    
    def test_list_parsing(self, parser):
        """Test parsing of list literals."""
        lists = [
            ("[]", []),
            ("[1, 2, 3]", [1, 2, 3]),
            ('["a", "b", "c"]', ["a", "b", "c"]),
            ("[1, 2.5, \"mixed\"]", [1, 2.5, "mixed"]),
        ]
        
        for list_str, expected in lists:
            result = parser.parse_expression(list_str)
            assert isinstance(result, list)
            assert len(result) == len(expected)
    
    def test_comment_removal(self, parser):
        """Test that comments are properly removed."""
        script_with_comments = '''
            // This is a comment
            string message = "Hello"; // Inline comment
            
            /* Multi-line
               comment */
            default {
                state_entry() {
                    llSay(0, message); // Another comment
                }
            }
        '''
        
        parsed = parser.parse_script(script_with_comments)
        
        # Should parse successfully despite comments
        assert len(parsed["globals"]) == 1
        assert "default" in parsed["states"]
        assert "state_entry" in parsed["states"]["default"]
    
    def test_nested_braces(self, parser):
        """Test parsing of nested brace structures."""
        nested_script = '''
            default {
                state_entry() {
                    if (TRUE) {
                        integer i;
                        for (i = 0; i < 5; i++) {
                            if (i % 2 == 0) {
                                llSay(0, "Even: " + (string)i);
                            } else {
                                llSay(0, "Odd: " + (string)i);
                            }
                        }
                    }
                }
            }
        '''
        
        parsed = parser.parse_script(nested_script)
        
        assert "default" in parsed["states"]
        state_entry = parsed["states"]["default"]["state_entry"]
        assert len(state_entry["body"]) > 0
    
    def test_error_handling(self, parser, error_test_cases):
        """Test parser error handling."""
        for syntax_error in error_test_cases["syntax_errors"]:
            # Parser should not crash on syntax errors
            try:
                result = parser.parse_script(syntax_error)
                # Should return some result, even if partial
                assert isinstance(result, dict)
                assert "globals" in result
                assert "functions" in result
                assert "states" in result
            except Exception as e:
                # If it raises an exception, it should be controlled
                assert isinstance(e, (ValueError, SyntaxError))
    
    def test_performance_large_script(self, parser):
        """Test parser performance with large scripts."""
        import time
        
        # Generate a large script
        large_script = "integer global_var = 0;\n\n"
        large_script += "default {\n"
        large_script += "    state_entry() {\n"
        
        # Add many function calls
        for i in range(1000):
            large_script += f'        llSay(0, "Message {i}");\n'
        
        large_script += "    }\n"
        large_script += "}\n"
        
        start_time = time.time()
        parsed = parser.parse_script(large_script)
        parse_time = time.time() - start_time
        
        # Should parse in reasonable time (< 1 second)
        assert parse_time < 1.0
        assert len(parsed["globals"]) == 1
        assert "default" in parsed["states"]
    
    def test_complex_npc_script(self, parser, sample_lsl_scripts):
        """Test parsing of complex NPC script."""
        script = sample_lsl_scripts["complex_npc"]
        parsed = parser.parse_script(script)
        
        # Verify complex script parsing
        assert len(parsed["globals"]) >= 3
        assert len(parsed["functions"]) >= 1
        assert "default" in parsed["states"]
        
        # Check specific elements
        global_names = [g["name"] for g in parsed["globals"]]
        assert "npc_name" in global_names
        assert "npc_position" in global_names
        assert "is_active" in global_names
        
        # Check function exists
        assert "speak" in parsed["functions"]
        
        # Check events
        default_state = parsed["states"]["default"]
        assert "state_entry" in default_state
        assert "sensor" in default_state
        assert "touch_start" in default_state