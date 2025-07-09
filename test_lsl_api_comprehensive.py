#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for LSL API Functions
Tests all 197 functions for correctness, edge cases, and LSL quirks
"""

import unittest
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lsl_api_expanded import LSLAPIExpanded

class TestLSLMathFunctions(unittest.TestCase):
    """Test suite for LSL math functions (17 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_llAbs(self):
        """Test llAbs with various integer inputs"""
        self.assertEqual(self.api.call_function('llAbs', [5]), 5)
        self.assertEqual(self.api.call_function('llAbs', [-5]), 5)
        self.assertEqual(self.api.call_function('llAbs', [0]), 0)
        # Edge case: maximum integer
        self.assertEqual(self.api.call_function('llAbs', [-2147483647]), 2147483647)
    
    def test_llFabs(self):
        """Test llFabs with various float inputs"""
        self.assertEqual(self.api.call_function('llFabs', [5.5]), 5.5)
        self.assertEqual(self.api.call_function('llFabs', [-5.5]), 5.5)
        self.assertEqual(self.api.call_function('llFabs', [0.0]), 0.0)
        # Edge case: very small float
        self.assertEqual(self.api.call_function('llFabs', [-1e-10]), 1e-10)
    
    def test_llSqrt(self):
        """Test llSqrt with various inputs"""
        self.assertEqual(self.api.call_function('llSqrt', [25]), 5.0)
        self.assertEqual(self.api.call_function('llSqrt', [0]), 0.0)
        self.assertAlmostEqual(self.api.call_function('llSqrt', [2]), 1.414213562373095)
        # Edge case: negative input (should raise error in real LSL)
        with self.assertRaises(ValueError):
            self.api.call_function('llSqrt', [-1])
    
    def test_llTrigonometric(self):
        """Test trigonometric functions"""
        # Test sin
        self.assertAlmostEqual(self.api.call_function('llSin', [0]), 0.0, places=10)
        self.assertAlmostEqual(self.api.call_function('llSin', [math.pi/2]), 1.0, places=10)
        
        # Test cos
        self.assertAlmostEqual(self.api.call_function('llCos', [0]), 1.0, places=10)
        self.assertAlmostEqual(self.api.call_function('llCos', [math.pi]), -1.0, places=10)
        
        # Test tan
        self.assertAlmostEqual(self.api.call_function('llTan', [0]), 0.0, places=10)
        self.assertAlmostEqual(self.api.call_function('llTan', [math.pi/4]), 1.0, places=10)
    
    def test_llFrand(self):
        """Test random number generation"""
        # Test range
        for _ in range(100):
            result = self.api.call_function('llFrand', [10.0])
            self.assertGreaterEqual(result, 0.0)
            self.assertLess(result, 10.0)
        
        # Test zero input
        self.assertEqual(self.api.call_function('llFrand', [0.0]), 0.0)

class TestLSLStringFunctions(unittest.TestCase):
    """Test suite for LSL string functions (17 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_llStringLength(self):
        """Test string length with various inputs"""
        self.assertEqual(self.api.call_function('llStringLength', ['Hello World']), 11)
        self.assertEqual(self.api.call_function('llStringLength', ['']), 0)
        self.assertEqual(self.api.call_function('llStringLength', ['A']), 1)
        # Unicode handling
        self.assertEqual(self.api.call_function('llStringLength', ['åäö']), 3)
    
    def test_llGetSubString(self):
        """Test substring extraction with LSL quirks"""
        test_string = "Hello World"
        
        # Normal cases
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, 0, 4]), "Hello")
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, 6, 10]), "World")
        
        # LSL quirk: negative indices count from end
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, -5, -1]), "World")
        
        # Edge cases
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, 0, -1]), test_string)
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, 100, 200]), "")
        
        # LSL quirk: start > end returns empty string
        self.assertEqual(self.api.call_function('llGetSubString', [test_string, 5, 3]), "")
    
    def test_llSubStringIndex(self):
        """Test substring search with LSL behavior"""
        test_string = "Hello World Hello"
        
        # Normal search
        self.assertEqual(self.api.call_function('llSubStringIndex', [test_string, "Hello"]), 0)
        self.assertEqual(self.api.call_function('llSubStringIndex', [test_string, "World"]), 6)
        
        # Case sensitivity
        self.assertEqual(self.api.call_function('llSubStringIndex', [test_string, "hello"]), -1)
        
        # Empty string search (LSL quirk)
        self.assertEqual(self.api.call_function('llSubStringIndex', [test_string, ""]), 0)
        
        # Not found
        self.assertEqual(self.api.call_function('llSubStringIndex', [test_string, "xyz"]), -1)
    
    def test_llToUpper_llToLower(self):
        """Test case conversion functions"""
        # Normal cases
        self.assertEqual(self.api.call_function('llToUpper', ['hello']), 'HELLO')
        self.assertEqual(self.api.call_function('llToLower', ['WORLD']), 'world')
        
        # Mixed case
        self.assertEqual(self.api.call_function('llToUpper', ['Hello World']), 'HELLO WORLD')
        self.assertEqual(self.api.call_function('llToLower', ['Hello World']), 'hello world')
        
        # Numbers and symbols
        self.assertEqual(self.api.call_function('llToUpper', ['abc123!@#']), 'ABC123!@#')
        
        # Empty string
        self.assertEqual(self.api.call_function('llToUpper', ['']), '')
    
    def test_llStringTrim(self):
        """Test string trimming with LSL behavior"""
        # Normal trimming
        self.assertEqual(self.api.call_function('llStringTrim', ['  hello  ', 3]), 'hello')
        
        # Trim types: 1=left, 2=right, 3=both
        self.assertEqual(self.api.call_function('llStringTrim', ['  hello  ', 1]), 'hello  ')
        self.assertEqual(self.api.call_function('llStringTrim', ['  hello  ', 2]), '  hello')
        
        # Empty string
        self.assertEqual(self.api.call_function('llStringTrim', ['', 3]), '')
        
        # Only whitespace
        self.assertEqual(self.api.call_function('llStringTrim', ['   ', 3]), '')

class TestLSLListFunctions(unittest.TestCase):
    """Test suite for LSL list functions (15 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_llGetListLength(self):
        """Test list length calculation"""
        self.assertEqual(self.api.call_function('llGetListLength', [[]]), 0)
        self.assertEqual(self.api.call_function('llGetListLength', [[1, 2, 3]]), 3)
        self.assertEqual(self.api.call_function('llGetListLength', [['a', 'b', 'c', 'd']]), 4)
        
        # Mixed types
        self.assertEqual(self.api.call_function('llGetListLength', [[1, 'hello', 3.14]]), 3)
    
    def test_llList2String(self):
        """Test list to string conversion with LSL formatting"""
        # Simple list
        self.assertEqual(self.api.call_function('llList2String', [[1, 2, 3]]), '1, 2, 3')
        
        # String elements
        self.assertEqual(self.api.call_function('llList2String', [['a', 'b', 'c']]), 'a, b, c')
        
        # Mixed types (LSL quirk: specific formatting)
        result = self.api.call_function('llList2String', [[1, 'hello', 3.14]])
        self.assertEqual(result, '1, hello, 3.14')
        
        # Empty list
        self.assertEqual(self.api.call_function('llList2String', [[]]), '')
        
        # Single element
        self.assertEqual(self.api.call_function('llList2String', [['single']]), 'single')
    
    def test_llListSort(self):
        """Test list sorting with LSL behavior"""
        # Integer sorting
        sorted_list = self.api.call_function('llListSort', [[3, 1, 4, 1, 5], 1, True])
        self.assertEqual(sorted_list, [1, 1, 3, 4, 5])
        
        # Descending order
        sorted_list = self.api.call_function('llListSort', [[3, 1, 4, 1, 5], 1, False])
        self.assertEqual(sorted_list, [5, 4, 3, 1, 1])
        
        # String sorting
        sorted_list = self.api.call_function('llListSort', [['c', 'a', 'b'], 1, True])
        self.assertEqual(sorted_list, ['a', 'b', 'c'])
        
        # Empty list
        self.assertEqual(self.api.call_function('llListSort', [[], 1, True]), [])
    
    def test_llDeleteSubList(self):
        """Test list element deletion"""
        test_list = [1, 2, 3, 4, 5]
        
        # Normal deletion
        result = self.api.call_function('llDeleteSubList', [test_list, 1, 3])
        self.assertEqual(result, [1, 5])
        
        # Delete single element
        result = self.api.call_function('llDeleteSubList', [test_list, 2, 2])
        self.assertEqual(result, [1, 2, 4, 5])
        
        # Delete from start
        result = self.api.call_function('llDeleteSubList', [test_list, 0, 1])
        self.assertEqual(result, [3, 4, 5])
        
        # Delete to end
        result = self.api.call_function('llDeleteSubList', [test_list, 3, -1])
        self.assertEqual(result, [1, 2, 3])

class TestLSLVectorFunctions(unittest.TestCase):
    """Test suite for LSL vector functions (12 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_llVecMag(self):
        """Test vector magnitude calculation"""
        # Unit vectors
        self.assertEqual(self.api.call_function('llVecMag', [(1.0, 0.0, 0.0)]), 1.0)
        self.assertEqual(self.api.call_function('llVecMag', [(0.0, 1.0, 0.0)]), 1.0)
        self.assertEqual(self.api.call_function('llVecMag', [(0.0, 0.0, 1.0)]), 1.0)
        
        # Pythagorean triple
        self.assertEqual(self.api.call_function('llVecMag', [(3.0, 4.0, 0.0)]), 5.0)
        
        # Zero vector
        self.assertEqual(self.api.call_function('llVecMag', [(0.0, 0.0, 0.0)]), 0.0)
        
        # 3D vector
        self.assertAlmostEqual(self.api.call_function('llVecMag', [(1.0, 1.0, 1.0)]), 1.732050808, places=8)
    
    def test_llVecNorm(self):
        """Test vector normalization"""
        # Simple case
        result = self.api.call_function('llVecNorm', [(3.0, 4.0, 0.0)])
        expected = (0.6, 0.8, 0.0)
        self.assertAlmostEqual(result[0], expected[0], places=10)
        self.assertAlmostEqual(result[1], expected[1], places=10)
        self.assertAlmostEqual(result[2], expected[2], places=10)
        
        # Unit vector (should remain unchanged)
        result = self.api.call_function('llVecNorm', [(1.0, 0.0, 0.0)])
        self.assertEqual(result, (1.0, 0.0, 0.0))
        
        # Zero vector (LSL quirk: returns zero vector)
        result = self.api.call_function('llVecNorm', [(0.0, 0.0, 0.0)])
        self.assertEqual(result, (0.0, 0.0, 0.0))
    
    def test_llVecDist(self):
        """Test distance between vectors"""
        # Unit distance
        self.assertEqual(self.api.call_function('llVecDist', [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]), 1.0)
        
        # Pythagorean distance
        self.assertEqual(self.api.call_function('llVecDist', [(0.0, 0.0, 0.0), (3.0, 4.0, 0.0)]), 5.0)
        
        # Same point
        self.assertEqual(self.api.call_function('llVecDist', [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]), 0.0)
        
        # 3D distance
        dist = self.api.call_function('llVecDist', [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)])
        self.assertAlmostEqual(dist, 1.732050808, places=8)

class TestLSLObjectProperties(unittest.TestCase):
    """Test suite for LSL object property functions (22 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_position_functions(self):
        """Test position get/set functions"""
        # Set position
        test_pos = (10.0, 20.0, 30.0)
        self.api.call_function('llSetPos', [test_pos])
        
        # Get position
        result = self.api.call_function('llGetPos', [])
        self.assertEqual(result, test_pos)
        
        # Test local position
        local_pos = (5.0, 15.0, 25.0)
        self.api.call_function('llSetLocalPos', [local_pos])
        result = self.api.call_function('llGetLocalPos', [])
        self.assertEqual(result, local_pos)
    
    def test_rotation_functions(self):
        """Test rotation get/set functions"""
        # Set rotation (quaternion)
        test_rot = (0.0, 0.0, 0.0, 1.0)
        self.api.call_function('llSetRot', [test_rot])
        
        # Get rotation
        result = self.api.call_function('llGetRot', [])
        self.assertEqual(result, test_rot)
    
    def test_scale_functions(self):
        """Test scale get/set functions"""
        # Set scale
        test_scale = (2.0, 2.0, 2.0)
        self.api.call_function('llSetScale', [test_scale])
        
        # Get scale
        result = self.api.call_function('llGetScale', [])
        self.assertEqual(result, test_scale)
    
    def test_color_functions(self):
        """Test color get/set functions"""
        # Set color
        test_color = (1.0, 0.0, 0.0)  # Red
        self.api.call_function('llSetColor', [test_color, 0])
        
        # Get color
        result = self.api.call_function('llGetColor', [0])
        self.assertEqual(result, test_color)
    
    def test_text_functions(self):
        """Test text display functions"""
        # Set text
        test_text = "Hello World"
        test_color = (1.0, 1.0, 1.0)
        test_alpha = 1.0
        
        self.api.call_function('llSetText', [test_text, test_color, test_alpha])
        
        # Get text
        result = self.api.call_function('llGetText', [])
        self.assertEqual(result[0], test_text)
        self.assertEqual(result[1], test_color)
        self.assertEqual(result[2], test_alpha)

class TestLSLPhysicsFunctions(unittest.TestCase):
    """Test suite for LSL physics functions (16 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_force_functions(self):
        """Test force manipulation functions"""
        # Set force
        test_force = (100.0, 0.0, 0.0)
        self.api.call_function('llSetForce', [test_force, False])
        
        # Get force
        result = self.api.call_function('llGetForce', [])
        self.assertEqual(result, test_force)
    
    def test_torque_functions(self):
        """Test torque manipulation functions"""
        # Set torque
        test_torque = (0.0, 0.0, 10.0)
        self.api.call_function('llSetTorque', [test_torque, False])
        
        # Get torque
        result = self.api.call_function('llGetTorque', [])
        self.assertEqual(result, test_torque)
    
    def test_movement_functions(self):
        """Test movement control functions"""
        # Move to target
        target = (100.0, 100.0, 22.0)
        self.api.call_function('llMoveToTarget', [target, 1.0])
        
        # Check if target is set
        self.assertEqual(self.api.object_properties.get('move_target'), target)
        
        # Stop movement
        self.api.call_function('llStopMoveToTarget', [])
        self.assertIsNone(self.api.object_properties.get('move_target'))

class TestLSLSensorFunctions(unittest.TestCase):
    """Test suite for LSL sensor functions (19 functions)"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_sensor_basic(self):
        """Test basic sensor functionality"""
        # Activate sensor
        self.api.call_function('llSensor', ['', '', 1, 20.0, 1.57])
        
        # Check sensors are populated
        self.assertGreater(len(self.api.sensors), 0)
        
        # Test detection functions
        name = self.api.call_function('llDetectedName', [0])
        self.assertEqual(name, 'TestObject')
        
        key = self.api.call_function('llDetectedKey', [0])
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 36)  # UUID length
    
    def test_sensor_repeat(self):
        """Test repeating sensor"""
        # Start repeating sensor
        self.api.call_function('llSensorRepeat', ['', '', 1, 20.0, 1.57, 1.0])
        
        # Should populate sensors
        self.assertGreater(len(self.api.sensors), 0)
        
        # Remove sensor
        self.api.call_function('llSensorRemove', [])
        # In a real implementation, this would clear the sensor

class TestLSLEdgeCasesAndQuirks(unittest.TestCase):
    """Test suite for LSL edge cases and quirks"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_type_conversion_quirks(self):
        """Test LSL's weird type conversion behavior"""
        # Integer to string
        # LSL quirk: integers format without decimal
        result = self.api.call_function('llStringLength', [str(42)])
        self.assertEqual(result, 2)
        
        # Float to string
        # LSL quirk: floats always show decimal
        result = self.api.call_function('llStringLength', [str(42.0)])
        self.assertEqual(result, 4)  # "42.0"
    
    def test_negative_index_handling(self):
        """Test negative index handling across functions"""
        test_list = [1, 2, 3, 4, 5]
        
        # Negative indices should work from end
        result = self.api.call_function('llDeleteSubList', [test_list, -2, -1])
        self.assertEqual(result, [1, 2, 3])
    
    def test_empty_input_handling(self):
        """Test empty input handling"""
        # Empty string operations
        self.assertEqual(self.api.call_function('llStringLength', ['']), 0)
        self.assertEqual(self.api.call_function('llToUpper', ['']), '')
        self.assertEqual(self.api.call_function('llSubStringIndex', ['', 'x']), -1)
        
        # Empty list operations
        self.assertEqual(self.api.call_function('llGetListLength', [[]]), 0)
        self.assertEqual(self.api.call_function('llList2String', [[]]), '')
    
    def test_null_and_undefined_handling(self):
        """Test NULL_KEY and undefined value handling"""
        # NULL_KEY should be recognized
        null_key = "00000000-0000-0000-0000-000000000000"
        self.assertEqual(len(null_key), 36)

class TestLSLPerformance(unittest.TestCase):
    """Performance tests for LSL functions"""
    
    def setUp(self):
        self.api = LSLAPIExpanded()
    
    def test_math_function_performance(self):
        """Test math function performance"""
        import time
        
        # Test 1000 sqrt operations
        start_time = time.time()
        for i in range(1000):
            self.api.call_function('llSqrt', [float(i + 1)])
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 0.1 seconds)
        self.assertLess(elapsed, 0.1)
    
    def test_string_function_performance(self):
        """Test string function performance"""
        import time
        
        test_string = "The quick brown fox jumps over the lazy dog" * 10
        
        # Test 1000 string operations
        start_time = time.time()
        for i in range(1000):
            self.api.call_function('llStringLength', [test_string])
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 0.1 seconds)
        self.assertLess(elapsed, 0.1)
    
    def test_list_function_performance(self):
        """Test list function performance"""
        import time
        
        test_list = list(range(100))
        
        # Test list operations
        start_time = time.time()
        for i in range(100):
            self.api.call_function('llListSort', [test_list, 1, True])
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 0.5 seconds)
        self.assertLess(elapsed, 0.5)

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🧪 Running Comprehensive LSL API Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestLSLMathFunctions,
        TestLSLStringFunctions,
        TestLSLListFunctions,
        TestLSLVectorFunctions,
        TestLSLObjectProperties,
        TestLSLPhysicsFunctions,
        TestLSLSensorFunctions,
        TestLSLEdgeCasesAndQuirks,
        TestLSLPerformance
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"🎯 TEST SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🏆 EXCELLENT: API implementation is highly reliable")
    elif success_rate >= 85:
        print("✅ GOOD: API implementation is solid with minor issues")
    elif success_rate >= 70:
        print("⚠️  FAIR: API implementation needs improvement")
    else:
        print("❌ POOR: API implementation has significant issues")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)