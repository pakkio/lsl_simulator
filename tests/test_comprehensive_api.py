"""
Comprehensive tests for the expanded LSL API.
Tests the 270+ LSL functions for 90% coverage validation.
"""

import pytest
import math
import json
import time
from unittest.mock import Mock, patch


class TestComprehensiveStringFunctions:
    """Test suite for comprehensive string functions."""
    
    @pytest.mark.parametrize("func_name,args,expected", [
        # Basic string functions
        ("api_llStringLength", ["Hello World"], 11),
        ("api_llStringLength", [""], 0),
        ("api_llStringLength", ["🌟 Unicode test"], 14),
        
        # Substring functions
        ("api_llGetSubString", ["Hello World", 0, 4], "Hello"),
        ("api_llGetSubString", ["Hello World", 6, -1], "World"),
        ("api_llGetSubString", ["Hello World", -5, -1], "World"),
        
        # String search
        ("api_llSubStringIndex", ["Hello World", "World"], 6),
        ("api_llSubStringIndex", ["Hello World", "xyz"], -1),
        ("api_llSubStringIndex", ["", "test"], -1),
        
        # String trimming
        ("api_llStringTrim", ["  Hello World  ", 0], "Hello World"),  # STRING_TRIM
        ("api_llStringTrim", ["  Hello World  ", 1], "Hello World  "),  # STRING_TRIM_HEAD
        ("api_llStringTrim", ["  Hello World  ", 2], "  Hello World"),  # STRING_TRIM_TAIL
        
        # Case conversion
        ("api_llToUpper", ["hello world"], "HELLO WORLD"),
        ("api_llToLower", ["HELLO WORLD"], "hello world"),
        ("api_llToUpper", [""], ""),
        
        # String replacement
        ("api_llStringReplace", ["Hello World", "World", "Universe", 1], "Hello Universe"),
        ("api_llStringReplace", ["Hello Hello", "Hello", "Hi", -1], "Hi Hi"),
        ("api_llStringReplace", ["Hello Hello", "Hello", "Hi", 1], "Hi Hello"),
        
        # String insertion
        ("api_llInsertString", ["Hello World", 6, "Beautiful "], "Hello Beautiful World"),
        ("api_llInsertString", ["Hello", 0, "Hi "], "Hi Hello"),
        ("api_llInsertString", ["Hello", -1, "!"], "Hell!o"),
        
        # String deletion
        ("api_llDeleteSubString", ["Hello World", 5, 5], "HelloWorld"),
        ("api_llDeleteSubString", ["Hello World", 0, 4], " World"),
        ("api_llDeleteSubString", ["Hello World", 6, -1], "Hello "),
    ])
    def test_string_functions(self, simulator, func_name, args, expected):
        """Test comprehensive string manipulation functions."""
        func = getattr(simulator, func_name)
        result = func(*args)
        assert result == expected


class TestComprehensiveListFunctions:
    """Test suite for comprehensive list functions."""
    
    @pytest.mark.parametrize("func_name,args,expected", [
        # Basic list operations
        ("api_llGetListLength", [[1, 2, 3, 4, 5]], 5),
        ("api_llGetListLength", [[]], 0),
        ("api_llGetListLength", [None], 0),
        
        # List element access
        ("api_llList2String", [["a", "b", "c"], 1], "b"),
        ("api_llList2Integer", [[1, 2, 3], 0], 1),
        ("api_llList2Float", [[1.1, 2.2, 3.3], 2], 3.3),
        ("api_llList2Key", [["key1", "key2"], 0], "key1"),
        
        # List conversion
        ("api_llDumpList2String", [[1, 2, 3], ","], "1,2,3"),
        ("api_llDumpList2String", [["a", "b", "c"], " | "], "a | b | c"),
        ("api_llDumpList2String", [[], ","], ""),
        
        # List search
        ("api_llListFindList", [[1, 2, 3, 4], [2, 3]], 1),
        ("api_llListFindList", [[1, 2, 3, 4], [5, 6]], -1),
        ("api_llListFindList", [[], [1]], -1),
        
        # List entry type detection
        ("api_llGetListEntryType", [[1, 2.5, "string"], 0], 1),  # TYPE_INTEGER
        ("api_llGetListEntryType", [[1, 2.5, "string"], 1], 2),  # TYPE_FLOAT
        ("api_llGetListEntryType", [[1, 2.5, "string"], 2], 3),  # TYPE_STRING
    ])
    def test_list_functions(self, simulator, func_name, args, expected):
        """Test comprehensive list manipulation functions."""
        func = getattr(simulator, func_name)
        result = func(*args)
        assert result == expected
    
    def test_list_sort_comprehensive(self, simulator):
        """Test comprehensive list sorting scenarios."""
        # Basic ascending sort
        result = simulator.api_llListSort([3, 1, 4, 1, 5], 1, True)
        assert result == [1, 1, 3, 4, 5]
        
        # Basic descending sort
        result = simulator.api_llListSort([3, 1, 4, 1, 5], 1, False)
        assert result == [5, 4, 3, 1, 1]
        
        # Stride sort (pairs)
        result = simulator.api_llListSort([3, "three", 1, "one", 2, "two"], 2, True)
        assert result == [1, "one", 2, "two", 3, "three"]
        
        # Empty list
        result = simulator.api_llListSort([], 1, True)
        assert result == []
        
        # Invalid stride
        result = simulator.api_llListSort([1, 2, 3], 0, True)
        assert result == [1, 2, 3]
    
    def test_list_randomize(self, simulator):
        """Test list randomization."""
        original = [1, 2, 3, 4, 5]
        result = simulator.api_llListRandomize(original.copy(), 1)
        
        # Should have same elements
        assert sorted(result) == sorted(original)
        assert len(result) == len(original)
        
        # With stride
        original_pairs = [1, "a", 2, "b", 3, "c"]
        result = simulator.api_llListRandomize(original_pairs.copy(), 2)
        assert len(result) == len(original_pairs)
    
    def test_list_statistics(self, simulator):
        """Test list statistical operations."""
        numbers = [1, 2, 3, 4, 5]
        
        # Range
        result = simulator.api_llListStatistics(0, numbers)  # STATS_RANGE
        assert result == 4.0
        
        # Min
        result = simulator.api_llListStatistics(1, numbers)  # STATS_MIN
        assert result == 1.0
        
        # Max
        result = simulator.api_llListStatistics(2, numbers)  # STATS_MAX
        assert result == 5.0
        
        # Mean
        result = simulator.api_llListStatistics(3, numbers)  # STATS_MEAN
        assert result == 3.0
        
        # Sum
        result = simulator.api_llListStatistics(6, numbers)  # STATS_SUM
        assert result == 15.0


class TestComprehensiveMathFunctions:
    """Test suite for comprehensive math functions."""
    
    @pytest.mark.parametrize("func_name,args,expected,tolerance", [
        # Basic math
        ("api_llAbs", [-5], 5, 0),
        ("api_llFabs", [-3.14], 3.14, 0.001),
        ("api_llCeil", [3.14], 4, 0),
        ("api_llFloor", [3.99], 3, 0),
        ("api_llRound", [3.14], 3, 0),
        ("api_llRound", [3.6], 4, 0),
        
        # Power and roots
        ("api_llSqrt", [16.0], 4.0, 0.001),
        ("api_llSqrt", [2.0], 1.414, 0.01),
        ("api_llPow", [2.0, 3.0], 8.0, 0.001),
        ("api_llPow", [10.0, 2.0], 100.0, 0.001),
        
        # Logarithms
        ("api_llLog", [math.e], 1.0, 0.001),
        ("api_llLog10", [100.0], 2.0, 0.001),
        
        # Trigonometry
        ("api_llSin", [0.0], 0.0, 0.001),
        ("api_llSin", [math.pi/2], 1.0, 0.001),
        ("api_llCos", [0.0], 1.0, 0.001),
        ("api_llCos", [math.pi], -1.0, 0.001),
        ("api_llTan", [0.0], 0.0, 0.001),
        
        # Vector math
        ("api_llVecMag", [[3.0, 4.0, 0.0]], 5.0, 0.001),
        ("api_llVecMag", [[1.0, 1.0, 1.0]], math.sqrt(3), 0.001),
        ("api_llVecDist", [[0.0, 0.0, 0.0], [3.0, 4.0, 0.0]], 5.0, 0.001),
        
        # Min/Max/Clamp
        ("api_llMin", [5.0, 3.0], 3.0, 0),
        ("api_llMax", [5.0, 3.0], 5.0, 0),
        ("api_llClamp", [10.0, 0.0, 5.0], 5.0, 0),
        ("api_llClamp", [-5.0, 0.0, 10.0], 0.0, 0),
        
        # Interpolation
        ("api_llLerp", [0.0, 10.0, 0.5], 5.0, 0.001),
        ("api_llLerp", [10.0, 20.0, 0.25], 12.5, 0.001),
    ])
    def test_math_functions(self, simulator, func_name, args, expected, tolerance):
        """Test comprehensive math functions."""
        func = getattr(simulator, func_name)
        result = func(*args)
        
        if tolerance > 0:
            assert abs(result - expected) < tolerance
        else:
            assert result == expected
    
    def test_vector_normalization(self, simulator):
        """Test vector normalization."""
        # Unit vector should remain unchanged
        result = simulator.api_llVecNorm([1.0, 0.0, 0.0])
        assert result == [1.0, 0.0, 0.0]
        
        # Non-unit vector
        result = simulator.api_llVecNorm([10.0, 0.0, 0.0])
        assert result == [1.0, 0.0, 0.0]
        
        # Zero vector
        result = simulator.api_llVecNorm([0.0, 0.0, 0.0])
        assert result == [0.0, 0.0, 0.0]
    
    def test_random_functions(self, simulator):
        """Test random number generation."""
        # Test range
        for _ in range(100):
            result = simulator.api_llFrand(10.0)
            assert 0.0 <= result <= 10.0
        
        # Test modular arithmetic
        result = simulator.api_llModPow(2, 3, 5)  # 2^3 mod 5 = 8 mod 5 = 3
        assert result == 3


class TestComprehensiveEncodingFunctions:
    """Test suite for encoding/decoding functions."""
    
    @pytest.mark.parametrize("func_name,args,operation", [
        ("api_llBase64ToString", ["SGVsbG8gV29ybGQ="], "decode"),  # "Hello World"
        ("api_llStringToBase64", ["Hello World"], "encode"),
        ("api_llEscapeURL", ["hello world!"], "url_encode"),
        ("api_llUnescapeURL", ["hello%20world%21"], "url_decode"),
    ])
    def test_encoding_functions(self, simulator, func_name, args, operation):
        """Test string encoding/decoding functions."""
        func = getattr(simulator, func_name)
        result = func(*args)
        
        if operation == "decode":
            assert result == "Hello World"
        elif operation == "encode":
            assert isinstance(result, str)
            assert len(result) > 0
        elif operation == "url_encode":
            assert " " not in result
            assert "!" not in result
        elif operation == "url_decode":
            assert result == "hello world!"
    
    def test_hash_functions(self, simulator):
        """Test cryptographic hash functions."""
        # MD5 with nonce
        result = simulator.api_llMD5String("test", 12345)
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hex length
        
        # SHA1
        result = simulator.api_llSHA1String("test")
        assert isinstance(result, str)
        assert len(result) == 40  # SHA1 hex length
    
    def test_character_functions(self, simulator):
        """Test character manipulation functions."""
        # Character to code
        result = simulator.api_llOrd("A", 0)
        assert result == 65
        
        # Code to character
        result = simulator.api_llChar(65)
        assert result == "A"
        
        # Out of bounds
        result = simulator.api_llOrd("Hello", 10)
        assert result == 0


class TestComprehensiveJSONFunctions:
    """Test suite for JSON functions."""
    
    def test_json_get_value_comprehensive(self, simulator):
        """Test comprehensive JSON value retrieval."""
        json_str = '{"name": "test", "count": 42, "items": [1, 2, 3], "nested": {"key": "value"}}'
        
        # Simple key access
        assert simulator.api_llJsonGetValue(json_str, "name") == "test"
        assert simulator.api_llJsonGetValue(json_str, "count") == "42"
        
        # Non-existent key
        assert simulator.api_llJsonGetValue(json_str, "nonexistent") == "invalid"
        
        # Invalid JSON
        assert simulator.api_llJsonGetValue("invalid json", "key") == "invalid"
    
    def test_json_list_conversion(self, simulator):
        """Test JSON to list conversion."""
        # Array conversion
        result = simulator.api_llJson2List('[1, 2, 3]')
        assert result == [1, 2, 3]
        
        # Object conversion
        result = simulator.api_llJson2List('{"a": 1, "b": 2}')
        assert len(result) == 4  # Should be [key1, value1, key2, value2]
        
        # Invalid JSON
        result = simulator.api_llJson2List('invalid')
        assert result == []


class TestComprehensiveTimeFunctions:
    """Test suite for time and date functions."""
    
    def test_time_functions(self, simulator):
        """Test time-related functions."""
        # Unix time should be reasonable
        unix_time = simulator.api_llGetUnixTime()
        assert isinstance(unix_time, int)
        assert unix_time > 1600000000  # After 2020
        
        # Time of day should be between 0 and 1
        time_of_day = simulator.api_llGetTimeOfDay()
        assert isinstance(time_of_day, float)
        assert 0.0 <= time_of_day <= 1.0
        
        # Date should be valid format
        date = simulator.api_llGetDate()
        assert isinstance(date, str)
        assert len(date) == 10  # YYYY-MM-DD
        assert date.count('-') == 2
        
        # Timestamp should be ISO format
        timestamp = simulator.api_llGetTimestamp()
        assert isinstance(timestamp, str)
        assert 'T' in timestamp
        assert timestamp.endswith('Z')


class TestComprehensiveObjectFunctions:
    """Test suite for object manipulation functions."""
    
    def test_position_functions(self, simulator):
        """Test position-related functions."""
        pos = simulator.api_llGetPos()
        assert isinstance(pos, list)
        assert len(pos) == 3
        assert all(isinstance(x, (int, float)) for x in pos)
        
        # Test bounding box
        bbox = simulator.api_llGetBoundingBox("test-key")
        assert isinstance(bbox, list)
        assert len(bbox) == 2  # [min_corner, max_corner]
    
    def test_rotation_functions(self, simulator):
        """Test rotation-related functions."""
        # Euler to rotation conversion
        euler = [0.0, 0.0, 0.0]
        rot = simulator.api_llEuler2Rot(euler)
        assert isinstance(rot, list)
        assert len(rot) == 4
        
        # Rotation to Euler conversion
        rotation = [0.0, 0.0, 0.0, 1.0]
        euler_result = simulator.api_llRot2Euler(rotation)
        assert isinstance(euler_result, list)
        assert len(euler_result) == 3
    
    def test_scale_and_mass(self, simulator):
        """Test scale and mass functions."""
        scale = simulator.api_llGetScale()
        assert isinstance(scale, list)
        assert len(scale) == 3
        
        mass = simulator.api_llGetMass()
        assert isinstance(mass, (int, float))
        assert mass > 0


class TestComprehensiveInventoryFunctions:
    """Test suite for inventory functions."""
    
    def test_inventory_queries(self, simulator):
        """Test inventory query functions."""
        # Inventory count
        count = simulator.api_llGetInventoryNumber(7)  # INVENTORY_NOTECARD
        assert isinstance(count, int)
        assert count >= 0
        
        # Inventory name
        name = simulator.api_llGetInventoryName(7, 0)
        assert isinstance(name, str)
        
        # Inventory type
        inv_type = simulator.api_llGetInventoryType("test_item")
        assert isinstance(inv_type, int)
        
        # Inventory key
        key = simulator.api_llGetInventoryKey("test_item")
        assert isinstance(key, str)


class TestComprehensivePerformance:
    """Performance tests for comprehensive API."""
    
    def test_function_call_performance(self, simulator):
        """Test performance of comprehensive API function calls."""
        import time
        
        # Test string function performance
        start_time = time.time()
        for i in range(1000):
            simulator.api_llStringLength(f"performance test {i}")
        string_time = time.time() - start_time
        assert string_time < 1.0  # Should be fast
        
        # Test math function performance
        start_time = time.time()
        for i in range(1000):
            simulator.api_llVecMag([float(i), float(i+1), float(i+2)])
        math_time = time.time() - start_time
        assert math_time < 1.0  # Should be fast
        
        # Test list function performance
        start_time = time.time()
        test_list = list(range(100))
        for i in range(100):
            simulator.api_llGetListLength(test_list)
        list_time = time.time() - start_time
        assert list_time < 0.5  # Should be very fast
    
    def test_api_delegation_performance(self, simulator):
        """Test performance of API delegation mechanism."""
        import time
        
        start_time = time.time()
        for i in range(1000):
            # Test that delegation doesn't add significant overhead
            simulator.api_llStringLength("test")
        delegation_time = time.time() - start_time
        assert delegation_time < 1.0
    
    def test_large_data_performance(self, simulator):
        """Test performance with large data sets."""
        # Large list operations
        large_list = list(range(10000))
        
        start_time = time.time()
        length = simulator.api_llGetListLength(large_list)
        list_time = time.time() - start_time
        
        assert length == 10000
        assert list_time < 0.1  # Should handle large lists efficiently
        
        # Large string operations
        large_string = "x" * 10000
        
        start_time = time.time()
        length = simulator.api_llStringLength(large_string)
        string_time = time.time() - start_time
        
        assert length == 10000
        assert string_time < 0.1  # Should handle large strings efficiently


class TestComprehensiveIntegration:
    """Integration tests for comprehensive API."""
    
    def test_function_chaining(self, simulator):
        """Test chaining multiple API functions."""
        # String processing chain
        original = "  Hello World  "
        trimmed = simulator.api_llStringTrim(original, 0)
        upper = simulator.api_llToUpper(trimmed)
        length = simulator.api_llStringLength(upper)
        
        assert trimmed == "Hello World"
        assert upper == "HELLO WORLD"
        assert length == 11
    
    def test_data_transformation_pipeline(self, simulator):
        """Test complex data transformation using multiple functions."""
        # Create data
        data = [1, 2, 3, 4, 5]
        
        # Transform data
        json_str = simulator.api_llList2Json("array", data)
        parsed_back = simulator.api_llJson2List(json_str)
        list_length = simulator.api_llGetListLength(parsed_back)
        
        assert isinstance(json_str, str)
        assert parsed_back == data
        assert list_length == 5
    
    def test_comprehensive_api_coverage(self, simulator):
        """Test that we have comprehensive API coverage."""
        # Test that functions from both API parts are available
        
        # From comprehensive_lsl_api.py
        assert hasattr(simulator.comprehensive_api, 'api_llStringLength')
        assert hasattr(simulator.comprehensive_api, 'api_llVecMag')
        assert hasattr(simulator.comprehensive_api, 'api_llList2Json')
        
        # From comprehensive_lsl_api_part2.py
        assert hasattr(simulator.comprehensive_api_part2, 'api_llHTTPRequest')
        assert hasattr(simulator.comprehensive_api_part2, 'api_llGetTime')
        assert hasattr(simulator.comprehensive_api_part2, 'api_llGetPos')
        
        # Test delegation works
        assert simulator.api_llStringLength("test") == 4
        assert isinstance(simulator.api_llGetPos(), list)