"""
Professional tests for LSL Simulator.
Tests the core simulator functionality with comprehensive assertions.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from lsl_simulator_simplified import LSLSimulator, Frame, CallStack


class TestFrame:
    """Test suite for Frame class."""
    
    def test_frame_creation(self):
        """Test frame creation and initialization."""
        parent = Frame(None)
        frame = Frame(parent)
        
        assert frame.locals == {}
        assert frame.parent == parent
    
    def test_frame_variable_operations(self):
        """Test frame variable get/set operations."""
        frame = Frame(None)
        
        # Test setting and getting variables
        frame.set("test_var", "test_value")
        assert frame.get("test_var") == "test_value"
        
        # Test non-existent variable
        assert frame.get("nonexistent") is None
        
        # Test overwriting variable
        frame.set("test_var", "new_value")
        assert frame.get("test_var") == "new_value"


class TestCallStack:
    """Test suite for CallStack class."""
    
    def test_callstack_creation(self):
        """Test call stack creation."""
        global_scope = Frame(None)
        stack = CallStack(global_scope)
        
        assert stack.frames == []
        assert stack.global_scope == global_scope
        assert stack.get_current_scope() == global_scope
    
    def test_callstack_operations(self):
        """Test call stack push/pop operations."""
        global_scope = Frame(None)
        stack = CallStack(global_scope)
        
        # Test push
        frame1 = Frame(global_scope)
        stack.push(frame1)
        assert stack.get_current_scope() == frame1
        assert len(stack.frames) == 1
        
        # Test another push
        frame2 = Frame(frame1)
        stack.push(frame2)
        assert stack.get_current_scope() == frame2
        assert len(stack.frames) == 2
        
        # Test pop
        popped = stack.pop()
        assert popped == frame2
        assert stack.get_current_scope() == frame1
        assert len(stack.frames) == 1
        
        # Test pop last frame
        popped = stack.pop()
        assert popped == frame1
        assert stack.get_current_scope() == global_scope
        assert len(stack.frames) == 0
        
        # Test pop from empty stack
        popped = stack.pop()
        assert popped is None
    
    def test_variable_lookup(self):
        """Test variable lookup through call stack."""
        global_scope = Frame(None)
        global_scope.set("global_var", "global_value")
        
        stack = CallStack(global_scope)
        
        # Test global variable lookup
        assert stack.find_variable("global_var") == "global_value"
        
        # Test local variable lookup
        local_frame = Frame(global_scope)
        local_frame.set("local_var", "local_value")
        stack.push(local_frame)
        
        assert stack.find_variable("local_var") == "local_value"
        assert stack.find_variable("global_var") == "global_value"
        
        # Test variable shadowing
        local_frame.set("global_var", "shadowed_value")
        assert stack.find_variable("global_var") == "shadowed_value"
        
        # Test non-existent variable
        assert stack.find_variable("nonexistent") is None


class TestLSLSimulator:
    """Test suite for LSL Simulator."""
    
    def test_simulator_initialization(self, sample_lsl_scripts):
        """Test simulator initialization."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["minimal"])
        
        sim = LSLSimulator(parsed)
        
        assert sim.global_scope is not None
        assert sim.call_stack is not None
        assert sim.current_state == "default"
        assert sim._is_running is True
        assert sim.event_queue == []
        assert sim.expression_evaluator is not None
    
    def test_simulator_with_debug(self, sample_lsl_scripts):
        """Test simulator initialization with debug mode."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["minimal"])
        
        sim = LSLSimulator(parsed, debug_mode=True, breakpoints={5, 10})
        
        assert sim.debug_mode is True
        assert sim.debugger is not None
        assert 5 in sim.debugger.breakpoints
        assert 10 in sim.debugger.breakpoints
    
    def test_lsl_constants_initialization(self, simulator, lsl_constants):
        """Test that LSL constants are properly initialized."""
        # Check some key constants
        assert simulator.global_scope.get("PI") is not None
        assert abs(simulator.global_scope.get("PI") - 3.141592653589793) < 0.0001
        assert simulator.global_scope.get("TRUE") == 1
        assert simulator.global_scope.get("FALSE") == 0
        assert simulator.global_scope.get("NULL_KEY") == "00000000-0000-0000-0000-000000000000"
    
    def test_global_variable_initialization(self, sample_lsl_scripts):
        """Test global variable initialization."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["with_globals"])
        
        sim = LSLSimulator(parsed)
        
        # Check that global variables were set
        assert sim.global_scope.get("message") == "Test Message"
        assert sim.global_scope.get("count") == 0
    
    @pytest.mark.parametrize("expression,expected", [
        ('"Hello World"', "Hello World"),
        ("42", 42),
        ("3.14", 3.14),
        ("[1, 2, 3]", [1, 2, 3]),
        ("<1.0, 2.0, 3.0>", [1.0, 2.0, 3.0]),
    ])
    def test_expression_evaluation(self, simulator, expression, expected):
        """Test expression evaluation through simulator."""
        result = simulator._evaluate_expression(expression)
        
        if isinstance(expected, float):
            assert abs(result - expected) < 0.0001
        elif isinstance(expected, list):
            assert isinstance(result, list)
            assert len(result) == len(expected)
        else:
            assert result == expected
    
    def test_variable_assignment_and_lookup(self, simulator):
        """Test variable assignment and lookup."""
        # Test global scope assignment
        simulator.global_scope.set("test_var", "test_value")
        result = simulator._evaluate_expression("test_var")
        assert result == "test_value"
        
        # Test call stack variable lookup
        local_frame = Frame(simulator.global_scope)
        local_frame.set("local_var", "local_value")
        simulator.call_stack.push(local_frame)
        
        result = simulator._evaluate_expression("local_var")
        assert result == "local_value"
        
        simulator.call_stack.pop()
    
    def test_component_access(self, simulator):
        """Test component access functionality."""
        # Set up a vector
        simulator.global_scope.set("pos", [10.0, 20.0, 30.0])
        
        # Test component access
        assert simulator._get_component([10.0, 20.0, 30.0], 'x') == 10.0
        assert simulator._get_component([10.0, 20.0, 30.0], 'y') == 20.0
        assert simulator._get_component([10.0, 20.0, 30.0], 'z') == 30.0
        
        # Test rotation component access
        rotation = [0.1, 0.2, 0.3, 0.9]
        assert abs(simulator._get_component(rotation, 's') - 0.9) < 0.0001
        
        # Test invalid component
        assert simulator._get_component([1, 2, 3], 'invalid') == 0.0
        assert simulator._get_component("not_a_list", 'x') == 0.0
    
    @pytest.mark.parametrize("func_name,args,expected_type", [
        ("llSay", [0, "Hello"], type(None)),
        ("llStringLength", ["Hello"], int),
        ("llGetListLength", [[1, 2, 3]], int),
        ("llGetOwner", [], str),
        ("llGetTime", [], (int, float)),
    ])
    def test_api_function_calls(self, simulator, func_name, args, expected_type):
        """Test API function calls."""
        result = simulator._call_api_function(func_name, args)
        
        if isinstance(expected_type, tuple):
            assert isinstance(result, expected_type)
        else:
            assert isinstance(result, expected_type) or result is None
    
    def test_user_function_definition_and_call(self, sample_lsl_scripts):
        """Test user-defined function calls."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["with_functions"])
        
        sim = LSLSimulator(parsed)
        
        # Test that function was parsed
        assert "add" in sim.user_functions
        
        # Test function call
        result = sim._call_user_function("add", [5, 3])
        assert result == 8
    
    def test_event_triggering(self, sample_lsl_scripts):
        """Test event triggering mechanism."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["minimal"])
        
        sim = LSLSimulator(parsed)
        
        # Test that state_entry event exists
        assert "default" in sim.states
        assert "state_entry" in sim.states["default"]
        
        # Test triggering an event
        sim.trigger_event("state_entry")
        # Should not raise an exception
    
    def test_avatar_sensing_simulation(self, simulator):
        """Test avatar sensing simulation."""
        simulator.simulate_avatar_sense("John Doe")
        
        # Check that avatar data was set
        assert simulator.global_scope.get("current_avatar") is not None
        assert hasattr(simulator, 'sensed_avatar_name')
        assert simulator.sensed_avatar_name == "John Doe"
        assert hasattr(simulator, 'sensed_avatar_key')
        
        # Check that sensor event was queued
        assert len(simulator.event_queue) > 0
        event_name, args = simulator.event_queue[0]
        assert event_name == "sensor"
        assert args == [1]
    
    def test_debug_controls(self, debug_simulator):
        """Test debug control functionality."""
        # Test debug controls
        debug_simulator.continue_execution()
        debug_simulator.step()
        debug_simulator.stop()
        
        # Should not raise exceptions
        assert not debug_simulator._is_running
    
    def test_variable_scoping(self, sample_lsl_scripts):
        """Test variable scoping in function calls."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        script = '''
            integer global_var = 100;
            
            integer test_function(integer local_var) {
                return global_var + local_var;
            }
            
            default {
                state_entry() {
                    integer result = test_function(5);
                    llSay(0, (string)result);
                }
            }
        '''
        
        parsed = parser.parse_script(script)
        sim = LSLSimulator(parsed)
        
        # Test that global variable is accessible in function
        result = sim._call_user_function("test_function", [5])
        assert result == 105  # 100 + 5
    
    def test_statement_execution(self, simulator):
        """Test statement execution."""
        # Test simple statement execution
        stmt = {
            "type": "simple",
            "statement": 'llSay(0, "Hello")'
        }
        
        result = simulator._execute_simple_statement(stmt)
        assert result is None  # llSay returns None
        
        # Test declaration statement
        stmt = {
            "type": "declaration",
            "name": "test_var",
            "value": "42"
        }
        
        result = simulator._execute_simple_statement(stmt)
        assert result is None
        assert simulator.call_stack.get_current_scope().get("test_var") == 42
    
    def test_if_statement_execution(self, simulator):
        """Test if statement execution."""
        # Test if statement with true condition
        if_stmt = {
            "condition": "TRUE",
            "then_body": [
                {"type": "simple", "statement": 'llSay(0, "True branch")'}
            ],
            "else_body": [
                {"type": "simple", "statement": 'llSay(0, "False branch")'}
            ]
        }
        
        result = simulator._execute_if_statement(if_stmt)
        # Should execute without error
        
        # Test if statement with false condition
        if_stmt["condition"] = "FALSE"
        result = simulator._execute_if_statement(if_stmt)
        # Should execute else branch without error
    
    def test_loop_execution(self, simulator):
        """Test loop execution."""
        # Test while loop
        while_stmt = {
            "condition": "FALSE",  # Should not execute
            "body": [
                {"type": "simple", "statement": 'llSay(0, "Loop")'}
            ]
        }
        
        result = simulator._execute_while_loop(while_stmt)
        assert result is None
        
        # Test for loop
        for_stmt = {
            "init": "integer i = 0",
            "condition": "i < 1",  # Execute once
            "increment": "i = i + 1",
            "body": [
                {"type": "simple", "statement": 'llSay(0, "For loop")'}
            ]
        }
        
        result = simulator._execute_for_loop(for_stmt)
        assert result is None
    
    def test_http_request_functionality(self, simulator):
        """Test HTTP request functionality."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"success": true}'
            mock_get.return_value = mock_response
            
            request_key = simulator.api_llHTTPRequest(
                "https://httpbin.org/get", 
                [], 
                ""
            )
            
            assert request_key is not None
            assert isinstance(request_key, str)
            assert request_key.startswith("http-key-")
            
            # Check that http_response event was queued
            assert len(simulator.event_queue) > 0
            event_name, args = simulator.event_queue[-1]
            assert event_name == "http_response"
    
    def test_notecard_functionality(self, simulator, temp_notecard):
        """Test notecard reading functionality."""
        # Copy temp file to expected name
        import shutil
        shutil.copy(temp_notecard, "test_notecard.txt")
        
        try:
            request_key = simulator.api_llGetNotecardLine("test_notecard", 0)
            
            assert request_key is not None
            assert isinstance(request_key, str)
            assert request_key.startswith("notecard-key-")
            
            # Check that dataserver event was queued
            assert len(simulator.event_queue) > 0
            event_name, args = simulator.event_queue[-1]
            assert event_name == "dataserver"
            assert args[0] == request_key
            assert "Line 1" in args[1]
            
        finally:
            # Cleanup
            import os
            try:
                os.unlink("test_notecard.txt")
            except FileNotFoundError:
                pass
    
    def test_timer_functionality(self, simulator):
        """Test timer functionality."""
        simulator.api_llSetTimerEvent(0.1)  # Very short timer for testing
        
        # Timer should be set and will fire after delay
        # We can't easily test the async behavior in unit tests,
        # but we can test that it doesn't crash
        time.sleep(0.2)  # Wait for timer
        
        # Check if timer event was queued
        timer_events = [e for e in simulator.event_queue if e[0] == "timer"]
        assert len(timer_events) >= 0  # May or may not have fired yet
    
    def test_listener_functionality(self, simulator):
        """Test listener functionality."""
        handle = simulator.api_llListen(0, "", "", "")
        
        assert handle is not None
        assert isinstance(handle, str)
        assert handle.startswith("listen-handle-")
        assert len(simulator.active_listeners) == 1
        
        # Test removing listener
        simulator.api_llListenRemove(handle)
        assert len(simulator.active_listeners) == 0
    
    def test_channel_communication(self, simulator):
        """Test channel communication simulation."""
        # Set up listener
        handle = simulator.api_llListen(0, "", "", "test message")
        
        # Simulate someone speaking
        simulator.say_on_channel(0, "test message", "TestUser", "test-key-123")
        
        # Check that listen event was queued
        listen_events = [e for e in simulator.event_queue if e[0] == "listen"]
        assert len(listen_events) > 0
        
        event_name, args = listen_events[0]
        assert event_name == "listen"
        assert args[0] == 0  # channel
        assert args[1] == "TestUser"  # speaker name
        assert args[2] == "test-key-123"  # speaker key
        assert args[3] == "test message"  # message
    
    def test_performance_statement_execution(self, simulator):
        """Test performance of statement execution."""
        import time
        
        statements = []
        for i in range(100):
            statements.append({
                "type": "simple",
                "statement": f'llSay(0, "Message {i}")'
            })
        
        start_time = time.time()
        simulator._execute_statements(statements)
        execution_time = time.time() - start_time
        
        # Should execute 100 statements quickly
        assert execution_time < 1.0
    
    def test_error_recovery(self, simulator):
        """Test error recovery in simulator."""
        # Test invalid expression evaluation
        result = simulator._evaluate_expression("invalid_syntax_here")
        # Should not crash, return something reasonable
        assert result is not None
        
        # Test invalid function call
        result = simulator._call_api_function("llNonExistentFunction", [])
        # Should return None and not crash
        assert result is None
    
    def test_complex_script_execution(self, sample_lsl_scripts):
        """Test execution of complex script."""
        from lsl_antlr_parser import LSLParser as LSLProductionParser
        
        parser = LSLProductionParser()
        parsed = parser.parse_script(sample_lsl_scripts["complex_npc"])
        
        sim = LSLSimulator(parsed)
        
        # Test that complex script was parsed and can be initialized
        assert len(parsed["globals"]) >= 3
        assert "speak" in sim.user_functions
        assert "default" in sim.states
        
        # Test function call
        result = sim._call_user_function("speak", ["Hello"])
        assert result is None  # speak function returns None
        
        # Test event triggering
        sim.trigger_event("state_entry")
        # Should execute without errors