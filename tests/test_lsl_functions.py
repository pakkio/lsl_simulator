"""
Professional tests for LSL API Functions.
Comprehensive test suite for all implemented LSL functions.
This test suite drives the requirement for 90% LSL function coverage.
"""

import pytest
import math
import json
import time
from unittest.mock import Mock, patch


class TestStringFunctions:
    """Test suite for LSL string functions."""
    
    @pytest.mark.parametrize("func_name,args,expected", [
        ("llStringLength", ["Hello"], 5),
        ("llStringLength", [""], 0),
        ("llStringLength", ["Hello World"], 11),
        ("llGetSubString", ["Hello World", 0, 4], "Hello"),
        ("llGetSubString", ["Hello World", 6, 10], "World"),
        ("llGetSubString", ["Hello World", 0, -1], "Hello World"),
        ("llSubStringIndex", ["Hello World", "World"], 6),
        ("llSubStringIndex", ["Hello World", "xyz"], -1),
        ("llStringTrim", [" Hello World ", 0], "Hello World"),
    ])
    def test_string_functions(self, simulator, func_name, args, expected):
        """Test string manipulation functions."""
        result = simulator._call_api_function(func_name, args)
        assert result == expected


class TestListFunctions:
    """Test suite for LSL list functions."""
    
    @pytest.mark.parametrize("func_name,args,expected", [
        ("llGetListLength", [[]], 0),
        ("llGetListLength", [[1, 2, 3]], 3),
        ("llGetListLength", [["a", "b", "c", "d"]], 4),
        ("llList2String", [[1, 2, 3], 0], "1"),
        ("llList2String", [[1, 2, 3], 1], "2"),
        ("llList2String", [[1, 2, 3], 5], ""),  # Out of bounds
        ("llDumpList2String", [[1, 2, 3], ","], "1,2,3"),
        ("llDumpList2String", [["a", "b", "c"], "|"], "a|b|c"),
        ("llListFindList", [[1, 2, 3, 4], [2, 3]], 1),
        ("llListFindList", [[1, 2, 3, 4], [5, 6]], -1),
    ])
    def test_list_functions(self, simulator, func_name, args, expected):
        """Test list manipulation functions."""
        result = simulator._call_api_function(func_name, args)
        assert result == expected
    
    def test_list_sort(self, simulator):
        """Test llListSort function."""
        # Simple sort
        result = simulator.api_llListSort([3, 1, 4, 1, 5], 1, True)
        assert result == [1, 1, 3, 4, 5]
        
        # Reverse sort
        result = simulator.api_llListSort([3, 1, 4, 1, 5], 1, False)
        assert result == [5, 4, 3, 1, 1]
        
        # Stride sort
        result = simulator.api_llListSort([3, "three", 1, "one", 2, "two"], 2, True)
        assert result == [1, "one", 2, "two", 3, "three"]


class TestMathFunctions:
    """Test suite for LSL math functions."""
    
    @pytest.mark.parametrize("func_name,args,expected", [
        ("llVecMag", [[3.0, 4.0, 0.0]], 5.0),
        ("llVecMag", [[1.0, 1.0, 1.0]], math.sqrt(3)),
        ("llVecNorm", [[10.0, 0.0, 0.0]], [1.0, 0.0, 0.0]),
        ("llVecNorm", [[0.0, 5.0, 0.0]], [0.0, 1.0, 0.0]),
    ])
    def test_vector_functions(self, simulator, func_name, args, expected):
        """Test vector math functions."""
        result = simulator._call_api_function(func_name, args)
        
        if isinstance(expected, list):
            assert len(result) == len(expected)
            for i in range(len(expected)):
                assert abs(result[i] - expected[i]) < 0.0001
        else:
            assert abs(result - expected) < 0.0001


class TestJSONFunctions:
    """Test suite for LSL JSON functions."""
    
    def test_list_to_json_array(self, simulator):
        """Test llList2Json with JSON_ARRAY."""
        result = simulator.api_llList2Json("array", [1, 2, 3])
        expected = json.dumps([1, 2, 3])
        assert result == expected
    
    def test_list_to_json_object(self, simulator):
        """Test llList2Json with JSON_OBJECT."""
        result = simulator.api_llList2Json("object", ["key1", "value1", "key2", "value2"])
        parsed = json.loads(result)
        assert parsed["key1"] == "value1"
        assert parsed["key2"] == "value2"
    
    def test_list_to_json_invalid(self, simulator):
        """Test llList2Json with invalid input."""
        # Odd number of elements for object
        result = simulator.api_llList2Json("object", ["key1", "value1", "key2"])
        assert result == "invalid"
        
        # Invalid type hint
        result = simulator.api_llList2Json("invalid_type", [1, 2, 3])
        assert result == "invalid"
    
    def test_json_get_value(self, simulator):
        """Test llJsonGetValue function."""
        json_str = '{"name": "test", "count": 42, "items": [1, 2, 3]}'
        
        # Test simple key access
        result = simulator.api_llJsonGetValue(json_str, "name")
        assert result == "test"
        
        result = simulator.api_llJsonGetValue(json_str, "count")
        assert result == "42"
        
        # Test non-existent key
        result = simulator.api_llJsonGetValue(json_str, "nonexistent")
        assert result == "invalid"
        
        # Test invalid JSON
        result = simulator.api_llJsonGetValue("invalid json", "key")
        assert result == "invalid"


class TestHTTPFunctions:
    """Test suite for LSL HTTP functions."""
    
    def test_http_request_get(self, simulator):
        """Test llHTTPRequest GET."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"result": "success"}'
            mock_get.return_value = mock_response
            
            request_key = simulator.api_llHTTPRequest(
                "https://httpbin.org/get", 
                [], 
                ""
            )
            
            assert request_key is not None
            assert request_key.startswith("http-key-")
            mock_get.assert_called_once()
    
    def test_http_request_post(self, simulator):
        """Test llHTTPRequest POST."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.text = '{"created": true}'
            mock_post.return_value = mock_response
            
            request_key = simulator.api_llHTTPRequest(
                "https://httpbin.org/post",
                ["method", "POST", "mimetype", "application/json"],
                '{"test": "data"}'
            )
            
            assert request_key is not None
            assert request_key.startswith("http-key-")
            mock_post.assert_called_once()


class TestTimerFunctions:
    """Test suite for LSL timer functions."""
    
    def test_timer_event(self, simulator):
        """Test llSetTimerEvent."""
        # Test setting timer
        simulator.api_llSetTimerEvent(0.1)
        
        # Timer should be set (we can't easily test the async firing)
        # But at least it shouldn't crash
        
        # Test disabling timer
        simulator.api_llSetTimerEvent(0.0)


class TestInventoryFunctions:
    """Test suite for LSL inventory functions."""
    
    def test_inventory_type(self, simulator):
        """Test llGetInventoryType."""
        result = simulator.api_llGetInventoryType("test_notecard")
        assert result == 7  # INVENTORY_NOTECARD
    
    def test_notecard_reading(self, simulator, temp_notecard):
        """Test llGetNotecardLine."""
        import shutil
        import os
        
        # Copy temp file to expected location
        shutil.copy(temp_notecard, "test_notecard.txt")
        
        try:
            request_key = simulator.api_llGetNotecardLine("test_notecard", 0)
            
            assert request_key is not None
            assert request_key.startswith("notecard-key-")
            
            # Check that dataserver event was queued
            dataserver_events = [e for e in simulator.event_queue if e[0] == "dataserver"]
            assert len(dataserver_events) > 0
            
            event_name, args = dataserver_events[0]
            assert args[0] == request_key
            assert "Line 1" in args[1]
            
        finally:
            try:
                os.unlink("test_notecard.txt")
            except FileNotFoundError:
                pass


class TestCommunicationFunctions:
    """Test suite for LSL communication functions."""
    
    def test_say_function(self, simulator, capsys):
        """Test llSay function."""
        simulator.api_llSay(0, "Hello World")
        
        captured = capsys.readouterr()
        assert "Hello World" in captured.out
    
    def test_region_say(self, simulator, capsys):
        """Test llRegionSay function."""
        simulator.api_llRegionSay(5, "Region message")
        
        captured = capsys.readouterr()
        assert "Region message" in captured.out
        assert "Channel 5" in captured.out
    
    def test_instant_message(self, simulator, capsys):
        """Test llInstantMessage function."""
        simulator.api_llInstantMessage("test-avatar-key", "Private message")
        
        captured = capsys.readouterr()
        assert "Private message" in captured.out
        assert "test-avatar-key" in captured.out
    
    def test_listen_functionality(self, simulator):
        """Test llListen function."""
        handle = simulator.api_llListen(0, "", "", "")
        
        assert handle is not None
        assert handle.startswith("listen-handle-")
        assert len(simulator.active_listeners) == 1
        
        listener = simulator.active_listeners[0]
        assert listener['channel'] == 0
        assert listener['active'] is True
    
    def test_listen_control(self, simulator):
        """Test llListenControl function."""
        handle = simulator.api_llListen(0, "", "", "")
        
        # Disable listener
        simulator.api_llListenControl(handle, False)
        
        listener = simulator.active_listeners[0]
        assert listener['active'] is False
        
        # Re-enable listener
        simulator.api_llListenControl(handle, True)
        assert listener['active'] is True
    
    def test_listen_remove(self, simulator):
        """Test llListenRemove function."""
        handle = simulator.api_llListen(0, "", "", "")
        assert len(simulator.active_listeners) == 1
        
        simulator.api_llListenRemove(handle)
        assert len(simulator.active_listeners) == 0


class TestSensorFunctions:
    """Test suite for LSL sensor functions."""
    
    def test_sensor_repeat(self, simulator, capsys):
        """Test llSensorRepeat function."""
        simulator.api_llSensorRepeat("", "", 1, 10.0, 3.14, 2.0)
        
        captured = capsys.readouterr()
        assert "Repeating scan" in captured.out
    
    def test_sensor_remove(self, simulator, capsys):
        """Test llSensorRemove function."""
        simulator.api_llSensorRemove()
        
        captured = capsys.readouterr()
        assert "Sensor removed" in captured.out
    
    def test_detected_functions(self, simulator):
        """Test llDetectedKey and llDetectedDist functions."""
        # Set up detected avatar
        simulator.sensed_avatar_key = "test-avatar-key"
        
        key = simulator.api_llDetectedKey(0)
        assert key == "test-avatar-key"
        
        dist = simulator.api_llDetectedDist(0)
        assert isinstance(dist, (int, float))
        assert dist >= 0


class TestUtilityFunctions:
    """Test suite for LSL utility functions."""
    
    def test_get_functions(self, simulator):
        """Test llGet* functions."""
        assert simulator.api_llGetOwner() == "npc-owner-uuid-12345"
        assert simulator.api_llGetKey() == "object-uuid-67890"
        assert simulator.api_llGetRegionName() == "Test Region"
        
        # Time functions
        time_result = simulator.api_llGetTime()
        assert isinstance(time_result, (int, float))
        
        unix_time = simulator.api_llGetUnixTime()
        assert isinstance(unix_time, int)
        assert unix_time > 0
    
    def test_position_functions(self, simulator):
        """Test position-related functions."""
        pos = simulator.api_llGetPos()
        assert isinstance(pos, list)
        assert len(pos) == 3
        assert all(isinstance(x, (int, float)) for x in pos)
    
    def test_key_to_name(self, simulator):
        """Test llKey2Name function."""
        # Test owner key
        owner_key = simulator.api_llGetOwner()
        name = simulator.api_llKey2Name(owner_key)
        assert name == "Test User"
        
        # Test sensed avatar
        simulator.sensed_avatar_key = "test-key"
        simulator.sensed_avatar_name = "Test Avatar"
        name = simulator.api_llKey2Name("test-key")
        assert name == "Test Avatar"
        
        # Test unknown key
        name = simulator.api_llKey2Name("unknown-key")
        assert name == "Unknown User"
    
    def test_object_details(self, simulator):
        """Test llGetObjectDetails function."""
        details = simulator.api_llGetObjectDetails("test-key", [1])  # OBJECT_POS
        assert isinstance(details, list)
        assert len(details) == 1
        assert isinstance(details[0], list)
        assert len(details[0]) == 3
    
    def test_parse_string_to_list(self, simulator):
        """Test llParseString2List function."""
        result = simulator.api_llParseString2List("a,b,c", [","], [])
        assert result == ["a", "b", "c"]
        
        result = simulator.api_llParseString2List("a|b|c", ["|"], [])
        assert result == ["a", "b", "c"]
        
        # Test with no separators
        result = simulator.api_llParseString2List("abc", [], [])
        assert result == ["abc"]
    
    def test_list_to_vector(self, simulator):
        """Test llList2Vector function."""
        result = simulator.api_llList2Vector([1.0, 2.0, 3.0])
        assert result == [1.0, 2.0, 3.0]
        
        # Test with insufficient elements
        result = simulator.api_llList2Vector([1.0, 2.0])
        assert result == [0.0, 0.0, 0.0]  # Should return zero vector
        
        # Test with more than 3 elements
        result = simulator.api_llList2Vector([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result == [1.0, 2.0, 3.0]  # Should take first 3


class TestNPCFunctions:
    """Test suite for LSL NPC functions (OpenSimulator)."""
    
    def test_is_npc(self, simulator, capsys):
        """Test osIsNpc function."""
        result = simulator.api_osIsNpc("test-key")
        assert result is True
        
        captured = capsys.readouterr()
        assert "osIsNpc" in captured.out
    
    def test_npc_create(self, simulator, capsys):
        """Test osNpcCreate function."""
        npc_key = simulator.api_osNpcCreate("John", "Doe", [128, 128, 25], "owner-key")
        
        assert npc_key is not None
        assert isinstance(npc_key, str)
        assert "npc-John-Doe" in npc_key
        
        captured = capsys.readouterr()
        assert "Created John Doe" in captured.out
    
    def test_npc_say(self, simulator, capsys):
        """Test osNpcSay function."""
        simulator.api_osNpcSay("npc-key", "Hello from NPC")
        
        captured = capsys.readouterr()
        assert "Hello from NPC" in captured.out


class TestErrorHandling:
    """Test suite for error handling in LSL functions."""
    
    def test_function_not_found(self, simulator):
        """Test calling non-existent function."""
        result = simulator._call_api_function("llNonExistentFunction", [])
        assert result is None
    
    def test_invalid_arguments(self, simulator):
        """Test functions with invalid arguments."""
        # Too many arguments
        result = simulator.api_llStringLength("test", "extra", "args")
        # Should not crash, might return something reasonable
        
        # Wrong argument types
        result = simulator.api_llGetListLength("not_a_list")
        assert result == 0  # Should handle gracefully
    
    def test_division_by_zero_in_expressions(self, simulator):
        """Test division by zero handling."""
        result = simulator._evaluate_expression("10 / 0")
        assert result == 0  # Should handle gracefully
        
        result = simulator._evaluate_expression("10 % 0")
        assert result == 0  # Should handle gracefully


class TestPerformance:
    """Test suite for performance characteristics."""
    
    def test_function_call_performance(self, simulator):
        """Test performance of function calls."""
        import time
        
        start_time = time.time()
        for i in range(1000):
            simulator.api_llStringLength(f"test string {i}")
        
        execution_time = time.time() - start_time
        assert execution_time < 1.0  # Should complete in under 1 second
    
    def test_expression_evaluation_performance(self, simulator):
        """Test performance of expression evaluation."""
        import time
        
        start_time = time.time()
        for i in range(1000):
            simulator._evaluate_expression(f'llStringLength("test {i}")')
        
        execution_time = time.time() - start_time
        assert execution_time < 2.0  # Should complete in reasonable time
    
    def test_large_list_performance(self, simulator):
        """Test performance with large lists."""
        large_list = list(range(1000))
        
        start_time = time.time()
        length = simulator.api_llGetListLength(large_list)
        execution_time = time.time() - start_time
        
        assert length == 1000
        assert execution_time < 0.1  # Should be very fast


class TestIntegration:
    """Integration tests combining multiple LSL functions."""
    
    def test_http_json_integration(self, simulator):
        """Test HTTP request with JSON processing."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"message": "success", "id": 123}'
            mock_post.return_value = mock_response
            
            # Create JSON payload
            payload = simulator.api_llList2Json("object", [
                "name", "test",
                "value", 42
            ])
            
            # Make HTTP request
            request_key = simulator.api_llHTTPRequest(
                "https://api.example.com/data",
                ["method", "POST", "mimetype", "application/json"],
                payload
            )
            
            assert request_key is not None
            
            # Check that response was parsed
            events = [e for e in simulator.event_queue if e[0] == "http_response"]
            assert len(events) > 0
    
    def test_avatar_communication_integration(self, simulator):
        """Test avatar sensing and communication integration."""
        # Set up listener
        handle = simulator.api_llListen(0, "", "", "hello")
        
        # Simulate avatar approach
        simulator.simulate_avatar_sense("Test User")
        
        # Simulate avatar speaking
        simulator.say_on_channel(0, "hello", "Test User", "test-key")
        
        # Check events were queued
        sensor_events = [e for e in simulator.event_queue if e[0] == "sensor"]
        listen_events = [e for e in simulator.event_queue if e[0] == "listen"]
        
        assert len(sensor_events) > 0
        assert len(listen_events) > 0
    
    def test_notecard_processing_integration(self, simulator, temp_notecard):
        """Test notecard reading and processing."""
        import shutil
        import os
        
        # Copy temp file
        shutil.copy(temp_notecard, "config.txt")
        
        try:
            # Read first line
            request_key = simulator.api_llGetNotecardLine("config", 0)
            
            # Check dataserver event
            events = [e for e in simulator.event_queue if e[0] == "dataserver"]
            assert len(events) > 0
            
            event_name, args = events[0]
            assert args[0] == request_key
            content = args[1]
            
            # Process the content
            length = simulator.api_llStringLength(content)
            assert length > 0
            
        finally:
            try:
                os.unlink("config.txt")
            except FileNotFoundError:
                pass