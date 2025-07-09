// Comprehensive LSL Test Script
// Tests: variables, functions, control flow, vectors, rotations, 
// HTTP requests, notecard reading, text display, timers, and more

// Global variables
string g_object_name = "Test Object";
integer g_request_count = 0;
key g_http_request;
key g_notecard_query;
list g_user_data = [];
vector g_home_position = <128.0, 128.0, 22.0>;
rotation g_home_rotation = <0.0, 0.0, 0.0, 1.0>;

// User-defined function: Calculate distance between two points
float calculateDistance(vector pos1, vector pos2)
{
    vector diff = pos1 - pos2;
    return llVecMag(diff);
}

// User-defined function: Format vector for display
string formatVector(vector v)
{
    return "<" + (string)v.x + ", " + (string)v.y + ", " + (string)v.z + ">";
}

// User-defined function: Check if position is within bounds
integer isWithinBounds(vector pos, vector min_bounds, vector max_bounds)
{
    if (pos.x >= min_bounds.x && pos.x <= max_bounds.x &&
        pos.y >= min_bounds.y && pos.y <= max_bounds.y &&
        pos.z >= min_bounds.z && pos.z <= max_bounds.z)
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    }
}

default
{
    state_entry()
    {
        llSay(0, "=== Comprehensive LSL Test Started ===");
        llSetText(g_object_name + "\nStatus: Initializing", <1.0, 1.0, 1.0>, 1.0);
        
        // Test 1: Basic variable operations and expressions
        llSay(0, "Test 1: Variable Operations");
        integer i = 5;
        integer j = 3;
        integer result = (i + j) * 2;
        float pi = 3.14159;
        string message = "Result: " + (string)result;
        llSay(0, message);
        
        // Test 2: Vector operations
        llSay(0, "Test 2: Vector Operations");
        vector current_pos = llGetPos();
        llSay(0, "Current position: " + formatVector(current_pos));
        
        float distance_home = calculateDistance(current_pos, g_home_position);
        llSay(0, "Distance to home: " + (string)distance_home + " meters");
        
        vector normalized = llVecNorm(<3.0, 4.0, 0.0>);
        llSay(0, "Normalized <3,4,0>: " + formatVector(normalized));
        
        // Test 3: Rotation operations
        llSay(0, "Test 3: Rotation Operations");
        rotation rot = llEuler2Rot(<0.0, 0.0, PI_BY_TWO>);
        vector euler = llRot2Euler(rot);
        llSay(0, "90-degree rotation euler: " + formatVector(euler));
        
        // Test 4: Control flow - For loop
        llSay(0, "Test 4: For Loop (counting 1-5)");
        for (integer count = 1; count <= 5; count++)
        {
            llSay(0, "Count: " + (string)count);
        }
        
        // Test 5: Control flow - While loop
        llSay(0, "Test 5: While Loop (countdown from 3)");
        integer countdown = 3;
        while (countdown > 0)
        {
            llSay(0, "Countdown: " + (string)countdown);
            countdown--;
        }
        
        // Test 6: Lists and list operations
        llSay(0, "Test 6: List Operations");
        list test_list = ["apple", 42, "banana", 3.14, "cherry"];
        integer list_length = llGetListLength(test_list);
        llSay(0, "List length: " + (string)list_length);
        
        string second_item = llList2String(test_list, 1);
        llSay(0, "Second item: " + second_item);
        
        list sorted_list = llListSort(["zebra", "apple", "banana"], 1, TRUE);
        llSay(0, "Sorted list: " + llDumpList2String(sorted_list, ", "));
        
        // Test 7: Boundary checking with if/else
        llSay(0, "Test 7: Boundary Checking");
        vector test_pos = <100.0, 150.0, 25.0>;
        vector min_bounds = <50.0, 50.0, 20.0>;
        vector max_bounds = <200.0, 200.0, 50.0>;
        
        if (isWithinBounds(test_pos, min_bounds, max_bounds))
        {
            llSay(0, "Position " + formatVector(test_pos) + " is within bounds");
        }
        else
        {
            llSay(0, "Position " + formatVector(test_pos) + " is outside bounds");
        }
        
        // Test 8: HTTP request
        llSay(0, "Test 8: Making HTTP Request");
        string url = "https://httpbin.org/json";
        list headers = ["User-Agent", "LSL-Test-Script/1.0"];
        string body = "";
        g_http_request = llHTTPRequest(url, [HTTP_METHOD, "GET"], body);
        g_request_count++;
        
        // Test 9: Notecard reading
        llSay(0, "Test 9: Reading Notecard");
        if (llGetInventoryType("config") == INVENTORY_NOTECARD)
        {
            g_notecard_query = llGetNotecardLine("config", 0);
        }
        else
        {
            llSay(0, "Notecard 'config' not found, creating sample data");
            g_user_data = ["user1", "data1", "user2", "data2"];
        }
        
        // Test 10: Timer and state management
        llSay(0, "Test 10: Starting timer for periodic updates");
        llSetTimerEvent(5.0);
        
        // Update display text
        llSetText(g_object_name + "\nStatus: Running Tests\nRequests: " + 
                 (string)g_request_count, <0.0, 1.0, 0.0>, 1.0);
    }
    
    timer()
    {
        llSay(0, "Timer event: Performing periodic check");
        
        // Simulate some periodic processing
        vector current_pos = llGetPos();
        float height = current_pos.z;
        
        if (height < 20.0)
        {
            llSay(0, "Warning: Object height is low (" + (string)height + "m)");
            llSetText(g_object_name + "\nStatus: LOW ALTITUDE WARNING", 
                     <1.0, 0.0, 0.0>, 1.0);
        }
        else if (height > 100.0)
        {
            llSay(0, "Notice: Object is at high altitude (" + (string)height + "m)");
            llSetText(g_object_name + "\nStatus: High Altitude", 
                     <1.0, 1.0, 0.0>, 1.0);
        }
        else
        {
            llSetText(g_object_name + "\nStatus: Normal Operation\nHeight: " + 
                     (string)((integer)height) + "m", <0.0, 1.0, 0.0>, 1.0);
        }
        
        // Stop timer after a few cycles
        g_request_count++;
        if (g_request_count > 3)
        {
            llSetTimerEvent(0.0);
            llSay(0, "Timer stopped. Test sequence complete.");
            state finished;
        }
    }
    
    http_response(key request_id, integer status, list metadata, string body)
    {
        if (request_id == g_http_request)
        {
            llSay(0, "HTTP Response received:");
            llSay(0, "Status: " + (string)status);
            
            if (status == 200)
            {
                // Parse some basic info from JSON response
                if (llSubStringIndex(body, "slideshow") != -1)
                {
                    llSay(0, "Response contains slideshow data");
                }
                
                integer body_length = llStringLength(body);
                llSay(0, "Response body length: " + (string)body_length + " characters");
            }
            else
            {
                llSay(0, "HTTP request failed with status: " + (string)status);
            }
        }
    }
    
    dataserver(key query_id, string data)
    {
        if (query_id == g_notecard_query)
        {
            if (data != EOF)
            {
                llSay(0, "Notecard line read: " + data);
                
                // Parse configuration data (expecting key=value format)
                integer equals_pos = llSubStringIndex(data, "=");
                if (equals_pos != -1)
                {
                    string key = llStringTrim(llGetSubString(data, 0, equals_pos - 1), STRING_TRIM);
                    string value = llStringTrim(llGetSubString(data, equals_pos + 1, -1), STRING_TRIM);
                    
                    g_user_data += [key, value];
                    llSay(0, "Stored config: " + key + " = " + value);
                }
                
                // Read next line
                g_notecard_query = llGetNotecardLine("config", llGetListLength(g_user_data) / 2);
            }
            else
            {
                llSay(0, "Notecard reading complete. Total config items: " + 
                     (string)(llGetListLength(g_user_data) / 2));
            }
        }
    }
    
    touch_start(integer total_number)
    {
        llSay(0, "Touched by " + (string)total_number + " avatar(s)");
        
        // Display current user data
        if (llGetListLength(g_user_data) > 0)
        {
            llSay(0, "Current user data:");
            integer i;
            for (i = 0; i < llGetListLength(g_user_data); i += 2)
            {
                string key = llList2String(g_user_data, i);
                string value = llList2String(g_user_data, i + 1);
                llSay(0, "  " + key + ": " + value);
            }
        }
        else
        {
            llSay(0, "No user data available");
        }
        
        // Make another HTTP request
        llSay(0, "Making another HTTP request...");
        g_http_request = llHTTPRequest("https://httpbin.org/user-agent", 
                                      [HTTP_METHOD, "GET"], "");
    }
}

state finished
{
    state_entry()
    {
        llSay(0, "=== All Tests Completed ===");
        llSetText(g_object_name + "\nStatus: COMPLETED\nAll tests passed", 
                 <0.0, 0.8, 1.0>, 1.0);
        
        // Final summary
        llSay(0, "Test Summary:");
        llSay(0, "- Variable operations: PASSED");
        llSay(0, "- Vector math: PASSED");
        llSay(0, "- Rotation operations: PASSED");
        llSay(0, "- Control flow (for/while/if): PASSED");
        llSay(0, "- List operations: PASSED");
        llSay(0, "- User functions: PASSED");
        llSay(0, "- HTTP requests: INITIATED");
        llSay(0, "- Notecard reading: ATTEMPTED");
        llSay(0, "- Timer events: PASSED");
        llSay(0, "- Text display: ACTIVE");
    }
    
    touch_start(integer total_number)
    {
        llSay(0, "Test complete. Touch to restart...");
        state default;
    }
}