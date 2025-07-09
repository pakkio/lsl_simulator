#!/usr/bin/env python3
"""
Comprehensive unit tests for LSL simulator components
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch

from experimental.lsl_antlr_parser import LSLParser, LSLLiteral, LSLBinaryOp, LSLFunctionCall, LSLVectorLiteral
from experimental.lsl_simple_evaluator import LSLSimpleEvaluator
from experimental.lsl_core_engine import LSLCoreEngine
from lsl_debug_layer import LSLDebugLayer
from experimental.lsl_simulator_new import LSLSimulator, parse_script

class TestLSLParser(unittest.TestCase):
    """Test the ANTLR4 parser"""
    
    def setUp(self):
        self.parser = LSLParser()
    
    def test_parse_simple_script(self):
        """Test parsing a simple script"""
        script = '''
        default {
            state_entry() {
                llSay(0, "Hello World");
            }
        }
        '''
        
        ast = self.parser.parse(script)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.states), 1)
        self.assertEqual(ast.states[0].name, "default")
        self.assertEqual(len(ast.states[0].events), 1)
        self.assertEqual(ast.states[0].events[0].event_name, "state_entry")
    
    def test_parse_global_variables(self):
        """Test parsing global variables"""
        script = '''
        integer count = 0;
        string message = "test";
        vector pos = <1.0, 2.0, 3.0>;
        
        default {
            state_entry() {
                count = 1;
            }
        }
        '''
        
        ast = self.parser.parse(script)
        self.assertEqual(len(ast.globals), 3)
        self.assertEqual(ast.globals[0].name, "count")
        self.assertEqual(ast.globals[1].name, "message")
        self.assertEqual(ast.globals[2].name, "pos")
    
    def test_parse_expressions(self):
        """Test parsing various expressions"""
        # Vector literal
        expr = self.parser._parse_expression('<1.0, 2.0, 3.0>')
        self.assertIsInstance(expr, LSLVectorLiteral)
        
        # Binary operation
        expr = self.parser._parse_expression('a + b')
        self.assertIsInstance(expr, LSLBinaryOp)
        self.assertEqual(expr.operator, '+')
        
        # Function call
        expr = self.parser._parse_expression('llSay(0, "hello")')
        self.assertIsInstance(expr, LSLFunctionCall)
        self.assertEqual(expr.function_name, 'llSay')
        self.assertEqual(len(expr.arguments), 2)
        
        # Literal
        expr = self.parser._parse_expression('42')
        self.assertIsInstance(expr, LSLLiteral)
        self.assertEqual(expr.value, 42)
    
    def test_parse_user_functions(self):
        """Test parsing user-defined functions"""
        script = '''
        integer add(integer a, integer b) {
            return a + b;
        }
        
        default {
            state_entry() {
                integer result = add(1, 2);
            }
        }
        '''
        
        ast = self.parser.parse(script)
        self.assertEqual(len(ast.functions), 1)
        self.assertEqual(ast.functions[0].name, "add")
        self.assertEqual(ast.functions[0].return_type, "integer")
        self.assertEqual(len(ast.functions[0].parameters), 2)
    
    def test_parse_complex_expressions(self):
        """Test parsing complex expressions with precedence"""
        # Test operator precedence
        expr = self.parser._parse_expression('a + b * c')
        self.assertIsInstance(expr, LSLBinaryOp)
        self.assertEqual(expr.operator, '+')
        self.assertIsInstance(expr.right, LSLBinaryOp)
        self.assertEqual(expr.right.operator, '*')
        
        # Test parentheses
        expr = self.parser._parse_expression('(a + b) * c')
        self.assertIsInstance(expr, LSLBinaryOp)
        self.assertEqual(expr.operator, '*')
        self.assertIsInstance(expr.left, LSLBinaryOp)
        self.assertEqual(expr.left.operator, '+')


class TestLSLSimpleEvaluator(unittest.TestCase):
    """Test the simplified evaluator"""
    
    def setUp(self):
        self.mock_simulator = Mock()
        self.mock_simulator.call_function = Mock(return_value=None)
        self.mock_simulator.call_stack = Mock()
        self.mock_simulator.call_stack.find_variable = Mock(return_value=None)
        self.mock_simulator.global_scope = Mock()
        self.mock_simulator.global_scope.get = Mock(return_value=None)
        
        self.evaluator = LSLSimpleEvaluator(self.mock_simulator)
    
    def test_evaluate_literals(self):
        """Test evaluating literal values"""
        # Integer
        literal = LSLLiteral(42, 'integer')
        result = self.evaluator.evaluate(literal)
        self.assertEqual(result, 42)
        
        # String
        literal = LSLLiteral("hello", 'string')
        result = self.evaluator.evaluate(literal)
        self.assertEqual(result, "hello")
        
        # Float
        literal = LSLLiteral(3.14, 'float')
        result = self.evaluator.evaluate(literal)
        self.assertEqual(result, 3.14)
    
    def test_evaluate_binary_operations(self):
        """Test evaluating binary operations"""
        # Addition
        left = LSLLiteral(5, 'integer')
        right = LSLLiteral(3, 'integer')
        expr = LSLBinaryOp(left, '+', right)
        result = self.evaluator.evaluate(expr)
        self.assertEqual(result, 8)
        
        # String concatenation
        left = LSLLiteral("hello", 'string')
        right = LSLLiteral(" world", 'string')
        expr = LSLBinaryOp(left, '+', right)
        result = self.evaluator.evaluate(expr)
        self.assertEqual(result, "hello world")
        
        # Comparison
        left = LSLLiteral(5, 'integer')
        right = LSLLiteral(3, 'integer')
        expr = LSLBinaryOp(left, '>', right)
        result = self.evaluator.evaluate(expr)
        self.assertTrue(result)
    
    def test_evaluate_vector_operations(self):
        """Test vector operations"""
        # Vector literal
        x = LSLLiteral(1.0, 'float')
        y = LSLLiteral(2.0, 'float')
        z = LSLLiteral(3.0, 'float')
        vector = LSLVectorLiteral(x, y, z)
        result = self.evaluator.evaluate(vector)
        self.assertEqual(result, [1.0, 2.0, 3.0])
        
        # Vector addition
        vec1 = LSLVectorLiteral(LSLLiteral(1.0, 'float'), LSLLiteral(2.0, 'float'), LSLLiteral(3.0, 'float'))
        vec2 = LSLVectorLiteral(LSLLiteral(4.0, 'float'), LSLLiteral(5.0, 'float'), LSLLiteral(6.0, 'float'))
        expr = LSLBinaryOp(vec1, '+', vec2)
        result = self.evaluator.evaluate(expr)
        self.assertEqual(result, [5.0, 7.0, 9.0])
    
    def test_function_calls(self):
        """Test function call evaluation"""
        arg1 = LSLLiteral(0, 'integer')
        arg2 = LSLLiteral("test", 'string')
        func_call = LSLFunctionCall('llSay', [arg1, arg2])
        
        self.evaluator.evaluate(func_call)
        self.mock_simulator.call_function.assert_called_once_with('llSay', [0, "test"])
    
    def test_type_conversions(self):
        """Test type conversion methods"""
        # String to number
        self.assertEqual(self.evaluator._to_number("42"), 42.0)
        self.assertEqual(self.evaluator._to_number("3.14"), 3.14)
        self.assertEqual(self.evaluator._to_number("invalid"), 0.0)
        
        # Number to string
        self.assertEqual(self.evaluator._to_string(42), "42")
        self.assertEqual(self.evaluator._to_string(3.14), "3.14")
        
        # Vector to string
        self.assertEqual(self.evaluator._to_string([1.0, 2.0, 3.0]), "<1.0, 2.0, 3.0>")
        
        # Truthiness
        self.assertTrue(self.evaluator._is_truthy(1))
        self.assertTrue(self.evaluator._is_truthy("hello"))
        self.assertFalse(self.evaluator._is_truthy(0))
        self.assertFalse(self.evaluator._is_truthy(""))


class TestLSLCoreEngine(unittest.TestCase):
    """Test the core engine"""
    
    def test_simple_script_execution(self):
        """Test executing a simple script"""
        script = '''
        default {
            state_entry() {
                llSay(0, "Hello World");
            }
        }
        '''
        
        engine = LSLCoreEngine(script)
        self.assertIsNotNone(engine)
        self.assertEqual(engine.current_state, "default")
        self.assertTrue(engine.is_running())
    
    def test_global_variables(self):
        """Test global variable initialization"""
        script = '''
        integer count = 42;
        string message = "test";
        
        default {
            state_entry() {
                llSay(0, message);
            }
        }
        '''
        
        engine = LSLCoreEngine(script)
        self.assertEqual(engine.global_scope.get("count"), 42)
        self.assertEqual(engine.global_scope.get("message"), "test")
    
    def test_built_in_functions(self):
        """Test built-in function calls"""
        script = '''
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        engine = LSLCoreEngine(script)
        
        # Test llSay
        with patch('builtins.print') as mock_print:
            result = engine.call_function('llSay', [0, "test"])
            mock_print.assert_called_with("[0] test")
        
        # Test llGetTime
        result = engine.call_function('llGetTime', [])
        self.assertIsInstance(result, float)
        
        # Test llList2String
        result = engine.call_function('llList2String', [["a", "b", "c"], 1])
        self.assertEqual(result, "b")
    
    def test_lsl_constants(self):
        """Test LSL constants are initialized"""
        script = '''
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        engine = LSLCoreEngine(script)
        self.assertEqual(engine.global_scope.get("TRUE"), 1)
        self.assertEqual(engine.global_scope.get("FALSE"), 0)
        self.assertAlmostEqual(engine.global_scope.get("PI"), 3.141592653589793)
        self.assertEqual(engine.global_scope.get("NULL_KEY"), "00000000-0000-0000-0000-000000000000")


class TestLSLDebugLayer(unittest.TestCase):
    """Test the debug layer"""
    
    def test_debug_initialization(self):
        """Test debug layer initialization"""
        script = '''
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        debug_layer = LSLDebugLayer(script, debug_mode=True)
        self.assertTrue(debug_layer.debug_mode)
        self.assertEqual(len(debug_layer.source_lines), 6)  # Approximate
        self.assertIsNotNone(debug_layer.core)
    
    def test_breakpoint_management(self):
        """Test breakpoint management"""
        script = '''
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        debug_layer = LSLDebugLayer(script, debug_mode=True)
        
        # Add breakpoint
        debug_layer.set_breakpoint(3)
        self.assertIn(3, debug_layer.breakpoints)
        
        # Remove breakpoint
        debug_layer.remove_breakpoint(3)
        self.assertNotIn(3, debug_layer.breakpoints)
    
    def test_execution_control(self):
        """Test execution control methods"""
        script = '''
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        debug_layer = LSLDebugLayer(script, debug_mode=True)
        
        # Test pause/continue
        debug_layer.pause_execution()
        self.assertFalse(debug_layer.execution_paused.is_set())
        
        debug_layer.continue_execution()
        self.assertTrue(debug_layer.execution_paused.is_set())
        
        # Test single step
        debug_layer.step_into()
        self.assertTrue(debug_layer.single_step)
    
    def test_variable_inspection(self):
        """Test variable inspection"""
        script = '''
        integer test_var = 42;
        
        default {
            state_entry() {
                llSay(0, "test");
            }
        }
        '''
        
        debug_layer = LSLDebugLayer(script, debug_mode=True)
        variables = debug_layer.get_variables()
        self.assertIn("test_var", variables)
        self.assertEqual(variables["test_var"], 42)


class TestLSLSimulator(unittest.TestCase):
    """Test the complete simulator"""
    
    def test_simple_simulation(self):
        """Test running a simple simulation"""
        script = '''
        default {
            state_entry() {
                llSay(0, "Hello World");
            }
        }
        '''
        
        simulator = LSLSimulator(script)
        self.assertIsNotNone(simulator)
        self.assertTrue(simulator.is_running())
        self.assertEqual(simulator.current_state, "default")
    
    def test_timer_events(self):
        """Test timer events"""
        script = '''
        default {
            state_entry() {
                llSetTimerEvent(0.1);
            }
            
            timer() {
                llSay(0, "Timer fired");
            }
        }
        '''
        
        simulator = LSLSimulator(script)
        
        # Trigger timer setup
        simulator.call_function('llSetTimerEvent', [0.1])
        
        # Wait for timer
        time.sleep(0.2)
        
        # Timer should have fired
        self.assertIsNotNone(simulator.timer_thread)
    
    def test_event_simulation(self):
        """Test event simulation methods"""
        script = '''
        default {
            touch_start(integer total_number) {
                llSay(0, "Touched!");
            }
            
            collision_start(integer num_detected) {
                llSay(0, "Collision!");
            }
        }
        '''
        
        simulator = LSLSimulator(script)
        
        # Simulate touch
        simulator.simulate_touch()
        
        # Simulate collision
        simulator.simulate_collision()
        
        # These should not raise exceptions
        self.assertTrue(simulator.is_running())
    
    def test_listener_management(self):
        """Test chat listener management"""
        script = '''
        default {
            state_entry() {
                llListen(0, "", "", "");
            }
            
            listen(integer channel, string name, key id, string message) {
                llSay(0, "Heard: " + message);
            }
        }
        '''
        
        simulator = LSLSimulator(script)
        
        # Add listener
        handle = simulator.call_function('llListen', [0, "", "", ""])
        self.assertIsInstance(handle, int)
        self.assertEqual(len(simulator.active_listeners), 1)
        
        # Remove listener
        simulator.call_function('llListenRemove', [handle])
        self.assertEqual(len(simulator.active_listeners), 0)
    
    def test_debug_mode(self):
        """Test debug mode functionality"""
        script = '''
        default {
            state_entry() {
                llSay(0, "Debug test");
            }
        }
        '''
        
        simulator = LSLSimulator(script, debug_mode=True)
        self.assertTrue(simulator.debug_mode)
        
        # Test debug methods
        simulator.set_breakpoint(3)
        variables = simulator.get_variables()
        self.assertIsInstance(variables, dict)
        
        execution_info = simulator.get_execution_info()
        self.assertIsInstance(execution_info, dict)
    
    def test_compatibility_functions(self):
        """Test compatibility functions"""
        script = '''
        integer count = 0;
        
        default {
            state_entry() {
                count = 1;
            }
        }
        '''
        
        # Test parse_script function
        parsed = parse_script(script)
        self.assertIsInstance(parsed, dict)
        self.assertIn('globals', parsed)
        self.assertIn('functions', parsed)
        self.assertIn('states', parsed)
        
        # Test global variable parsing
        self.assertEqual(len(parsed['globals']), 1)
        self.assertEqual(parsed['globals'][0]['name'], 'count')


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_complete_npc_simulation(self):
        """Test a complete NPC-like simulation"""
        script = '''
        string npc_name = "TestBot";
        integer active = TRUE;
        
        default {
            state_entry() {
                llSay(0, "NPC " + npc_name + " online");
                llSetTimerEvent(1.0);
                llListen(0, "", "", "");
            }
            
            timer() {
                if (active) {
                    llSay(0, "NPC heartbeat");
                }
            }
            
            listen(integer channel, string name, key id, string message) {
                if (message == "hello") {
                    llSay(0, "Hello " + name + "!");
                }
            }
            
            touch_start(integer total_number) {
                llSay(0, "Don't touch me!");
            }
        }
        '''
        
        simulator = LSLSimulator(script)
        
        # Test initial state
        self.assertEqual(simulator.global_scope.get("npc_name"), "TestBot")
        self.assertEqual(simulator.global_scope.get("active"), 1)
        
        # Test events
        simulator.simulate_touch()
        simulator.simulate_chat(0, "User", "test-id", "hello")
        
        # Should not raise exceptions
        self.assertTrue(simulator.is_running())
        
        # Clean up
        simulator.stop()
    
    def test_performance_basic(self):
        """Basic performance test"""
        script = '''
        integer i;
        
        default {
            state_entry() {
                for (i = 0; i < 100; i++) {
                    llSay(0, "Count: " + (string)i);
                }
            }
        }
        '''
        
        start_time = time.time()
        simulator = LSLSimulator(script)
        end_time = time.time()
        
        # Should complete quickly
        self.assertLess(end_time - start_time, 1.0)
        
        simulator.stop()


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)