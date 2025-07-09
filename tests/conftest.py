"""
Pytest configuration and fixtures for LSL Simulator tests.
Professional test setup with reusable components.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lsl_antlr_parser import LSLParser
from lsl_simulator_simplified import LSLSimulator


@pytest.fixture(scope="session")
def parser():
    """Session-scoped parser fixture to avoid recreation overhead."""
    return LSLParser()


@pytest.fixture
def simulator():
    """Basic simulator fixture with minimal setup."""
    parsed = {"globals": [], "functions": {}, "states": {}}
    return LSLSimulator(parsed)


@pytest.fixture
def debug_simulator():
    """Simulator with debug mode enabled."""
    parsed = {"globals": [], "functions": {}, "states": {}}
    return LSLSimulator(parsed, debug_mode=True)


@pytest.fixture
def sample_lsl_scripts():
    """Collection of sample LSL scripts for testing."""
    return {
        "minimal": """
            default {
                state_entry() {
                    llSay(0, "Hello World");
                }
            }
        """,
        
        "with_globals": """
            string message = "Test Message";
            integer count = 0;
            
            default {
                state_entry() {
                    llSay(0, message);
                    count = count + 1;
                }
            }
        """,
        
        "with_functions": """
            integer add(integer a, integer b) {
                return a + b;
            }
            
            default {
                state_entry() {
                    integer result = add(5, 3);
                    llSay(0, "Result: " + (string)result);
                }
            }
        """,
        
        "with_timer": """
            integer count = 0;
            
            default {
                state_entry() {
                    llSetTimerEvent(1.0);
                }
                
                timer() {
                    count++;
                    llSay(0, "Timer: " + (string)count);
                    if (count >= 5) {
                        llSetTimerEvent(0.0);
                    }
                }
            }
        """,
        
        "with_http": """
            default {
                state_entry() {
                    llHTTPRequest("https://httpbin.org/get", [], "");
                }
                
                http_response(key request_id, integer status, list metadata, string body) {
                    llSay(0, "HTTP Response: " + (string)status);
                }
            }
        """,
        
        "complex_npc": """
            string npc_name = "TestNPC";
            vector npc_position = <128, 128, 25>;
            integer is_active = TRUE;
            
            speak(string message) {
                if (is_active) {
                    llSay(0, npc_name + ": " + message);
                }
            }
            
            default {
                state_entry() {
                    speak("NPC initialized");
                    llSensorRepeat("", "", AGENT, 10.0, PI, 2.0);
                }
                
                sensor(integer detected) {
                    speak("Avatar detected: " + llDetectedKey(0));
                }
                
                touch_start(integer total_number) {
                    speak("Touched by " + llDetectedKey(0));
                }
            }
        """
    }


@pytest.fixture
def temp_notecard():
    """Temporary notecard file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1: Test content\\n")
        f.write("Line 2: More test content\\n")
        f.write("Line 3: Final line\\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def lsl_constants():
    """Standard LSL constants for testing."""
    return {
        "PI": 3.141592653589793,
        "TWO_PI": 6.283185307179586,
        "PI_BY_TWO": 1.5707963267948966,
        "DEG_TO_RAD": 0.017453292519943295,
        "RAD_TO_DEG": 57.29577951308232,
        "SQRT2": 1.4142135623730951,
        "TRUE": 1,
        "FALSE": 0,
        "NULL_KEY": "00000000-0000-0000-0000-000000000000",
        "EOF": "EOF",
        "ZERO_VECTOR": [0.0, 0.0, 0.0],
        "ZERO_ROTATION": [0.0, 0.0, 0.0, 1.0],
    }


@pytest.fixture
def expression_test_cases():
    """Comprehensive expression test cases."""
    return [
        # Literals
        ("42", 42),
        ("3.14", 3.14),
        ('"Hello World"', "Hello World"),
        ("TRUE", 1),
        ("FALSE", 0),
        
        # Lists and Vectors
        ("[1, 2, 3]", [1, 2, 3]),
        ("<1.0, 2.0, 3.0>", [1.0, 2.0, 3.0]),
        ("<0, 0, 0, 1>", [0.0, 0.0, 0.0, 1.0]),
        
        # Simple arithmetic
        ("5 + 3", 8),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("15 / 3", 5),
        ("17 % 5", 2),
        
        # String operations
        ('"Hello" + " " + "World"', "Hello World"),
        
        # Comparisons
        ("5 == 5", True),
        ("5 != 3", True),
        ("10 > 5", True),
        ("3 < 8", True),
        ("5 >= 5", True),
        ("4 <= 7", True),
        
        # Logical operations
        ("TRUE && TRUE", True),
        ("TRUE || FALSE", True),
        ("FALSE && TRUE", False),
    ]


@pytest.fixture
def lsl_function_test_cases():
    """Test cases for LSL functions."""
    return {
        "string_functions": [
            ("llStringLength", ["Hello"], 5),
            ("llGetSubString", ["Hello World", 0, 4], "Hello"),
            ("llSubStringIndex", ["Hello World", "World"], 6),
            ("llStringTrim", [" Hello World ", 0], "Hello World"),
        ],
        
        "list_functions": [
            ("llGetListLength", [[1, 2, 3, 4, 5]], 5),
            ("llList2String", [[1, 2, 3], 1], "2"),
            ("llDumpList2String", [[1, 2, 3], ","], "1,2,3"),
        ],
        
        "math_functions": [
            ("llVecMag", [[3.0, 4.0, 0.0]], 5.0),
            ("llVecNorm", [[10.0, 0.0, 0.0]], [1.0, 0.0, 0.0]),
        ],
        
        "json_functions": [
            ("llList2Json", ["array", [1, 2, 3]], '[1, 2, 3]'),
            ("llList2Json", ["object", ["key", "value"]], '{"key": "value"}'),
        ],
        
        "utility_functions": [
            ("llGetOwner", [], "npc-owner-uuid-12345"),
            ("llGetKey", [], "object-uuid-67890"),
            ("llGetRegionName", [], "Test Region"),
        ]
    }


@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for testing."""
    return {
        "success": {
            "status_code": 200,
            "text": '{"message": "success", "data": "test"}',
            "headers": {"Content-Type": "application/json"}
        },
        "error": {
            "status_code": 404,
            "text": '{"error": "not found"}',
            "headers": {"Content-Type": "application/json"}
        },
        "timeout": {
            "exception": "requests.exceptions.Timeout"
        }
    }


@pytest.fixture(autouse=True)
def reset_simulator_state():
    """Automatically reset any global state between tests."""
    yield
    # Any cleanup code here if needed


# Performance benchmarking fixtures
@pytest.fixture
def performance_scripts():
    """Scripts for performance testing."""
    return {
        "simple_loop": """
            default {
                state_entry() {
                    integer i;
                    for (i = 0; i < 1000; i++) {
                        llSay(0, "Count: " + (string)i);
                    }
                }
            }
        """,
        
        "complex_expressions": """
            default {
                state_entry() {
                    integer i;
                    for (i = 0; i < 100; i++) {
                        vector pos = llGetPos();
                        float distance = llVecMag(pos - <128, 128, 25>);
                        string message = "Distance: " + (string)distance;
                        llSay(0, message);
                    }
                }
            }
        """
    }


# Error testing fixtures
@pytest.fixture
def error_test_cases():
    """Test cases that should generate specific errors."""
    return {
        "syntax_errors": [
            "invalid syntax here",
            "default { state_entry( { }",  # Missing )
            "integer x = ;",  # Missing value
        ],
        
        "runtime_errors": [
            ("division_by_zero", "10 / 0"),
            ("invalid_function", "llNonExistentFunction()"),
            ("type_error", "llStringLength(123, 456)"),  # Wrong arg count
        ]
    }


@pytest.fixture(scope="session")
def performance_test_data():
    """Generate test data for performance testing."""
    return {
        "small_list": list(range(100)),
        "medium_list": list(range(1000)),
        "large_list": list(range(10000)),
        "small_string": "x" * 100,
        "medium_string": "x" * 1000,
        "large_string": "x" * 10000,
        "test_vectors": [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [3.0, 4.0, 0.0],
            [1.0, 1.0, 1.0]
        ],
        "test_rotations": [
            [0.0, 0.0, 0.0, 1.0],
            [0.707, 0.0, 0.0, 0.707],
            [0.0, 0.707, 0.0, 0.707],
            [0.0, 0.0, 0.707, 0.707]
        ]
    }


@pytest.fixture
def comprehensive_test_script():
    """Provide a comprehensive LSL script for testing."""
    return '''
        // Comprehensive test script
        string message = "Test Message";
        integer count = 0;
        vector position = <128.0, 128.0, 25.0>;
        rotation rot = <0.0, 0.0, 0.0, 1.0>;
        list test_list = [1, 2, 3, "four", 5.0];
        
        string process_string(string input) {
            string trimmed = llStringTrim(input, 0);
            string upper = llToUpper(trimmed);
            return upper;
        }
        
        integer calculate_distance(vector pos1, vector pos2) {
            vector diff = pos1 - pos2;
            float distance = llVecMag(diff);
            return llRound(distance);
        }
        
        default {
            state_entry() {
                llSay(0, "Comprehensive test starting");
                
                // String operations
                string processed = process_string("  hello world  ");
                llOwnerSay("Processed: " + processed);
                
                // Math operations  
                vector test_vec = <3.0, 4.0, 0.0>;
                float magnitude = llVecMag(test_vec);
                llOwnerSay("Vector magnitude: " + (string)magnitude);
                
                // List operations
                integer length = llGetListLength(test_list);
                string json_data = llList2Json("array", test_list);
                llOwnerSay("List length: " + (string)length);
                llOwnerSay("JSON: " + json_data);
                
                // HTTP request
                string url = "https://httpbin.org/get";
                list options = ["method", "GET"];
                string request_key = llHTTPRequest(url, options, "");
                
                // Timer
                llSetTimerEvent(1.0);
            }
            
            timer() {
                count = count + 1;
                llSay(0, "Timer event " + (string)count);
                
                if (count >= 3) {
                    llSetTimerEvent(0.0); // Stop timer
                }
            }
            
            http_response(string request_id, integer status, list metadata, string body) {
                llOwnerSay("HTTP Response: " + (string)status);
                llOwnerSay("Body: " + body);
            }
            
            sensor(integer detected) {
                llSay(0, "Detected " + (string)detected + " objects");
                
                integer i;
                for (i = 0; i < detected; i++) {
                    string name = llDetectedName(i);
                    string key = llDetectedKey(i);
                    float distance = llDetectedDist(i);
                    
                    llOwnerSay("Object " + (string)i + ": " + name + " (" + (string)distance + "m)");
                }
            }
            
            listen(integer channel, string name, string id, string message) {
                llOwnerSay("Heard on channel " + (string)channel + ": " + message);
                
                if (message == "test string functions") {
                    string test = "Hello World";
                    integer len = llStringLength(test);
                    string sub = llGetSubString(test, 0, 4);
                    integer pos = llSubStringIndex(test, "World");
                    
                    llSay(0, "String tests: len=" + (string)len + " sub=" + sub + " pos=" + (string)pos);
                }
                else if (message == "test math functions") {
                    float result1 = llSqrt(16.0);
                    float result2 = llPow(2.0, 3.0);
                    float result3 = llSin(PI_BY_TWO);
                    
                    llSay(0, "Math tests: sqrt(16)=" + (string)result1 + " 2^3=" + (string)result2 + " sin(pi/2)=" + (string)result3);
                }
                else if (message == "test list functions") {
                    list numbers = [5, 2, 8, 1, 9];
                    list sorted_asc = llListSort(numbers, 1, TRUE);
                    list sorted_desc = llListSort(numbers, 1, FALSE);
                    
                    string asc_str = llDumpList2String(sorted_asc, ",");
                    string desc_str = llDumpList2String(sorted_desc, ",");
                    
                    llSay(0, "List tests: asc=" + asc_str + " desc=" + desc_str);
                }
            }
        }
    '''


@pytest.fixture
def api_function_categories():
    """Categorize API functions for systematic testing."""
    return {
        "string_functions": [
            "llStringLength", "llGetSubString", "llSubStringIndex", "llStringTrim",
            "llToUpper", "llToLower", "llStringReplace", "llInsertString",
            "llDeleteSubString", "llEscapeURL", "llUnescapeURL"
        ],
        "list_functions": [
            "llGetListLength", "llList2String", "llList2Integer", "llList2Float",
            "llList2Key", "llList2Vector", "llList2Rot", "llDumpList2String",
            "llParseString2List", "llListSort", "llListRandomize", "llListFindList"
        ],
        "math_functions": [
            "llAbs", "llFabs", "llCeil", "llFloor", "llRound", "llSqrt", "llPow",
            "llLog", "llLog10", "llSin", "llCos", "llTan", "llVecMag", "llVecNorm"
        ],
        "communication_functions": [
            "llSay", "llShout", "llWhisper", "llRegionSay", "llOwnerSay",
            "llInstantMessage", "llListen", "llListenControl", "llListenRemove"
        ],
        "time_functions": [
            "llGetTime", "llGetUnixTime", "llGetTimeOfDay", "llGetDate",
            "llGetTimestamp", "llSetTimerEvent"
        ],
        "object_functions": [
            "llGetPos", "llSetPos", "llGetRot", "llSetRot", "llGetScale",
            "llSetScale", "llGetMass", "llGetVel"
        ],
        "inventory_functions": [
            "llGetInventoryNumber", "llGetInventoryName", "llGetInventoryType",
            "llGetInventoryKey", "llGiveInventory"
        ],
        "http_functions": [
            "llHTTPRequest", "llHTTPResponse", "llRequestURL", "llReleaseURL"
        ],
        "sensor_functions": [
            "llSensor", "llSensorRepeat", "llSensorRemove", "llDetectedName",
            "llDetectedKey", "llDetectedDist", "llDetectedType"
        ],
        "encoding_functions": [
            "llBase64ToString", "llStringToBase64", "llMD5String", "llSHA1String",
            "llChar", "llOrd"
        ],
        "json_functions": [
            "llJsonGetValue", "llList2Json", "llJson2List"
        ]
    }


@pytest.fixture
def test_data_sets():
    """Provide various test data sets for comprehensive testing."""
    return {
        "strings": {
            "empty": "",
            "simple": "hello",
            "with_spaces": "  hello world  ",
            "unicode": "🌟 Unicode test 🚀",
            "long": "x" * 1000,
            "special_chars": "!@#$%^&*()_+-={}|[]\\:;\"'<>?,./",
            "json": '{"key": "value", "number": 42, "array": [1, 2, 3]}'
        },
        "numbers": {
            "integers": [0, 1, -1, 42, -42, 1000, -1000],
            "floats": [0.0, 1.0, -1.0, 3.14, -3.14, 1.234567, -1.234567],
            "large": [1e6, -1e6, 1e-6, -1e-6]
        },
        "lists": {
            "empty": [],
            "integers": [1, 2, 3, 4, 5],
            "floats": [1.1, 2.2, 3.3, 4.4, 5.5],
            "strings": ["a", "b", "c", "d", "e"],
            "mixed": [1, "two", 3.0, "four", 5],
            "nested": [[1, 2], [3, 4], [5, 6]],
            "large": list(range(1000))
        },
        "vectors": {
            "zero": [0.0, 0.0, 0.0],
            "unit_x": [1.0, 0.0, 0.0],
            "unit_y": [0.0, 1.0, 0.0],
            "unit_z": [0.0, 0.0, 1.0],
            "pythagorean": [3.0, 4.0, 0.0],
            "normalized": [0.577, 0.577, 0.577]
        },
        "rotations": {
            "identity": [0.0, 0.0, 0.0, 1.0],
            "x_90": [0.707, 0.0, 0.0, 0.707],
            "y_90": [0.0, 0.707, 0.0, 0.707],
            "z_90": [0.0, 0.0, 0.707, 0.707]
        }
    }